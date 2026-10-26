#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Exact idle-gap quadratic scheduling for the SCHED lane.

The gate sequence is fixed.  A schedule is a layer number for each native
operation (reset+h and h+measure are native RX/MX units); barriers are emitted
between every nonempty layer.  The objective is exact2's second-order
polynomial with only idle-channel probabilities changed.
"""
import argparse
import json
import math
import os
import random
import re
import statistics
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
import tprep  # noqa: E402
import tprep.noise  # noqa: E402

QRE = re.compile(r"q\[(\d+)\]")
OP_RE = re.compile(r"^(reset|h|t|tdg|s|sdg|z|x|y|id|cx|measure)\b", re.I)
P = 1e-3


def qasm_ops(text):
    """Return (header, raw operation statements, detector/declaration suffix)."""
    lines = text.splitlines()
    first_op = None
    det = None
    raw = []
    for i, line in enumerate(lines):
        s = line.split("//", 1)[0].strip()
        comment = line.strip()
        if comment.startswith("// DETECTOR") or comment.startswith("// POSTSELECT") or comment.startswith("// FRAME_"):
            det = i if det is None else det
        if OP_RE.match(s):
            if first_op is None:
                first_op = i
            raw.append((s, i))
    if first_op is None:
        raise ValueError("no operations")
    header = [l for l in lines[:first_op] if not l.split("//", 1)[0].strip().startswith("barrier")]
    suffix_start = det if det is not None else len(lines)
    suffix = lines[suffix_start:]
    # Preserve any post-operation comments that are not a barrier.  Detector
    # comments are the only semantically relevant suffix in these circuits.
    if det is None:
        suffix = [l for l in lines[first_op + 1:] if not l.split("//", 1)[0].strip()]
    return header, [s for s, _ in raw], suffix


def name_qs(stmt):
    name = stmt.split()[0].lower()
    return name, tuple(int(x) for x in QRE.findall(stmt))


class Unit:
    __slots__ = ("lines", "name", "qs", "raw_indices", "last_is_measure")

    def __init__(self, lines, raw_indices):
        self.lines = lines
        self.raw_indices = raw_indices
        n, q = name_qs(lines[0])
        self.qs = tuple(sorted(set(sum((list(name_qs(s)[1]) for s in lines), []))))
        if n == "reset" and len(lines) == 2 and name_qs(lines[1])[0] == "h":
            self.name = "RX"
        elif n == "h" and name_qs(lines[1])[0] == "measure":
            self.name = "MX"
        elif n == "h":
            self.name = "H"
        else:
            self.name = n.upper()
        self.last_is_measure = name_qs(lines[-1])[0] == "measure"


def fold_units(raw):
    """Fold the same native pairs as tprep.qasm.convert, ignoring barriers."""
    parsed = [name_qs(s) for s in raw]
    per_q = {}
    for i, (n, qs) in enumerate(parsed):
        for q in qs:
            per_q.setdefault(q, []).append(i)
    partner = {}
    for seq in per_q.values():
        for k, i in enumerate(seq[:-1]):
            j = seq[k + 1]
            ni, nj = parsed[i][0], parsed[j][0]
            if ni == "reset" and nj == "h":
                partner[i] = (j,)
            elif ni == "h" and nj == "measure":
                # qasm.py folds h+measure when the next use is absent, reset,
                # or h (the latter includes the retained X state).
                after = parsed[seq[k + 2]][0] if k + 2 < len(seq) else None
                if after in (None, "reset", "h"):
                    partner[i] = (j,) + ((seq[k + 2],) if after == "h" else ())
    used = set()
    units = []
    for i, s in enumerate(raw):
        if i in used:
            continue
        if i in partner:
            js = partner[i]
            inds = (i,) + js
            used.update(inds)
            units.append(Unit([raw[k] for k in inds], list(inds)))
        else:
            used.add(i)
            units.append(Unit([s], [i]))
    return units


def emit(header, units, times, suffix):
    used = sorted({q for u in units for q in u.qs})
    by = {}
    for i, t in enumerate(times):
        by.setdefault(int(t), []).append(i)
    layers = sorted(by)
    out = list(header)
    for li, t in enumerate(layers):
        for i in sorted(by[t]):
            out.extend(units[i].lines)
        if li + 1 < len(layers):
            out.append("barrier " + ",".join(f"q[{q}]" for q in used) + ";")
    out.extend(suffix)
    return "\n".join(out).rstrip() + "\n"


def compress(times):
    vals = sorted(set(times))
    mp = {v: i for i, v in enumerate(vals)}
    return [mp[t] for t in times]


def source_times(text, units):
    """Layer times from barriers in the source text, folded to native units."""
    _, raw, _ = qasm_ops(text)
    raw_t = {}
    t = 0
    for s in raw:
        raw_t[len(raw_t)] = t
        # barriers are not in raw; recover the layer by walking original lines
    # Re-scan all statements, counting barriers.  This is deliberately textual
    # because the supplied baselines use one barrier per layer.
    layer = 0
    raw_t = {}
    ri = 0
    for line in text.splitlines():
        s = line.split("//", 1)[0].strip()
        if not s:
            continue
        if s.startswith("barrier"):
            layer += 1
        elif OP_RE.match(s):
            raw_t[ri] = layer
            ri += 1
    return compress([min(raw_t[j] for j in u.raw_indices) for u in units])


def native_qasm_index(text):
    """Map each qasm instruction number in convert() labels to native unit index."""
    lines = []
    # exact2.qasm_lines is intentionally not imported to avoid a second parser.
    for _, s in enumerate(text.splitlines(), 1):
        x = s.split("//", 1)[0].strip()
        if not x or x.startswith(("OPENQASM", "include", "qreg", "creg")):
            continue
        if x.startswith("//"):
            continue
        lines.append(x)
    out = {}
    ri = 0
    # The labels' instruction number includes barriers, and qasm's parser keeps
    # them in qc.data.  Associate every non-barrier statement with raw order.
    for k, s in enumerate(lines, 1):
        if s.startswith("barrier"):
            continue
        out[k] = ri
        ri += 1
    return out


