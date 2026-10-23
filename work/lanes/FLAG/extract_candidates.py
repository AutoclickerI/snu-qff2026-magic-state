#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Enumerate and retain a larger best-candidate prefix for the FLAG lane.

The EXENC native engine keeps only 20 circuits in its ``top`` array.  The
flag search needs a few hundred circuits, ordered by the same tuple used by
the engine (danger units, depth, CX, pivots, layers).  This script makes a
private source copy under FLAG, changes only that retention limit, compiles
it, runs the exact exhaustive 11--13 CX search, and writes the raw engine
JSON under FLAG.  It does not modify EXENC or synth.py.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
EXENC = HERE.parent / "EXENC"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--extra", type=int, default=2)
    ap.add_argument("--out", default="prepA_L5_flag_candidates.json")
    args = ap.parse_args()
    if args.limit < 1 or not 1 <= args.workers <= 16 or args.extra < 0:
        raise SystemExit("limit >= 1, workers in 1..16, extra >= 0 required")

    src = EXENC / "exact.cpp"
    text = src.read_text()
    # Keep this assertion strict so an upstream source change cannot silently
    # produce an incomplete candidate list.
    needle = "using namespace std;\n"
    if text.count(needle) != 1:
        raise RuntimeError("unexpected exact.cpp layout")
    text = text.replace(needle, needle + f"constexpr size_t TOP_LIMIT = {args.limit};\n", 1)
    replacements = {
        "if(top.size()<20 || better(c,top.back()))":
            "if(top.size()<TOP_LIMIT || better(c,top.back()))",
        "if(top.size()>20) top.pop_back();":
            "if(top.size()>TOP_LIMIT) top.pop_back();",
        "if(merged.top.size()>20) merged.top.resize(20);":
            "if(merged.top.size()>TOP_LIMIT) merged.top.resize(TOP_LIMIT);",
    }
    for old, new in replacements.items():
        if text.count(old) != 1:
            raise RuntimeError(f"expected one occurrence of {old!r}")
        text = text.replace(old, new, 1)

    private_src = HERE / "exact_top.cpp"
    binary = HERE / "exact_top"
    raw = HERE / "prepA_L5_flag_candidates_raw.json"
    out = HERE / args.out
    private_src.write_text(text)
    tmp = HERE / ".tmp"
    tmp.mkdir(exist_ok=True)
    subprocess.run(
        ["g++", "-O3", "-std=c++20", "-pthread", "-Wall", "-Wextra",
         str(private_src), "-o", str(binary)],
        check=True, env={**os.environ, "TMPDIR": str(tmp)},
    )
    cells = [1, 14, 8, 9, 2, 16, 15]
    # The native engine's input is n, k, extra, workers, alternatives,
    # enumerate, max_class, followed by available cells.  With no helpers,
    # n=7 and k=5 for the four Steane Z checks plus the |+_L> row.
    request = " ".join(map(str, [7, 5, args.extra, args.workers, 1, 1, 0, *cells])) + "\n"
    with raw.open("w") as f:
        subprocess.run([str(binary)], input=request, text=True, stdout=f, check=True)
    result = json.loads(raw.read_text())
    if result.get("unreachable"):
        raise RuntimeError(f"unreachable search: {result}")
    top = result.get("top", [])
    if len(top) < args.limit:
        raise RuntimeError(f"engine returned {len(top)} candidates, expected {args.limit}")
    # Retain the full engine result for provenance and a compact candidate
    # list that the flag scorer can consume directly.
    out.write_text(json.dumps(top, indent=2) + "\n")
    result["top"] = top
    (HERE / "prepA_L5_flag_candidates_stats.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps({"candidates": len(top), "out": str(out),
                      "engine_seconds": result.get("engine_seconds")}))


if __name__ == "__main__":
    main()
