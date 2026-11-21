# bp09/npa_twirl.py -- symmetry-twirled commuting-NPA (Beat-130)
# Abelian twirl: moment matrix block-diagonalizes into one small block per character.
# Block formula: M_chi[O,O'] = (1/sqrt(s_O*s_O')) * sum_k chi(k) * z(class(w_O, k.w_O'))
# where O ranges over word-orbits with chi|Stab(O)=1, s_O=|Stab(O)|.
# z = variables over (NF-class U G-orbit) equivalence classes of word-pair moments.
# Certificate (z-form): max c.z <= -sum_rho<Y_rho,F0_rho> + sum_rho max(0,lam_max(Y_rho))*U_rho + ||r||_1
#   r_c = sum_rho<F_c^rho,Y_rho> - c_c ;  U_rho = sum_O |G|/s_O + tr(F0_rho)   (|z|<=1)
import numpy as np, itertools, time, os

class TwirlNPA:
    def __init__(self, letters, povm_of, basis_words, gens, obj):
        # letters: list of letter keys (tuples); povm_of: letter->povm id
        # basis_words: list of tuples of letter-indices (A-side first)
        # gens: list of dict letter-idx -> letter-idx (group generators)
        # chars: list of complex arrays len |G| (one per conjugate pair representative)
        # obj: list of (w1_idx, w2_idx, coef)
        self.letters=letters; self.povm_of=povm_of; self.W=basis_words
        self.n=len(letters); self.N=len(basis_words)
        # group closure (gens = list of (permdict, expvec)); exps tracked mod 4
        assert len(gens[0])==2, 'gens must be (permdict, expvec) pairs'
        ngen=len(gens)
        G=[{i:i for i in range(self.n)}]; exps=[(0,)*ngen]
        seen={tuple(g[i] for i in range(self.n)):0 for g in G}
        q=list(G)
        while q:
            g=q.pop(); gi=seen[tuple(g[i] for i in range(self.n))]; eg=exps[gi]
            for hi,(h,eh) in enumerate(gens):
                for comp,ee in (({i:g[h[i]] for i in range(self.n)}, tuple((eg[j]+eh[j])%4 for j in range(ngen))),
                                ({i:h[g[i]] for i in range(self.n)}, tuple((eh[j]+eg[j])%4 for j in range(ngen)))):
                    key=tuple(comp[i] for i in range(self.n))
                    if key not in seen:
                        seen[key]=len(G); G.append(comp); exps.append(ee); q.append(comp)
        self.G=G; self.oG=len(G); self.exps=exps
        self.chars=None; self.char_names=None
        # word action table: gt[g][w] -> word index
        self.wpos={w:i for i,w in enumerate(self.W)}
        self.gt=np.zeros((self.oG,self.N),dtype=np.int64)
        for gi,g in enumerate(G):
            for wi,w in enumerate(self.W):
                self.gt[gi,wi]=self.wpos[tuple(g[l] for l in w)]
        # orbits & stabilizers
        self.orb=np.full(self.N,-1); self.reps=[]; self.stab=[]  # stab: list of g-indices fixing rep
        for wi in range(self.N):
            if self.orb[wi]>=0: continue
            oid=len(self.reps); members=set(self.gt[:,wi]); rep=min(members)
            for m in members: self.orb[m]=oid
            self.reps.append(rep)
            self.stab.append([gi for gi in range(self.oG) if self.gt[gi,rep]==rep])
        self.norb=len(self.reps)
        self.obj=obj
        self._classcache={}; self._zcache={}
    # ---- normal form of a word-pair moment ----
    def _redside(self, seq):
        if len(seq)==2:
            a,b=seq
            if self.povm_of[a]==self.povm_of[b]:
                return (a,) if a==b else None   # None = ZERO
        return tuple(seq)
    def class_key(self, wi, wj):
        # moment(w_i^dag w_j): letters reversed(w_i) + w_j, split sides, reduce
        key=(wi,wj)
        c=self._classcache.get(key)
        if c is not None: return c
        seq=tuple(reversed(self.W[wi]))+self.W[wj]
        As=tuple(l for l in seq if self.povm_of[l][0]==0)
        Bs=tuple(l for l in seq if self.povm_of[l][0]==1)
        ra=self._redside(As); rb=self._redside(Bs)
        if ra is None or rb is None: c='Z'
        else:
            k=(ra,rb); rev=(tuple(reversed(ra)),tuple(reversed(rb)))
            c=min(k,rev)
        self._classcache[key]=c; return c
    def _g_on_class(self, ck, gi):
        if ck=='Z': return 'Z'
        g=self.G[gi]; (ra,rb)=ck
        ka=tuple(g[l] for l in ra); kb=tuple(g[l] for l in rb)
        # still normal (G maps povms to povms)
        rev=(tuple(reversed(ka)),tuple(reversed(kb)))
        return min((ka,kb),rev)
    def zid_of_class(self, ck):
        if ck=='Z': return -1
        z=self._zcache.get(ck)
        if z is not None: return z
        orb={self._g_on_class(ck,gi) for gi in range(self.oG)}
        rep=min(orb)
        z=self._zcache.get(rep)
        if z is None:
            z=len(self.zmap); self.zmap.append(rep); self._zcache[rep]=z
        for o in orb: self._zcache[o]=z
        return z
    def set_chars(self, chars, char_names):
        assert len(chars[0])==self.oG, 'char length must equal |G|=%d'%self.oG
        self.chars=chars; self.char_names=char_names
    # ---- build blocks ----
    def build(self, verbose=True):
        self.zmap=[]; self._zcache={}
        t0=time.time()
        # allowed orbits per char
        self.blocks=[]
        for ci,chi in enumerate(self.chars):
            allowed=[o for o in range(self.norb) if all(abs(chi[h]-1)<1e-12 for h in self.stab[o])]
            entries={}  # (a,b) -> dict zid->coef(complex)
            for ai,O in enumerate(allowed):
                sO=len(self.stab[O]); wO=self.reps[O]
                for bi,O2 in enumerate(allowed):
                    sO2=len(self.stab[O2]); wO2=self.reps[O2]
                    acc={}
                    for k in range(self.oG):
                        c=self.class_key(wO, self.gt[k,wO2])
                        z=self.zid_of_class(c)
                        if z<0: continue
                        acc[z]=acc.get(z,0)+chi[k]/np.sqrt(sO*sO2)
                    entries[(ai,bi)]=acc
            self.blocks.append(dict(chi=ci,name=self.char_names[ci],allowed=allowed,entries=entries,
                                    size=len(allowed)))
        self.nz=len(self.zmap)
        # objective vector
        self.c=np.zeros(self.nz)
        for wi,wj,coef in self.obj:
            z=self.zid_of_class(self.class_key(wi,wj))
            assert z>=0
            self.c[z]+=coef
        # constant term: z for identity pair class = 1
        I_w=self.wpos[()]
        cI=self.class_key(I_w,I_w)
        zI=self.zid_of_class(cI)
        self.zI=zI
        if verbose:
            print('twirl build: |G|=%d words=%d orbits=%d z-vars=%d (%.1fs)'%(
                self.oG,self.N,self.norb,self.nz,time.time()-t0))
            print('blocks:', [(b['name'],b['size']) for b in self.blocks])
        return self
    # ---- assemble block matrices ----
    def block_mats(self, z):
        # returns list of complex matrices M_rho(z) (excluding constant F0)
        mats=[]
        for b in self.blocks:
            n=b['size']; M=np.zeros((n,n),complex)
            for (ai,bi),acc in b['entries'].items():
                v=sum(co*z[zi] for zi,co in acc.items())
                M[ai,bi]=v
            mats.append(M)
        return mats
    def F0_mats(self):
        # constant part from z_I = 1
        mats=[]
        for b in self.blocks:
            n=b['size']; M=np.zeros((n,n),complex)
            for (ai,bi),acc in b['entries'].items():
                v=sum(co*(1.0 if zi==self.zI else 0.0) for zi,co in acc.items())
                M[ai,bi]=v
            mats.append(M)
        return mats

    # ---- solver: ADMM on  max c.z s.t. F_rho(z)+F0_rho PSD for all rho ----
    def solve(self, mu=0.05, iters=2000, verbose=True):
        import scipy.sparse as sp
        from scipy.linalg import solve_triangular
        vid={z:i for i,z in enumerate(z for z in range(self.nz) if z!=self.zI)}
        nv=len(vid)
        cv=np.array([self.c[z] for z in range(self.nz) if z!=self.zI])
        Ss=[]; F0s=[]; sizes=[]
        for b in self.blocks:
            n=b['size']; F0=np.zeros((n,n),complex)
            rows=[];cols=[];vals=[]
            for (ai,bi),acc in b['entries'].items():
                for zi,co in acc.items():
                    if zi==self.zI: F0[ai,bi]+=co
                    else: rows.append(ai*n+bi); cols.append(vid[zi]); vals.append(co)
            Ss.append(sp.csr_matrix((vals,(rows,cols)),shape=(n*n,nv),dtype=complex))
            F0s.append(F0); sizes.append(n)
        # dense Gram (nv expected <= ~6000; else raise)
        Gm=np.zeros((nv,nv))
        for S in Ss:
            Gm+=(S.conj().T@S).real.toarray()
        Gm+=1e-9*np.eye(nv)
        LG=np.linalg.cholesky(Gm)
        def gsolve(rhs):
            t=solve_triangular(LG,rhs,lower=True)
            return solve_triangular(LG.T,t,lower=False)
        # exact per-block trace bound: tr X_rho = tr F_rho(z)+tr F0_rho ; |z|<=1
        Utr=[]
        for b,S,F0,n in zip(self.blocks,Ss,F0s,sizes):
            ub=0.0
            for ai in range(n):
                acc=b['entries'].get((ai,ai),{})
                ub+=sum(abs(co) for zi,co in acc.items() if zi!=self.zI)
            Utr.append(ub+abs(np.trace(F0)))
        def assemble(z):
            return [(S@z).reshape(n,n)+F0 for S,F0,n in zip(Ss,F0s,sizes)]
        Xs=[np.zeros((n,n),complex) for n in sizes]
        Ys=[np.zeros((n,n),complex) for n in sizes]
        z=np.zeros(nv)
        t0=time.time()
        for it in range(iters):
            rhs=mu*cv
            for S,Y,X,F0 in zip(Ss,Ys,Xs,F0s):
                rhs=rhs+(S.conj().T@(mu*Y+X-F0).reshape(-1)).real
            z=gsolve(rhs)
            mats=assemble(z)
            for i in range(len(Ss)):
                M=mats[i]-mu*Ys[i]; M=(M+M.conj().T)/2
                ev,U=np.linalg.eigh(M)
                Xs[i]=(U*np.clip(ev,0,None))@U.conj().T
                Ys[i]=Ys[i]+(Xs[i]-mats[i])/mu
            if verbose and (it+1)%500==0:
                rr=cv.copy()
                for S,Y in zip(Ss,Ys): rr+=(S.conj().T@Y.reshape(-1)).real
                print('  it=%d obj=%.10f rnorm=%.3e'%(it+1,float(cv@z),float(np.abs(rr).sum())))
        obj=float(cv@z)
        # ADMM saddle sign: sum S^T Y -> -cv at convergence, so evaluate cert at tY=-Y
        cert=0.0
        for Y,F0,ub in zip(Ys,F0s,Utr):
            lm=np.linalg.eigvalsh((Y+Y.conj().T)/2).min()
            cert+=np.real(np.trace(F0.conj().T@Y))+max(0.0,-lm)*ub
        r=np.zeros(nv)
        for S,Y in zip(Ss,Ys):
            r+=(S.conj().T@Y.reshape(-1)).real
        r=r+cv
        cert+=float(np.abs(r).sum())
        pres=float(max(0.0,max(-np.linalg.eigvalsh((m+m.conj().T)/2).min() for m in mats)))
        if verbose: print('solve: obj=%.10f cert=%.10f pres=%.1e rnorm=%.1e (%.1fs, nv=%d)'%(
            obj,cert,pres,np.abs(r).sum(),time.time()-t0,nv))
        return dict(obj=obj,cert=float(cert),pres=pres,rnorm=float(np.abs(r).sum()),z=z)

    # ---- large-scale solver: ADMM with warm-started CG inner solve + checkpointing ----
    def solve_cg(self, mu=0.1, iters=4000, verbose=True, ckpt=None, cg_tol=1e-6, cg_max=80, reg=1e-7, alpha=1.0):
        import scipy.sparse as sp
        vid={z:i for i,z in enumerate(z for z in range(self.nz) if z!=self.zI)}
        nv=len(vid)
        cv=np.array([self.c[z] for z in range(self.nz) if z!=self.zI])
        Ss=[]; F0s=[]; sizes=[]
        for b in self.blocks:
            n=b['size']; F0=np.zeros((n,n),complex)
            rows=[];cols=[];vals=[]
            for (ai,bi),acc in b['entries'].items():
                for zi,co in acc.items():
                    if zi==self.zI: F0[ai,bi]+=co
                    else: rows.append(ai*n+bi); cols.append(vid[zi]); vals.append(co)
            Ss.append(sp.csr_matrix((vals,(rows,cols)),shape=(n*n,nv),dtype=complex))
            F0s.append(F0); sizes.append(n)
        # merged real operator: St = vstack([Re S; Im S]) over all blocks; row slices per block
        St=sp.vstack([sp.vstack([S.real,S.imag]) for S in Ss]).tocsr()
        StT=St.T.tocsr()
        roff=np.cumsum([0]+[2*n*n for n in sizes])
        # diagonal preconditioner of Gram
        dg=reg+np.asarray(St.multiply(St).sum(axis=0)).ravel()
        Minv=1.0/dg
        def Aop(x):
            return StT@(St@x)+reg*x
        self.cgit=0
        def cg(b,x0):
            x=x0.copy(); r=b-Aop(x); z0=Minv*r; p=z0.copy(); rz=float(r@z0)
            bnorm=max(1e-30,float(b@b))**0.5
            for itc in range(cg_max):
                Ap=Aop(p); alpha=rz/max(1e-300,float(p@Ap))
                x+=alpha*p; r-=alpha*Ap
                self.cgit+=1
                if float(r@r)**0.5<cg_tol*bnorm: break
                z0=Minv*r; rz2=float(r@z0); p=z0+(rz2/max(1e-300,rz))*p; rz=rz2
            return x
        Utr=[]
        for b,F0,n in zip(self.blocks,F0s,sizes):
            ub=0.0
            for ai in range(n):
                acc=b['entries'].get((ai,ai),{})
                ub+=sum(abs(co) for zi,co in acc.items() if zi!=self.zI)
            Utr.append(ub+abs(np.trace(F0)))
        Xs=[np.zeros((n,n),complex) for n in sizes]
        Ys=[np.zeros((n,n),complex) for n in sizes]
        z=np.zeros(nv); it0=0
        if ckpt and os.path.exists(ckpt):
            d=np.load(ckpt,allow_pickle=True)
            z=d['z']; Xs=list(d['Xs']); Ys=list(d['Ys']); it0=int(d['it0'])
            if verbose: print('resumed from it=%d'%it0)
        def stackvec(mats_like):  # concat [Re vec; Im vec] per block
            return np.concatenate([np.concatenate([m.reshape(-1).real,m.reshape(-1).imag]) for m in mats_like])
        t0=time.time()
        Yacc=[np.zeros((n,n),complex) for n in sizes]; nacc=0
        acct0=it0+iters//2
        for it in range(it0,it0+iters):
            rhs=mu*cv+StT@stackvec([mu*Y+X-F0 for Y,X,F0 in zip(Ys,Xs,F0s)])
            z=cg(rhs,z)
            zfull=St@z
            mats=[(zfull[roff[i]:roff[i]+n*n]+1j*zfull[roff[i]+n*n:roff[i+1]]).reshape(n,n)+F0
                  for i,(n,F0) in enumerate(zip(sizes,F0s))]
            for i in range(len(Ss)):
                H=alpha*mats[i]+(1.0-alpha)*Xs[i]
                M=H-mu*Ys[i]; M=(M+M.conj().T)/2
                ev,U=np.linalg.eigh(M)
                Xs[i]=(U*np.clip(ev,0,None))@U.conj().T
                Ys[i]=Ys[i]+(Xs[i]-H)/mu
            if it>=acct0:
                for i in range(len(Ss)): Yacc[i]+=Ys[i]
                nacc+=1
            if ckpt and (it+1)%200==0:
                np.savez(ckpt,z=z,Xs=np.array(Xs,dtype=object),Ys=np.array(Ys,dtype=object),it0=it+1)
            if verbose and (it+1)%250==0:
                rr=cv+StT@stackvec(Ys)
                print('  it=%d obj=%.10f rnorm=%.3e cg/it=%.1f (%.0fs)'%(
                    it+1,float(cv@z),float(np.abs(rr).sum()),self.cgit/float(it+1-it0),time.time()-t0))
        obj=float(cv@z)
        cert=0.0; dualobj=0.0; pen=0.0
        for Y,F0,ub in zip(Ys,F0s,Utr):
            lm=np.linalg.eigvalsh((Y+Y.conj().T)/2).min()
            dualobj+=np.real(np.trace(F0.conj().T@Y)); pen+=max(0.0,-lm)*ub
        cert=dualobj+pen
        r=cv+StT@stackvec(Ys)
        cert+=float(np.abs(r).sum())
        # ergodic-average certificate (second-half Y average: cancels oscillation)
        certa=None; rnorma=None; duala=None; pena=None
        if nacc>0:
            Ybar=[Y/nacc for Y in Yacc]
            dualobja=0.0; pena2=0.0
            for Y,F0,ub in zip(Ybar,F0s,Utr):
                lm=np.linalg.eigvalsh((Y+Y.conj().T)/2).min()
                dualobja+=np.real(np.trace(F0.conj().T@Y)); pena2+=max(0.0,-lm)*ub
            ra=cv+StT@stackvec(Ybar)
            rnorma=float(np.abs(ra).sum())
            duala=float(dualobja); pena=float(pena2)
            certa=float(dualobja+pena2+rnorma)
        zc=z.astype(complex)
        mats=[(S@zc).reshape(n,n)+F0 for S,F0,n in zip(Ss,F0s,sizes)]
        pres=float(max(0.0,max(-np.linalg.eigvalsh((m+m.conj().T)/2).min() for m in mats)))
        if verbose: print('solve_cg: obj=%.10f cert=%.10f pres=%.1e rnorm=%.1e dualobj=%.10f pen=%.2e (%.1fs, nv=%d)'%(
            obj,cert,pres,np.abs(r).sum(),dualobj,pen,time.time()-t0,nv))
        if certa is not None:
            if verbose: print('  AVG-cert: %.10f (dualobj=%.10f pen=%.1e rnorm=%.1e, n=%d)'%(certa,duala,pena,rnorma,nacc))
        if ckpt: np.savez(ckpt,z=z,Xs=np.array(Xs,dtype=object),Ys=np.array(Ys,dtype=object),it0=it0+iters)
        return dict(obj=obj,cert=float(cert),pres=pres,rnorm=float(np.abs(r).sum()),z=z,
                    dualobj=float(dualobj),pen=float(pen),
                    cert_avg=certa,rnorm_avg=rnorma,dualobj_avg=duala,pen_avg=pena)
