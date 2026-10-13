# BOUND-PROOF-07 — d=4 Entanglement-Assisted Random Access Code (4² → 1 ququart)

**Date**: 2026-10-13 · **Line**: qfa · **Beat**: 128 · **Engine**: bound-proof (BP-07)
**Status**: classical EXACT · quantum LB certified 3/4 · quantum UB = **conjecture** (numeric plateau, 迭诫七 — see-saw 平台 ≠ 上界, NOT proved)

## Problem

Alice holds x = (X₁,X₂) ∈ ℤ₄² (16 inputs). She sends one ququart message m ∈ ℤ₄.
Bob receives y ∈ {0,1} and the message, and must guess X_y. Success probability

S = (1/32) Σ_{x,y,m} tr[ σ_{m|x} M_{x_y}^{y,m} ],

where {σ_{m|x}} is the assemblage prepared by Alice on Bob's half of a shared state,
and {M_v^{y,m}}_{v∈ℤ₄} is Bob's POVM for question y given message m.

## Results

| Bound | Value | Status |
|---|---|---|
| Classical | **5/8 = 0.625** | EXACT (proved, exhaustive) |
| Quantum LB | **3/4 = 0.75** | certified construction (this work) |
| Quantum UB | **3/4 (conjectured)** | numeric plateau 24/24 restarts + LBFGS, sub-1e-12; **NOT proved** (迭诫七) |
| Two-CHSH bit-plane product | ((2+√2)/4)² = (3+2√2)/8 ≈ 0.728553 | EXACT, strictly < 3/4 |
| Affine-subspace ceiling (W-game) | classical 5/8 EXACT; quantum ≈ 0.74048866 | numeric, < 3/4 |

### 1. Classical value = 5/8 (EXACT)

Lower bound (certificate): Alice sends m = X₁. Bob y=0 reads v=m (always correct);
y=1 guesses 0 (correct 4/16 of inputs). Win-sum = 16+4 = 20 → S ≥ 20/32 = 5/8.

Upper bound (exhaustive, exact): for any deterministic Alice colouring of the 16 cells
into 4 message classes, Bob's optimal decoding picks per class c a row-representative
v₁(c) and column-representative v₂(c). Given all 4⁴×4⁴ representative pairs, the optimal
colouring assigns each cell independently to its best class — per-cell independent max.
Enumerating all representative pairs with per-cell optimal assignment is globally exact:

  max win-sum = 20  →  S ≤ 5/8.   ∎  (verify_bound07.py, checks 1–3)

### 2. Fourier (T-operator) decomposition — definitionally exact

With Q_y^{m,k} = Σ_v ω^{kv} M_v^{y,m} (ω = i) and T_k = Σ_{x,y,m} ω^{−k·x_y} tr[σ_{m|x} Q_y^{m,k}]:

  S = 1/4 + (2 Re T₁ + T₂)/128,   T₀ = 32 (normalization).

O-operator collapse (proved, check 4): for every POVM and every X,
  R_X := 2 Re_Hermitian(ω^{−X} Q¹) + ω^{−2X} Q² = 4 M_X − I
(coefficients r_d = 2cos(πd/2)+(−1)^d = (3,−1,−1,−1)). Hence the Fourier form is an
identity, not a bound — all content lives in joint constraints among (T₁, T₂, T₃).

### 3. Quantum lower bound 3/4 (certified)

Numerical optimization (torch, batched Cayley-parametrized unitaries: Alice 16 projective
POVMs, Bob 8 projective POVMs, Schmidt-vector DOF; Adam×4500 + LBFGS strong-Wolfe polish):

- **24/24 restarts converge to S = 0.750000000000000** (machine precision after polish).
- Optimum uses the **maximally entangled state** (Schmidt coefficients uniform 1/2).
- All measurements **rank-1 projective**.
- **Uniform winning**: P(win|x,y) = 3/4 for **every** (x,y) (dev 5.6e-16).
- Fourier spectrum at the optimum: **T₁ = T₂ = T₃ = 64/3** (T₀ = 32), i.e.
  S = 1/4 + (2·64/3 + 64/3)/128 = 3/4 exactly.

The full strategy (24 unitaries + Schmidt vector) is embedded compressed in
verify_bound07.py / result07.json: independent numpy re-evaluation gives
S = 0.750000000000000 (|Δ| < 1e-15). → **S_quantum ≥ 3/4, certified.**

### 4. Genuine ququart advantage

Splitting the ququart as two qubits and running two independent d=2 EA-RACs
(bit-planes, value (2+√2)/4 each) yields ((2+√2)/4)² = (3+2√2)/8 ≈ 0.728553 < 3/4.
The 3/4 optimum is therefore an intrinsically 4-dimensional protocol.

### 5. Affine reduction and its ceiling

Strategies whose message is an affine function m = ã + X₁ reduce to the ℤ₄ Bell game
W (Alice u ∈ ℤ₄, Bob ŷ ∈ {0,1}, outputs ã,b̃ ∈ ℤ₄, win ã + b̃ ≡ u·ŷ mod 4).

- W classical = 5/8 EXACT: win-count = |U₀|+|U₁| ≤ 5 since |U₀ ∩ U₁| ≤ 1 (check 9).
- W quantum ≈ 0.74048866 (see-saw; constant unidentified) < 3/4.

→ Non-affine strategies strictly beat affine ones; the 3/4 optimum is non-affine.

### 6. Upper-bound status (honest, 迭诫七)

- Per-mode trivial bound |T_k| ≤ 32 (‖Q^k‖∞ ≤ 1 by Naimark dilation) gives only S ≤ 1.
- R_X = 4M_X − I has spectrum {3,−1,−1,−1}; per-term bounds do not joint-constrain.
- Tsirelson's vector theorem does not extend to ℤ₄ (non-XOR) games.
- **Conjecture**: S_quantum = 3/4. Evidence: 24/24 independent restarts + LBFGS to
  sub-1e-12; uniform-win symmetry; triple-degenerate Fourier modes 64/3.
  This is a numeric plateau, NOT a proved upper bound. (DEBT-BOUND06-D4-01 stays open.)

## Verification

`python3 verify_bound07.py` — numpy-only, ~0.3 s, 10 checks:

1. classical-LB-certificate (win-sum 20)
2. classical-UB-exact (representative enumeration, globally exact)
3. classical-exact-5/8
4. O-operator-identity (random-POVM symbolic check)
5. quantum-LB-3/4 (embedded certificate strategy, |S−3/4| < 1e-12)
6. uniform-win (per-(x,y) flatness)
7. T-structure (T₀=32, T₁=T₂=T₃=64/3)
8. ququart-advantage (exact algebra)
9. affine-W-classical (brute-force exact)
10. (implicit aggregate) — exit 0 iff all pass

## Solver lineage (audit)

quadratic-penalty (ill-conditioned) → isometric packing with √2 off-diagonal scaling
(factor-2 gradient fix) → softplus eigen-penalty (log-sum-exp soft-max bug found: rewards
infeasibility; fixed to ρμ·log1p(exp(λ_max/μ))) → ellipsoid (rank-1 cut degradation) →
**torch batched Adam + LBFGS on GPU** (winner). Assemblage transpose convention:
σ_{m|x} = (A_x^m)ᵀ/4 for |Φ₄⟩; a sign/place error here cost one debugging round
(ratio 2.615 anomaly), resolved by the no-pre-conjugation fix.
