#!/usr/bin/env python3
# verify_bound06.py — BOUND-PROOF-06 machine verifier (qfa, beat-126)
# Self-contained; numpy only; deterministic seeds. 6 checks.
import numpy as np, itertools, sys
XS2 = list(itertools.product([0,1],[0,1])); XS4 = list(itertools.product(range(4), range(4)))
I2 = np.eye(2); fails = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("  | " + detail if detail else ""))
    if not ok: fails.append(name)

# V1 norm duality ||D||_1 = tr[sign(D) D]
rng = np.random.default_rng(126)
A = rng.normal(size=(4,4)) + 1j*rng.normal(size=(4,4)); D = (A+A.conj().T)/2
w,U = np.linalg.eigh(D); sgn = U@np.diag(np.sign(w))@U.conj().T
dev = abs(np.trace(sgn@D) - np.linalg.norm(D,'nuc'))
check("V1 norm duality", dev < 1e-12, f"dev={dev:.2e}")

# V2 balancedness: sum_x (-1)^{x_y} = 0 and C-term vanishes for any contractions
bal = all(sum((-1)**x[y] for x in XS2) == 0 for y in (0,1))
r = 2
C = []
for y in (0,1):
    B = rng.normal(size=(r,r))+1j*rng.normal(size=(r,r)); Q = (B+B.conj().T)/2
    C.append(Q/(np.linalg.norm(Q,2)+1e-9))
rho = rng.random((r,r)); rho = rho@rho.T; rho /= np.trace(rho)
ct = sum(sum((-1)**x[y] for x in XS2)*np.trace(C[y]@rho).real for y in (0,1))
check("V2 balancedness C-term=0", bal and abs(ct) < 1e-14, f"C-term={ct:.2e}")

# V3 functional identity: E/Q form == contraction form (random instances)
lam = np.sqrt(rng.random(r)); lam /= np.sqrt((lam**2).sum()); Dd = np.diag(lam)
psi = np.zeros(r*r, dtype=complex)
for i in range(r): psi[i*r+i] = lam[i]
rp = np.outer(psi, psi.conj())
def rc_():
    B = rng.normal(size=(r,r))+1j*rng.normal(size=(r,r)); Q = (B+B.conj().T)/2
    return Q/(np.linalg.norm(Q,2)+1e-9)
Ax = {}
for x in XS2:
    Xx = rng.normal(size=(2*r, r))+1j*rng.normal(size=(2*r, r)); q,_ = np.linalg.qr(Xx)
    Ax[x] = q[0:r].conj().T@q[0:r]
Qy = {(m,y): rc_() for m in (0,1) for y in (0,1)}
LHS = sum((-1)**x[y]*np.trace(np.kron((Ax[x] if m==0 else I2-Ax[x]).T, Qy[(m,y)])@rp).real
          for x in XS2 for y in (0,1) for m in (0,1))
RHS = sum((-1)**x[y]*np.trace(np.kron((2*Ax[x]-I2).T, (Qy[(0,y)]-Qy[(1,y)])/2)@rp).real
          for x in XS2 for y in (0,1))
dev = abs(LHS-RHS)
check("V3 E/Q-to-contraction identity", dev < 1e-12, f"dev={dev:.2e}")

# V4 vector bound: 200k random unit-vector tuples never exceed 4sqrt2; construction attains
best = 0.0
for t in range(200000):
    Ux = rng.normal(size=(4,3)); Ux /= np.linalg.norm(Ux, axis=1, keepdims=True)
    Vy = rng.normal(size=(2,3)); Vy /= np.linalg.norm(Vy, axis=1, keepdims=True)
    best = max(best, sum((-1)**x[y]*np.dot(Ux[xi],Vy[y]) for xi,x in enumerate(XS2) for y in (0,1)))
V0 = np.array([1.,0,0]); V1 = np.array([0.,1,0])
attain = sum(np.linalg.norm((-1)**x[0]*V0+(-1)**x[1]*V1) for x in XS2)
check("V4 vector max=4sqrt2", best <= 4*np.sqrt(2)+1e-9 and abs(attain-4*np.sqrt(2)) < 1e-12,
      f"rand_best={best:.6f} attain={attain:.12f}")

