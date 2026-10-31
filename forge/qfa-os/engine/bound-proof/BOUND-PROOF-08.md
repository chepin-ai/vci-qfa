# BOUND-PROOF-08 — d=4 EA-RAC quantum upper bounds via NPA (Beat-129)

**Status: sealed. First nontrivial certified upper bound for the d=4 EA-RAC quantum value.**

## 1. Problem

d=4 EA-RAC (BP-07 setting): Alice gets x=(X₁,X₂)∈ℤ₄², sends m∈ℤ₄; Bob gets y∈{0,1} and guesses X_y.
Beat-127/128 established: classical value = **5/8 EXACT**; quantum value ≥ **3/4** (certified construction,
uniform-win, T₀=32, T₁=T₂=T₃=64/3). The quantum **upper** bound remained open (trivial UB = 1).
This beat attacks the UB with the commuting-operator NPA hierarchy.

## 2. Machinery (all code in `npa_core.py` / `npa_1ab.py`, validated below)

- **Level-1 NPA**: letters = Alice projectors {A_x^m} (64) + Bob projectors {M_v^{y,m}} (32),
  Naimark per side; moment matrix Γ (97×97, real symmetric WLOG since all coefficients real).
  Constraints: Γ[I,I]=1; within-POVM orthogonality; completeness Σ_m Γ[A_x^m,S]=Γ[I,S] ∀S. m=2473 rows.
- **Level 1+AB** (W game): basis {I} ∪ letters ∪ A·M words, N=153; constraints = normal-form
  equalities (orthogonality/idempotency/completeness reductions, reversal symmetry), 7421 rows.
- **Solver**: custom ADMM (Wen–Goldfarb–Yin dual form), one Cholesky of AAᵀ, `solve_triangular` per
  iteration. Deterministic from zero init.
- **Certificate (rigorous at any iteration)**: for primal max⟨C,X⟩ s.t. AX=b, X⪰0, and ANY dual y,
  with D = Cv − Aᵀy (Cv=−C):
  `max⟨C,X⟩ ≤ −bᵀy + max(0,−λ_min(D))·trX`
  where trX is FIXED by completeness: RAC-4: 25, W-L1: 7, W-1AB: 15 (Γ[I,I] + Σ POVM unit traces + Σ AB-word diagonals = correlations summing to input count).

## 3. Results

| object | bound | certificate |
|---|---|---|
| d=2 RAC, level-1 | **(2+√2)/4 = 0.8535533906** | matches known exact value to 1e-10 — machinery validated |
| **d=4 RAC, level-1** | **UB = (2+3√2)/8 = 0.7803300859** | λ_min=−1.1e-14, pres=3.9e-14; first nontrivial certified UB |
| W game, level-1 (corrected) | **UB = (2+3√2)/8 = 0.7803300859** | identical to RAC-4 to 10 digits: affine reduction preserves the level-1 relaxation value |
| W game, 1+AB | **UB = 0.7441360147** | 2400 iters, λ_min=−1.1e-6, pres=3.7e-8; converged (trajectory 0.74866→0.74420→0.74415→0.74414) |

**Intervals after this beat:**
- d=4 EA-RAC quantum value ∈ **[3/4, (2+3√2)/8]** = [0.75, 0.7803300859]
- W game quantum value ∈ **[0.7404886669, 0.7441360147]** (see-saw LB vs 1+AB UB)

Classical optimal strategies (5/8, from BP-07 certificates) are exactly feasible (residual 0.0) in all
three constraint systems — independent correctness check of the encodings.

## 4. W-game adjudication (互纠三条 post-mortem)

The first W-NPA encoding returned 0.6730167462, **below** the see-saw lower bound 0.7404886669 —
impossible for a relaxation, so a bug was certain. Cross-validation chain:

1. See-saw re-run (dim 4/5/6, fresh restarts): 0.7404885021 / 0.7404886669 — beat-128 number **reproduced twice**.
2. The see-saw strategy's level-1 moment matrix, built independently: feasible in the *corrected* W system
   (residual 3.1e-16, eigmin −1.6e-16) with objective exactly 0.7404886669.
3. Root cause: **letter-namespace collision** — Alice letters (u,a) and Bob letters (y,b) were bare 2-tuples;
   dict-key aliasing mapped Bob letters onto Alice slots, producing a void program whose output 0.6730167462
   never certified anything.
4. Fix: side-tagged letters ('A',·)/('B',·); regression check `namespace-disjointness` added to the verifier.

**Disposition: BP-07 stands. No erratum required.** The RAC-4 NPA (letters of disjoint arities) was never
affected.

## 5. Assessment and next steps

- Level-1 is NOT tight for d=4 (gap 0.0303 above 3/4). The 1+AB result on W shows the hierarchy tightens
  fast (gap ×10 smaller), and the see-saw's structured optimum (uniform win, T-degeneracy) suggests 3/4 is
  the true quantum value.
- RAC-4 1+AB dense is infeasible (N=2145, ~1M constraint rows). Next beat: **symmetry-twirled** 1+AB/level-2
  (translation ℤ₄² × message-shift ℤ₄ × swap × unit-mult; abelian part alone splits Γ into 64 blocks ~33×33,
  making level-2 cheap), plus analytic extraction of the level-1 dual certificate (y₄ stored).

**Verifier**: `verify_bound08.py` — quick mode (runner, ~2.5 min, 12 checks) / full mode (audit, ~8 min).
Quick mode: ALL PASS (2026-10-13, sandbox).
