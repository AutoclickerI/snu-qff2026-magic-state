"""Cross-check: inject chosen fault sets into the judge's own engine (deterministic Pauli errors, all other noise at 0)
and compare acceptance*score (averaged over the engine's random measurement outcomes) with the exact tables."""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ[v]="1"
import sys, json, warnings, random
import numpy as np
from exact2 import *
import xtim
import tprep.check as _tc
tc = sys.modules["tprep.check"]
from tprep.noise import noise_blocks, STANDARD
from tprep.parse import count_measurements

def judge_value(ev, fault_ids, shots=20000, seed=0):
    m = ev.m
    text = m.text
    blocks = noise_blocks(text, 0.0, STANDARD)[1]
    plan = tc.Plan(m.data, m.frame, m.post, count_measurements(text))
    inject = {}
    for i in fault_ids:
        f = m.faults[i]; ch = m.chans[f["chan"]]
        inject.setdefault((ch["blk"], ch["jl"]), []).append(f)
    lines = []
    for b, blk in enumerate(blocks):
        for j, l in enumerate(blk):
            if (b, j) in inject:
                gl = []
                for f in inject[(b, j)]:
                    for P, q in zip(f["pauli"], f["qubits"]):
                        if P != "I": gl.append(f"{P}_ERROR(1) {q}")
                lines.append("\n".join(gl))
            else:
                lines.append(l)
    body = "\n".join(lines)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        r = tc._sample(xtim.Circuit(body + "\n" + plan.tail), shots, seed, plan)
    a = r["acceptance"] / ev.e.A0
    return a, (0 if r["acceptance"] == 0 else a * r["score"])

if __name__ == "__main__":
    q = sys.argv[1]
    data = json.load(open(q.rsplit(".", 1)[0] + ".json"))["data_qubits"]
    ev = Eval(open(q).read(), data)
    m = ev.m
    rnd = random.Random(1)
    # my exact n,a for a set
    def mine(ids):
        s = d = e = 0
        for i in ids:
            f = m.faults[i]; s ^= f["s"]; d ^= f["d"]; e ^= f["e"]
        a, n = ev.e.ntable(s, d)
        return a, (0 if n is None else n[e])
    # pairs: top pairs from run, plus random pairs with acceptance>0 and random triples
    r = run(ev, 8, keep_thr=1e-12)
    big = sorted(r["big"], key=lambda b: -abs(b[0]))
    sets = [[b[1], b[2]] for b in big[:6]] + [[b[1], b[2]] for b in rnd.sample(big, 6)]
    nf = len(m.faults)
    for _ in range(40):
        ids = rnd.sample(range(nf), 2)
        if m.faults[ids[0]]["chan"] != m.faults[ids[1]]["chan"]:
            a, n = mine(ids)
            if a > 0: sets.append(ids)
        if len(sets) > 28: break
    for _ in range(6):
        ids = rnd.sample([b[1] for b in big] + [b[2] for b in big], 3)
        if len({m.faults[i]["chan"] for i in ids}) == 3: sets.append(ids)
    worst = 0
    for ids in sets:
        a1, n1 = mine(ids)
        a2, n2 = judge_value(ev, ids)
        print(len(ids), f"exact a={a1:.4f} n={n1:.4f} | judge-engine a={a2:.4f} n={n2:.4f}", [ev.fault_label(i) for i in ids][:3], flush=True)
        worst = max(worst, abs(n1 - n2), abs(a1 - a2))
    print("max |diff| (statistical, 20000 shots):", worst)
