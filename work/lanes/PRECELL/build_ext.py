"""Echo-end extensions whose measurement doubles as the next role's init (one fewer reset, one more covered tick):
q14 (X-echo on q20: CX 35->36, MX 36->37 = A's |+> init), q19 (Z-echo on q20: CX 31->32, M 32->33 = C's |0> init),
q13 (Z-echo on q7: CX 31->32, M 32->33 = B's |0> init). q2ext (X-echo on q8: CX 26->27, MX 27->28 = blue ancilla's
|+>) is valid but hits the xtim slow path (216 s per 1e6), so it is not used.
Stacked on the q6 Z-guard variants of build_q6c."""
import sys
sys.path.insert(0, '.')
from redit import *
from build_q6c import base_g, q14ext, BASE


def q19ext(c):
    rm(c, 31, 'cx q[20],q[19]'); add(c, 32, ['cx q[20],q[19];'])
    rm(c, 32, 'measure q[19] -> c[274]'); rm(c, 33, 'reset q[19]')
    add(c, 33, ['measure q[19] -> c[274];'])
    return c


def q13ext(c):
    rm(c, 31, 'cx q[7],q[13]'); add(c, 32, ['cx q[7],q[13];'])
    rm(c, 32, 'measure q[13] -> c[280]'); rm(c, 33, 'reset q[13]')
    add(c, 33, ['measure q[13] -> c[280];'])
    return c


def q2ext(c):
    rm(c, 26, 'cx q[2],q[8]'); add(c, 27, ['cx q[2],q[8];'])
    rm(c, 27, 'measure q[2] -> c[10]'); rm(c, 28, 'reset q[2]')
    add(c, 28, ['h q[2];', 'measure q[2] -> c[10];', 'h q[2];'])
    return c


G33 = '33=0,34=7,35=7,36=7,37=7,38=7,39=7,40=7'


def g_from33():
    c = base_g(G33)  # R at 31 still; move to 32
    rm(c, 31, 'reset q[6]'); add(c, 32, ['reset q[6];'])
    return c


V = {
    'v36d_q19ext': q19ext(load(BASE)),
    'v36d_q13ext': q13ext(load(BASE)),
    'x_g1_19': q19ext(q14ext(base_g())),
    'x_g1_13_19': q13ext(q19ext(q14ext(g_from33()))),
    'x_g1_13': q13ext(q14ext(g_from33())),
}
for k, c in V.items():
    save(c, BASE, 'c/' + k, dict(source='PRECELL build_ext ' + k))
print(list(V))
