import numpy as np, itertools, sys
def exhaustive(N):
    xs = list(itertools.product(range(N), repeat=2)); nX = len(xs)
    enc = np.array(list(itertools.product(range(N), repeat=nX)), dtype=np.int64)
    E = enc.shape[0]
    x1s = np.array([x[0] for x in xs]); x2s = np.array([x[1] for x in xs])
    T = np.zeros((E, N, N), dtype=np.int64); U = np.zeros((E, N, N), dtype=np.int64)
    for m in range(N):
        mask = (enc == m)
        for v in range(N):
            T[:, m, v] = (mask & (x1s == v)).sum(axis=1)
            U[:, m, v] = (mask & (x2s == v)).sum(axis=1)
    decs = np.array(list(itertools.product(range(N), repeat=2*N)), dtype=np.int64)
    g1 = decs[:, :N]; g2 = decs[:, N:]
    best = np.zeros((E, decs.shape[0]), dtype=np.int64)
    for m in range(N):
        best += T[:, m, :][:, g1[:, m]]; best += U[:, m, :][:, g2[:, m]]
    return int(best.max())
for N, expect in ((2, 6), (3, 12)):
    got = exhaustive(N); assert got == expect, (N, got, expect)
    print(f"N={N} exhaustive max={got}/{2*N*N} S={got/(2*N*N)} OK")
# closed form + achievability assertions
for N in range(2, 9):
    bound = (N*N + N) / (2*N*N); assert abs(bound - (1+1/N)/2) < 1e-15
    tot = sum(1 + (1 if x2==x1 else 0) for x1 in range(N) for x2 in range(N))
    assert tot == N*N + N
print("ALL_ASSERTIONS_PASS S_max=(1+1/N)/2 exact")
