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
sys.path[:0] = [str(ROOT / "work" / "lanes" / "EVAL"), str(ROOT / "work")]
from exact2 import Eval  # noqa: E402
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


class Quadratic:
    """Exact2 second-order loss as a quadratic in channel probabilities."""

    def __init__(self, text, data, units, header, suffix):
        self.units = units
        self.header, self.suffix = header, suffix
        # A fully serial witness makes every possible inter-operation gap
        # positive.  Its idle signatures are the signatures at the same fixed
        # operation boundary in every other schedule.
        serial = emit(header, units, list(range(len(units))), suffix)
        self.ev = Eval(serial, data)
        ev = self.ev
        self.p0 = np = __import__("numpy")
        self.p0 = np.array([c["prob"] for c in ev.m.chans], dtype=float)
        self.frac = ev.fp / np.array([self.p0[c] for c in ev.fch])
        self.idle = {}
        labels = native_qasm_index(serial)
        for c, ch in enumerate(ev.m.chans):
            if ch["gap"] is None:
                continue
            ii = ch["ins"]
            lab = ev.m.labels[ev.m.prog[ii].line_no - 1]
            m = re.match(r"instruction (\d+)", lab)
            if not m:
                raise AssertionError(lab)
            raw_i = labels[int(m.group(1))]
            # raw_i is a raw statement index; map to its native unit.
            u = next((j for j, x in enumerate(units) if raw_i in x.raw_indices), None)
            if u is None:
                raise AssertionError((raw_i, ch, lab))
            q = int(ch["gap"][0])
            key = (u, q)
            if key in self.idle:
                raise AssertionError(("duplicate idle", key))
            self.idle[key] = c
        self._prepare()

    @staticmethod
    def gap_prob(n):
        return 0.75 * (1.0 - (1.0 - 4.0 * P / 3.0) ** n) if n > 0 else 0.0

    def _prepare(self):
        ev = self.ev
        nchan = len(ev.m.chans)
        # Per-channel linear coefficients.
        self.nlin = __import__("numpy").bincount(ev.fch, weights=self.frac * ev.n_single, minlength=nchan)
        self.alin = __import__("numpy").bincount(ev.fch, weights=self.frac * (1.0 - ev.a_single), minlength=nchan)
        self.same = self.nlin * self.alin
        self.K = __import__("numpy").zeros((nchan, nchan), dtype=float)
        # Cache all (s,d) tables used by group pairs.  This is the same table
        # that exact2._pair_chunk calls, but it is evaluated once per channel
        # model rather than once per candidate schedule.
        cache = {}
        for ga, (sa, da) in enumerate(ev.gkeys):
            for gb in range(ga, len(ev.gkeys)):
                sb, db = ev.gkeys[gb]
                key = (sa ^ sb, da ^ db)
                if key not in cache:
                    cache[key] = ev.e.ntable(*key)[1]
        for ga, (sa, da) in enumerate(ev.gkeys):
            for gb in range(ga, len(ev.gkeys)):
                sb, db = ev.gkeys[gb]
                aa, ab = ev.ga[ga], ev.ga[gb]
                ia, ib = ev.gmem[ga], ev.gmem[gb]
                ci, cj = ev.fch[ia], ev.fch[ib]
                cross = ci[:, None] != cj[None, :]
                if ga == gb:
                    cross &= __import__("numpy").triu(__import__("numpy").ones_like(cross, dtype=bool), 1)
                if not cross.any():
                    continue
                ni = ev.n_single[ia][:, None]
                nj = ev.n_single[ib][None, :]
                nij = 0.0 if cache[(sa ^ sb, da ^ db)] is None else cache[(sa ^ sb, da ^ db)][ev.fe[ia][:, None] ^ ev.fe[ib][None, :]]
                w = self.frac[ia][:, None] * self.frac[ib][None, :] * (nij - ab * ni - aa * nj)
                w = w * cross
                lo = __import__("numpy").minimum(ci[:, None], cj[None, :])
                hi = __import__("numpy").maximum(ci[:, None], cj[None, :])
                for x, y, z in zip(lo[cross], hi[cross], w[cross]):
                    self.K[int(x), int(y)] += float(z)
        self.base_nonidle = self.p0.copy()
        self.n_idle = len(self.idle)
        # A serial witness can still have no idle channel when two successive
        # units on a wire happen to occupy adjacent layers.  Such a boundary
        # has a fixed zero gap in the reference model; keep it adjacent during
        # local search rather than inventing an unmodelled signature.
        self.no_gap = set()
        self.no_tail = set()
        byq = {}
        for i, u in enumerate(self.units):
            for q in u.qs:
                byq.setdefault(q, []).append(i)
        for q, seq in byq.items():
            for a, b in zip(seq, seq[1:]):
                if (a, q) not in self.idle and self.units[b].name not in ("RESET", "RX"):
                    self.no_gap.add((a, b))
            a = seq[-1]
            if not self.units[a].last_is_measure and (a, q) not in self.idle:
                self.no_tail.add(a)

    def feasible(self, times):
        for a, b in self.no_gap:
            if times[b] != times[a] + 1:
                return False
        for a in self.no_tail:
            if times[a] != max(times):
                return False
        return True

    def probabilities(self, times):
        Pch = self.base_nonidle.copy()
        # First set every known idle channel to zero; a zero-length gap has no
        # channel in noise_blocks and is represented exactly this way.
        for c in self.idle.values():
            Pch[c] = 0.0
        last = {}
        end = max(times) + 1
        for i, u in enumerate(self.units):
            for q in u.qs:
                if q in last:
                    j, t, measured = last[q]
                    n = int(times[i] - t - 1)
                    # waiting before reset is free; all other positive gaps are
                    # merged by the judge into one channel.
                    if n > 0 and u.name not in ("RESET", "RX"):
                        c = self.idle.get((j, q))
                        if c is None:
                            raise AssertionError(("missing idle key", j, q, i, n))
                        Pch[c] = self.gap_prob(n)
                last[q] = (i, int(times[i]), u.last_is_measure)
        for q, (j, t, measured) in last.items():
            n = int(end - t - 1)
            if n > 0 and not measured:
                c = self.idle.get((j, q))
                if c is None:
                    raise AssertionError(("missing tail key", j, q))
                Pch[c] = self.gap_prob(n)
        return Pch

    def score(self, times):
        Pch = self.probabilities(times)
        loss2 = float((Pch * Pch * self.same).sum())
        for i in range(len(Pch)):
            if Pch[i] == 0:
                continue
            loss2 += float(Pch[i] * (Pch[i + 1:] * self.K[i, i + 1:]).sum())
        A1 = float((Pch * self.alin).sum())
        loss1 = float((Pch * self.nlin).sum())
        return dict(loss2=loss2, loss1=loss1, A1=A1, exp_minus_A1=math.exp(-A1), probabilities=Pch)


