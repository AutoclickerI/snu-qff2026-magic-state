import sys, time
sys.path.insert(0, '.')
import l2model as L
name, lmax = sys.argv[1], int(sys.argv[2])
m = L.variant(name)
t = time.time()
ok, n = L.starts(m, lmax, 5, 1, tries=3, per=30, seconds=15)
print(name, lmax, 'tried', n, 'valid', len(ok), 'best', [round(r[0]*1e4, 5) for r in ok[:5]], f'{time.time()-t:.0f}s', flush=True)
