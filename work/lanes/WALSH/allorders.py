#!/usr/bin/env python3
"""All-orders evaluation of the judge's conditional infidelity.

The EVAL model turns every independent judge channel into a categorical Pauli
factor.  A fault contributes an XOR signature on the rotation signs, detector
records, and decoder observables.  In the Walsh domain a channel is therefore

    chi_c(w) = (1-q_c) + sum_f p_f (-1)**(w . v_f).

The small quantum function is transformed on the rotation variables and on
the few non-identity detector projectors.  The other detector Fourier
variables are eliminated from the product of the channel factors.  This is a
variable-elimination calculation, so mutually exclusive Paulis from one
channel remain in one categorical factor.

Usage:
    allorders.py circuit.qasm [--json circuit.json] [--procs N]

The printed loss is conditional (the accepted numerator divided by the
acceptance), exactly as tprep.check reports it.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import multiprocessing as mp
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVAL = ROOT / "work" / "lanes" / "EVAL"
BCSYN2 = ROOT / "work" / "lanes" / "BCSYN2"
sys.path.insert(0, str(EVAL))
sys.path.insert(0, str(BCSYN2))

import exact2  # noqa: E402

try:
    import moments  # noqa: E402
except ImportError:  # pragma: no cover - only useful for a broken checkout
    moments = None


# Width 23 is the reviewer-3 v22/v23 case.  v24 measures at width 26 and is
# still tractable on the available hosts (about a 2**27 double tensor in its
# largest contraction); larger widths are rejected before allocation.
MAX_WIDTH = 26
MAX_ACTIVE_BITS = 23


def fwht(a: "object") -> None:
    """In-place unnormalised Walsh-Hadamard transform.

    The first axis is transformed.  Keeping the transform unnormalised makes
    the Parseval/Fourier factors explicit at the final contraction.
    """

    import numpy as np

    n = a.shape[0]
    if n == 0 or n & (n - 1):
        raise ValueError(f"Walsh dimension must be a power of two, got {n}")
    h = 1
    while h < n:
        x = a.reshape(-1, 2 * h, *a.shape[1:])
        # Keep only one half-sized temporary.  The previous two-copy form
        # caused NumPy's allocator to retain several gigabytes for a 2^19 x
        # 73 table even though the live table is only a few hundred MB.
        u = x[:, :h, ...].copy()
        x[:, :h, ...] += x[:, h:2 * h, ...]
        np.subtract(u, x[:, h:2 * h, ...], out=x[:, h:2 * h, ...])
        h <<= 1


def _pack_signature(sig: int, positions: tuple[int, ...]) -> int:
    out = 0
    for j, bit in enumerate(positions):
        out |= ((sig >> bit) & 1) << j
    return out


@dataclass
class Factor:
    scope: tuple[int, ...]
    values: object


def _factor_product(factors: list[Factor], union: tuple[int, ...]):
    """Multiply factors, aligning their little-endian scope indices."""

    import numpy as np

    if not factors:
        return np.ones(1, dtype=np.float64)
    n = 1 << len(union)
    idx = np.arange(n, dtype=np.uint64)
    out = np.ones(n, dtype=np.float64)
    where = {v: i for i, v in enumerate(union)}
    for f in factors:
        if not f.scope:
            out *= float(f.values[0])
            continue
        packed = np.zeros(n, dtype=np.uint32)
        for j, v in enumerate(f.scope):
            packed |= ((idx >> where[v]) & 1).astype(np.uint32) << j
        out *= np.asarray(f.values, dtype=np.float64)[packed]
    return out


def _scope_index_map(union: tuple[int, ...], scope: tuple[int, ...]):
    """Map union assignments to a factor's little-endian local index."""

    import numpy as np

    n = 1 << len(union)
    idx = np.arange(n, dtype=np.uint64)
    where = {v: i for i, v in enumerate(union)}
    packed = np.zeros(n, dtype=np.uint32)
    for j, v in enumerate(scope):
        packed |= ((idx >> where[v]) & 1).astype(np.uint32) << j
    return packed


def _eliminate_one(factors: list[Factor], variable: int) -> tuple[list[Factor], int]:
    import numpy as np

    take = [f for f in factors if variable in f.scope]
    if not take:
        return factors, 0
    rest = [f for f in factors if variable not in f.scope]
    union = tuple(sorted({v for f in take for v in f.scope}))
    prod = _factor_product(take, union)
    # Arrays use NumPy's big-endian reshape axes, whereas factor indices use
    # little-endian bit positions (scope[0] is bit 0).
    axis = len(union) - 1 - union.index(variable)
    shape = (2,) * len(union)
    reduced = prod.reshape(shape).sum(axis=axis)
    reduced_scope = tuple(v for v in union if v != variable)
    rest.append(Factor(reduced_scope, np.asarray(reduced, dtype=np.float64).reshape(-1)))
    return rest, len(union) - 1


