# bp08/npa_core.py -- Beat-129 NPA machinery (self-contained, deterministic)
# Level-1 commuting-operator NPA for d=4 EA-RAC and the affine W game.
# Certification: for primal max<C,X> s.t. AX=b, X PSD:
#   <C,X> = -b^T y - <D,X>  with D = Cv - A^T y (Cv=-C)
#   => max <= -b^T y + max(0,-lam_min(D)) * trX ,  trX fixed by completeness.
import numpy as np, scipy.sparse as sp, time
from scipy.linalg import solve_triangular

def build_npa_level1(d):
    nx=d*d
    A_letters=[('A',x,m) for x in range(nx) for m in range(d)]
    M_letters=[('B',y,m,v) for y in range(2) for m in range(d) for v in range(d)]
    W=['I']+A_letters+M_letters
    idx={w:i for i,w in enumerate(W)}
    AlicePOVMs=[[('A',x,m) for m in range(d)] for x in range(nx)]
    BobPOVMs=[[('B',y,m,v) for v in range(d)] for y in range(2) for m in range(d)]
    rows=[];b=[]
    def add(c,r): rows.append(c); b.append(r)
    add({('I','I'):1.0},1.0)
    for povm in AlicePOVMs+BobPOVMs:
        for i in range(len(povm)):
            for j in range(i+1,len(povm)):
                add({(povm[i],povm[j]):1.0},0.0)
        for S in W:
            c={}
            for l in povm: c[(l,S)]=c.get((l,S),0)+1.0
            c[('I',S)]=c.get(('I',S),0)-1.0
            add(c,0.0)
    C={}
    for x in range(nx):
        Xy=[x//d,x%d]
        for y in range(2):
            for m in range(d):
                C[(('A',x,m),('B',y,m,Xy[y]))]=1.0/(2*nx)
    return W,idx,rows,np.array(b,float),C

def build_bell_W():
    W=['I']+[('A',u,a) for u in range(4) for a in range(4)]+[('B',y,b) for y in range(2) for b in range(4)]
    idx={w:i for i,w in enumerate(W)}
    rows=[];b=[]
    def add(c,r): rows.append(c); b.append(r)
    add({('I','I'):1.0},1.0)
    povms=[[('A',u,a) for a in range(4)] for u in range(4)]+[[('B',y,b) for b in range(4)] for y in range(2)]
    for povm in povms:
        for i in range(len(povm)):
            for j in range(i+1,len(povm)): add({(povm[i],povm[j]):1.0},0.0)
        for S in W:
            c={}
            for l in povm: c[(l,S)]=c.get((l,S),0)+1.0
            c[('I',S)]=c.get(('I',S),0)-1.0
            add(c,0.0)
    C={}
    for u in range(4):
        for y in range(2):
            for a in range(4):
                for bb in range(4):
                    if (a+bb)%4==(u*y)%4:
                        C[(('A',u,a),('B',y,bb))]=1.0/8
    return W,idx,rows,np.array(b,float),C

def build_full(W,idx,rows,b,C):
    N=len(W); Ar=[];Ac=[];Av=[]
    for r,coefs in enumerate(rows):
        for (wi,wj),val in coefs.items():
            i,j=idx[wi],idx[wj]
            Ar.append(r);Ac.append(i*N+j);Av.append(val/2)
            Ar.append(r);Ac.append(j*N+i);Av.append(val/2)
    A=sp.csr_matrix((Av,(Ar,Ac)),shape=(len(rows),N*N))
    Cm=np.zeros((N,N))
    for (wi,wj),val in C.items():
        i,j=idx[wi],idx[wj]; Cm[i,j]+=val/2; Cm[j,i]+=val/2
    return A,b,Cm

def admm_cert(A,b,Cm,N,mu,iters,trX,L=None):
    Cv=-Cm; cv=Cv.reshape(-1)
    if L is None:
        L=np.linalg.cholesky((A@A.T).toarray()+1e-12*np.eye(A.shape[0]))
    X=np.zeros((N,N)); S=np.zeros((N,N))
    for it in range(iters):
        rhs=(b-A@X.reshape(-1))/mu + A@(cv-S.reshape(-1))
        t=solve_triangular(L,rhs,lower=True)
        y=solve_triangular(L.T,t,lower=False)
        Aty=(A.T@y).reshape(N,N)
        M=Cv-Aty-X/mu; M=(M+M.T)/2
        ev,U=np.linalg.eigh(M); S=(U*np.clip(ev,0,None))@U.T
        X=X+mu*(Aty+S-Cv)
    D=Cv-Aty; D=(D+D.T)/2; lm=np.linalg.eigvalsh(D)[0]
    pres=np.abs(A@X.reshape(-1)-b).max()
    cert=-(b@y)+max(0.0,-lm)*trX
    return dict(cert=float(cert),mbTy=float(-(b@y)),lam_min=float(lm),pres=float(pres)),X,y,L
# bp08/npa_1ab.py -- Level 1+AB NPA for the affine W game (self-contained)

def build_1ab_W():
    A_lets=[('A',u,a) for u in range(4) for a in range(4)]
    B_lets=[('B',y,b) for y in range(2) for b in range(4)]
    W=[()]+[(l,) for l in A_lets]+[(l,) for l in B_lets]+[(a,bb) for a in A_lets for bb in B_lets]
    N=len(W)
    def redside(S):
        if len(S)==2 and S[0][:2]==S[1][:2]:
            return (S[0],) if S[0]==S[1] else 'Z'
        return tuple(S)
    def nf_key(word):
        As=tuple(l for l in word if l[0]=='A'); Bs=tuple(l for l in word if l[0]=='B')
        ra,rb=redside(As),redside(Bs)
        if ra=='Z' or rb=='Z': return 'Z'
        return (ra,rb)
    def canon(k):
        if k=='Z': return 'Z'
        ra,rb=k; rev=(tuple(reversed(ra)),tuple(reversed(rb)))
        return min((ra,rb),rev)
    cls={}; rep={}
    for i in range(N):
        wi=W[i]
        for j in range(i,N):
            k=canon(nf_key(tuple(reversed(wi))+W[j]))
            cls[(i,j)]=k
            if k!='Z' and k not in rep: rep[k]=(i,j)
    rows=[];b=[]
    def add(c,r): rows.append(c); b.append(r)
    add({(0,0):1.0},1.0)
    for (i,j),k in cls.items():
        if k=='Z': add({(i,j):1.0},0.0)
        elif rep[k]!=(i,j):
            ri,rj=rep[k]; add({(i,j):1.0,(ri,rj):-1.0},0.0)
    C={}
    for u in range(4):
        for y in range(2):
            for a in range(4):
                for bb in range(4):
                    if (a+bb)%4==(u*y)%4:
                        i=1+u*4+a; j=1+16+y*4+bb
                        C[(i,j)]=1.0/8
    return W,rows,np.array(b,float),C,N

def build_full_idx(rows,b,C,N):
    Ar=[];Ac=[];Av=[]
    for r,coefs in enumerate(rows):
        for (i,j),val in coefs.items():
            Ar.append(r);Ac.append(i*N+j);Av.append(val/2)
            Ar.append(r);Ac.append(j*N+i);Av.append(val/2)
    A=sp.csr_matrix((Av,(Ar,Ac)),shape=(len(rows),N*N))
    Cm=np.zeros((N,N))
    for (i,j),val in C.items():
        Cm[i,j]+=val/2; Cm[j,i]+=val/2
    return A,b,Cm


# ================= verify_bound08.py main =================
# Modes: quick (runner, ~100s) | full (sandbox, ~6min)
# Certificate theorem (auditable):
#   primal: max <C,X> s.t. AX=b, X PSD.  For ANY y, D := -C - A^T y:
#   <C,X> = -b^T y - <D,X>  <=  -b^T y + max(0,-lam_min(D)) * trX
#   trX is FIXED by completeness: trX = 1 + (#Alice POVMs) + (#Bob POVMs) [+ #AB words for 1AB]
import sys
MODE = sys.argv[1] if len(sys.argv)>1 else 'quick'
IT = {'quick':dict(d2=(0.1,2000),d4=(0.1,800),wl1=(0.1,1500),w1ab=(0.1,500)),
      'full' :dict(d2=(0.1,2000),d4=(0.05,1500),wl1=(0.05,4000),w1ab=(0.05,2400))}[MODE]
fails=[]
def check(name,cond,info=''):
    print(('PASS' if cond else 'FAIL'),name,info); 
    if not cond: fails.append(name)

# --- check 0: namespace disjointness (regression: beat-129 collision bug) ---
for nm,bld in [('rac2',lambda:build_npa_level1(2)),('rac4',lambda:build_npa_level1(4)),('w',build_bell_W)]:
    W=bld()[0]; check('namespace-'+nm, len(set(W))==len(W), 'letters=%d'%len(W))

# --- check 1: d=2 RAC level-1 == (2+sqrt2)/4 (machinery validation) ---
W2,idx2,rows2,b2,C2=build_npa_level1(2)
A2,b2,Cm2=build_full(W2,idx2,rows2,b2,C2)
r2,_,_,_=admm_cert(A2,b2,Cm2,len(W2),IT['d2'][0],IT['d2'][1],9)
exact2=(2+2**0.5)/4
check('d2-L1-exact',abs(r2['cert']-exact2)<1e-9,'cert=%.10f exact=%.10f'%(r2['cert'],exact2))

# --- check 2: d=4 RAC level-1 certified UB == (2+3*sqrt2)/8 ---
W4,idx4,rows4,b4,C4=build_npa_level1(4)
A4,b4,Cm4=build_full(W4,idx4,rows4,b4,C4)
r4,_,_,_=admm_cert(A4,b4,Cm4,len(W4),IT['d4'][0],IT['d4'][1],25)
t4=(2+3*2**0.5)/8
check('d4-L1-UB',abs(r4['cert']-t4)<1e-7,'cert=%.10f target=%.10f lam=%.1e pres=%.1e'%(r4['cert'],t4,r4['lam_min'],r4['pres']))
check('d4-L1-above-LB',r4['cert']>=0.75,'UB must dominate quantum LB 3/4')

# --- check 3: W game level-1 == same value, dominates see-saw LB 0.7404886669 ---
Ww,idxw,rowsw,bw,Cw=build_bell_W()
Aw,bw,Cmw=build_full(Ww,idxw,rowsw,bw,Cw)
rw,_,_,_=admm_cert(Aw,bw,Cmw,len(Ww),IT['wl1'][0],IT['wl1'][1],7)
check('W-L1-UB',abs(rw['cert']-t4)<1e-7,'cert=%.10f'%rw['cert'])
check('W-L1-above-seesaw',rw['cert']>=0.7404886669,'see-saw LB 0.7404886669 (bp07, reproduced twice)')

# --- check 4: classical optimal strategy (5/8) feasible in d=4 RAC L1 system ---
def classical_gamma_rac4(idx,N):
    G=np.zeros((N,N))
    def valA(x,m): return 1.0 if m==x//4 else 0.0
    def valB(y,m,v): return 1.0 if (v==(m if y==0 else 0)) else 0.0
    for w,i in idx.items():
        for w2,j in idx.items():
            if w=='I' and w2=='I': G[i,j]=1.0
            elif w=='I': G[i,j]= valA(*w2[1:]) if w2[0]=='A' else valB(*w2[1:])
            elif w2=='I': G[i,j]= valA(*w[1:]) if w[0]=='A' else valB(*w[1:])
            else:
                v1= valA(*w[1:]) if w[0]=='A' else valB(*w[1:])
                v2= valA(*w2[1:]) if w2[0]=='A' else valB(*w2[1:])
                G[i,j]=v1*v2
    return G
G=classical_gamma_rac4(idx4,len(W4))
res=np.abs(A4@G.reshape(-1)-b4).max(); obj=np.sum(Cm4*G)
check('classical-rac4-feasible',res<1e-9 and abs(obj-0.625)<1e-12,'res=%.1e obj=%.12f (5/8)'%(res,obj))

# --- check 5: classical optimal (5/8) feasible in W L1 system ---
def classical_gamma_w(idx,N):
    def lv(w): return 1.0 if (w[0] in ('A','B') and w[2]==0) else 0.0
    G=np.zeros((N,N))
    for w,i in idx.items():
        for w2,j in idx.items():
            if w=='I' and w2=='I': G[i,j]=1.0
            elif w=='I': G[i,j]=lv(w2)
            elif w2=='I': G[i,j]=lv(w)
            else: G[i,j]=lv(w)*lv(w2)
    return G
Gw=classical_gamma_w(idxw,len(Ww))
res=np.abs(Aw@Gw.reshape(-1)-bw).max(); obj=np.sum(Cmw*Gw)
check('classical-W-feasible',res<1e-9 and abs(obj-0.625)<1e-12,'res=%.1e obj=%.12f'%(res,obj))

# --- check 6: classical (5/8) feasible in W 1+AB system (validates 7421-row constraint set) ---
Wab,rows_ab,b_ab,C_ab,Nab=build_1ab_W()
Aab,b_ab,Cmab=build_full_idx(rows_ab,b_ab,C_ab,Nab)
def letter_val(l): return 1.0 if l[2]==0 else 0.0
G2=np.zeros((Nab,Nab))
for i,w1 in enumerate(Wab):
    for j,w2 in enumerate(Wab):
        p=1.0
        for l in w1: p*=letter_val(l)
        for l in w2: p*=letter_val(l)
        G2[i,j]=p
res=np.abs(Aab@G2.reshape(-1)-b_ab).max(); obj=np.sum(Cmab*G2)
check('classical-W-1AB-feasible',res<1e-9 and abs(obj-0.625)<1e-12,'res=%.1e obj=%.12f'%(res,obj))

# --- check 7: W 1+AB certified UB (valid at any iteration via lam_min correction) ---
rab,_,_,_=admm_cert(Aab,b_ab,Cmab,Nab,IT['w1ab'][0],IT['w1ab'][1],15)
check('W-1AB-valid-UB',rab['cert']>=0.7404886669,'cert=%.10f iters=%d'%(rab['cert'],IT['w1ab'][1]))
if MODE=='full':
    check('W-1AB-converged',abs(rab['cert']-0.7441360147)<5e-4,'cert=%.10f'%rab['cert'])

print()
print('BOUND-PROOF-08 %s mode: %s'%(MODE,'ALL PASS' if not fails else 'FAILS: '+str(fails)))
sys.exit(0 if not fails else 1)
