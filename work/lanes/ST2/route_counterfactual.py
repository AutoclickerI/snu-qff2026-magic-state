"""Route the LADDER separate-block counterfactual with reversible nearest-neighbour paths."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
src = ROOT / "work/lanes/LADDER/f01_sepBC.qasm"
out = ROOT / "work/lanes/ST2/routed_f01_sepBC"

def adjacent(a, b):
    return abs(a // 6 - b // 6) + abs(a % 6 - b % 6) == 1

def path(a, b):
    r, c = divmod(a, 6); tr, tc = divmod(b, 6); p = [a]
    while r != tr:
        r += 1 if tr > r else -1; p.append(6 * r + c)
    while c != tc:
        c += 1 if tc > c else -1; p.append(6 * r + c)
    return p

def cx(a, b): return f"cx q[{a}],q[{b}];"

def route(a, b):
    if adjacent(a, b): return [cx(a, b)]
    p = path(a, b); lines = []
    for u, v in zip(p, p[1:-1]):
        lines += [cx(u, v), cx(v, u), cx(u, v)]
    lines.append(cx(p[-2], b))
    for u, v in reversed(list(zip(p, p[1:-1]))):
        lines += [cx(u, v), cx(v, u), cx(u, v)]
    return lines

lines = src.read_text().splitlines(); out_lines = []; extra = 0
for line in lines:
    m = re.match(r"cx q\[(\d+)\],q\[(\d+)\];$", line)
    if not m:
        out_lines.append(line); continue
    a, b = map(int, m.groups()); rr = route(a, b)
    out_lines.extend(rr); extra += len(rr) - 1
text = "\n".join(out_lines) + "\n"
out.with_suffix(".qasm").write_text(text)
md = json.loads(src.with_suffix(".json").read_text())
md.update({"source": str(src), "method": "shortest-path SWAP routing",
           "counterfactual_extra_cx": extra,
           "cx": sum(x.startswith("cx ") for x in out_lines)})
out.with_suffix(".json").write_text(json.dumps(md, indent=2) + "\n")
print(json.dumps({"extra_cx": extra, "total_cx": md["cx"]}))
