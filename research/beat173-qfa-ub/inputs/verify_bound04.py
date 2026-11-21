# verify_bound04.py — BP-04 机验(无依赖可复算)
# Th A: 经典(2→1,ℤ_N)RAC+任意共享随机性: S_max=(1+1/N)/2 紧(混合凸性+BP-03)
# Th B: 见证界 ½(1+√(r/8)) 于 r=1 非紧(公式值>紧界), r=8 平凡紧
import itertools, math, random

def classical_max_exact(N):
    # 独立第二实现: 穷举编码 f, 解码取纤化多数(BP-03 步1 证其最优)
    best = 0
    for f in itertools.product(range(N), repeat=N*N):
        fib = {}
        for a in range(N):
            for b in range(N):
                fib.setdefault(f[a*N+b], []).append((a,b))
        tot = 0
        for m, cells in fib.items():
            c1, c2 = {}, {}
            for a, b in cells:
                c1[a] = c1.get(a,0)+1; c2[b] = c2.get(b,0)+1
            tot += max(c1.values()) + max(c2.values())
        best = max(best, tot)
    return best, best/(2*N*N)

bound = lambda N: (1+1/N)/2
b2, s2 = classical_max_exact(2); assert abs(s2-bound(2)) < 1e-12
print('N=2 exact impl#2:', b2, '/8 =', s2, 'OK')
b3, s3 = classical_max_exact(3); assert abs(s3-bound(3)) < 1e-12
print('N=3 exact impl#2:', b3, '/18 =', s3, 'OK')

rng = random.Random(20261013); trials = 0
for N in (2,3,4):
    bnd = bound(N)
    for _ in range(40000):
        K = rng.randint(1,6); S = 0.0
        ws = [rng.random() for _ in range(K)]; sw = sum(ws)
        for k in range(K):
            f = [rng.randrange(N) for _ in range(N*N)]
            g = [[rng.randrange(N), rng.randrange(N)] for _ in range(N)]
            cnt = 0
            for a in range(N):
                for b in range(N):
                    m = f[a*N+b]
                    if g[m][0]==a: cnt += 1
                    if g[m][1]==b: cnt += 1
            S += (ws[k]/sw)*cnt/(2*N*N)
        trials += 1
        assert S <= bnd + 1e-12, (N,S,bnd)
print('ThA mixture MC:', trials, 'mixtures, 0 violations OK')

w1 = 0.5*(1+math.sqrt(1/8)); tight = bound(4); gap = w1-tight
assert gap > 0 and abs(gap-0.0517767) < 1e-6
assert abs(0.5*(1+math.sqrt(8/8))-1.0) < 1e-12
print('ThB: witness(r=1)=%.7f > tight=0.625, looseness=%.7f OK; r=8=1.0 OK' % (w1, gap))
print('ALL_ASSERTIONS_PASS')
