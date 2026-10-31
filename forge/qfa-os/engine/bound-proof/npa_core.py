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
