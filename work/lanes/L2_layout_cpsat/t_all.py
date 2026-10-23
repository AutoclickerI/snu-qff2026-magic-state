import sys, time
sys.path.insert(0, '.')
import l2model as L
for a in L.T1:
    for b in L.T2:
        name = f"{a}+{b}"
        try:
            m = L.variant(name)
        except AssertionError as e:
            print(name, 'BAD', e); continue
        for lmax in (8, 9, 10):
            t = time.time()
            ok, n = L.starts(m, lmax, 3, 1, tries=2, per=10, seconds=10)
            print(name, lmax, 'valid', len(ok), '/', n, 'best', f"{ok[0][0]:.4e}" if ok else None, f"{time.time()-t:.0f}s", flush=True)