# V5 end-to-end Bell maximizer converges to 4sqrt2 and never above
def ptrB(M4): return np.trace(M4.reshape(2,2,2,2), axis1=1, axis2=3)
def ptrA(M4): return np.trace(M4.reshape(2,2,2,2), axis1=0, axis2=2)
def signop(H):
    H = (H+H.conj().T)/2; w,U = np.linalg.eigh(H)
    return U@np.diag(np.sign(np.where(np.abs(w)<1e-14,1.0,w)))@U.conj().T
def bell_max(seed, iters=300):
    rr = np.random.default_rng(seed)
    As = [signop(rr.normal(size=(2,2))+1j*rr.normal(size=(2,2))) for _ in range(4)]
    Bs = [signop(rr.normal(size=(2,2))+1j*rr.normal(size=(2,2))) for _ in range(2)]
    g = rr.normal(size=(4,1))+1j*rr.normal(size=(4,1)); g /= np.linalg.norm(g); psi = g@g.conj().T
    last = -1
    for _ in range(iters):
        Bop = sum((-1)**x[y]*np.kron(As[xi],Bs[y]) for xi,x in enumerate(XS2) for y in (0,1))
        w,U = np.linalg.eigh(Bop); psi = np.outer(U[:,-1],U[:,-1].conj())
        for xi in range(4):
            As[xi] = signop(sum((-1)**XS2[xi][y]*ptrB(np.kron(I2,Bs[y])@psi) for y in (0,1)))
        for y in (0,1):
            Bs[y] = signop(sum((-1)**x[y]*ptrA(np.kron(As[xi],I2)@psi) for xi,x in enumerate(XS2)))
        val = sum((-1)**x[y]*np.trace(np.kron(As[xi],Bs[y])@psi).real for xi,x in enumerate(XS2) for y in (0,1))
        if abs(val-last) < 1e-13: break
        last = val
    return last
vals = [bell_max(s) for s in range(1,13)]
check("V5 Bell max = 4sqrt2", max(vals) <= 4*np.sqrt(2)+1e-9 and max(vals) >= 4*np.sqrt(2)-1e-9,
      f"seed_max={max(vals):.12f}")

# V6 d=4 Fourier decomposition identity (infrastructure for DEBT-BOUND06-D4-01)
rng4 = np.random.default_rng(444); om = np.exp(1j*np.pi/2); rr4 = 2
X = rng4.normal(size=(rr4,rr4))+1j*rng4.normal(size=(rr4,rr4)); rhoB = X@X.conj().T; rhoB /= np.trace(rhoB)
w,U = np.linalg.eigh(rhoB); sq = U@np.diag(np.sqrt(w))@U.conj().T
F = {}; Mp = {}
for x in XS4:
    Ax4 = rng4.normal(size=(4*rr4, rr4))+1j*rng4.normal(size=(4*rr4, rr4)); q,_ = np.linalg.qr(Ax4)
    F[x] = [sq@(q[m*rr4:(m+1)*rr4].conj().T@q[m*rr4:(m+1)*rr4])@sq for m in range(4)]
for m in range(4):
    for y in range(2):
        Ax4 = rng4.normal(size=(4*rr4, rr4))+1j*rng4.normal(size=(4*rr4, rr4)); q,_ = np.linalg.qr(Ax4)
        Mp[(m,y)] = [q[v*rr4:(v+1)*rr4].conj().T@q[v*rr4:(v+1)*rr4] for v in range(4)]
S_d = sum(np.trace(F[x][m]@Mp[(m,y)][x[y]]).real for x in XS4 for y in range(2) for m in range(4))/32.0
S_f = 0.25
for k in (1,2,3):
    Tk = sum(om**(-k*x[y])*np.trace(F[x][m]@sum(om**(k*v)*Mp[(m,y)][v] for v in range(4)))
             for x in XS4 for y in range(2) for m in range(4))
    S_f += Tk/128.0
dev = abs(S_d-S_f)
check("V6 d4 Fourier decomposition", dev < 1e-12, f"dev={dev:.2e}")

print("\n%d checks, %d failed" % (6, len(fails)))
sys.exit(1 if fails else 0)
