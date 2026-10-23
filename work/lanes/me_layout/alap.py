"""Apply L5's pre-cycle ALAP rescheduling (lanes/L5_precycle/schedules.py, greedy reverse, no commutation)
to a gmodel variant's full circuit; final cycle left as emitted. Usage: python alap.py <res json> <idx> [tag]"""
import copy
import json
import os
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import tprep  # noqa: E402
import fast_check  # noqa: E402
import run_moves as R  # noqa: E402
from verify import load_assign  # noqa: E402
from qcirc import Circ  # noqa: E402

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/L5_precycle")
from schedules import greedy  # noqa: E402


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
    f, idx = sys.argv[1], int(sys.argv[2])
    tag = sys.argv[3] if len(sys.argv) > 3 else "alap"
    cost, a, o, seed, name = json.load(open(f))[idx]
    m = R.variant(name)
    for cm in (False, True):
        c, data = alap_circuit(m, load_assign(a), o, can_commute=cm)
        text = c.text()
        rep = fast_check.check(text, data, shots=10**8, procs=int(os.environ.get("PROCS", 20)))
        c1 = tprep.fault_scan(text, data).c1 if rep.passed else None
        lab = f"cand_{name}_{tag}{'_cm' if cm else ''}"
        print(f"{lab}: 1-F {rep.score:.5e} ± {rep.sem:.1e} acc {rep.acceptance:.4f} 2q {rep.n_2q} pass {rep.passed} c1 {c1}", flush=True)
        if rep.passed:
            open(lab + ".qasm", "w").write(text)
            json.dump({"data_qubits": data, "score": rep.score, "sem": rep.sem, "acceptance": rep.acceptance,
                       "n_2q": rep.n_2q, "c1": c1, "source": f"{f}#{idx} + L5 pre-cycle ALAP (commute={cm})"},
                      open(lab + ".json", "w"), indent=1)
