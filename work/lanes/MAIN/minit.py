"""Replace first-use pure Z resets with `measure` + DETECTOR (judge: 2p/3 flip after M vs p after R).

    python minit.py <in stem> <out dir> [q,q,...]   -> <out dir>/<name>_m<q>.qasm/.json per site and _mall,
                                                       or only the listed sites as _m<q>_<q>...
"""
import json, re, sys
stem, out = sys.argv[1], sys.argv[2]
src = open(stem + ".qasm").read().split("\n")
data = json.load(open(stem + ".json"))["data_qubits"]
seen, sites = set(), []
for i, l in enumerate(src):
    if l.startswith(("barrier", "qreg", "OPENQASM", "include", "creg", "//")) or not l.strip():
        continue
    for q in map(int, re.findall(r"q\[(\d+)\]", l)):
        if q in seen:
            continue
        seen.add(q)
        if l.strip() == f"reset q[{q}];":
            nxt = next(m for m in src[i + 1:] if re.search(rf"q\[{q}\]", m) and not m.startswith("barrier"))
            if not nxt.startswith(f"h q[{q}]"):
                sites.append((i, q))
creg = next(i for i, l in enumerate(src) if l.startswith("creg"))
n0 = int(re.search(r"\[(\d+)\]", src[creg]).group(1))
name = stem.split("/")[-1]


def emit(sub, tag):
    lines, n, dets = list(src), n0, []
    for i, q in sub:
        lines[i] = f"measure q[{q}] -> c[{n}];"
        dets.append(f"// DETECTOR c[{n}]")
        n += 1
    lines[creg] = f"creg c[{n}];"
    txt = "\n".join(lines).rstrip("\n") + "\n" + "".join(d + "\n" for d in dets)
    open(f"{out}/{name}_{tag}.qasm", "w").write(txt)
    json.dump({"data_qubits": data, "source": f"{stem} with first-use resets {[q for _, q in sub]} measured (minit.py)"},
              open(f"{out}/{name}_{tag}.json", "w"))


if len(sys.argv) > 3:
    pick = [int(x) for x in sys.argv[3].split(",")]
    emit([s for s in sites if s[1] in pick], "m" + "_".join(map(str, pick)))
else:
    for s in sites:
        emit([s], f"m{s[1]}")
    emit(sites, "mall")
print("sites", [q for _, q in sites])
