import json, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/me_layout"); sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import run_moves as R, gmodel as G, proxy2, stim
from verify import load_assign
from qcirc import Circ
from tprep.noise import STANDARD, apply_noise
from tprep.qasm import to_stim
cost, a, o, seed, name = json.load(open("../me_layout/res_A1_9b_1792752451.json"))[0]
m = R.variant(name); A = load_assign(a)
c = Circ(); c.g("id", *[G.P(q) for q in G.DATA0]); m.emit(c, A, o)
bit_check = {b: (t if B == "X" else 3 + t) for (t, B), bits in m.checks.items() for b in bits}
c.detectors = []
c = c.rescheduled(lazy_init=True)
print(c.text())
s, err = to_stim(c.text())
noisy = apply_noise(s, 1e-3, STANDARD)
bits = [b for kind, qs, b in c.sops if kind in ("M", "MX")]
lines = noisy.splitlines()
def loss(ls):
    t = "\n".join(ls)
    return proxy2.joint_loss(*(m._full(t, bits, bit_check, L) for L in "XZ"))
base = loss(lines); print("base", base)
res = []
for i, l in enumerate(lines):
    if l.startswith(("DEPOLARIZE", "X_ERROR", "Z_ERROR")):
        ls = lines[:i] + lines[i+1:]
        res.append((base - loss(ls), i, l, lines[i-1] if i else ""))
res.sort(reverse=True)
for r in res[:45]: print("%.3e"%r[0], r[1], r[2], "| after:", r[3])