def _min_fill_order(scopes: list[tuple[int, ...]], n_variables: int,
                    eliminate: set[int]) -> tuple[list[int], int]:
    """Choose a deterministic min-fill order and return its induced width."""

    adj = [set() for _ in range(n_variables)]
    for scope in scopes:
        for v in scope:
            adj[v].update(u for u in scope if u != v)
    alive = set(range(n_variables))
    order: list[int] = []
    width = 0
    while eliminate & alive:
        candidates = eliminate & alive

        def fill(v: int) -> int:
            ns = adj[v]
            return sum(1 for a in ns for b in ns if a < b and b not in adj[a])

        v = min(candidates, key=lambda x: (fill(x), len(adj[x]), x))
        ns = set(adj[v])
        width = max(width, len(ns))
        order.append(v)
        alive.remove(v)
        for u in ns:
            if u in alive:
                adj[u].update(ns - {u})
                adj[u].discard(v)
        adj[v].clear()
    return order, width


class WalshEvaluator:
    """Build the exact2 quantum tables and all channel factors."""

    def __init__(self, qasm_text: str, data_qubits: list[int], p: float = 1e-3,
                 procs: int = 1):
        import numpy as np

        self.p = p
        self.ev = exact2.Eval(qasm_text, data_qubits, p=p)
        self.m = self.ev.m
        self.engine = self.ev.e
        self.n_rot = len(self.m.rots)
        self.n_det = self.m.n_det
        self.n_variables = self.n_rot + self.n_det
        self.active_det = tuple(i for i, (x, z, _c) in enumerate(self.engine.projs)
                                if x or z)
        self.active_det_set = set(self.active_det)
        self.active_vars = tuple(range(self.n_rot)) + tuple(self.n_rot + i for i in self.active_det)
        self.active_pos = {v: j for j, v in enumerate(self.active_vars)}
        self.inactive_vars = set(range(self.n_variables)) - set(self.active_vars)
        self.K = len(self.active_vars)
        if self.K > MAX_ACTIVE_BITS:
            raise ValueError(
                f"quantum Walsh table has {self.K} active variables (limit {MAX_ACTIVE_BITS})")

        # Decoder characters.  High bits in a Q mask which no physical fault
        # can flip are harmless constants and naturally disappear from chi.
        self.qcoeff = np.asarray(self.engine.W * self.engine.beta, dtype=np.float64)
        self.qmasks = []
        for T, a, b in self.engine.keys:
            mask = a | (b << 3) | (1 << 6)
            if T == "X":
                mask |= 1 << 8
            else:
                mask |= (1 << 7) | (1 << 9)
            self.qmasks.append(int(mask))
        self.qmasks = tuple(self.qmasks)
        self.emasks = tuple(dict.fromkeys((0,) + self.qmasks))

        # Every non-identity projector is retained in the quantum table.  An
        # identity detector is still represented as a Fourier variable below;
        # its sum enforces that the corresponding noisy detector bit is zero.
        self._build_quantum_walsh()
        self._build_channel_data()

        scopes = [tuple(i for i in range(self.n_variables) if sig >> i & 1)
                  for sig in self.channel_scope_masks]
        self.elim_order, self.width = _min_fill_order(scopes, self.n_variables,
                                                      self.inactive_vars)
        if self.width > MAX_WIDTH:
            raise ValueError(
                f"channel-factor elimination width {self.width} exceeds limit {MAX_WIDTH}")
        self._compile_elimination()
        self.procs = max(1, int(procs))

    def _build_quantum_walsh(self) -> None:
        import numpy as np

        n = 1 << self.K
        self.n_quantum = len(self.engine.keys)
        vals = np.empty((n, 1 + self.n_quantum), dtype=np.float64)
        # Precompute the 32-dimensional magic state once per rotation-sign
        # pattern.  This is much cheaper than re-running it for every active
        # detector pattern.
        phis = np.asarray([self.engine.phi(s) for s in range(1 << self.n_rot)])
        mask_s = (1 << self.n_rot) - 1
        active_projectors = list(self.active_det)
        basis_idx = np.arange(self.engine.N, dtype=np.int64)
        q_perm = np.asarray([basis_idx ^ int(self.engine.Qs[key][0]) for key in self.engine.keys])
        q_phase = np.asarray([
            complex(self.engine.Qs[key][2]) * self.engine.sgn(self.engine.Qs[key][1])
            for key in self.engine.keys
        ])
        # A postselect projector can precede the ordinary detectors; the
        # order in engine.projs is the judge's order and must be preserved.
        chunk = 1 << 12
        for lo in range(0, n, chunk):
            hi = min(n, lo + chunk)
            x = np.arange(lo, hi, dtype=np.uint64)
            s = (x & mask_s).astype(np.int64)
            d = np.zeros(hi - lo, dtype=np.uint64)
            for j, det in enumerate(self.active_det):
                d |= ((x >> (self.n_rot + j)) & 1) << det
            acc = phis[s].copy()
            for k in active_projectors:
                mj, wj, coef = self.engine.projs[k]
                sign = (1.0 - 2.0 * ((int(self.engine.v[k]) ^ (d >> k)) & 1)).astype(np.float64)
                perm = self.engine.idx_i.astype(np.int64) ^ int(mj) if hasattr(self.engine, "idx_i") else None
                if perm is None:
                    idx = np.arange(self.engine.N, dtype=np.int64)
                    perm = idx ^ int(mj)
                sg = self.engine.sgn(wj)
                acc = (acc + sign[:, None] * complex(coef) * (sg[None, :] * acc)[:, perm]) / 2
            A = (np.abs(acc) ** 2).sum(axis=1)
            vals[lo:hi, 0] = A / self.engine.A0
            # Evaluate all 72 decoder Pauli expectations as one broadcasted
            # contraction.  The old Python loop repeated the 4096x32 complex
            # gather 72 times and dominated setup time.
            gathered = np.take(acc, q_perm, axis=1)
            vals[lo:hi, 1:] = (
                np.conj(gathered) * q_phase[None, :, :] * acc[:, None, :]
            ).sum(axis=2).real / self.engine.A0
        # vals[x] is the primal quantum function.  Its Walsh transform is
        # the factor needed by the characteristic-function contraction.
        fwht(vals)
        self.quantum_hat = vals

    def _build_channel_data(self) -> None:
        import numpy as np

        # A channel scope includes all detector bits, including the 39 whose
        # projectors are identities.  Those variables are eliminated later.
        self.channel_scope_masks: list[int] = []
        self.channel_scopes: list[tuple[int, ...]] = []
        self.channel_faults: list[list[tuple[int, float, int]]] = []
        self.scope_channels: dict[tuple[int, ...], list[int]] = collections.defaultdict(list)
        for c, ch in enumerate(self.m.chans):
            faults = []
            scope_mask = 0
            for f in self.m.faults:
                if f["chan"] != c:
                    continue
                sig = int(f["s"]) | (int(f["d"]) << self.n_rot)
                local = sig
                faults.append((local, float(f["p"]), int(f["e"])))
                scope_mask |= sig
            scope = tuple(i for i in range(self.n_variables) if scope_mask >> i & 1)
            self.channel_scope_masks.append(scope_mask)
            self.channel_scopes.append(scope)
            self.channel_faults.append(faults)
            self.scope_channels[scope].append(c)

        # Channel tables are Walsh transforms of each categorical outcome
        # distribution.  Storing all 73 decoder masks is small because the
        # sum of 2**scope over v22's 468 channels is only 65,215.
        self.channel_tables: list[dict[int, object]] = []
        for c, ch in enumerate(self.m.chans):
            scope = self.channel_scopes[c]
            width = len(scope)
            tables = {}
            packed_faults = [(_pack_signature(sig, scope), p_f, e)
                             for sig, p_f, e in self.channel_faults[c]]
            for emask in self.emasks:
                arr = np.zeros(1 << width, dtype=np.float64)
                arr[0] = 1.0 - float(ch["prob"])
                for sig, p_f, e in packed_faults:
                    arr[sig] += p_f * (-1.0 if (e & emask).bit_count() & 1 else 1.0)
                fwht(arr)
                tables[emask] = arr
            self.channel_tables.append(tables)

    def _compile_elimination(self) -> None:
        """Compile symbolic elimination and its index maps once.

        Rebuilding bit-packed index arrays for every e-character was the
        dominant cost of the first implementation.  The scopes and order do
        not depend on the character, so all maps are safely shared by forked
        workers.
        """

        initial = [(scope, c) for scope, cs in self.scope_channels.items() for c in cs]
        # Runtime factors are keyed by a stable integer id.  Initial factors
        # are in exactly the order used by _factors().
        scopes: dict[int, tuple[int, ...]] = {i: scope for i, (scope, _c) in enumerate(initial)}
        active_ids = list(scopes)
        next_id = len(active_ids)
        steps = []
        for v in self.elim_order:
            selected = [fid for fid in active_ids if v in scopes[fid]]
            if not selected:
                continue
            union = tuple(sorted({u for fid in selected for u in scopes[fid]}))
            new_scope = tuple(u for u in union if u != v)
            new_id = next_id
            next_id += 1
            rest = [fid for fid in active_ids if fid not in set(selected)]
            steps.append((tuple(selected), tuple(rest), union, v, new_id, new_scope))
            scopes[new_id] = new_scope
            active_ids = rest + [new_id]
        self._initial_factor_order = tuple(c for _scope, c in initial)
        self._elim_steps = steps
        self._final_factor_ids = tuple(active_ids)
        self._factor_scopes = scopes
        appearing = {v for scope in self.channel_scopes for v in scope}
        self._missing_inactive = len(self.inactive_vars - appearing)

    def _factors(self, emask: int) -> list[Factor]:
        # One categorical factor per channel.  Stable order lets the compiled
        # elimination plan use integer ids; same-scope factors are still
        # combined by the first multiplication at that scope.
        return [Factor(self.channel_scopes[c], self.channel_tables[c][emask])
                for c in self._initial_factor_order]

    def _group_table(self, scope: tuple[int, ...], emask: int):
        import numpy as np

        out = np.ones(1 << len(scope), dtype=np.float64)
        for c in self.scope_channels[scope]:
            out *= self.channel_tables[c][emask]
        return out

    def eliminate(self, emask: int):
        """Eliminate inactive detector Fourier variables for one e-character."""

        import numpy as np

        factors = {i: f.values for i, f in enumerate(self._factors(emask))}
        max_seen = 0
        for selected, rest, union, v, new_id, new_scope in self._elim_steps:
            # Contract directly as a tensor network.  Operand axes are
            # reversed because flat factor indices are little-endian.  The
            # output labels are reversed in the same way, so flattening gives
            # the new little-endian factor index without a large gather map.
            where = {x: i for i, x in enumerate(union)}
            args = []
            for fid in selected:
                scope = self._factor_scopes[fid]
                tensor = factors[fid].reshape((2,) * len(scope))
                args.extend((tensor, [where[x] for x in reversed(scope)]))
            args.append([where[x] for x in reversed(new_scope)])
            reduced = np.einsum(*args, optimize=True).reshape(-1)
            for fid in selected:
                del factors[fid]
            factors[new_id] = reduced
            max_seen = max(max_seen, len(union) - 1)
            if max_seen > MAX_WIDTH:
                raise ValueError(f"runtime elimination width {max_seen} exceeds limit {MAX_WIDTH}")
        # Remaining factors have only active variables.  Their product is the
        # effective Fourier factor H(z_active) = sum_{z_inactive} prod chi.
        final_factors = [Factor(self._factor_scopes[fid], factors[fid])
                         for fid in self._final_factor_ids]
        union = self.active_vars
        out = _factor_product(final_factors, union)
        if self._missing_inactive:
            out *= float(1 << self._missing_inactive)
        return np.asarray(out, dtype=np.float64), max_seen

    def _one_mask(self, emask: int):
        import numpy as np

        h, width = self.eliminate(emask)
        scale = math.ldexp(1.0, -self.n_variables)
        # The first quantum column is acceptance; the remaining columns are
        # the decoder Pauli expectation functions.
        a = float(np.dot(h, self.quantum_hat[:, 0]) * scale)
        q = np.asarray([np.dot(h, self.quantum_hat[:, 1 + j]) * scale
                        for j in range(self.n_quantum)], dtype=np.float64)
        return emask, a, q, width

    def evaluate(self):
        t0 = time.monotonic()
        jobs = list(self.emasks)
        global _WORKER
        _WORKER = self
        if self.procs > 1 and len(jobs) > 1:
            with mp.get_context("fork").Pool(self.procs) as pool:
                rows = pool.map(_worker_mask, jobs, chunksize=1)
        else:
            rows = [self._one_mask(x) for x in jobs]
        by_mask = {r[0]: r for r in rows}
        _, acceptance, _q0, _ = by_mask[0]
        numerator = 0.5 * acceptance
        for j, coeff in enumerate(self.qcoeff):
            numerator -= 0.5 * float(coeff) * float(by_mask[self.qmasks[j]][2][j])
        loss = numerator / acceptance
        return {
            "loss": float(loss),
            "numerator": float(numerator),
            "acceptance": float(acceptance),
            "width": int(max(r[3] for r in rows)),
            "active_variables": self.K,
            "rotation_variables": self.n_rot,
            "active_detectors": len(self.active_det),
            "channels": len(self.m.chans),
            "faults": len(self.m.faults),
            "seconds": time.monotonic() - t0,
        }


