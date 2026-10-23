import sys
sys.path.insert(0, '.')
import l2model as L
m = L.variant('v6+z42')
print(m.zext, m.zmem, m.extras)
g = L.Gen(m, 9); print('no prop', len(g.solutions(1, 10, 0)))
for B in 'XZ':
    for nm in ['s0', 's1', 's2', 'L', 'c0', 'c1', 'c2']:
        g = L.Gen(m, 9); g.install_propagation(only={B + nm})
        print(B + nm, len(g.solutions(1, 10, 0)))
