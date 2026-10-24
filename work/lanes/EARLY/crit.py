"""Critical path of a candidate: per-qubit written order (optionally commuting CX pairs), ASAP with
no barriers, ALAP slack against the actual end. Prints the longest chain(s) ending in the round.

usage: crit.py <stem> [commute]
"""
import sys, json
sys.path.insert(0, "/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem")
from tprep.qasm import convert
from tprep.noise import schedule

NAMES = {"R": "R", "RX": "RX", "M": "M", "MX": "MX", "H": "H", "T": "T", "T_DAG": "t", "CX": "CX"}


def ops_of(stem):
    stim, _, err = convert(open(stem + ".qasm").read())
    assert not err, err
    prog, steps, gaps = schedule(stim)
    ops = []
    for ins, groups in zip(prog, steps):
        if ins.name == "DETECTOR":
            continue
        for g, t in groups:
            ops.append(dict(name=ins.name, qs=list(g), t=t))
    return ops


def commutes(a, b):
    if a["name"] == "CX" and b["name"] == "CX":
        return a["qs"][0] != b["qs"][1] and b["qs"][0] != a["qs"][1]
    # diagonal single-qubit (T, Tdg) on a CX control
    for x, y in ((a, b), (b, a)):
        if x["name"] in ("T", "T_DAG") and y["name"] == "CX" and x["qs"][0] == y["qs"][0]:
            return True
    return False


def analyze(ops, commute=False):
    n = len(ops)
    pre = [set() for _ in range(n)]
    if commute:
        byq = {}
        for j, o in enumerate(ops):
            for q in o["qs"]:
                for i in byq.get(q, []):
                    if not commutes(ops[i], o):
                        pre[j].add(i)
                byq.setdefault(q, []).append(j)
    else:
        last = {}
        for j, o in enumerate(ops):
            for q in o["qs"]:
                if q in last:
                    pre[j].add(last[q])
                last[q] = j
    es = [0] * n
    for j in range(n):
        es[j] = max((es[i] + 1 for i in pre[j]), default=0)
    end = max(es) + 1
    succ = [[] for _ in range(n)]
    for j in range(n):
        for i in pre[j]:
            succ[i].append(j)
    ls = [end - 1] * n
    for i in reversed(range(n)):
        if succ[i]:
            ls[i] = min(ls[i], min(ls[j] - 1 for j in succ[i]))
    return pre, es, ls, end


def fmt(o):
    if o["name"] == "CX":
        return f"CX{o['qs'][0]}>{o['qs'][1]}"
    return f"{NAMES.get(o['name'], o['name'])}{o['qs'][0]}"


def main():
    stem = sys.argv[1]
    commute = len(sys.argv) > 2 and sys.argv[2] == "commute"
    ops = ops_of(stem)
    pre, es, ls, end = analyze(ops, commute)
    print("written end", max(o["t"] for o in ops) + 1, "ASAP end", end, "commute", commute)
    # longest chains: ops with slack 0, grouped by time
    crit = [j for j in range(len(ops)) if ls[j] == es[j]]
    byt = {}
    for j in crit:
        byt.setdefault(es[j], []).append(j)
    for t in sorted(byt):
        print(t, " ".join(f"{fmt(ops[j])}(w{ops[j]['t']})" for j in byt[t]))


if __name__ == "__main__":
    main()
