# BEAT174 QFA canonical-quotient numeric bound

Fresh commands from this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B inputs/beat172/verify_bound07.py
PYTHONDONTWRITEBYTECODE=1 python3 -B portable_verify.py
```

The verifier independently reconstructs the 28,438-to-15,070 variable quotient,
all 36 SDP blocks, 745 completeness equalities, classical 5/8 and quantum 3/4
controls, the transferred dual certificate, and a fresh HiGHS LP. The floating-
point upper bound is 0.752718187871213. This is not an exact 3/4 theorem, a
canonical-full convergence claim, a model-equivalence or novelty proof, a real-
QPU experiment, or seat approval.
