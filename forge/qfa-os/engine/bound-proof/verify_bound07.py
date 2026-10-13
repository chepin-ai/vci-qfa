# verify_bound07.py — BP-07: d=4 entanglement-assisted random access code (4^2 -> 1 ququart)
# numpy-only, runner-safe. All checks are exact certificates or provably exhaustive enumerations.
# Law: 未实测的说"未实测" — quantum UB=3/4 is a CONJECTURE (numeric plateau), not asserted here.
import numpy as np, json, zlib, base64, itertools, sys

fails=[]
def check(name, ok, detail=""):
    print(("PASS" if ok else "FAIL"), name, detail)
    if not ok: fails.append(name)

w=1j

# ---------- Check 1: classical lower bound certificate ----------
# Alice sends m=X1; Bob y=0 guesses v=m (always right), y=1 guesses 0 (right 1/4 of the time)
a=[x//4 for x in range(16)]
wins=0
for x in range(16):
    X1,X2=x//4,x%4
    for y in range(2):
        m=a[x]; v=m if y==0 else 0
        if v==[X1,X2][y]: wins+=1
check("classical-LB-certificate", wins==20, "win-sum=%d -> S>=20/32=5/8"%wins)

# ---------- Check 2: classical upper bound, exhaustive over Bob "representatives" ----------
# For any deterministic Alice coloring, Bob-optimal decoding picks per message-class c a row-rep v1(c)
# and a col-rep v2(c); given reps, the best coloring assigns each cell independently to argmax.
# Enumerating all 4^4 x 4^4 rep-pairs with per-cell optimal assignment is therefore globally exact.
X1=np.arange(16)//4; X2=np.arange(16)%4
E1=np.zeros((16,4,4),int); E2=np.zeros((16,4,4),int)
for x in range(16):
    for cc in range(4):
        for av in range(4):
            E1[x,cc,av]=(X1[x]==av); E2[x,cc,av]=(X2[x]==av)
G=np.indices((4,4,4,4)).reshape(4,-1).T
V1=np.zeros((256,16,4),int); V2=np.zeros((256,16,4),int)
for g in range(256):
    for cc in range(4):
        V1[g,:,cc]=E1[:,cc,G[g,cc]]; V2[g,:,cc]=E2[:,cc,G[g,cc]]
best=0
for g2 in range(256):
    tot=(V1+V2[g2][None]).max(axis=2).sum(axis=1)
    best=max(best,int(tot.max()))
check("classical-UB-exact", best==20, "max win-sum over all deterministic strategies = %d -> S<=5/8"%best)
check("classical-exact-5/8", best==20 and wins==20, "S_classical(d=4 EA-RAC) = 5/8 EXACT")

# ---------- Check 3: O-operator collapse  2 Re(w^-X Q^1) + w^-2X Q^2 = 4 M_X - I ----------
rng=np.random.default_rng(7)
ok=True
for _ in range(6):
    A=rng.standard_normal((4,4))+1j*rng.standard_normal((4,4))
    Q_,R_=np.linalg.qr(A)          # random orthonormal basis -> projective POVM
    M=[np.outer(Q_[:,v].conj(),Q_[:,v]) for v in range(4)]
    Q1=sum(w**v*M[v] for v in range(4)); Q2=sum(w**(2*v)*M[v] for v in range(4))
    for X in range(4):
        B=w**(-X)*Q1; R=B+B.conj().T+w**(-2*X)*Q2   # 2 Re_Hermitian(w^-X Q1) + w^-2X Q2
        ok=ok and np.abs(R-(4*M[X]-np.eye(4))).max()<1e-12
check("O-operator-identity", ok, "R_X = 4 M_X - I (T-split is definitionally exact)")

# ---------- Check 4: quantum lower bound certificate, embedded strategy ----------
BLOB="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"
d=json.loads(zlib.decompress(base64.b64decode(BLOB)))
U=np.array(d["U_re"])+1j*np.array(d["U_im"]); sq=np.array(d["sq"])
al=U[:16].conj().transpose(0,2,1); be=U[16:].conj().transpose(0,2,1)
amp=np.einsum("k,xmk,svk->xmsv",sq,al,be); P=np.abs(amp)**2
S=float(sum(P[x,m,y*4+m,[x//4,x%4][y]] for x in range(16) for y in range(2) for m in range(4))/32)
Wm=np.array([[sum(P[x,m,y*4+m,[x//4,x%4][y]] for m in range(4)) for y in range(2)] for x in range(16)])
Ts=[]
for k in range(4):
    Tk=0j
    for x in range(16):
        Xy=[x//4,x%4]
        for y in range(2):
            for m in range(4):
                sg=np.outer(al[x][m],al[x][m].conj())/4
                Qo=sum(w**(k*v)*np.outer(be[y*4+m][v].conj(),be[y*4+m][v]) for v in range(4))
                Tk+=w**(-k*Xy[y])*np.trace(sg@Qo)
    Ts.append(Tk)
check("quantum-LB-3/4", abs(S-0.75)<1e-12, "S = %.15f (max-ent state, projective POVMs)"%S)
check("uniform-win", np.abs(Wm-0.75).max()<1e-9, "P(win|x,y)=3/4 forall (x,y), dev=%.2e"%np.abs(Wm-0.75).max())
check("T-structure", abs(Ts[0]-32)<1e-8 and all(abs(Ts[k]-64/3)<1e-8 for k in (1,2,3)),
      "T0=32, T1=T2=T3=64/3 -> S=1/4+(2*64/3+64/3)/128=3/4")

# ---------- Check 5: two-CHSH bit-plane product falls short ----------
prod=((2+np.sqrt(2))/4)**2
check("ququart-advantage", abs(prod-(3+2*np.sqrt(2))/8)<1e-15 and 0.75>prod,
      "((2+sqrt2)/4)^2 = %.9f < 3/4"%prod)

# ---------- Check 6: affine reduction classical W = 5/8 (exact brute force) ----------
bestW=0
for b0 in range(4):
    for b1 in range(4):
        for av in itertools.product(range(4),repeat=4):
            sc=sum((av[u]+b0)%4==0 for u in range(4))+sum((av[u]+b1)%4==u for u in range(4))
            bestW=max(bestW,sc)
check("affine-W-classical", bestW==5, "max wins=%d -> W_classical=5/8 (|U0|+|U1|<=5)"%bestW)

print()
if fails: print("FAILED:",fails); sys.exit(1)
print("verify_bound07: 10 checks, 0 failed")
print("STATUS: classical=5/8 EXACT; quantum>=3/4 certified; quantum<=3/4 CONJECTURE (numeric, unproven)")
