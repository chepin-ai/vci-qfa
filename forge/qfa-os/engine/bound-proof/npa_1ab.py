# bp08/npa_1ab.py -- Level 1+AB NPA for the affine W game (self-contained)
import numpy as np, scipy.sparse as sp, time
from scipy.linalg import solve_triangular

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