_WORKER = None


def _worker_mask(emask: int):
    return _WORKER._one_mask(emask)


def third_order(ev):
    """The already validated exact-to-third-order reference contraction."""

    if moments is None:
        return float("nan")
    try:
        return float(moments.evaluate(ev)["total"])
    except (AssertionError, ValueError):
        return float("nan")


def brute_force_channels(ev, channels: list[int]):
    """Enumerate a small channel subset, for an independent validation check.

    This deliberately uses Engine.table directly rather than any Walsh code.
    It is intended for three or fewer channels (the categorical outcome count
    grows as 16**number_of_DEPOLARIZE2 channels).
    """

    import numpy as np

    # Outcomes are (signature s, d, e, probability).  No-fault is one
    # categorical outcome, so exclusive Paulis cannot be double-counted.
    states = {(0, 0, 0): 1.0}
    for c in channels:
        ch = ev.m.chans[c]
        outs = [(0, 0, 0, 1.0 - float(ch["prob"]))]
        for f in ev.m.faults:
            if f["chan"] == c:
                outs.append((int(f["s"]), int(f["d"]), int(f["e"]), float(f["p"])))
        new = collections.defaultdict(float)
        for (s0, d0, e0), p0 in states.items():
            for s, d, e, pf in outs:
                new[(s0 ^ s, d0 ^ d, e0 ^ e)] += p0 * pf
        states = dict(new)
    coeff = np.asarray(ev.e.W * ev.e.beta, dtype=np.float64)
    masks = []
    for T, a, b in ev.e.keys:
        m = a | (b << 3) | (1 << 6)
        m |= (1 << 8) if T == "X" else ((1 << 7) | (1 << 9))
        masks.append(m)
    cache = {}
    den = num = 0.0
    for (s, d, e), p0 in states.items():
        key = (s, d)
        if key not in cache:
            table = ev.e.table(s, d)
            if table is None:
                cache[key] = (0.0, np.zeros(len(ev.e.keys)))
            else:
                a0, E = table
                cache[key] = (float(a0), np.asarray(E, dtype=np.float64))
        a0, E = cache[key]
        n0 = 0.5 * (a0 - float(np.sum(coeff * np.asarray(
            [(-1.0 if (e & m).bit_count() & 1 else 1.0) * x for m, x in zip(masks, E)]))))
        den += p0 * a0
        num += p0 * n0
    return num / den, den, num, len(states)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("qasm")
    ap.add_argument("--json", default=None)
    ap.add_argument("--procs", type=int, default=1)
    ap.add_argument("--p", type=float, default=1e-3)
    a = ap.parse_args(argv)
    qasm = Path(a.qasm)
    jf = Path(a.json) if a.json else qasm.with_suffix(".json")
    data = json.loads(jf.read_text())["data_qubits"]
    text = qasm.read_text()

    t0 = time.monotonic()
    w = WalshEvaluator(text, data, p=a.p, procs=a.procs)
    build_seconds = time.monotonic() - t0
    result = w.evaluate()
    result["build_seconds"] = build_seconds
    t3 = third_order(w.ev)
    result["third_order"] = t3
    print(f"circuit {qasm}: {result['channels']} channels, {result['faults']} faults, "
          f"{result['rotation_variables']} rotation variables, {result['active_detectors']} "
          f"nontrivial projectors, elimination width {result['width']}")
    print(f"all-orders 1-F = {result['loss']:.10e}  acceptance = {result['acceptance']:.10f}")
    if math.isfinite(t3):
        print(f"third-order truncation = {t3:.10e}")
    else:
        print("third-order truncation = unavailable (exact2/moments requires c1 = 0)")
    print(f"runtime = {result['seconds'] + build_seconds:.1f}s "
          f"(build {build_seconds:.1f}s, elimination {result['seconds']:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
