"""Refinements on q6z_g (q6 Z-guard: R 31, CX 6->7 at 32, 34-40, CX 6->0 at 33, M 41 = B init; q1 pairs with q0 at
35-36 instead of q7)."""
import sys
sys.path.insert(0, '.')
from redit import *
from build_q6 import strip_q6, zguard, BASE

S = lambda s: [(int(t), int(d)) for t, d in (x.split('=') for x in s.split(','))]
G = '32=7,33=0,34=7,35=7,36=7,37=7,38=7,39=7,40=7'


def base_g(seq=G, pair='cx q[1],q[0];'):
    c = strip_q6()
    rm(c, 41, 'reset q[6]')
    for t in (35, 36):
        rm(c, t, 'cx q[1],q[7]')
        add(c, t, [pair])
    return zguard(c, 6, S(seq), 31, 41)


def q14ext(c):
    """q14's X-echo on q20 ends at 36 (CX 14->20) and its MX at 37 doubles as A's |+> init (was CX 35, MX 36, RX 37)."""
    rm(c, 35, 'cx q[14],q[20]'); add(c, 36, ['cx q[14],q[20];'])
    g = rm(c, 36, 'measure q[14] -> c[12]')
    rm(c, 37, 'reset q[14]')
    add(c, 37, ['h q[14];', 'measure q[14] -> c[12];', 'h q[14];'])
    return c


V = {
    'q6c_g1': q14ext(base_g()),
    'q6c_g3': base_g('32=7,33=0,34=0,35=7,36=7,37=7,38=7,39=7,40=7'),
    'q6c_g4': base_g(pair='cx q[0],q[1];'),
    'q6c_g1b': q14ext(base_g('32=7,33=0,34=0,35=7,36=7,37=7,38=7,39=7,40=7')),
}
c = load(BASE); V['v36d_q14ext'] = q14ext(c)
for k, c in V.items():
    save(c, BASE, 'c/' + k, dict(source='PRECELL build_q6c ' + k))
print(list(V))
