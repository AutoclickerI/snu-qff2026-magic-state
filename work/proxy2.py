"""Second-order loss proxy for a final stabilizer cycle (Clifford part only).

The cycle alone is run in Stim with the judge's exact noise (tprep's QASM conversion, idle
schedule included), starting from an ideal code state (MPP-prepared) plus input depolarizing
noise on the data. Each DEM error gets (detectors, final stabilizer flips, logical flip); errors
with equal detector sets pair up into undetected combinations. After the judge's lookup
correction the X_L / Z_L parities flip when (logical flip) xor (syndrome nonzero) is 1, since a
single-qubit correction anticommutes with X^7 / Z^7. Proxy = P(X_L flips) + 0.5 P(Z_L flips)
(Z_L costs 1 for the T state, X_L or Y_L 1/2), to second order, not counting 3+ faults.
"""
import stim

import cultiv_port as cp
from qcirc import Circ
from tprep.noise import STANDARD, apply_noise
from tprep.qasm import to_stim

TILES = [((1, 0), [(3, 0), (0, 0), (1, 1), (2, 1)]),
         ((1, 2), [(3, 2), (1, 1), (2, 3), (2, 1)]),
         ((3, 1), [(2, 1), (3, 2), (3, 0), (4, 0)])]
SUPPORT = [sorted(cp.phys(d) for d in ds) for _, ds in TILES]
DATA = sorted(cp.DATA)


def cycle_text(emit_fn, lazy=True):
    """emit_fn(c) appends the cycle; data get an `id` first so their idle from the cycle start counts.
    Returns noisy Stim text and the list of (qubit, basis) per measurement record, in order."""
    c = Circ()
    c.g("id", *DATA)
    emit_fn(c)
    c.detectors = []
    if lazy:
        c = c.rescheduled(lazy_init=True)
    s, err = to_stim(c.text())
    assert not err, err
    noisy = apply_noise(s, 1e-3, STANDARD)
    meas = []
    for line in noisy.splitlines():
        name, *args = line.split()
        if name in ("M", "MX"):
            meas += [(int(a), name) for a in args]
    return noisy, meas


def _mpp(B, qs):
    return "MPP " + "*".join(f"{B}{q}" for q in qs)


def full_circuit(noisy, meas, logical, q_in):
    stabs = [("X", s) for s in SUPPORT] + [("Z", s) for s in SUPPORT]
    lines = [_mpp(B, s) for B, s in stabs] + [_mpp(logical, DATA)]
    if q_in:
        lines.append(f"DEPOLARIZE1({q_in}) " + " ".join(map(str, DATA)))
    lines += [l for l in noisy.splitlines() if not l.startswith(("DETECTOR", "OBSERVABLE"))]
    lines += [_mpp(B, s) for B, s in stabs] + [_mpp(logical, DATA)]
    n_meas = 7 + len(meas) + 7
    rec = lambda i: f"rec[{i - n_meas}]"
    # each cycle measurement belongs to the tile whose ancilla pair holds that qubit
    anc_tile = {}
    for t, (m, _) in enumerate(TILES):
        anc_tile[cp.phys(m)] = t
        anc_tile[cp.phys((m[0] + 1, m[1]))] = t
    for j, (q, name) in enumerate(meas):
        t = anc_tile[q]
        k = t if name == "MX" else 3 + t
        lines.append(f"DETECTOR {rec(7 + j)} {rec(k)}")
    for k in range(6):
        lines.append(f"OBSERVABLE_INCLUDE({k}) {rec(7 + len(meas) + k)} {rec(k)}")
    lines.append(f"OBSERVABLE_INCLUDE(6) {rec(7 + len(meas) + 6)} {rec(6)}")
    return stim.Circuit("\n".join(lines))


