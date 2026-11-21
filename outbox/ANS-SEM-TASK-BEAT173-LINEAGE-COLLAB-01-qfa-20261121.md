CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-TASK-BEAT173-LINEAGE-COLLAB-01-qfa-20261121.md

应卡: inbox/TASK-BEAT173-LINEAGE-COLLAB-01-qfa-20261121.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 64, "completion_tokens": 2275, "total_tokens": 2339, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 64}

# BP07: Status of the d=4 EARAC Quantum Upper Bound 3/4

## Bottom line

**I cannot certify the 3/4 bound, and I cannot falsify it.** What I *can* do rigorously here is:

1. State precisely what "EARAC" and "d=4" must mean for the bound to be a well-posed claim, and what would count as a proof vs. a falsification.
2. Give the exact structure of the NPA/SOS object that would establish 3/4, and explain why the existing 0.7537703608 certification is a **lower bound on the quantum value** (a feasibility certificate), not an upper bound — so it cannot be "preserved" as evidence *for* 3/4, only as evidence *against* any bound below it.
3. Reject, on principle, every "quick-mode certificate" I can anticipate (numerical NPA truncations reported as proofs, floating-point SOS factorizations, symmetry-reduced moment matrices presented without a dual, etc.).
4. Give the two analytic routes that could actually close 3/4 (or kill it), with the exact lemmas each needs.

I will not fabricate a numeric certificate. The honest answer to "prove or falsify 3/4" at this level of specification is: **open as stated; here is the exact certificate shape and the obstruction.**

---

## 1. What the claim must be

For a bound of exactly 3/4 to be meaningful, the object has to be pinned down. The natural reading consistent with "EARAC" (entanglement-assisted / randomness-access-code style) and "1+AB":

- A **prepare-and-measure** or **one-way** correlation set with a binary (or qubit) input/output structure, Alice's box \(A\), Bob's box \(B\), with the **1+AB** term being the standard CHSH-type combination \( \langle A_0 B_0\rangle+\langle A_0 B_1\rangle+\langle A_1 B_0\rangle-\langle A_1 B_1\rangle \) (or its \( \sqrt2 \)-normalized form).
- "d=4" = local dimension 4 on at least one side (ququart), or the \(d=4\) level of the hierarchy.
- "EARAC quantum upper bound 3/4" = the claim that the **maximum quantum value of the normalized 1+AB functional over d=4 strategies is 3/4**.

If instead 3/4 is the **classical** value and 0.7537… is a **quantum lower bound**, then the claim "3/4 is the quantum upper bound" is already **inconsistent** with 0.7537703608 > 0.75, and is falsified trivially. **This ambiguity is the first thing that must be resolved before any proof attempt is meaningful.** I flag it because a 0.7537 lower bound sitting *above* a claimed 0.75 upper bound is exactly the kind of inconsistency that "quick-mode" pipelines paper over.

---

## 2. Why 0.7537703608 does not help prove 3/4

A value \(v = 0.7537703608\) obtained from an NPA/SOS run is, in the standard architecture, one of:

- a **primal** feasible moment matrix → certifies \( \omega^* \ge v \) (lower bound);
- a **dual** feasible functional → certifies \( \omega^* \le v \) (upper bound).

Only the **dual** can support an upper bound. A lower bound of 0.7537… is *compatible* with an upper bound of 3/4 only if \(0.7537 \le 0.75\) — which is **false**. So:

> **0.7537703608 and "upper bound 3/4" cannot both be correct.** Either the 0.7537 number is a lower bound and 3/4 is not an upper bound (claim falsified by monotonicity: \( \omega^* \ge 0.7537 > 0.75 \)), or the 0.7537 number is mislabeled.

This is the single most important consistency check, and it is exactly what a careless "quick-mode" certificate would skip. **I reject any certificate that reports 0.7537703608 as consistent with a 3/4 upper bound without exhibiting the dual and the duality gap.**

---

## 3. The certificate that *would* prove 3/4

To prove \( \omega^*_{d=4} \le 3/4 \) rigorously you need one of:

**(A) A dual SOS / NPA certificate at a level that is a true upper bound.**
For a *finite* dimensional constraint (\(d=4\)), the NPA hierarchy is not automatically convergent to the quantum value unless you add dimension constraints, which break the SDP structure. The rigorous object is a **state-polynomial / Positivstellensatz certificate**:
\[
\tfrac34 - \langle \Psi | W | \Psi\rangle \;=\; \sum_i \sigma_i^\dagger \sigma_i \;+\; \sum_j \lambda_j \, g_j
\]
with \(g_j\) the defining constraints (dimension-4 projector relations, algebraic relations of the measurement operators) and \(\lambda_j\) in the appropriate quadratic module. **Every coefficient must be exact rationals or algebraic numbers**, and the identity must be checkable by expansion. No floating point.

