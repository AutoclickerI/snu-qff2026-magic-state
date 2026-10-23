import itertools, sys, time
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/DR")
import steane
W3 = steane.W3
print(len(W3), [sorted(s) for s in W3], flush=True)
k = int(sys.argv[1]); BASE = int(sys.argv[2])
res = []
for combo in itertools.combinations(range(len(W3)), k):
    t = time.time()
    try:
        r, c = steane.score(ver=tuple(W3[i] for i in combo), base=BASE)
        res.append((r, combo)); print(combo, f"{r:.4e}", c.n, f"{time.time()-t:.1f}s", flush=True)
    except Exception as e:
        print(combo, "err", e, flush=True)
res.sort(); print("best", res[:3])