def loss(circ, syn_bits):
    dem = circ.detector_error_model(decompose_errors=False, approximate_disjoint_errors=True)
    groups = {}
    for inst in dem.flattened():
        if inst.type != "error":
            continue
        p = inst.args_copy()[0]
        dets, mask = [], 0
        for t in inst.targets_copy():
            if t.is_relative_detector_id():
                dets.append(t.val)
            elif t.is_logical_observable_id():
                mask ^= 1 << t.val
        groups.setdefault(frozenset(dets), []).append((p, mask))

    def flip(mask):
        return ((mask >> 6) & 1) ^ (1 if mask & syn_bits else 0)

    first = sum(p for p, m in groups.get(frozenset(), []) if flip(m))
    second = 0.0
    for g in groups.values():
        for i in range(len(g)):
            pi, mi = g[i]
            for j in range(i + 1, len(g)):
                pj, mj = g[j]
                if flip(mi ^ mj):
                    second += pi * pj
    return first, second


def proxy(emit_fn, q_in=3e-3, lazy=True):
    noisy, meas = cycle_text(emit_fn, lazy)
    fa, sa = loss(full_circuit(noisy, meas, "X", q_in), 0b000111)   # X_L flips: Z/Y logical
    fb, sb = loss(full_circuit(noisy, meas, "Z", q_in), 0b111000)   # Z_L flips: X/Y logical
    return {"first": fa + fb, "xl": sa, "zl": sb, "cost": fa + 0.5 * fb + sa + 0.5 * sb}


if __name__ == "__main__":
    import json
    import pickle
    import cycle_interleave as ci
    import cycle_opt as co
    best = json.load(open("batch_1792737466.json"))
    spec = [r for r in best if r["passed"]][0]["spec"]
    lay = co.plan(tuple(map(tuple, spec["pf"])), tuple(map(tuple, spec["ps"])), spec["first"])
    for q_in in (0.0, 3e-3):
        print("v4", q_in, proxy(lambda c: co.emit(c, lay), q_in=q_in))
    il = json.load(open("batch_il_1792738661.json"))
    res = pickle.load(open("interleave2_l7.pkl", "rb"))
    for r in il[:5] + il[-5:]:
        i = r["spec"]["idx"]
        pr = proxy(lambda c: ci.emit(c, res[i][1], 7))
        print(f"il#{i} MC {r['score']:.4g}  proxy {pr}")


def _mechanisms(circ):
    dem = circ.detector_error_model(decompose_errors=False, approximate_disjoint_errors=True)
    out = {}
    for inst in dem.flattened():
        if inst.type != "error":
            continue
        dets, mask = [], 0
        for t in inst.targets_copy():
            if t.is_relative_detector_id():
                dets.append(t.val)
            elif t.is_logical_observable_id():
                mask ^= 1 << t.val
        out.setdefault((frozenset(dets), mask & 63), []).append((inst.args_copy()[0], (mask >> 6) & 1))
    return out


def joint_loss(circ_x, circ_z):
    """Second-order T-state infidelity with the logical type known per pair: Z_L costs 1, X_L
    and Y_L cost 1/2 (proxy() charges a Y_L as 1.5). Mechanisms of the X_L and Z_L circuits are
    matched by (detectors, stabilizer flips); where that is ambiguous the two flips are paired in
    order of probability."""
    A, B = _mechanisms(circ_x), _mechanisms(circ_z)
    mech = []
    for k in set(A) | set(B):
        la = sorted(A.get(k, []), reverse=True)
        lb = sorted(B.get(k, []), reverse=True)
        n = max(len(la), len(lb))
        for i in range(n):
            pa, fa = la[i] if i < len(la) else (0.0, 0)
            pb, fb = lb[i] if i < len(lb) else (0.0, 0)
            mech.append((k[0], k[1], max(pa, pb), fa, fb))
    groups = {}
    for dets, stab, p, fa, fb in mech:
        groups.setdefault(dets, []).append((p, stab, fa, fb))

    def cost(stab, fa, fb):
        fx = fa ^ (1 if stab & 0b000111 else 0)
        fz = fb ^ (1 if stab & 0b111000 else 0)
        return 1.0 if (fx and not fz) else (0.5 if fz else 0.0)

    first = sum(p * cost(s, fa, fb) for p, s, fa, fb in groups.get(frozenset(), []))
    second = 0.0
    for gl in groups.values():
        for i in range(len(gl)):
            pi, si, ai, bi = gl[i]
            for j in range(i + 1, len(gl)):
                pj, sj, aj, bj = gl[j]
                c = cost(si ^ sj, ai ^ aj, bi ^ bj)
                if c:
                    second += pi * pj * c
    return first + second
