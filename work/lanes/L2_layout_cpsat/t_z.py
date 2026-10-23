import sys, time
sys.path.insert(0, '.')
import l2model as L
for name in sys.argv[1:]:
    m = L.variant(name)
    for lmax in (9,):
        t = time.time()
        ok, n = L.starts(m, lmax, 3, 1, tries=2, per=10, seconds=10)
        bad = 0
        print(name, lmax, 'valid', len(ok), '/', n, 'best', f"{ok[0][0]:.4e}" if ok else None, f"{time.time()-t:.0f}s", flush=True)
        if n and not ok:
            g = L.Gen(m, lmax); g.install_propagation(); a, o = g.solutions(1, 10, 0)[0]
            print(' feasible', m.feasible(a, o))
            try: m.proxy(a, o)
            except Exception as e: print(' ERR', str(e)[:200])
