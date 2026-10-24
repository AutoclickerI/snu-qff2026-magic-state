"""On z_a: q6's guard readout M at 41 dropped; the guard runs through 41 (q6 enters B at 42 as the never-fired |0>
control; a guard X fault stays on q6, is copied to C by B->C at 44 and flagged by C's literal-zero detectors)."""
import sys
sys.path.insert(0, '.')
from redit import *
from build_q6c import BASE

V = {}
for d in (7, 0):
    c = load('c/z_a')
    rm(c, 41, 'measure q[6] -> c[295]'); rmdet(c, 295)
    add(c, 41, [f'cx q[6],q[{d}];'])
    V[f'nom_{d}'] = c
c = load('c/z_a')
rm(c, 41, 'measure q[6] -> c[295]'); rmdet(c, 295)
V['nom_none'] = c
for k, c in V.items():
    save(c, BASE, 'c/' + k, dict(source='PRECELL build_nom ' + k))
print(list(V))

# tick reassignments on nom_7
c = load('c/nom_7'); rm(c, 40, 'cx q[6],q[7]'); add(c, 40, ['cx q[6],q[0];']); V2 = {'nom_7b': c}
c = load('c/nom_7'); rm(c, 39, 'cx q[6],q[7]'); add(c, 39, ['cx q[6],q[0];']); V2['nom_7c'] = c
for k, c in V2.items():
    save(c, BASE, 'c/' + k, dict(source='PRECELL build_nom ' + k))
print(list(V2))
