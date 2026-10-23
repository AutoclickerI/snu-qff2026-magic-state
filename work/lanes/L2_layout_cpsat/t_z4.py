import sys
sys.path.insert(0, '.')
import l2model as L
for name in ['v6+z42', 'A1z+e42']:
    m = L.variant(name)
    for lmax in (10, 12):
        g = L.Gen(m, lmax); g.install_propagation()
        s = g.solutions(1, 20, 0)
        print(name, lmax, len(s), flush=True)
        if s:
            a, o = s[0]; print(m.feasible(a, o)); print(m.cost(a, o))