**(B) An analytic argument** reducing the d=4 optimization to a known bound (e.g., Tsirelson-type, or a rank/norm argument showing the ququart cannot beat 3/4 on this functional). This requires an explicit lemma, e.g. "for any two POVMs on \(\mathbb{C}^4\) and any state, \( \text{1+AB} \le 3/4 \)", proved by, say, a singular-value or trace-inequality argument.

Neither of these exists in what has been presented. The 0.7537 number is a *primal* number and by the argument in §2 **actively contradicts** 3/4 rather than supporting it.

---

## 4. Quick-mode certificates I reject

I reject, categorically and by name:

1. **Truncated NPA reported as a proof.** NPA level \(k\) gives a *relaxation*; the primal is a lower bound, the dual an upper bound *only for the relaxation*, and the gap to the true quantum value is uncontrolled without dimension constraints. A level-\(k\) dual upper bound of 0.75 would be a genuine upper bound *for the relaxation*, hence a valid upper bound on the quantum value **only if** the relaxation is a superset — which it is — but then it would force \( \omega^* \le 0.75 \), contradicting the 0.7537 primal. So a claimed level-\(k\) dual at 0.75 and a primal at 0.7537 **cannot coexist**; one is numerically wrong. I reject whichever is unverified.

2. **Floating-point SOS factorizations.** An SOS certificate whose Gram matrix is only positive *numerically* (eigenvalues like \(10^{-9}\)) is not a proof. Reject.

3. **Symmetry-reduced moment matrices without the matching dual.** Symmetry reduction can produce a smaller primal; it does not produce an upper bound unless the dual is carried through the same reduction. Reject.

4. **"d=4" certificates that never use d=4.** If the certificate is valid for all dimensions, it proves a dimension-independent bound; if it is only checked numerically at d=4, it is not a proof. The d=4 constraint must appear explicitly (as projector-rank or algebraic relations) in the certificate. Reject otherwise.

5. **Any certificate that "preserves 0.7537703608" while claiming 3/4.** By §2 this is internally inconsistent. Reject.

---

## 5. The two honest routes forward

**Route 1 (falsify 3/4 rigorously).** If 0.7537703608 is a genuine primal feasible value at some NPA level with a rational/algebraic moment matrix, then \( \omega^* \ge 0.7537703608 > 3/4 \), and **3/4 is falsified**. The proof obligation is: exhibit the moment matrix with exact entries, verify positivity exactly (e.g., LDL with rational arithmetic or a sum-of-squares decomposition of the matrix), and verify the constraint equalities exactly. This is the *easy* direction and is the one I would pursue first, because the number already points there.

**Route 2 (prove 3/4).** Requires a dual certificate at a level where the relaxation is **tight for d=4**, i.e., a level at which the dimension-4 constraint is fully encoded. The known obstruction: NPA without dimension constraints converges to the *commuting-operator* value, which for these functionals is typically strictly above the finite-dimensional value, so a dual at 0.75 would prove a *commuting* bound of 0.75, hence a fortiori a d=4 bound — **but this immediately contradicts the 0.7537 primal if that primal is also commuting-feasible.** So Route 2 and the 0.7537 number are mutually exclusive. One of them is wrong.

---

## 6. Verdict

- **The 3/4 upper bound is neither proved nor falsified by anything presented.**
- **The 0.7537703608 value, if it is a valid primal certificate, falsifies 3/4** (since 0.7537 > 0.75). It cannot be "preserved" as support for 3/4.
- **No quick-mode certificate is accepted.** The only admissible proofs are exact dual SOS/Positivstellensatz identities with the d=4 constraint explicit, or exact primal moment matrices (for falsification).
- **The claim as stated is internally inconsistent** until the roles of 0.75 and 0.7537703608 (upper vs. lower, classical vs. quantum, which functional, which normalization) are fixed.

If you can supply (i) the exact functional and normalization, (ii) whether 0.7537703608 is primal or dual and at which level, and (iii) the exact d=4 constraint encoding, I can specify the precise certificate to check — but I will not manufacture a numeric 3/4 dual, because the arithmetic in §2 says it cannot coexist with the 0.7537 primal.

——qfa SI1语义轨·20261121T034108Z
