"""Split the cycle proxy of a gen2 schedule into tail pairs (both errors undetected), partial-window
pairs (equal non-empty detector sets), and per-qubit tail masses comparable with bounds.py."""
import ast
import json
import sys

import bounds
import gen2_cycle as g2
import proxy2
from qcirc import Circ
from tprep.noise import STANDARD, apply_noise
from tprep.qasm import to_stim

COLS = {}
for di, xy in enumerate([(0, 0), (2, 3), (1, 1), (4, 0), (3, 0), (3, 2), (2, 1)]):
    COLS[sum(1 << t for t, (m, ds) in enumerate(proxy2.TILES) if xy in ds)] = di


def key(k):
    t, d, typ = k
    if d in ("U", "A"):
        return (int(t), d, ast.literal_eval(typ) if d == "A" else typ)
    return (int(t), ast.literal_eval(d), typ)


def circuits(f, idx):
    r = json.load(open(f))[idx]
    a, o = r[1], r[2]
    ex = r[4] if len(r) > 4 else []
    m = g2.Model(ex)
    a = {key(k): L for k, L in a}
    c = Circ(); c.g("id", *proxy2.DATA); m.emit(c, a, o)
    bit_check = {}
    for (t, B), bits in m.checks.items():
        for b in bits:
            bit_check[b] = t if B == "X" else 3 + t
    c.detectors = []
    c = c.rescheduled(lazy_init=True)
    s, err = to_stim(c.text())
    noisy = apply_noise(s, 1e-3, STANDARD)
    bits = [b for kind, qs, b in c.sops if kind in ("M", "MX")]
    return m._full(noisy, bits, bit_check, "X"), m._full(noisy, bits, bit_check, "Z")


def split(cx, cz):
    A, B = proxy2._mechanisms(cx), proxy2._mechanisms(cz)
    groups = {}
    for k in set(A) | set(B):
        la, lb = sorted(A.get(k, []), reverse=True), sorted(B.get(k, []), reverse=True)
        for i in range(max(len(la), len(lb))):
            pa, fa = la[i] if i < len(la) else (0.0, 0)
            pb, fb = lb[i] if i < len(lb) else (0.0, 0)
            groups.setdefault(k[0], []).append((max(pa, pb), k[1], fa, fb))

    def c(stab, fa, fb):
        fx = fa ^ (1 if stab & 0b000111 else 0)
        fz = fb ^ (1 if stab & 0b111000 else 0)
        return 1.0 if (fx and not fz) else (0.5 if fz else 0.0)

    out = {"first": 0.0, "tail_pairs": 0.0, "window_pairs": 0.0}
    masses = [dict(X=0.0, Y=0.0, Z=0.0) for _ in range(7)]
    for dets, gl in groups.items():
        for i, (pi, si, ai, bi) in enumerate(gl):
            if not dets:
                out["first"] += pi * c(si, ai, bi)
                sx, sz = si & 7, (si >> 3) & 7      # X-check flips (Z part), Z-check flips (X part)
                if sx and sz and sx == sz:
                    masses[COLS[sx]]["Y"] += pi
                elif sx and not sz:
                    masses[COLS[sx]]["Z"] += pi
                elif sz and not sx:
                    masses[COLS[sz]]["X"] += pi
            for pj, sj, aj, bj in gl[i + 1:]:
                v = pi * pj * c(si ^ sj, ai ^ aj, bi ^ bj)
                out["tail_pairs" if not dets else "window_pairs"] += v
    return out, masses


if __name__ == "__main__":
    f, idx = sys.argv[1], int(sys.argv[2])
    out, masses = split(*circuits(f, idx))
    print({k: f"{v:.3e}" for k, v in out.items()}, "total", f"{sum(out.values()):.4e}")
    print("tail masses (units of p):")
    for d, m in enumerate(masses):
        print(f"  d{d}: X {m['X']/1e-3:.2f}  Y {m['Y']/1e-3:.2f}  Z {m['Z']/1e-3:.2f}")
    print("formula on these masses:", f"{bounds.pair_loss(masses):.3e}")
    for kind in ("direct", "bell"):
        fl = [bounds.tail(kind, "X") for _ in range(7)]
        print(f"floor per qubit ({kind}): X {fl[0]['X']/1e-3:.2f} Y {fl[0]['Y']/1e-3:.2f} Z {fl[0]['Z']/1e-3:.2f}")
