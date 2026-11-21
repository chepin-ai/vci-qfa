# bp09/facial_polish.py -- facial-reduction exact dual polish for twirled NPA (Beat-130)
# Given a converged ADMM state (z,Y) on the twirled RAC4-1AB relaxation:
#   1) active-face extraction: Q_rho = null-space basis of block M_rho(z) (eig < tol)
#   2) restricted dual feasibility solve: find Y_rho = Q_rho Yh_rho Q_rho^H with
#      StT @ vec(Y) = -cv   (LSQR on implicit linear map)
#   3) rigorous certificate at the resulting Y (dualobj + pen + ||r||_1)
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import lsqr, LinearOperator

def load_system(t):
    vid={z:i for i,z in enumerate(z for z in range(t.nz) if z!=t.zI)}
    nv=len(vid)
    cv=np.array([t.c[z] for z in range(t.nz) if z!=t.zI])
    Ss=[]; F0s=[]; sizes=[]
    for b in t.blocks:
        n=b['size']; F0=np.zeros((n,n),complex)
        rows=[];cols=[];vals=[]
        for (ai,bi),acc in b['entries'].items():
            for zi,co in acc.items():
                if zi==t.zI: F0[ai,bi]+=co
                else: rows.append(ai*n+bi); cols.append(vid[zi]); vals.append(co)
        Ss.append(sp.csr_matrix((vals,(rows,cols)),shape=(n*n,nv),dtype=complex))
        F0s.append(F0); sizes.append(n)
    St=sp.vstack([sp.vstack([S.real,S.imag]) for S in Ss]).tocsr()
    return cv,Ss,F0s,sizes,St

def stackvec(ms):
    return np.concatenate([np.concatenate([m.reshape(-1).real,m.reshape(-1).imag]) for m in ms])

def cert_eval(Ys,cv,StT,F0s,Utr):
    du=0.0; pen=0.0
    for Y,F0,ub in zip(Ys,F0s,Utr):
        lm=np.linalg.eigvalsh((Y+Y.conj().T)/2).min()
        du+=np.real(np.trace(F0.conj().T@Y)); pen+=max(0.0,-lm)*ub
    r=cv+StT@stackvec(Ys)
    return du+pen+float(np.abs(r).sum()), float(du), float(pen), float(np.abs(r).sum())

def make_Utr(t,F0s,sizes):
    Utr=[]
    for b,F0,n in zip(t.blocks,F0s,sizes):
        ub=0.0
        for ai in range(n):
            acc=b['entries'].get((ai,ai),{})
            ub+=sum(abs(co) for zi,co in acc.items() if zi!=t.zI)
        Utr.append(ub+abs(np.trace(F0)))
    return Utr

def facial_polish(t, z, tol=1e-5, iter_lim=1500, verbose=True):
    cv,Ss,F0s,sizes,St=load_system(t)
    StT=St.T.tocsr()
    nv=len(cv)
    zfull=St@z
    roff=np.cumsum([0]+[2*n*n for n in sizes])
    Qs=[]; ks=[]
    for i,(n,F0) in enumerate(zip(sizes,F0s)):
        M=(zfull[roff[i]:roff[i]+n*n]+1j*zfull[roff[i]+n*n:roff[i+1]]).reshape(n,n)+F0
        Mh=(M+M.conj().T)/2
        ev,U=np.linalg.eigh(Mh)
        k=int((ev<tol).sum()); ks.append(k); Qs.append(U[:,:k])
    koff=np.cumsum([0]+[k*k for k in ks]); nred=int(koff[-1])
    if verbose: print('face: nred=%d nv=%d'%(nred,nv))
    # precompute triangular index arrays per block
    TRI=[]
    for k in ks:
        p,q=np.triu_indices(k,1)
        TRI.append((p,q))
    def Kmv(u):
        out=np.zeros(roff[-1])
        for i,(n,Q) in enumerate(zip(sizes,Qs)):
            k=ks[i]
            if k==0: continue
            seg=u[koff[i]:koff[i+1]]
            Yh=np.zeros((k,k),complex)
            Yh[np.diag_indices(k)]=seg[:k]
            p,q=TRI[i]
            a=seg[k:].reshape(-1,2)
            Yh[p,q]=(a[:,0]+1j*a[:,1])/np.sqrt(2)
            Yh[q,p]=(a[:,0]-1j*a[:,1])/np.sqrt(2)
            Y=Q@Yh@Q.conj().T
            out[roff[i]:roff[i]+n*n]=Y.reshape(-1).real
            out[roff[i]+n*n:roff[i+1]]=Y.reshape(-1).imag
        return out
    def Krmv(w):
        u=np.zeros(nred)
        for i,(n,Q) in enumerate(zip(sizes,Qs)):
            k=ks[i]
            if k==0: continue
            Y=w[roff[i]:roff[i]+n*n]+1j*w[roff[i]+n*n:roff[i+1]]
            U2=Q.conj().T@Y.reshape(n,n)@Q
            U2=(U2+U2.conj().T)/2  # Hermitian part: adjoint defined on full space
            seg=np.zeros(k*k)
            seg[:k]=np.diag(U2).real
            p,q=TRI[i]
            a=seg[k:].reshape(-1,2)
            a[:,0]=np.sqrt(2)*U2[p,q].real
            a[:,1]=np.sqrt(2)*U2[p,q].imag
            u[koff[i]:koff[i+1]]=seg
        return u
    def Wmv(u): return StT@Kmv(u)
    def Wrmv(w): return Krmv(St@w)
    W=LinearOperator((nv,nred),matvec=Wmv,rmatvec=Wrmv)
    out=lsqr(W,-cv,atol=1e-13,btol=1e-13,iter_lim=iter_lim)
    u=out[0]
    if verbose: print('lsqr: iters=%d residL2=%.3e'%(out[2],np.sqrt(np.sum((Wmv(u)+cv)**2))))
    # rebuild Ys
    Ys=[]
    uu=Kmv(u)
    for i,n in enumerate(sizes):
        Ys.append((uu[roff[i]:roff[i]+n*n]+1j*uu[roff[i]+n*n:roff[i+1]]).reshape(n,n))
    Utr=make_Utr(t,F0s,sizes)
    c,du,pen,rn=cert_eval(Ys,cv,StT,F0s,Utr)
    if verbose: print('facial cert=%.10f dualobj=%.10f pen=%.2e rnorm=%.2e'%(c,du,pen,rn))
    return dict(Ys=Ys,cert=c,dualobj=du,pen=pen,rnorm=rn,ks=ks)
