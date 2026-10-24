"""On precell_e: q19's Z-echo on q20 (CX 20->19 at 18/31, M 32, C role from R 35) ends later at a q20 idle tick,
its M moving to the C role's init tick 35 (r3 starts q19 with R at 35)."""
import sys
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/PRECELL')
from redit import *
B = '/home/jihoon/competitions/quantumn/work/lanes/PRECELL/precell_e'
V = {}
for t in (32, 34):
    c = load(B)
    rm(c, 31, 'cx q[20],q[19]'); add(c, t, ['cx q[20],q[19];'])
    g = rm(c, 32, 'measure q[19] -> c[274]'); rm(c, 35, 'reset q[19]')
    add(c, 35, ['measure q[19] -> c[274];'])
    V[f'e19_{t}'] = c
for k, c in V.items():
    save(c, B, '/home/jihoon/competitions/quantumn/work/lanes/PRECELL/c/' + k, dict(source='PRECELL build_e19 ' + k))
print(list(V))
