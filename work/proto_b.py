"""Prototype B (no grid): inject -> W check -> Z checks (bare) -> X checks (flagged). Target c1 = 0."""
import sys
from itertools import permutations
from qcirc import Circ, allow_any_coupling, evaluate

allow_any_coupling()
DATA = list(range(7))
SUPPORTS = [(0, 2, 4, 6), (1, 2, 5, 6), (3, 4, 5, 6)]
LINES = {frozenset(s) for s in [(0,1,2),(0,3,4),(0,5,6),(1,3,5),(1,4,6),(2,3,6),(2,4,5)]}
WORDS4 = {frozenset(set(range(7)) - l) for l in LINES}


def safe_order():
    for perm in permutations(DATA):
        bad = False
        for k in range(1, 7):
            pre = frozenset(perm[:k])
            if pre in LINES or pre in WORDS4:
                bad = True
                break
        if not bad:
            return list(perm)


def inject(c):
    c.rx(0, 1, 3, 2)
    c.t(2)
    c.cxs([(2, 4), (2, 5), (0, 2), (0, 4), (0, 6), (1, 2), (1, 5), (1, 6), (3, 4), (3, 5), (3, 6)])


def w_check(c, anc=7, order=None):
    order = order or safe_order()
    c.t(*DATA)
    c.rx(anc)
    for d in order:
        c.cx(anc, d)
    b = c.mx(anc)
    c.tdg(*DATA)
    c.detector(b)


def z_checks(c, a):
    for s in SUPPORTS:
        c.reset(a)
        for d in s:
            c.cx(d, a)
        c.detector(c.measure(a)); a += 1
    return a


def x_checks_flagged(c, a):
    for s in SUPPORTS:
        anc, flag = a, a + 1
        c.rx(anc); c.reset(flag)
        c.cx(anc, s[0]); c.cx(anc, flag); c.cx(anc, s[1]); c.cx(anc, s[2]); c.cx(anc, flag); c.cx(anc, s[3])
        c.detector(c.mx(anc)); c.detector(c.measure(flag)); a += 2
    return a


c = Circ()
inject(c)
w_check(c)
a = z_checks(c, 8)
x_checks_flagged(c, a)
print("order", safe_order(), "n_2q", c.n_2q())
if __name__ == "__main__":
    r = evaluate(c.text(), DATA, shots=int(float(sys.argv[1])) if len(sys.argv) > 1 else 10**6)
