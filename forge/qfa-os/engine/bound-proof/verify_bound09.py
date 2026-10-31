# bp09/verify_bound09.py -- BP-09 verification harness (Beat-130)
# Validates the symmetry-twirled NPA engine and the certified RAC-4 1+AB upper bound.
# Modes: quick (default) / full (deeper ADMM convergence). Exit 0 iff all checks PASS.
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from npa_twirl import TwirlNPA
from test_twirl import build_W_1AB, build_RAC4_L1, build_RAC4_1AB, make_chars_Z4, make_chars_Z4cube
from facial_polish import load_system, cert_eval, make_Utr

MODE = sys.argv[1] if len(sys.argv) > 1 else 'quick'
HERE = os.path.dirname(os.path.abspath(__file__))
TGT_L1 = (2 + 3 * np.sqrt(2)) / 8          # 0.7803300859 BP-08 certified L1 value
W1AB_B08 = 0.7441360147                    # BP-08 certified W 1+AB UB
W_SEESAW = 0.7404886669                    # BP-07 quantum see-saw lower bound
RAC4_LB = 0.75                             # BP-07 quantum lower bound (uniform-win strategy)
results = []

def check(name, ok, detail=''):
    results.append((name, bool(ok), detail))
    print('[%s] %s %s' % ('PASS' if ok else 'FAIL', name, detail))

# ---------- check 1: W-game 1+AB twirl vs BP-08 numbers ----------
l, p, w, g, o = build_W_1AB()
t = TwirlNPA(l, p, w, g, o)
c, n = make_chars_Z4(t); t.set_chars(c, n); t.build(verbose=False)
iters = 2000 if MODE == 'quick' else 6000
r = t.solve_cg(mu=0.1, iters=iters, verbose=False, alpha=1.6)
ok1 = (r['obj'] >= W_SEESAW - 1e-9) and (r['cert'] <= W1AB_B08 + 2e-5) and (r['cert'] >= r['obj'] - 5e-8)
check('W-1AB-twirl-vs-BP08', ok1, 'obj=%.10f cert=%.10f pres=%.1e' % (r['obj'], r['cert'], r['pres']))

# ---------- check 2: RAC4 level-1 twirl reproduces BP-08 L1 value ----------
l, p, w, g, o = build_RAC4_L1()
t = TwirlNPA(l, p, w, g, o)
c, n = make_chars_Z4cube(t); t.set_chars(c, n)
t.build(verbose=False)
ok_struct = (t.oG == 64) and (t.norb == 4)
iters = 6000 if MODE == 'quick' else 20000
r = t.solve(mu=0.1, iters=iters, verbose=False)
tolc = 1e-3 if MODE == 'quick' else 2e-6
ok2 = abs(r['obj'] - TGT_L1) < 1e-6 and (TGT_L1 - 1e-9) <= r['cert'] <= TGT_L1 + tolc
check('RAC4-L1-twirl-eq-BP08', ok2 and ok_struct,
      'obj=%.10f cert=%.10f struct=%s' % (r['obj'], r['cert'], ok_struct))

# ---------- check 3: RAC4 1+AB structure invariants ----------
l, p, w, g, o = build_RAC4_1AB()
t = TwirlNPA(l, p, w, g, o)
c, n = make_chars_Z4cube(t); t.set_chars(c, n); t.build(verbose=False)
sizes = sorted(b['size'] for b in t.blocks)
ok_sizes = sizes == sorted([36] + [35]*2 + [34]*14 + [33]*19)
cv, Ss, F0s, sizes_l, St = load_system(t)
# F0 invariant: constant part comes only from the identity class; per block it is E_{00}
# on the identity orbit (only in the trivial-character block), else 0.  => sum_rho tr F0 = 1
f0_tr = sum(float(np.trace(F0).real) for F0 in F0s)
f0_fr = sum(float(np.sum(np.abs(F0)**2)) for F0 in F0s)
f0_ok = abs(f0_tr - 1.0) < 1e-12 and abs(f0_fr - 1.0) < 1e-12
ok3 = (t.oG == 64) and (t.norb == 36) and (t.nz == 28439) and (len(t.blocks) == 36) and ok_sizes and f0_ok
check('RAC4-1AB-structure', ok3, 'G=%d orbits=%d z=%d blocks=%d sumtr(F0)=%.6f' % (t.oG, t.norb, t.nz, len(t.blocks), f0_tr))

# ---------- check 4: sealed dual witness reproduces the certified UB ----------
StT = St.T.tocsr()
Utr = make_Utr(t, F0s, sizes_l)
d = np.load(os.path.join(HERE, 'y_best.npz'), allow_pickle=True)
Ys = [np.array(y) for y in d['Ys']]
cert_w, du_w, pen_w, rn_w = cert_eval(Ys, cv, StT, F0s, Utr)
ok4 = (cert_w <= 0.7540) and (cert_w >= RAC4_LB - 1e-9) and (abs(du_w - 0.75) < 2e-3)
check('RAC4-1AB-witness-cert', ok4,
      'cert=%.10f dualobj=%.10f pen=%.1e rnorm=%.2e' % (cert_w, du_w, pen_w, rn_w))

# ---------- check 5: classical 5/8 strategy feasible in twirled system ----------
# deterministic protocol: Alice m = X1 ; Bob g(0,m)=m, g(1,m)=0  -> win rate 5/8.
letters = t.letters
def letter_val(li):
    lt = letters[li]
    if lt[0] == 'A':
        _, x, m = lt
        return 1.0 if m == x // 4 else 0.0          # m = X1
    _, y, m, v = lt
    g = m if y == 0 else 0
    return 1.0 if v == g else 0.0
wv = np.array([letter_val(li) for li in range(len(letters))])
def word_val(wd):
    v = 1.0
    for li in wd:
        v *= wv[li]
    return v
# symmetrized classical z: z_sym[class] = (1/|G|) sum_g Gamma_cl[g.wi, g.wj]
gt = t.gt
zsym = np.zeros(t.nz)
reps = [int(x) for x in t.reps]
wvals = {wd: word_val(wd) for wd in t.W}
for O in range(t.norb):
    for O2 in range(t.norb):
        for k in range(t.oG):
            wi = reps[O]; wj = int(gt[k, reps[O2]])
            ck = t.class_key(wi, wj)
            zid = t.zid_of_class(ck)
            if zid < 0:
                continue
            s = 0.0
            for gi in range(t.oG):
                s += wvals[t.W[int(gt[gi, wi])]] * wvals[t.W[int(gt[gi, wj])]]
            zsym[zid] = s / t.oG
zsym[t.zI] = 1.0
# assemble blocks and test PSD
min_ev = 1e300
for b in t.blocks:
    nb = b['size']
    M = np.zeros((nb, nb), complex)
    for (ai, bi), acc in b['entries'].items():
        M[ai, bi] = sum(co * (1.0 if zi == t.zI else zsym[zi]) for zi, co in acc.items())
    M = (M + M.conj().T) / 2
    min_ev = min(min_ev, float(np.linalg.eigvalsh(M).min()))
obj_c = float(sum(t.c[zi] * (1.0 if zi == t.zI else zsym[zi]) for zi in range(t.nz)))
ok5 = (min_ev > -1e-9) and abs(obj_c - 0.625) < 1e-12
check('classical-5/8-feasible', ok5, 'min block eig=%.2e obj_classical=%.12f' % (min_ev, obj_c))

# ---------- summary ----------
nfail = sum(1 for _, ok, _ in results if not ok)
print('BP-09 verify (%s): %d checks, %d fail' % (MODE, len(results), nfail))
sys.exit(1 if nfail else 0)
