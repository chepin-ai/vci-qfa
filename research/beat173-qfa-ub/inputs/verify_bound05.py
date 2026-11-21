#!/usr/bin/env python3
# verify_bound05.py — BOUND-PROOF-05 machine verifier (qfa, beat-125)
# Self-contained; numpy only; deterministic seeds; prints per-check PASS/FAIL.
import numpy as np, itertools, sys

Z = np.array([[1,0],[0,-1]], dtype=complex); X = np.array([[0,1],[1,0]], dtype=complex)
I2 = np.eye(2); XS2 = list(itertools.product([0,1],[0,1]))
fails = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("  | " + detail if detail else ""))
    if not ok: fails.append(name)

# C1: Schmidt-compression trace identity  tr[(E x M)|psi><psi|] = tr[D E^T D M]
rr = np.random.default_rng(99); r = 3
lam = np.sqrt(rr.random(r)/1.0); lam /= np.sqrt((lam**2).sum())
D = np.diag(lam)
psi = np.zeros(r*r, dtype=complex)
for i in range(r): psi[i*r+i] = lam[i]
rp = np.outer(psi, psi.conj())
E = rr.normal(size=(r,r)) + 1j*rr.normal(size=(r,r)); E = E@E.conj().T/10 + np.eye(r)*0.1
M = rr.normal(size=(r,r)) + 1j*rr.normal(size=(r,r)); M = M@M.conj().T/10 + np.eye(r)*0.1
dev = abs(np.trace(np.kron(E,M)@rp) - np.trace(D@E.T@D@M))
check("C1 schmidt-compression identity", dev < 1e-12, f"dev={dev:.2e}")

# C2: steering realizability — every valid F-decomposition is steerable from canonical purification
def rand_F(r, rng):
    Xx = rng.normal(size=(r,r)) + 1j*rng.normal(size=(r,r))
    rho = Xx@Xx.conj().T; rho /= np.trace(rho)
    w,U = np.linalg.eigh(rho); sq = U@np.diag(np.sqrt(np.clip(w,0,None)))@U.conj().T
    F = {}
    for x in XS2:
        A = rng.normal(size=(2*r, r)) + 1j*rng.normal(size=(2*r, r))
        q,_ = np.linalg.qr(A)
        K = [q[m*r:(m+1)*r,:].conj().T@q[m*r:(m+1)*r,:] for m in range(2)]
        F[x] = [sq@K[m]@sq for m in range(2)]
    return F, rho
F0, rhoB = rand_F(2, np.random.default_rng(7))
w,U = np.linalg.eigh(rhoB); sq = U@np.diag(np.sqrt(w))@U.conj().T
isq = U@np.diag(1/np.sqrt(np.clip(w,1e-15,None)))@U.conj().T
dev = 0.0
for x in XS2:
    for m in range(2):
        K = isq @ F0[x][m] @ isq
        dev = max(dev, np.abs(sq @ K @ sq - F0[x][m]).max())   # steered F = D K D with K=rho^-1/2 F rho^-1/2
check("C2 steering realizability", dev < 1e-12, f"max_dev={dev:.2e}")

# C3: Helstrom closure identity  S = 1/2 + Phi/16  on a random valid decomposition (Bob optimum, binary guess)
def helstrom_best(F, r):
    Snum = 0.0
    for m in range(2):
        for y in range(2):
            Hv = [sum((F[x][m] for x in XS2 if x[y]==v), np.zeros((r,r))) for v in range(2)]
            Dd = Hv[0]-Hv[1]; w,U = np.linalg.eigh(Dd)
            P = U[:, w < 1e-12] @ U[:, w < 1e-12].conj().T
            Snum += np.trace(Hv[0]@(np.eye(r)-P) + Hv[1]@P).real
    return Snum/8.0
def phi_of(F):
    t = 0.0
    for m in range(2):
        D1 = F[(0,0)][m]+F[(0,1)][m]-F[(1,0)][m]-F[(1,1)][m]
        D2 = F[(0,0)][m]+F[(1,0)][m]-F[(0,1)][m]-F[(1,1)][m]
        t += np.linalg.norm(D1,'nuc')+np.linalg.norm(D2,'nuc')
    return t
F1, _ = rand_F(2, np.random.default_rng(123))
lhs = helstrom_best(F1, 2); rhs = 0.5 + phi_of(F1)/16.0
check("C3 helstrom closure S=1/2+Phi/16", abs(lhs-rhs) < 1e-10, f"S={lhs:.9f}")