def build_dag(units):
    pred = [set() for _ in units]
    succ = [set() for _ in units]
    last = {}
    for i, u in enumerate(units):
        for q in u.qs:
            if q in last:
                pred[i].add(last[q]); succ[last[q]].add(i)
            last[q] = i
    return pred, succ


def feasible(times, units, pred, succ):
    for i, u in enumerate(units):
        for j in pred[i]:
            if times[j] >= times[i]:
                return False
        for j in succ[i]:
            if times[i] >= times[j]:
                return False
    occ = {}
    for i, u in enumerate(units):
        key = int(times[i])
        for q in u.qs:
            if (q, key) in occ:
                return False
            occ[(q, key)] = i
    return True


def optimize(quad, times, steps, seed, iterations, max_a1=None):
    rng = random.Random(seed)
    pred, succ = build_dag(quad.units)
    times = compress(times)
    assert feasible(times, quad.units, pred, succ)
    assert quad.feasible(times)
    cur = quad.score(times)
    best = (cur["loss2"], list(times), cur)
    # A greedy local search with occasional annealed uphill moves.  Every
    # proposal is evaluated by the exact quadratic, not a gap-length proxy.
    temp0 = max(1e-12, cur["loss2"] * 0.01)
    for it in range(iterations):
        i = rng.randrange(len(times))
        lo = max((times[j] + 1 for j in pred[i]), default=0)
        hi = min((times[j] - 1 for j in succ[i]), default=max(times) + 1)
        choices = []
        occupied = {(q, times[j]) for j, u in enumerate(quad.units) if j != i for q in u.qs}
        for t in range(max(0, lo), min(max(times) + 1, hi) + 1):
            if t == times[i] or any((q, t) in occupied for q in quad.units[i].qs):
                continue
            choices.append(t)
        if not choices:
            continue
        nt = list(times); nt[i] = rng.choice(choices); nt = compress(nt)
        if not feasible(nt, quad.units, pred, succ) or not quad.feasible(nt):
            continue
        ns = quad.score(nt)
        if max_a1 is not None and ns["A1"] > max_a1:
            continue
        delta = ns["loss2"] - cur["loss2"]
        temp = temp0 * (1.0 - it / max(1, iterations))
        if delta <= 0 or rng.random() < math.exp(-delta / max(1e-18, temp)):
            times, cur = nt, ns
            if cur["loss2"] < best[0]:
                best = (cur["loss2"], list(times), cur)
        if steps and (it + 1) % steps == 0:
            print(json.dumps({"iter": it + 1, "current": cur["loss2"], "best": best[0], "depth": max(times) + 1}), flush=True)
    return best[1], best[2]


def random_schedule(units, pred, succ, rng):
    rem = set(range(len(units)))
    times = [-1] * len(units)
    occ = set()
    t = 0
    while rem:
        ready = [i for i in rem if all(times[j] >= 0 for j in pred[i])]
        rng.shuffle(ready)
        took = []
        for i in ready:
            if any((q, t) in occ for q in units[i].qs):
                continue
            took.append(i)
            for q in units[i].qs:
                occ.add((q, t))
        if not took:
            t += 1
            continue
        for i in took:
            times[i] = t
            rem.remove(i)
        t += 1
    return compress(times)


