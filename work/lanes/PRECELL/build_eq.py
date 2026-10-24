"""v36e-specific: under r3, q13 (B from its M-init at 37, c296) is a deterministic |0> and free at 33-36, next to q7.
A Z-guard CX 13->7 there is read by the existing M at 37. q6's guard then serves q0 on those ticks.
Variants on top of the full port (G, X, S; P as named):
  q_a: 34-36 q13->7, q6->0; q1's 35-36 pair dropped
  q_b: 34-36 q13->7; 34 q6->0; q1 pair with q0 at 35-36 (P), q6 idle at 35-36
  q_c: 34-36 q13->7 ... no: 34 q13->7, q6->0; 35-36 q1 pair with q7 (original), q6->0
  q_d: 34 q13->7, q6->0; rest as e_all (35-36 q6->7, q1 pair with q0)"""
import sys
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/PRECELL')
from redit import *
from build_e import BASE, strip_q6, X, S

PATH = '/home/jihoon/competitions/quantumn/work/lanes/PRECELL/c/'


def make(q6seq, q13ticks, pair):
    c = load(BASE)
    if pair == 'drop':
        for t in (35, 36):
            rm(c, t, 'cx q[1],q[7]')
    elif pair == 'q0':
        for t in (35, 36):
            rm(c, t, 'cx q[1],q[7]'); add(c, t, ['cx q[1],q[0];'])
    strip_q6(c)
    add(c, 31, ['reset q[6];'])
    for t, d in q6seq.items():
        add(c, t, [f'cx q[6],q[{d}];'])
    for t in q13ticks:
        add(c, t, ['cx q[13],q[7];'])
    X(c); S(c)
    return c


base7 = {32: 7, 33: 0, 37: 7, 38: 7, 39: 7, 40: 7, 41: 7}
V = {
    'q_a': make({**base7, 34: 0, 35: 0, 36: 0}, (34, 35, 36), 'drop'),
    'q_b': make({**base7, 34: 0}, (34, 35, 36), 'q0'),
    'q_c': make({**base7, 34: 0, 35: 0, 36: 0}, (34,), 'q7'),
    'q_d': make({**base7, 34: 0, 35: 7, 36: 7}, (34,), 'q0'),
}
for k, c in V.items():
    save(c, BASE, PATH + k, dict(source='PRECELL build_eq ' + k))
print(list(V))

# leave-one-outs of q_a
from build_e import X as _X, S as _S


def make2(q6seq, q13ticks, pair, x=True, s=True, g=True):
    c = load(BASE)
    if pair == 'drop':
        for t in (35, 36):
            rm(c, t, 'cx q[1],q[7]')
    if g:
        strip_q6(c)
        add(c, 31, ['reset q[6];'])
        for t, d in q6seq.items():
            add(c, t, [f'cx q[6],q[{d}];'])
    for t in q13ticks:
        add(c, t, ['cx q[13],q[7];'])
    if x:
        _X(c)
    if s:
        _S(c)
    return c


qa6 = {**base7, 34: 0, 35: 0, 36: 0}
L = {
    'qa_noQ13': make2(qa6, (), 'drop'),
    'qa_noS': make2(qa6, (34, 35, 36), 'drop', s=False),
    'qa_noXS': make2(qa6, (34, 35, 36), 'drop', x=False, s=False),
    'qa_noG': make2(None, (34, 35, 36), 'drop', g=False),
}
for k, c in L.items():
    save(c, BASE, PATH + k, dict(source='PRECELL build_eq ' + k))
print(list(L))