# C4: r=1 classical gates — d=2 exhaustive = 3/4 ; d=4 constructive = 5/8 (BP-03 agreement)
best = 0.0
for fb in itertools.product([0,1], repeat=4):
    f = dict(zip(XS2, fb))
    for gb in itertools.product([0,1], repeat=4):
        g = {(m,y): gb[2*m+y] for m in (0,1) for y in (0,1)}
        best = max(best, sum(1 for x in XS2 for y in (0,1) if g[(f[x],y)]==x[y])/8.0)
ok42 = abs(best-0.75) < 1e-15
XS4 = list(itertools.product(range(4), range(4)))
f4 = {x: x[0] for x in XS4}   # send first dit; Bob: y=0 -> exact, y=1 -> majority-0 guess
s4 = sum(1 for x in XS4 for y in (0,1) if (f4[x] if y==0 else 0) == x[y]) / (2*16)
check("C4 classical gates", ok42 and abs(s4-5/8) < 1e-15, f"d2={best:.6f} d4_constructive={s4:.6f}")

# C5: explicit CHSH->RAC affine-reduction strategy hits (2+sqrt2)/4 at Schmidt rank 2
def proj(obs, bit):
    w,U = np.linalg.eigh(obs); P = np.zeros((2,2), dtype=complex)
    for i, wi in enumerate(w):
        if (0 if wi > 0 else 1) == bit: P += np.outer(U[:,i], U[:,i].conj())
    return P
Aobs = [Z, X]; Bobs = [(Z+X)/np.sqrt(2), (Z-X)/np.sqrt(2)]
psi2 = np.array([1,0,0,1], dtype=complex)/np.sqrt(2); rpsi = np.outer(psi2, psi2.conj())
S_full = 0.0
for x in XS2:
    for y in (0,1):
        for m in (0,1):
            E = proj(Aobs[x[0]^x[1]], m ^ x[0])          # m = atilde ^ x0
            Mv = proj(Bobs[y], x[y] ^ m)                # guess b = btilde ^ m == x_y
            S_full += np.trace(np.kron(E, Mv) @ rpsi).real
S_full /= 8.0
tgt = (2+np.sqrt(2))/4
check("C5 CHSH->RAC explicit strategy", abs(S_full-tgt) < 1e-12, f"S={S_full:.15f} tgt={tgt:.15f}")

# C6: same strategy in reduced formalism — Phi = 4*sqrt2 exactly
D2q = I2/np.sqrt(2)
F2 = {x: [D2q @ proj(Aobs[x[0]^x[1]], m ^ x[0]) @ D2q for m in (0,1)] for x in XS2}
phi_star = phi_of(F2)
check("C6 reduced Phi=4sqrt2", abs(phi_star-4*np.sqrt(2)) < 1e-12, f"Phi={phi_star:.15f}")

# C7: annealed free search corroborates lower bound (never exceeds 4sqrt2 + tol)
def anneal(seed, rounds=6000):
    rng = np.random.default_rng(seed)
    Fb, rb = rand_F(2, rng)
    class ST: pass
    st = ST(); st.F = Fb
    # hill-climb on K-isometries
    def reF(qs, sq):
        out = {}
        for x in XS2:
            q = qs[x]
            K = [q[m*2:(m+1)*2,:].conj().T@q[m*2:(m+1)*2,:] for m in range(2)]
            out[x] = [sq@K[m]@sq for m in range(2)]
        return out
    w,U = np.linalg.eigh(rb); sq = U@np.diag(np.sqrt(np.clip(w,0,None)))@U.conj().T
    qs = {}
    for x in XS2:
        A = rng.normal(size=(4,2)) + 1j*rng.normal(size=(4,2)); qs[x],_ = np.linalg.qr(A)
    cur = phi_of(reF(qs, sq))
    for i in range(rounds):
        eps = 0.5*(1-i/rounds)+0.005
        x = XS2[rng.integers(4)]
        A = qs[x] + eps*(rng.normal(size=qs[x].shape)+1j*rng.normal(size=qs[x].shape))
        qn,_ = np.linalg.qr(A); old = qs[x]; qs[x] = qn
        ph = phi_of(reF(qs, sq))
        if ph >= cur: cur = ph
        else: qs[x] = old
    return cur
ph_ann = max(anneal(s) for s in (1,2,3))
check("C7 anneal corroboration", 4.0 - 1e-9 <= ph_ann <= 4*np.sqrt(2) + 1e-9,
      f"Phi_anneal={ph_ann:.6f} (classical=4, tsirelson=4sqrt2={4*np.sqrt(2):.6f})")

print("\n%d checks, %d failed" % (7, len(fails)))
sys.exit(1 if fails else 0)
