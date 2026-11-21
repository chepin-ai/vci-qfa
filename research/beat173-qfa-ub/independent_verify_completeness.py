#!/usr/bin/env python3
"""Second-entry, fail-closed recomputation of the BEAT173 RAC4 numeric upper bound."""
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent
INPUT = HERE / 'inputs'
sys.path.insert(0, str(INPUT))
from npa_twirl import TwirlNPA
from test_twirl import build_RAC4_1AB, make_chars_Z4cube


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = HERE / 'portable-replay-result.json'
    if out.exists(): raise RuntimeError('verification generation exists')
    claim = json.loads((HERE/'rac4-completeness-polish-l1-02.json').read_text())
    letters, povm_of, words, gens, obj = build_RAC4_1AB()
    t = TwirlNPA(letters, povm_of, words, gens, obj)
    chars, names = make_chars_Z4cube(t); t.set_chars(chars, names); t.build(verbose=False)
    # Independently assemble the real block operator and constant matrices.
    nonid = [z for z in range(t.nz) if z != t.zI]; vid = {z: i for i, z in enumerate(nonid)}
    cv = np.array([t.c[z] for z in nonid]); Ss=[]; F0s=[]; sizes=[]
    for block in t.blocks:
        n=block['size']; F0=np.zeros((n,n),complex); rr=[];cc=[];vv=[]
        for (a,b),terms in block['entries'].items():
            for zid,coef in terms.items():
                if zid==t.zI:F0[a,b]+=coef
                else:rr.append(a*n+b);cc.append(vid[zid]);vv.append(coef)
        Ss.append(sp.csr_matrix((vv,(rr,cc)),shape=(n*n,len(nonid)),dtype=complex));F0s.append(F0);sizes.append(n)
    St=sp.vstack([sp.vstack([S.real,S.imag]) for S in Ss]).tocsr();StT=St.T.tocsr()
    # Independently derive every sum_outcome Gamma(l,S)-Gamma(I,S)=0 row.
    single={w[0]:i for i,w in enumerate(t.W) if len(w)==1}; I=t.wpos[()]
    povms={}
    for li,povm in povm_of.items():povms.setdefault(povm,[]).append(li)
    unique={};raw_count=0
    for povm,ls in sorted(povms.items()):
        for si in range(t.N):
            row={};raw_count+=1
            for li in sorted(ls):
                zid=t.zid_of_class(t.class_key(single[li],si))
                if zid>=0:row[zid]=row.get(zid,0)-1
            zid=t.zid_of_class(t.class_key(I,si))
            if zid>=0:row[zid]=row.get(zid,0)+1
            if not row:continue
            # Preserve the stored matrix's legacy sign convention: zero-valued
            # cancelled entries still participate in choosing the sign key.
            # This affects representation only, never the represented equation.
            if row[min(row)]<0:row={k:-v for k,v in row.items()}
            scale=max(abs(v) for v in row.values())
            key=tuple(sorted((k,float(v/scale)) for k,v in row.items() if abs(v)>1e-14))
            unique[key]=(povm,si)
    keys=sorted(unique);rr=[];cc=[];vv=[];constants=[]
    for ri,key in enumerate(keys):
        constant=0.0
        for zid,value in key:
            if zid==t.zI:constant+=value
            else:rr.append(ri);cc.append(vid[zid]);vv.append(value)
        constants.append(constant)
    E2=sp.csr_matrix((vv,(rr,cc)),shape=(len(keys),len(nonid)));e02=np.array(constants)
    stored=np.load(HERE/'rac4-completeness-equalities-01.npz',allow_pickle=True)
    E=sp.csr_matrix((stored['data'],stored['indices'],stored['indptr']),shape=tuple(stored['shape']))
    e0=stored['e0'];diff=E-E2
    equality_matrix_match=bool(E.shape==E2.shape and diff.nnz==0 and np.array_equal(e0,e02) and raw_count==51480)
    # Load the original sealed Y and only the new equality multipliers from generation 02.
    old=np.load(INPUT/'y_best.npz',allow_pickle=True);Ys=[np.array(y) for y in old['Ys']]
    nu=np.load(HERE/'rac4-completeness-polish-l1-02.npz',allow_pickle=True)['nu']
    dual0=0.0;pen=0.0;mineigs=[]
    for block,Y,F0 in zip(t.blocks,Ys,F0s):
        n=block['size'];H=(Y+Y.conj().T)/2;lm=float(np.linalg.eigvalsh(H).min());mineigs.append(lm)
        dual0+=float(np.real(np.trace(F0.conj().T@Y)))
        ub=float(abs(np.trace(F0)))
        for ai in range(n):
            ub+=sum(abs(co) for zi,co in block['entries'].get((ai,ai),{}).items() if zi!=t.zI)
        pen+=max(0.0,-lm)*ub
    yreal=np.concatenate([np.concatenate([Y.reshape(-1).real,Y.reshape(-1).imag]) for Y in Ys])
    r0=cv+StT@yreal;r=r0+E.T@nu
    eqdual=float(e0@nu);dual=dual0+eqdual;rn=float(np.abs(r).sum());cert=dual+pen+rn
    # Positive control: a deterministic classical strategy must satisfy every completeness row.
    vals=[]
    for lt in letters:
        if lt[0]=='A':_,x,m=lt;vals.append(float(m==x//4))
        else:_,y,m,v=lt;g=m if y==0 else 0;vals.append(float(v==g))
    vals=np.array(vals);wval={w:float(np.prod(vals[list(w)])) if w else 1.0 for w in t.W}
    zc=np.zeros(t.nz)
    for o in range(t.norb):
        for o2 in range(t.norb):
            for k in range(t.oG):
                wi=t.reps[o];wj=int(t.gt[k,t.reps[o2]]);zid=t.zid_of_class(t.class_key(wi,wj))
                if zid<0:continue
                zc[zid]=sum(wval[t.W[int(t.gt[g,wi])]]*wval[t.W[int(t.gt[g,wj])]] for g in range(t.oG))/t.oG
    zc[t.zI]=1.0;zcn=np.delete(zc,t.zI);classical_res=E2@zcn+e02
    classical_obj=float(t.c@zc)
    positive_control=bool(np.max(np.abs(classical_res))<1e-10 and abs(classical_obj-0.625)<1e-12)
    # Discriminating negative controls: completeness violation, residual removal, and non-PSD Y.
    zbad=zcn.copy();row=int(np.argmax(np.asarray(np.abs(E2).sum(axis=1)).ravel()));col=int(E2[row].indices[0]);zbad[col]+=0.03125
    nc_completeness=bool(np.max(np.abs(E2@zbad+e02))>1e-3)
    nc_residual=bool(float(np.abs(r0).sum())>rn+1e-6)
    Ybad=[Y.copy() for Y in Ys];Ybad[0]=Ybad[0]-np.eye(Ybad[0].shape[0])
    bad_lm=float(np.linalg.eigvalsh((Ybad[0]+Ybad[0].conj().T)/2).min())
    nc_nonpsd=bool(bad_lm < -0.5)
    log=(HERE/'portable-bound07.log').read_text();rc=int((HERE/'portable-bound07.rc').read_text())
    lb_replayed=bool(rc==0 and 'quantum-LB-3/4' in log and 'quantum>=3/4 certified' in log and '10 checks, 0 failed' in log)
    claim_match=abs(cert-float(claim['new_certificate']['cert']))<5e-12
    guards={'equality_matrix_independent_match':equality_matrix_match,'classical_positive_control':positive_control,
            'completeness_negative_control':nc_completeness,'residual_negative_control':nc_residual,
            'nonpsd_negative_control':nc_nonpsd,'known_quantum_lb_replayed':lb_replayed,
            'claim_numeric_match':claim_match,'cert_not_below_lb_1e-7':cert>=0.75-1e-7,
            'cert_improves_previous':cert<0.7537703608,'cert_improves_generation_01':cert<0.7533021836843592}
    ok=all(guards.values())
    doc={'schema':'BEAT173-QFA-UPPER-BOUND-INDEPENDENT-REPLAY-01',
         'ts':dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z'),'remote_writes':0,
         'recomputed':{'cert':cert,'dualobj':dual,'base_dualobj':dual0,'equality_dualobj':eqdual,
                       'psd_penalty':pen,'residual_l1':rn,'residual_l2':float(np.linalg.norm(r)),
                       'residual_linf':float(np.abs(r).max()),'min_psd_eigenvalue':min(mineigs)},
         'old_cert_recomputed':dual0+pen+float(np.abs(r0).sum()),
         'equation_system':{'raw':raw_count,'unique':E2.shape[0],'variables':E2.shape[1],'nnz':E2.nnz},
         'guards':guards,'negative_controls':{'completeness_violation_detected':nc_completeness,
                   'removing_multipliers_increases_residual':nc_residual,'nonpsd_min_eigenvalue':bad_lm},
         'verdict':'PASS_INDEPENDENT_NUMERIC_UB_0_7527858612248398__EXACT_3_OVER_4_NOT_PROVEN' if ok else 'FAIL_INDEPENDENT_REPLAY',
         'boundary':'Independent floating-point dual recomputation only. It improves the numeric UB but does not prove quantum<=3/4, exactness, model equivalence, novelty, or seat approval.',
         'inputs_sha256':{'claim':sha(HERE/'rac4-completeness-polish-l1-02.json'),
                          'witness':sha(HERE/'rac4-completeness-polish-l1-02.npz'),
                          'equalities':sha(HERE/'rac4-completeness-equalities-01.npz'),
                          'original_y':sha(INPUT/'y_best.npz'),'npa_twirl':sha(INPUT/'npa_twirl.py'),
                          'test_twirl':sha(INPUT/'test_twirl.py'),'lb_log':sha(HERE/'portable-bound07.log')},
         'verifier_source_sha256':sha(Path(__file__).resolve())}
    out.write_text(json.dumps(doc,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'output':str(out),'sha256':sha(out),'verdict':doc['verdict'],
                      'recomputed':doc['recomputed'],'guards':guards},ensure_ascii=False,indent=2))
    return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
