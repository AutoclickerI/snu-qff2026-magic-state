"""q6 (B from tick 41) re-tasked: its X-echo + CX pairs on q0 (32-40) become one Z-guard (|0> control, CX 6->d every
tick, M at 41 = B's measured init) shared by q0 and q7. Variants differ in the per-tick target and start."""
import sys
sys.path.insert(0, '.')
from redit import *
from build_q6 import strip_q6, zguard, BASE


def variant(seq, rtick=32, drop_pair17=False, pair10=False):
    c = strip_q6()
    rm(c, 41, 'reset q[6]')
    if drop_pair17:
        for t in (35, 36):
            rm(c, t, 'cx q[1],q[7]')
        if pair10:
            for t in (35, 36):
                add(c, t, ['cx q[1],q[0];'])
    return zguard(c, 6, seq, rtick, 41)


S = lambda s: [(int(t), int(d)) for t, d in (x.split('=') for x in s.split(','))]
V = {
    'q6z_a': variant(S('33=0,34=7,35=0,36=0,37=7,38=7,39=7,40=7')),
    'q6z_b': variant(S('32=7,33=0,34=7,35=0,36=0,37=7,38=7,39=7,40=7'), rtick=31),
    'q6z_c': variant(S('33=0,34=7,35=0,36=0,37=7,38=7,39=7,40=0')),
    'q6z_d': variant(S('33=0,34=7,35=0,36=0,37=7,38=7,39=0,40=0')),
    'q6z_e': variant(S('33=0,34=7,35=7,36=7,37=7,38=7,39=7,40=7'), drop_pair17=True),
    'q6z_f': variant(S('33=0,34=7,35=7,36=7,37=7,38=7,39=7,40=7'), drop_pair17=True, pair10=True),
    'q6z_g': variant(S('32=7,33=0,34=7,35=7,36=7,37=7,38=7,39=7,40=7'), rtick=31, drop_pair17=True, pair10=True),
    'q6z_h': variant(S('32=7,33=0,34=0,35=0,36=0,37=7,38=7,39=7,40=7'), rtick=31),
    'q6z_i': variant(S('33=0,34=7,35=0,36=0,37=0,38=7,39=7,40=7')),
    'q6z_j': variant(S('32=7,33=0,34=7,35=0,36=0,37=7,38=0,39=7,40=7'), rtick=31),
}
for k, c in V.items():
    save(c, BASE, 'c/' + k, dict(source='PRECELL build_q6b ' + k))
print(list(V))
