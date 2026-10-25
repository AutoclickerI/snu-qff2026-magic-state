"""Insert one noisy tick (id on every live qubit) before native tick t. usage: insert.py <stem> <t> <outstem>"""
import sys, json, shutil
sys.path.insert(0, "/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem")
from tprep.qasm import convert
from tprep.noise import schedule
from qedit import load

def qops(stem):
    stim, _, err = convert(open(stem + ".qasm").read())
    assert not err, err
    prog, steps, gaps = schedule(stim)
    ops = {}
    for ins, groups in zip(prog, steps):
        if ins.name == "DETECTOR":
            continue
        for g, t in groups:
            for q in g:
                ops.setdefault(q, []).append((t, ins.name))
    return {q: sorted(v) for q, v in ops.items()}

def live_at(ops, t):
    out = []
    for q, v in ops.items():
        before = [x for x in v if x[0] < t]
        after = [x for x in v if x[0] >= t]
        if not before:
            continue
        if after:
            if after[0][1] in ("R", "RX"):
                continue
            out.append(q)
        elif before[-1][1] not in ("M", "MX"):
            out.append(q)
    return sorted(out)

if __name__ == "__main__":
    stem, t, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    c = load(stem)
    assert len(c.segs) == max(x[0] for v in qops(stem).values() for x in v) + 1, len(c.segs)
    live = live_at(qops(stem), t)
    c.segs.insert(t, [[f"id q[{q}];"] for q in live])
    open(out + ".qasm", "w").write(c.text())
    meta = json.load(open(stem + ".json"))
    meta = {"data_qubits": meta["data_qubits"], "source": f"{stem} + noisy tick inserted before {t}", "live": live}
    json.dump(meta, open(out + ".json", "w"), indent=1)
    print(t, len(live), live)