def random_variant(quad, start, pred, succ, rng, moves=200):
    """Perturb a valid schedule while retaining all fixed-zero-gap boundaries."""
    ts = list(start)
    for _ in range(moves):
        i = rng.randrange(len(ts))
        lo = max((ts[j] + 1 for j in pred[i]), default=0)
        hi = min((ts[j] - 1 for j in succ[i]), default=max(ts) + 1)
        occ = {(q, ts[j]) for j, u in enumerate(quad.units) if j != i for q in u.qs}
        choices = [t for t in range(max(0, lo), min(max(ts) + 1, hi) + 1)
                   if t != ts[i] and not any((q, t) in occ for q in quad.units[i].qs)]
        if not choices:
            continue
        nt = list(ts); nt[i] = rng.choice(choices); nt = compress(nt)
        if feasible(nt, quad.units, pred, succ) and quad.feasible(nt):
            ts = nt
    return ts


def exact_json(path, text, data):
    q = Path(path)
    q.write_text(text)
    j = q.with_suffix(".json")
    j.write_text(json.dumps({"data_qubits": data, "source": "SCHED exact quadratic scheduler"}, indent=2) + "\n")
    out = q.with_suffix(".exact.json")
    subprocess.run([sys.executable, str(ROOT / "work" / "lanes" / "EVAL" / "exact2.py"), str(q), "--procs", "2", "--top", "0", "--json", str(out)], check=True, stdout=subprocess.DEVNULL)
    return json.loads(out.read_text())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=("v12", "cand2"))
    ap.add_argument("--iterations", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20261024)
    ap.add_argument("--validate", type=int, default=5)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()
    if args.target == "v12":
        seed_path = ROOT / "work" / "lanes" / "PRE" / "alap_best.qasm"
        data = json.loads((ROOT / "work" / "lanes" / "PRE" / "alap_best.json").read_text())["data_qubits"]
        out_stem = HERE / "v12_scheduled"
    else:
        seed_path = ROOT / "work" / "lanes" / "ST_BC" / "cand2.qasm"
        data = json.loads((ROOT / "work" / "lanes" / "ST_BC" / "cand2.json").read_text())["data_qubits"]
        out_stem = HERE / "cand2_scheduled"
    source = seed_path.read_text()
    header, raw, suffix = qasm_ops(source)
    units = fold_units(raw)
    seed_times = source_times(source, units)
    quad = Quadratic(source, data, units, header, suffix)
    pred, succ = build_dag(units)
    base = quad.score(seed_times)
    assert quad.feasible(seed_times)
    print(json.dumps({"target": args.target, "units": len(units), "idle_channels": quad.n_idle, "baseline_model": {k: base[k] for k in ("loss2", "loss1", "A1", "exp_minus_A1")}, "depth": max(seed_times) + 1}), flush=True)

    # Required model check: five random feasible schedules against uncached
    # exact2's second-order output.
    rng = random.Random(args.seed + 91)
    checks = []
    for k in range(args.validate):
        ts = random_variant(quad, seed_times, pred, succ, rng)
        txt = emit(header, units, ts, suffix)
        q = HERE / f"modelcheck_{args.target}_{k}.qasm"
        ex = exact_json(q, txt, data)
        pred2 = quad.score(ts)["loss2"]
        rel = abs(pred2 - ex["loss2"]) / max(abs(ex["loss2"]), 1e-30)
        checks.append({"k": k, "predicted": pred2, "exact2": ex["loss2"], "relative_error": rel, "depth": max(ts) + 1})
        if rel > 1e-9:
            raise AssertionError(checks[-1])
    (HERE / f"modelcheck_{args.target}.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps({"model_checks": checks}), flush=True)

    max_a1 = 0.69 if args.target == "cand2" else None
    best_times, best = optimize(quad, seed_times, max(1, args.iterations // 10), args.seed, args.iterations, max_a1=max_a1)
    text = emit(header, units, best_times, suffix)
    out_qasm = out_stem.with_suffix(".qasm")
    out_json = out_stem.with_suffix(".json")
    out_qasm.write_text(text)
    out_json.write_text(json.dumps({"data_qubits": data, "source": str(seed_path), "schedule": {"times": best_times, "units": len(units)}, "quadratic": {k: best[k] for k in ("loss2", "loss1", "A1", "exp_minus_A1")}, "depth": max(best_times) + 1, "model_checks": checks}, indent=2) + "\n")
    print(json.dumps({"best": {k: best[k] for k in ("loss2", "loss1", "A1", "exp_minus_A1")}, "depth": max(best_times) + 1, "out": str(out_qasm)}), flush=True)


if __name__ == "__main__":
    main()
