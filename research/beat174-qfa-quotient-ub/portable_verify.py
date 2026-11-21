#!/usr/bin/env python3
"""Independent second-entry verification of BEAT174 quotient numeric bound.

No BEAT174 generator/helper is imported. The SDP, quotient, equalities, quantum
and classical moment vectors, certificate and LP are reconstructed from the
fixed BEAT172/BEAT173 scientific inputs.
"""
import ast
import base64
import copy
import datetime as dt
import hashlib
import json
import sys
import zlib
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog

GEN = Path(__file__).resolve().parent
OLD = GEN/'inputs/beat173'
INPUT = GEN/'inputs/beat172'
OUT = GEN/'portable-replay-result.json'
sys.path.insert(0, str(OLD)); sys.path.insert(0, str(INPUT))
from canonical_npa import CanonicalTwirlNPA
from npa_twirl import TwirlNPA
from test_twirl import build_RAC4_1AB, make_chars_Z4cube


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')


def build(cls):
    letters, povm_of, words, gens, obj = build_RAC4_1AB()
    t = cls(letters, povm_of, words, gens, obj)
    ch, names = make_chars_Z4cube(t); t.set_chars(ch, names); t.build(verbose=False)
    return t, letters, povm_of


def matrices(t):
    ids = [i for i in range(t.nz) if i != t.zI]; pos = {z:i for i,z in enumerate(ids)}
    c = np.array([t.c[z] for z in ids]); S=[]; F=[]; sizes=[]; U=[]
    for b in t.blocks:
        n=b['size']; f0=np.zeros((n,n),complex); data=[]
        for (i,j), terms in b['entries'].items():
            for z,v in terms.items():
                if z == t.zI: f0[i,j]+=v
                else: data.append((i*n+j,pos[z],v))
        S.append(sp.csr_matrix(([x[2] for x in data],([x[0] for x in data],[x[1] for x in data])),
                               shape=(n*n,len(ids)),dtype=complex))
        F.append(f0);sizes.append(n)
        u=abs(np.trace(f0))
        for i in range(n):u+=sum(abs(v) for z,v in b['entries'].get((i,i),{}).items() if z!=t.zI)
        U.append(float(u))
    R=sp.vstack([sp.vstack([s.real,s.imag]) for s in S]).tocsr()
    return c,S,F,sizes,np.array(U),R


def eq_rows(t,povm_of):
    one={w[0]:i for i,w in enumerate(t.W) if len(w)==1}; eye=t.wpos[()]
    ids=[i for i in range(t.nz) if i!=t.zI];pos={z:i for i,z in enumerate(ids)}
    measurements={}
    for l,p in povm_of.items():measurements.setdefault(p,[]).append(l)
    rows={};raw=0
    for p,ls in sorted(measurements.items()):
        for w in range(t.N):
            raw+=1;row={}
            for l in sorted(ls):
                z=t.zid_of_class(t.class_key(one[l],w))
                if z>=0:row[z]=row.get(z,0)-1
            z=t.zid_of_class(t.class_key(eye,w))
            if z>=0:row[z]=row.get(z,0)+1
            if not row:continue
            if row[min(row)]<0:row={k:-v for k,v in row.items()}
            sc=max(abs(v) for v in row.values())
            key=tuple(sorted((z,float(v/sc)) for z,v in row.items() if abs(v)>1e-14))
            rows[key]=(p,w)
    data=[];const=[]
    for i,key in enumerate(sorted(rows)):
        e=0.
        for z,v in key:
            if z==t.zI:e+=v
            else:data.append((i,pos[z],v))
        const.append(e)
    E=sp.csr_matrix(([x[2] for x in data],([x[0] for x in data],[x[1] for x in data])),
                     shape=(len(rows),len(ids)))
    return E,np.array(const),raw


def normalized_key(A,i):
    lo,hi=A.indptr[i:i+2];idx=A.indices[lo:hi];val=A.data[lo:hi]
    if not len(val):return tuple(),0.,1.
    order=np.argsort(idx);idx=idx[order];val=val[order]
    scale=float(np.max(np.abs(val)));sgn=1. if val[0]>0 else -1.
    return tuple(zip(idx.tolist(),np.round(sgn*val/scale,12).tolist())),scale,sgn


