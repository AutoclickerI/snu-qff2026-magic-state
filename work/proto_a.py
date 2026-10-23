"""Prototype A (no grid): non-FT injection -> W check (T, MX^7, T†) -> stabilizer round."""
import sys
from qcirc import Circ, allow_any_coupling, evaluate

allow_any_coupling()
DATA = list(range(7))
SUPPORTS = [(0, 2, 4, 6), (1, 2, 5, 6), (3, 4, 5, 6)]


def inject(c):
    c.rx(0, 1, 3, 2)
    c.t(2)
    c.cxs([(2, 4), (2, 5), (0, 2), (0, 4), (0, 6), (1, 2), (1, 5), (1, 6), (3, 4), (3, 5), (3, 6)])


def w_check(c, anc=7, order=DATA):
    c.t(*DATA)
    c.rx(anc)
    for d in order:
        c.cx(anc, d)
    b = c.mx(anc)
    c.tdg(*DATA)
    c.detector(b)


def stab_round(c, first_anc=8):
    a = first_anc
    for s in SUPPORTS:          # X checks
        c.rx(a)
        for d in s:
            c.cx(a, d)
        c.detector(c.mx(a)); a += 1
    for s in SUPPORTS:          # Z checks
        c.reset(a)
        for d in s:
            c.cx(d, a)
        c.detector(c.measure(a)); a += 1


variant = sys.argv[1] if len(sys.argv) > 1 else "inject"
c = Circ()
inject(c)
if "w" in variant:
    w_check(c)
if "s" in variant:
    stab_round(c)
print(variant, "n_2q", c.n_2q())
evaluate(c.text(), DATA)
