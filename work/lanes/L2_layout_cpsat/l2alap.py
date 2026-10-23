"""ALAP pre-cycle variants (L5 greedy reverse, priority seeds) of an l2run result, official seed-0 score.
Usage: python l2alap.py <res json> <idx> <nseeds> [S0]   -> alapvar/<hash>.qasm/.json, one line per variant.
PROCS env sets fast_check processes. CMONLY=1 keeps only can_commute=True (the better family so far)."""
import copy
import hashlib
import json
import os
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/L2_layout_cpsat")
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/L5_precycle")
import l2model as L  # noqa: E402
import fast_check  # noqa: E402
from qcirc import Circ  # noqa: E402
from schedules import greedy  # noqa: E402


def load_assign(a):
    import ast
    out = {}
    for k, v in a:
        k0, k1, k2 = k
        if k0 == "M":
            out[("M", int(k1), int(k2))] = v
        elif k1 == "U":
            out[(int(k0), "U", "")] = v
        elif k1 == "A":
            out[(int(k0), "A", ast.literal_eval(k2))] = v
        else:
            out[(int(k0), int(k1), k2)] = v
    return out


def emit(ops, template):
    c = Circ(template.n)
    c.nbits = template.nbits
    c.detectors = copy.deepcopy(template.detectors)
    c.postselect = copy.deepcopy(template.postselect)
    c.frame = copy.deepcopy(template.frame)
    for kind, qs, b in ops:
        if kind == "cx": c.cx(*qs)
        elif kind == "RX": c.rx(*qs)
        elif kind == "R": c.reset(*qs)
        elif kind == "barrier": c.barrier(*qs)
        elif kind in ("M", "MX"):
            if kind == "MX": c.ops.append(f"h q[{qs[0]}];")
            c.ops.append(f"measure q[{qs[0]}] -> c[{b}];")
            c.sops.append((kind, qs, b))
        else: c.g(kind[2:], *qs)
    return c


def alap_circuit(m, assign, orient, seed=0, can_commute=False):
    c, data = m.full_circuit(assign, orient, lazy=False)
    split = next(i for i, op in enumerate(c.sops) if op[0] == "barrier")
    pre = c.sops[:split]
    ts = greedy(pre, seed, True, can_commute)
    used = sorted({q for k, qs, b in pre for q in qs})
    out = []
    for t in range(max(ts) + 1):
        out.extend(op for op, s in zip(pre, ts) if s == t)
        if t < max(ts):
            out.append(("barrier", tuple(used), None))
    return emit(out + c.sops[split:], c).rescheduled(lazy_init=True), data


if __name__ == "__main__":
    f, idx, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    S0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    cost, a, o, seed, name = json.load(open(f))[idx]
    m = L.variant(name)
    os.makedirs("alapvar", exist_ok=True)
    seen = set()
    for s in range(S0, S0 + n):
        for cm in ((True,) if os.environ.get("CMONLY") else (False, True)):
            c, data = alap_circuit(m, load_assign(a), o, seed=s, can_commute=cm)
            text = c.text()
            h = hashlib.sha1(text.encode()).hexdigest()[:10]
            if h in seen:
                continue
            seen.add(h)
            rep = fast_check.check(text, data, shots=10**8, procs=int(os.environ.get("PROCS", 20)))
            open(f"alapvar/{h}.qasm", "w").write(text)
            json.dump({"data_qubits": data, "score": rep.score, "sem": rep.sem, "acceptance": rep.acceptance,
                       "n_2q": rep.n_2q, "passed": rep.passed, "proxy": cost, "variant": name, "alap_seed": s,
                       "commute": cm, "source": f"L2 {f}#{idx} ({name}, proxy {cost:.5e}) + L5 ALAP seed {s} commute {cm}"},
                      open(f"alapvar/{h}.json", "w"), indent=1)
            print(f"{h} {name} proxy {cost:.5e} s{s} cm{int(cm)} 1-F {rep.score:.5e} acc {rep.acceptance:.4f} "
                  f"2q {rep.n_2q} pass {rep.passed}", flush=True)
