"""Real variants: free q9 (A from tick 38) by hopping D6 8->14->15 instead of 8->9->15; the q14 X-echo on q20
ends at tick 30 (MX 31, R 32) instead of 35; q9 then runs an X-guard (|+>, CX d->9, MX at 38 = A's RX init)."""
import sys
sys.path.insert(0, '.')
from redit import *

BASE = '../MAIN/v36d'


def reroute(echo_end=30, z19=29):
    c = load(BASE)
    # q19's Z-echo on q20 (CX 20->19 at 18 and 31, M 32) ends at z19 (M at z19+2) so that it nests inside the X-echo
    rm(c, 31, 'cx q[20],q[19]')
    add(c, z19, ['cx q[20],q[19];'])
    g = rm(c, 32, 'measure q[19] -> c[274]')
    add(c, 31, g)
    # q14 echo on q20: end at echo_end instead of 35, MX at echo_end+1 (record c12), R at 32
    rm(c, 35, 'cx q[14],q[20]')
    g = rm(c, 36, 'measure q[14] -> c[12]')
    add(c, echo_end, ['cx q[14],q[20];'])
    add(c, echo_end + 1, ['h q[14];', 'measure q[14] -> c[12];'])
    add(c, 32, ['reset q[14];'])
    # D6 hops 8->14 (33,34), 14->15 (35,36)
    rm(c, 32, 'reset q[9]')
    rm(c, 33, 'cx q[8],q[9]'); add(c, 33, ['cx q[8],q[14];'])
    rm(c, 34, 'cx q[9],q[8]'); add(c, 34, ['cx q[14],q[8];'])
    rm(c, 35, 'cx q[9],q[15]'); add(c, 35, ['cx q[14],q[15];'])
    rm(c, 36, 'cx q[15],q[9]'); add(c, 36, ['cx q[15],q[14];'])
    rm(c, 37, 'measure q[9] -> c[56]')
    rmdet(c, 56)
    return c


def xguard(c, h, seq, rtick, mtick, bit=None, replace_init=None):
    add(c, rtick, [f'reset q[{h}];', f'h q[{h}];'])
    for t, d in seq:
        add(c, t, [f'cx q[{d}],q[{h}];'])
    if replace_init is not None:
        rm(c, mtick, replace_init)
    b = newbit(c) if bit is None else bit
    add(c, mtick, [f'h q[{h}];', f'measure q[{h}] -> c[{b}];', f'h q[{h}];'])
    adddet(c, [b])
    return c


V = {}
V['q9_none'] = reroute()
seqs = {
    'q9_g3': [(34, 3), (35, 3), (36, 3), (37, 3)],
    'q9_g3x10': [(34, 3), (35, 10), (36, 10), (37, 10)],
    'q9_g3alt': [(34, 3), (35, 10), (36, 3), (37, 10)],
    'q9_g3b': [(34, 3), (35, 3), (36, 10), (37, 10)],
}
for k, s in seqs.items():
    c = reroute()
    V[k] = xguard(c, 9, s, 33, 38, bit=56, replace_init='reset q[9]')
c = reroute(29, 28)
V['q9_g3_e29'] = xguard(c, 9, seqs['q9_g3'], 33, 38, bit=56, replace_init='reset q[9]')
for k, c in V.items():
    save(c, BASE, 'c/' + k, dict(source='PRECELL build_q9 ' + k))
print(list(V))
