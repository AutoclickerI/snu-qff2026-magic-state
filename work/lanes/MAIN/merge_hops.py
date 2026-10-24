#!/usr/bin/env python
"""Apply a HOPS variant's edits (made on v20) to another base that shares v20's pre-stage and hop units.

    merge_hops.py <base stem> <out stem> [hop_early|advance_watch_all]

Each edited v20 unit is found in the base by (lines, native step); every one must exist unchanged. New
detector bits start after the base's creg. Native timing of the result is checked against the requested steps.
"""
import json
import re
import sys
from pathlib import Path

HOPS = Path(__file__).resolve().parents[1] / "HOPS"
sys.path.insert(0, str(HOPS))
from build import ROOT, S, native_times, read  # noqa: E402

# v20 unit indices, from HOPS monitor.py and combine.py
EDITS = {
    "hop_early": dict(shift=[112, 118, 116, 132, 117, 121, 133, 144, 154, 134, 145, 153, 161, 167, 168, 176, 184],
                      minit=[154, 193, 223], watch=[(9, 37), (15, 37)], drop=[], tdg=[], swap=[], reuse=[]),
    "advance_watch_all": dict(shift=[121, 133, 144, 154, 145, 153, 161, 167, 168, 176, 184], minit=[154, 223],
                              watch=[(9, 37), (15, 37)], drop=[134], tdg=[(15, 22), (8, 21)], swap=[145, 153], reuse=[118]),
}


def main():
    base, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    mode = sys.argv[3] if len(sys.argv) > 3 else "hop_early"
    e = EDITS[mode]
    _, u0, t0, _, _ = read(ROOT / "work/lanes/MAIN/v20")
    h, u, ts, tail, meta = read(base)
    tdg0 = {src: next(i for i, x in enumerate(u0) if x.lines == [f"tdg q[{src}];"]) for src, _ in e["tdg"]}
    where = {}
    for j, (x, t) in enumerate(zip(u, ts)):
        where.setdefault((tuple(x.lines), t), []).append(j)
    idx = {}
    for i in set(e["shift"] + e["minit"] + e["drop"] + e["swap"] + e["reuse"] + list(tdg0.values())):
        hit = where.get((tuple(u0[i].lines), t0[i]))
        assert hit and len(hit) == 1, (i, u0[i].lines, t0[i], hit)
        idx[i] = hit[0]
    bit = int(re.search(r"creg c\[(\d+)\]", "\n".join(h)).group(1))
    for src, dst in e["tdg"]:
        j = idx[tdg0[src]]
        u[j] = S.Unit([f"tdg q[{dst}];"], [])
        ts[j] = 44
    for i in e["reuse"]:
        u[idx[i]] = S.Unit(u[idx[i]].lines + [f"h q[{u[idx[i]].qs[0]}];"], [])
    for i in e["swap"]:
        a, b = re.findall(r"q\[(\d+)\]", u[idx[i]].lines[0])
        u[idx[i]] = S.Unit([f"cx q[{b}],q[{a}];"], [])
    for i in e["shift"]:
        ts[idx[i]] -= 1
    for i in e["minit"]:
        q = u[idx[i]].qs[0]
        assert u[idx[i]].lines == [f"reset q[{q}];"]
        u[idx[i]] = S.Unit([f"measure q[{q}] -> c[{bit}];"], [])
        tail.append(f"// DETECTOR c[{bit}]")
        bit += 1
    for q, t in e["watch"]:
        u.append(S.Unit([f"measure q[{q}] -> c[{bit}];"], []))
        ts.append(t)
        tail.append(f"// DETECTOR c[{bit}]")
        bit += 1
    drop = {idx[i] for i in e["drop"]}
    u = [x for j, x in enumerate(u) if j not in drop]
    ts = [t for j, t in enumerate(ts) if j not in drop]
    h = [re.sub(r"creg c\[\d+\]", f"creg c[{bit}]", s) for s in h]
    text = S.emit(h, u, ts, tail)
    _, rr, _ = S.qasm_ops(text)
    nu = S.fold_units(rr)
    nt = native_times(text, nu)
    order = sorted(range(len(u)), key=lambda i: (ts[i], i))
    assert [u[i].lines for i in order] == [x.lines for x in nu]
    assert [S.compress(ts)[i] for i in order] == nt, "native timing mismatch"
    meta.update(source=str(base), method=f"HOPS {mode} edits", CX=sum(x.name == "CX" for x in nu), native_depth=max(nt) + 1)
    meta.pop("prefix_unit_indices", None)
    out.with_suffix(".qasm").write_text(text)
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")
    print(out.name, "CX", meta["CX"], "depth", meta["native_depth"])


if __name__ == "__main__":
    main()
