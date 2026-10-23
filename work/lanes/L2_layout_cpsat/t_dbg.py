import sys, json
sys.path.insert(0, '.')
import l2model as L
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/me_layout')
from verify import load_assign
m = L.variant('A1+e42')
g = L.Gen(m, 9); g.install_propagation()
sols = g.solutions(5, 10, 1)
for a, o in sols[:3]:
    print('feasible', m.feasible(a, o), o)
    try:
        print(m.proxy(a, o))
    except Exception as e:
        print('ERR', type(e).__name__, str(e)[:300])
# known good A1 schedule: check it satisfies my CP-SAT constraints
r = json.load(open('/home/jihoon/competitions/quantumn/work/lanes/me_layout/res_A1_9b_1792752451.json'))[0]
a0 = load_assign(r[1]); o0 = r[2]
print('known', r[0], m.cost(a0, o0))
g2 = L.Gen(m, 9); g2.install_propagation()
for k, v in g2.v.items(): g2.c.add(v == a0[k])
for t in range(3): g2.c.add(g2.o[t] == o0[t])
print('known in CP model:', len(g2.solutions(1, 10, 0)))
print(sorted(a0.items(), key=lambda kv: kv[1]))
