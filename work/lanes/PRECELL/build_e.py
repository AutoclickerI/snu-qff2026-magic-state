"""Port of precell_nom7's four edits onto v36e (= v36d with BFLAG's 56-CX r3 B/C resource), plus leave-one-outs.
q6's late window is unchanged under r3 (MX 40 -> R 41 -> CX 12->6 at 42 as the B target), so the unread guard ports.
Edits: G = q6 Z-guard (R 31; CX 6->7 at 32, 34-41 (35-36 only with P); CX 6->0 at 33 (and 35-36 without P); no readout;
       q6 enters B at 42), Gm = same with M at 41 (readout, guard on q7 to 40);
       P = q1's CX pair at 35-36 moved from q7 to q0; X = q14 X-echo end 35->36, MX at 37 = A init; S = q21 echo end 34->35."""
import sys
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/PRECELL')
from redit import *

BASE = '/home/jihoon/competitions/quantumn/work/lanes/MAIN/v36e'


def strip_q6(c):
    rm(c, 32, 'reset q[6]'); rm(c, 33, 'cx q[6],q[0]')
    for t in (35, 36, 37, 38):
        rm(c, t, 'cx q[0],q[6]')
    rm(c, 39, 'cx q[6],q[0]'); rm(c, 40, 'measure q[6] -> c[273]'); rmdet(c, 273); rm(c, 41, 'reset q[6]')


def G(c, pair_moved=True, readout=False):
    strip_q6(c)
    add(c, 31, ['reset q[6];'])
    seq = {32: 7, 33: 0, 34: 7, 35: 7 if pair_moved else 0, 36: 7 if pair_moved else 0, 37: 7, 38: 7, 39: 7, 40: 7}
    if not readout:
        seq[41] = 7
    for t, d in seq.items():
        add(c, t, [f'cx q[6],q[{d}];'])
    if readout:
        add(c, 41, ['measure q[6] -> c[273];']); adddet(c, [273])
    return c


def P(c):
    for t in (35, 36):
        rm(c, t, 'cx q[1],q[7]'); add(c, t, ['cx q[1],q[0];'])
    return c


def X(c):
    rm(c, 35, 'cx q[14],q[20]'); add(c, 36, ['cx q[14],q[20];'])
    rm(c, 36, 'measure q[14] -> c[12]'); rm(c, 37, 'reset q[14]')
    add(c, 37, ['h q[14];', 'measure q[14] -> c[12];', 'h q[14];'])
    return c


def S(c):
    rm(c, 34, 'cx q[20],q[21]'); add(c, 35, ['cx q[20],q[21];'])
    return c


def build(g=True, p=True, x=True, s=True, readout=False):
    c = load(BASE)
    if p:
        P(c)
    if g:
        G(c, pair_moved=p, readout=readout)
    if x:
        X(c)
    if s:
        S(c)
    return c


V = {
    'e_all': build(),
    'e_allm': build(readout=True),
    'e_noP': build(p=False),
    'e_noX_noS': build(x=False, s=False),
    'e_noS': build(s=False),
    'e_noGP': build(g=False, p=False),
}
if __name__ == '__main__':
    for k, c in V.items():
        save(c, BASE, '/home/jihoon/competitions/quantumn/work/lanes/PRECELL/c/' + k, dict(source='PRECELL build_e ' + k))
    print(list(V))
