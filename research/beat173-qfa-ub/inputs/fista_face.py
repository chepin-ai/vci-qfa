# bp09/fista_face.py -- FISTA with exact PSD projection in the reduced face space (Beat-130)
# min_u ||W u + cv||^2  s.t. Yh_i(u) PSD per block  -> exact dual feasible point for the cert
import numpy as np, pickle, time
import scipy.sparse as sp
from scipy.sparse.linalg import LinearOperator, lsqr

def build_face(t, z, tol=1e-5):
    from facial_polish import load_system
    cv,Ss,F0s,sizes,St=load_system(t)
    nv=len(cv)
    zfull=St@z
    roff=np.cumsum([0]+[2*n*n for n in sizes])
    Qs=[]; ks=[]
    for i,(n,F0) in enumerate(zip(sizes,F0s)):
        M=(zfull[roff[i]:roff[i]+n*n]+1j*zfull[roff[i]+n*n:roff[i+1]]).reshape(n,n)+F0
        ev,U=np.linalg.eigh((M+M.conj().T)/2)
        k=int((ev<tol).sum()); ks.append(k); Qs.append(U[:,:k])
    koff=np.cumsum([0]+[k*k for k in ks]); nred=int(koff[-1])
    TRI=[np.triu_indices(k,1) for k in ks]
    return cv,Ss,F0s,sizes,St,roff,Qs,ks,koff,nred,TRI

def make_maps(sizes,Qs,ks,koff,nred,roff,TRI,St,StT):
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
            U2=(U2+U2.conj().T)/2
            seg=np.zeros(k*k)
            seg[:k]=np.diag(U2).real
            p,q=TRI[i]
            a=seg[k:].reshape(-1,2)
            a[:,0]=np.sqrt(2)*U2[p,q].real
            a[:,1]=np.sqrt(2)*U2[p,q].imag
            u[koff[i]:koff[i+1]]=seg
        return u
    return Kmv,Krmv

def proj_cone(u,sizes,ks,koff,TRI):
    # exact projection onto {u : Yh_i(u) PSD} (blockwise eigh, isometric basis)
    u=u.copy()
    for i in range(len(sizes)):
        k=ks[i]
        if k==0: continue
        seg=u[koff[i]:koff[i+1]]
        Yh=np.zeros((k,k),complex)
        Yh[np.diag_indices(k)]=seg[:k]
        p,q=TRI[i]
        a=seg[k:].reshape(-1,2)
        Yh[p,q]=(a[:,0]+1j*a[:,1])/np.sqrt(2)
        Yh[q,p]=(a[:,0]-1j*a[:,1])/np.sqrt(2)
        ev,U=np.linalg.eigh(Yh)
        if ev[0]<0:
            Yh=(U*np.clip(ev,0,None))@U.conj().T
            seg2=np.zeros(k*k)
            seg2[:k]=np.diag(Yh).real
            a2=seg2[k:].reshape(-1,2)
            a2[:,0]=np.sqrt(2)*Yh[p,q].real
            a2[:,1]=np.sqrt(2)*Yh[p,q].imag
            u[koff[i]:koff[i+1]]=seg2
    return u

def fista_polish(t, z, tol=1e-5, iters=2000, gamma=1e-7, verbose=True):
    from facial_polish import cert_eval, make_Utr, stackvec
    cv,Ss,F0s,sizes,St,roff,Qs,ks,koff,nred,TRI=build_face(t,z,tol)
    StT=St.T.tocsr()
    Kmv,Krmv=make_maps(sizes,Qs,ks,koff,nred,roff,TRI,St,StT)
    def Wmv(u): return StT@Kmv(u)
    def Wrmv(w): return Krmv(St@w)
    # dualobj linear functional q = K^T F0vec
    F0vec=np.concatenate([np.concatenate([F0.reshape(-1).real,F0.reshape(-1).imag]) for F0 in F0s])
    q=Krmv(F0vec)
    # power iteration for L = 2||W||^2
    v=np.random.default_rng(0).standard_normal(nred)
    for _ in range(60):
        w=Wrmv(Wmv(v)); nrm=np.sqrt(w@w); v=w/max(nrm,1e-300)
    L=2.0*float(v@Wrmv(Wmv(v)))
    if verbose: print('face nred=%d L~%.3e'%(nred,L))
    # warm start from facial LSQR
    W=LinearOperator((len(cv),nred),matvec=Wmv,rmatvec=Wrmv)
    u=lsqr(W,-cv,atol=1e-13,btol=1e-13,iter_lim=800)[0]
    u=proj_cone(u,sizes,ks,koff,TRI)
    if verbose:
        r0=Wmv(u)+cv
        print('warm: rnormL1=%.3e dualobj=%.10f'%(np.abs(r0).sum(), float(q@u)))
    y=u.copy(); tk=1.0; t0=time.time()
    best=None; bestcert=1e300
    Utr=make_Utr(t,F0s,sizes)
    for it in range(iters):
        r=Wmv(y)+cv
        g=2.0*Wrmv(r)+gamma*q
        unew=proj_cone(y-g/L,sizes,ks,koff,TRI)
        tk2=(1+np.sqrt(1+4*tk*tk))/2
        y=unew+((tk-1)/tk2)*(unew-u)
        u=unew; tk=tk2
        if (it+1)%200==0:
            rr=Wmv(u)+cv
            uu=Kmv(u)
            Ys=[(uu[roff[i]:roff[i]+n*n]+1j*uu[roff[i]+n*n:roff[i+1]]).reshape(n,n) for i,n in enumerate(sizes)]
            c,du,pen,rn=cert_eval(Ys,cv,StT,F0s,Utr)
            if c<bestcert: bestcert=c; best=[Y.copy() for Y in Ys]
            if verbose: print('  fista it=%d cert=%.10f dualobj=%.10f pen=%.1e rnorm=%.2e (%.0fs)'%(it+1,c,du,pen,rn,time.time()-t0))
    return dict(Ys=best,cert=bestcert)