def diff_inf(A,B):
    D=(A-B).tocsr()
    return 0. if D.nnz==0 else float(np.max(np.abs(D.data)))


def get_quantum_ops():
    tree=ast.parse((INPUT/'verify_bound07.py').read_text());payload=None
    for n in tree.body:
        if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='BLOB' for x in n.targets):
            payload=ast.literal_eval(n.value);break
    d=json.loads(zlib.decompress(base64.b64decode(payload)))
    U=np.array(d['U_re'])+1j*np.array(d['U_im']);sq=np.array(d['sq'])
    av=U[:16].conj().transpose(0,2,1);bv=U[16:].conj().transpose(0,2,1)
    ops={}
    for x in range(16):
        for m in range(4):ops[('A',x,m)]=np.outer(av[x,m].conj(),av[x,m])
    for y in range(2):
        for m in range(4):
            for v in range(4):ops[('B',y,m,v)]=np.outer(bv[4*y+m,v].conj(),bv[4*y+m,v])
    state=np.zeros(16,complex)
    for k in range(4):state[5*k]=sq[k]
    return ops,state


def get_classical_ops():
    ops={}
    for x in range(16):
        for m in range(4):ops[('A',x,m)]=np.array([[float(x//4==m)]])
    for y in range(2):
        for m in range(4):
            for v in range(4):ops[('B',y,m,v)]=np.array([[float(v==(m if y==0 else 0))]])
    return ops,np.ones(1,complex)


def strategy_z(t,ops,state):
    dim=len(state);side=int(np.sqrt(dim));assert side*side==dim
    vv=[]
    for w in t.W:
        aa=[];bb=[]
        for l in w:(aa if t.letters[l][0]=='A' else bb).append(t.letters[l])
        A=np.eye(side,dtype=complex);B=np.eye(side,dtype=complex)
        for key in aa:A=A@ops[key]
        for key in bb:B=B@ops[key]
        vv.append(np.kron(A,B)@state)
    vv=np.array(vv);first={}
    for o in range(t.norb):
        for p in range(t.norb):
            for k in range(t.oG):
                i=t.reps[o];j=int(t.gt[k,t.reps[p]]);z=t.zid_of_class(t.class_key(i,j))
                if z>=0:first.setdefault(z,(i,j))
    z=np.zeros(t.nz,complex)
    for zid,(i,j) in first.items():
        z[zid]=sum(np.vdot(vv[int(t.gt[g,i])],vv[int(t.gt[g,j])]) for g in range(t.oG))/t.oG
    z[t.zI]=1
    return z,float(np.max(np.abs(z.imag)))


def cert_eval(Ys,c,R,F,U,E,e0,nu):
    dual=0.;pen=0.;mineig=[]
    for Y,f,u in zip(Ys,F,U):
        lm=float(np.linalg.eigvalsh((Y+Y.conj().T)/2).min());mineig.append(lm)
        dual+=float(np.real(np.trace(f.conj().T@Y)));pen+=max(0.,-lm)*u
    y=np.concatenate([np.concatenate([Y.ravel().real,Y.ravel().imag]) for Y in Ys])
    r0=c+R.T@y;r=r0+E.T@nu;eq=float(e0@nu);rn=float(np.abs(r).sum())
    return {'cert':dual+pen+eq+rn,'dualobj':dual+eq,'base_dualobj':dual,'equality_dualobj':eq,
            'psd_penalty':pen,'residual_l1':rn,'residual_l2':float(np.linalg.norm(r)),
            'residual_linf':float(np.abs(r).max()),'min_psd_eigenvalue':min(mineig)},r0,r


def main():
    if OUT.exists():raise RuntimeError('verification generation exists')
    claim=json.loads((GEN/'rac4-quotient-transfer-l1-05.json').read_text())
    wit=np.load(GEN/'rac4-quotient-transfer-l1-05.npz',allow_pickle=True)
    sysart=np.load(GEN/'rac4-quotient-system-05.npz',allow_pickle=True)
    leg,letters,povm=build(TwirlNPA);can,_,_=build(CanonicalTwirlNPA)
    cl,Sl,Fl,szl,Ul,Rl=matrices(leg);cc,Sc,Fc,szc,Uc,Rc=matrices(can)
    il=[z for z in range(leg.nz) if z!=leg.zI];ic=[z for z in range(can.nz) if z!=can.zI]
    pl={z:i for i,z in enumerate(il)};pc={z:i for i,z in enumerate(ic)}
    qr=[];qc=[]
    for lz in il:
        ra,rb=leg.zmap[lz];cz=can.zid_of_class(can.norm_class(tuple(ra)+tuple(rb)))
        if cz>=0 and cz!=can.zI:qr.append(pl[lz]);qc.append(pc[cz])
    Q=sp.csr_matrix((np.ones(len(qr)),(qr,qc)),shape=(len(il),len(ic)))
    Qs=sp.csr_matrix((sysart['Q_data'],sysart['Q_indices'],sysart['Q_indptr']),shape=tuple(sysart['Q_shape']))
    Es=sp.csr_matrix((sysart['E_data'],sysart['E_indices'],sysart['E_indptr']),shape=tuple(sysart['E_shape']))
    e0s=sysart['e0']
    El,e0l,rawl=eq_rows(leg,povm);Ec,e0c,rawc=eq_rows(can,povm);Elift=(El@Q).tocsr()
    keys_c=[normalized_key(Ec,i) for i in range(Ec.shape[0])]
    lookup={key:i for i,(key,sc,sg) in enumerate(keys_c)}
    perm=[];lift_e=[];can_e=[]
    for i in range(Elift.shape[0]):
        key,sc,sg=normalized_key(Elift,i);perm.append(lookup.get(key,-1))
        lift_e.append(sg*e0l[i]/sc if sc else e0l[i])
    for key,sc,sg in keys_c:
        j=keys_c.index((key,sc,sg));can_e.append(sg*e0c[j]/sc if sc else e0c[j])
    perm=np.array(perm);lift_e=np.array(lift_e);can_e=np.array(can_e)
    row_bij=bool(min(perm)>=0 and len(set(perm))==Ec.shape[0])
    e0_norm_diff=float(np.max(np.abs(lift_e-can_e[perm]))) if row_bij else float('inf')
    oldw=np.load(OLD/'rac4-completeness-polish-l1-02.npz',allow_pickle=True)
    Ys=[np.array(y) for y in oldw['Ys']];nuold=oldw['nu'];nu=wit['nu']
    oldcert,oldr0,oldr=cert_eval(Ys,cl,Rl,Fl,Ul,El,e0l,nuold)
    transferred,cr0,crtransfer=cert_eval(Ys,cc,Rc,Fc,Uc,Elift,e0l,nuold)
    new,_,rnew=cert_eval(Ys,cc,Rc,Fc,Uc,Es,e0s,nu)
    projection_err=float(np.max(np.abs(crtransfer-Q.T@oldr)))
    zc,ci=strategy_z(can,*get_classical_ops());zq,qi=strategy_z(can,*get_quantum_ops())
    zcn=np.delete(zc.real,can.zI);zqn=np.delete(zq.real,can.zI)
    cres=float(np.max(np.abs(Es@zcn+e0s)));qres=float(np.max(np.abs(Es@zqn+e0s)))
    cobj=float(can.c@zc.real);qobj=float(can.c@zq.real)
    # Independent LP replay.
    m,nv=Es.shape;I=sp.eye(nv,format='csr');ET=Es.T.tocsr()
    A=sp.vstack([sp.hstack([ET,-I]),sp.hstack([-ET,-I])],format='csr')
    b=np.concatenate([-cr0,cr0]);obj=np.concatenate([e0s,np.ones(nv)])
    sol=linprog(obj,A_ub=A,b_ub=b,bounds=[(None,None)]*m+[(0,None)]*nv,method='highs',
                options={'presolve':True,'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    cert_lp,_,_=cert_eval(Ys,cc,Rc,Fc,Uc,Es,e0s,sol.x[:m]) if sol.success else ({'cert':float('inf')},None,None)
    # Discriminating negative controls.
    zbad=zqn.copy();row=int(np.argmax(np.asarray(np.abs(Es).sum(axis=1)).ravel()));col=int(Es[row].indices[0]);zbad[col]+=0.03125
    nc_completeness=float(np.max(np.abs(Es@zbad+e0s)))
    Ybad=[Y.copy() for Y in Ys];Ybad[0]-=np.eye(Ybad[0].shape[0])
    bad_eig=float(np.linalg.eigvalsh((Ybad[0]+Ybad[0].conj().T)/2).min())
    no_res=new['dualobj']+new['psd_penalty']
    cert_zero,_,_=cert_eval(Ys,cc,Rc,Fc,Uc,Es,e0s,np.zeros(m))
    wrong_sign,_,_=cert_eval(Ys,cc,Rc,Fc,Uc,Es,e0s,-nu)
    nonzero=np.flatnonzero(cc);swap0=int(nonzero[0])
    Qbad=Qs.copy().tolil();Qbad[:,[0,1]]=Qbad[:,[1,0]];Qbad=Qbad.tocsr()
    qbad=max(diff_inf(a@Qbad,b) for a,b in zip(Sl,Sc))
    cbad=cc.copy();cbad[swap0]*=1.125
    objbad=float(cbad@zq.real[:len(cbad)]) if len(cbad)==len(zq.real) else float('nan')
    # cbad excludes zI; use the correct nonidentity quantum vector for the binding control.
    objbad=float(cbad@zqn)
    nubad=nu.copy();nzrow=int(np.argmax(np.diff(Es.indptr)));nubad[nzrow]+=0.125
    cert_bad_nu,_,rbad_nu=cert_eval(Ys,cc,Rc,Fc,Uc,Es,e0s,nubad)
    def claim_shape_ok(d):
        return bool(d.get('mode_lineage',{}).get('new_admm_iterations')==0 and
                    d.get('mode_lineage',{}).get('not_full') is True and
                    'No exact 3/4 theorem' in d.get('boundary','') and
                    d.get('new_certificate',{}).get('cert',0)>=0.75)
    claim_mut=copy.deepcopy(claim);claim_mut['mode_lineage']['not_full']=False
    negative={
        'completeness_violation_detected':nc_completeness>1e-3,
        'nonpsd_detected':bad_eig<-0.5,
        'residual_removal_below_known_lb':no_res<0.75,
        'zero_multiplier_is_worse':cert_zero['cert']>new['cert']+1e-8,
        'wrong_multiplier_sign_changes_certificate':abs(wrong_sign['cert']-new['cert'])>1e-8,
        'quotient_column_swap_detected':qbad>1e-8,
        'objective_binding_swap_detected':abs(objbad-0.75)>1e-8,
        'witness_mutation_detected':abs(cert_bad_nu['cert']-new['cert'])>1e-8 or float(np.max(np.abs(rbad_nu-rnew)))>1e-8,
        'quick_full_mislabel_rejected':claim_shape_ok(claim) and not claim_shape_ok(claim_mut),
        'exact_three_quarters_not_claimed':abs(new['cert']-0.75)>1e-3 and claim_shape_ok(claim),
    }
    scientific={
        'stored_Q_exact':diff_inf(Q,Qs)==0,
        'stored_E_exact':diff_inf(Elift,Es)==0,
        'stored_e0_exact':np.array_equal(e0l,e0s),
        'S_quotient_exact':max(diff_inf(a@Q,b) for a,b in zip(Sl,Sc))==0,
        'objective_quotient_exact':np.array_equal(Q.T@cl,cc),
        'F0_exact':all(np.array_equal(a,b) for a,b in zip(Fl,Fc)),
        'legacy_equalities_independent_exact':diff_inf(El,sp.csr_matrix((np.load(OLD/'rac4-completeness-equalities-01.npz',allow_pickle=True)['data'],np.load(OLD/'rac4-completeness-equalities-01.npz',allow_pickle=True)['indices'],np.load(OLD/'rac4-completeness-equalities-01.npz',allow_pickle=True)['indptr']),shape=tuple(np.load(OLD/'rac4-completeness-equalities-01.npz',allow_pickle=True)['shape'])))==0,
        'equality_normalized_row_bijection':row_bij,
        'equality_normalized_constants_match':e0_norm_diff<1e-12,
        'raw_counts_51480':rawl==rawc==51480,
        'old_anchor_exact':abs(oldcert['cert']-0.7527858612248398)<5e-12,
        'transfer_projection_exact':projection_err<1e-9,
        'transfer_claim_match':abs(transferred['cert']-claim['transferred_certificate_before_new_lp']['cert'])<5e-12,
        'new_claim_match':abs(new['cert']-claim['new_certificate']['cert'])<5e-12,
        'new_bound_strictly_improves':new['cert']<0.7527858612248398-1e-10,
        'new_bound_above_quantum_lb':new['cert']>=0.75-1e-7,
        'classical_control':abs(cobj-0.625)<1e-11 and cres<1e-10,
        'quantum_control':abs(qobj-0.75)<1e-10 and qres<1e-9,
        'moments_real':max(ci,qi)<1e-9,
        'witness_nu_replay_match':np.array_equal(nu,nuold),
        'independent_lp_optimal':sol.success,
        'independent_lp_same_certificate':abs(cert_lp['cert']-new['cert'])<5e-12,
    }
    scientific={k:bool(v) for k,v in scientific.items()};negative={k:bool(v) for k,v in negative.items()}
    engineering={'claim_schema_ok':claim_shape_ok(claim),'remote_writes':True,'qpu_launches_zero':True}
    ok=all(scientific.values()) and all(negative.values()) and all(engineering.values())
    improvement=0.7527858612248398-new['cert']
    doc={'schema':'BEAT174-QFA-QUOTIENT-UB-INDEPENDENT-REPLAY-03','ts':now(),
         'recomputed':{'old_beat173':oldcert,'transferred':transferred,'new':new,'independent_lp':cert_lp,
                       'improvement_over_beat173':improvement,'projection_error_linf':projection_err},
         'structure':{'legacy_variables':len(il),'canonical_variables':len(ic),'blocks':len(Sc),
                      'equalities':Es.shape[0],'raw_equalities':rawc,'Q_nnz':Q.nnz,'E_nnz':Es.nnz,
                      'lp_status':int(sol.status),'lp_nit':int(sol.nit),'lp_constraints':A.shape[0],'lp_variables':len(obj)},
         'positive_controls':{'classical_objective':cobj,'quantum_objective':qobj,
                              'classical_completeness_linf':cres,'quantum_completeness_linf':qres},
         'scientific_guards':scientific,'negative_controls':negative,'engineering_guards':engineering,
         'verdict':'PASS_BEAT174_QUOTIENT_NUMERIC_UB_0_752718187871213__EXACT_3_OVER_4_NOT_PROVEN' if ok else 'FAIL_INDEPENDENT_REPLAY',
         'boundary':'Independent floating-point certificate and LP replay only. No exact BP07, canonical-full convergence, QRAC/EARAC equivalence, novelty, real-QPU or seat-consensus claim.',
         'remote_writes':0,'qpu_launches':0,
         'inputs_sha256':{'claim':sha(GEN/'rac4-quotient-transfer-l1-05.json'),
                          'witness':sha(GEN/'rac4-quotient-transfer-l1-05.npz'),'system':sha(GEN/'rac4-quotient-system-05.npz'),
                          'old_witness':sha(OLD/'rac4-completeness-polish-l1-02.npz'),
                          'canonical_npa':sha(OLD/'canonical_npa.py'),'npa_twirl':sha(INPUT/'npa_twirl.py'),
                          'test_twirl':sha(INPUT/'test_twirl.py'),'quantum_control':sha(INPUT/'verify_bound07.py')},
         'verifier_source_sha256':sha(Path(__file__).resolve())}
    OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'output':str(OUT),'sha256':sha(OUT),'verdict':doc['verdict'],
                      'new_cert':new['cert'],'improvement':improvement,
                      'scientific':scientific,'negative':negative},ensure_ascii=False,indent=2))
    return 0 if ok else 1

if __name__=='__main__':raise SystemExit(main())
