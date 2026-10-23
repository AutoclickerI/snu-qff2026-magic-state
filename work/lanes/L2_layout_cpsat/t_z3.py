import sys, itertools
sys.path.insert(0, '.')
import l2model as L
m = L.variant('v6+z42')
names = [B + n for B in 'XZ' for n in ['s0', 's1', 's2', 'L', 'c0', 'c1', 'c2']]
def ok(sel):
    g = L.Gen(m, 9); g.install_propagation(only=set(sel)); return len(g.solutions(1, 10, 0))
print('allX', ok([n for n in names if n[0] == 'X']), 'allZ', ok([n for n in names if n[0] == 'Z']))
for a, b in itertools.combinations(names, 2):
    if not ok([a, b]): print('conflict', a, b, flush=True)
