#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Exhaustive one/two-flag search for the block-A encoder.

This module keeps all flag work under ``work/lanes/FLAG``.  A flag window is
specified in *base encoder layer* coordinates: boundary ``i`` means just
before base layer ``i`` (``i == depth`` means after the last layer).  The
flag CNOT is put in that slot when its target is idle.  When the target is
busy, a dedicated layer is inserted immediately before the base layer.  Base
layer order is otherwise unchanged.  Consequently each flag has a precise
final timeline and a reproducible depth.

The scorer is intentionally imported from FLAG; it is a local extension of
``synth.dangerous_z`` and must not modify the DR implementation.
"""
from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
CELLS = [1, 14, 8, 9, 2, 16, 15]
FREE = set(range(36)) - set(CELLS)
COLS = 6


def neighbours(q: int) -> list[int]:
    r, c = divmod(q, COLS)
    return [rr * COLS + cc for rr, cc in ((r - 1, c), (r + 1, c),
                                            (r, c - 1), (r, c + 1))
            if 0 <= rr < 6 and 0 <= cc < COLS]


def flag_cells(q: int) -> list[int]:
    """Free grid cells adjacent to code cell ``q``."""
    return [f for f in neighbours(q) if f in FREE]


def _busy(layer: Iterable[tuple[int, int]]) -> set[int]:
    return {q for e in layer for q in e}


def build_flagged_layers(base: list[list[list[int]]], flags: list[dict]) -> tuple[list[list[tuple[int, int]]], list[dict]]:
    """Return ``(layers, normalized_flags)`` for one or two flag gadgets.

    ``base`` has encoder layers only.  Each flag dictionary contains ``cell``,
    ``q``, ``t1`` and ``t2`` in base-boundary coordinates.  The returned layer
    indices include the prep layer at index 0; flags' ``t1``/``t2`` are
    rewritten to those final indices.  Prep and MX are represented as events,
    not CX layers, so the CX timeline is ``[base + flag CNOTs]`` and its
    physical depth is ``len(layers)+2``.

    A slot can contain several flag CNOTs only when all pairs are disjoint.
    If a conflict exists, dedicated layers are emitted one at a time while
    preserving the input flag order.  This keeps every returned layer a valid
    matching on the grid, including two flags that share a target q.
    """
    base = [[(int(u), int(v)) for u, v in layer] for layer in base]
    flags = [dict(f) for f in flags]
    T = len(base)
    if not flags:
        return base, flags
    for f in flags:
        if f["cell"] not in FREE:
            raise ValueError(f"flag cell {f['cell']} is not free")
        if f["q"] not in CELLS or f["cell"] not in neighbours(f["q"]):
            raise ValueError(f"flag edge {f['cell']}->{f['q']} is not valid")
        if not 0 <= f["t1"] < f["t2"] <= T:
            raise ValueError(f"window out of range: {f}")
    if len({f["cell"] for f in flags}) != len(flags):
        raise ValueError("two flags must use distinct ancilla cells")

    # Keep operations as records until boundaries are expanded.  At each
    # boundary, flags targeting q-idle base layers are appended to that layer;
    # the rest are packed into as few dedicated matching layers as possible.
    gate_at: dict[int, list[tuple[int, int, int]]] = {}
    for fi, f in enumerate(flags):
        gate_at.setdefault(f["t1"], []).append((fi, 0, f["q"]))
        gate_at.setdefault(f["t2"], []).append((fi, 1, f["q"]))
    out: list[list[tuple[int, int]]] = []
    final_pos: dict[tuple[int, int], int] = {}
    for i in range(T + 1):
        orig = base[i] if i < T else None
        base_busy = _busy(orig or ())
        pending = list(gate_at.get(i, ()))

        # A gate may share a base layer iff both q and f are free and no other
        # pending gate in that layer touches either endpoint.
        augment: list[tuple[int, int, int]] = []
        dedicated: list[tuple[int, int, int]] = []
        used = set(base_busy)
        if orig is None:
            dedicated = pending
        else:
            for item in pending:
                fi, gi, q = item
                f = flags[fi]["cell"]
                if q in used or f in used:
                    dedicated.append(item)
                else:
                    augment.append(item)
                    used.update((f, q))

        # One or more dedicated matching layers precede the base layer.  We
        # greedily pack pairwise-disjoint gates; this is optimal for at most
        # two flags and deterministic for replay.
        while dedicated:
            layer: list[tuple[int, int]] = []
            used_d: set[int] = set()
            keep: list[tuple[int, int, int]] = []
            for item in dedicated:
                fi, gi, q = item
                f = flags[fi]["cell"]
                if q not in used_d and f not in used_d:
                    layer.append((f, q))
                    used_d.update((f, q))
                    final_pos[(fi, gi)] = len(out) + 1  # prep shifts by one
                else:
                    keep.append(item)
            out.append(layer)
            dedicated = keep

        if orig is not None:
            layer = list(orig)
            for fi, gi, q in augment:
                f = flags[fi]["cell"]
                layer.append((f, q))
                # final index includes a prep event at index zero
                final_pos[(fi, gi)] = len(out) + 1
            out.append(layer)
        else:
            # Boundary T has no base layer.  Dedicated gates were emitted
            # above; no empty layer is needed.
            pass

    for fi, f in enumerate(flags):
        f["t1"] = final_pos[(fi, 0)]
        f["t2"] = final_pos[(fi, 1)]
    return out, flags


def placements(base_depth: int) -> Iterable[dict]:
    """Yield all one-flag placements for a base circuit."""
    for q in CELLS:
        for cell in flag_cells(q):
            for t1 in range(base_depth):
                for t2 in range(t1 + 1, base_depth + 1):
                    yield {"cell": cell, "q": q, "t1": t1, "t2": t2}


def rank_key(r: dict) -> tuple:
    return (r["danger"], r["depth"], r["cx"],
            tuple((f["cell"], f["q"], f["t1"], f["t2"]) for f in r.get("flags", [])))


def pareto(rows: Iterable[dict]) -> list[dict]:
    """Return danger/depth Pareto points, ordered by depth then danger."""
    best = {}
    for r in rows:
        k = (r["depth"], r["danger"])
        old = best.get(k)
        if old is None or rank_key(r) < rank_key(old):
            best[k] = r
    out = []
    min_d = float("inf")
    for r in sorted(best.values(), key=lambda x: (x["depth"], x["danger"], x["cx"])):
        if r["danger"] < min_d - 1e-18:
            out.append(r)
            min_d = r["danger"]
    return out


def _score_one(args):
    """Worker entry point; ``flag_scorer`` import stays process-local."""
    ci, circuit, cells, avail, flags, mode = args
    from flag_scorer import score_flagged
    layers, ff = build_flagged_layers(circuit["ops"], flags)
    s = score_flagged(layers, circuit["pivots"], cells, avail, ff)
    row = dict(circuit)
    row.update(s)
    row["flags"] = ff
    row["candidate"] = ci
    row["cx"] = sum(map(len, layers))
    row["depth"] = len(layers) + 2
    row["flag_mode"] = mode
    return row


def run(candidates: list[dict], out: Path, workers: int = 16,
        pair: bool = True) -> dict:
    """Search candidates; return and write JSON summary under FLAG."""
    if not 1 <= workers <= 16:
        raise ValueError("workers must be between 1 and 16")
    jobs = []
    for ci, c in enumerate(candidates):
        T = len(c["ops"])
        one = list(placements(T))
        for f in one:
            jobs.append((ci, c, CELLS, CELLS, [f], 1))
        # For two flags, retain all ordered combinations of distinct ancillae
        # and canonicalize by (cell,q,t1,t2) to avoid swapping labels.
        if pair:
            for a, b in itertools.combinations(one, 2):
                if a["cell"] == b["cell"]:
                    continue
                jobs.append((ci, c, CELLS, CELLS, [a, b], 2))
    # Caller can use workers=1 for deterministic debugging.  A pool is needed
    # for the full candidate sweep; max worker count is constrained by AGENTS.
    with mp.Pool(processes=workers) as pool:
        rows = list(pool.imap_unordered(_score_one, jobs, chunksize=64))
    rows.sort(key=rank_key)
    summary = {"candidates": len(candidates), "placements": len(jobs),
               "pareto": pareto(rows), "best": rows[:20]}
    out.write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default="prepA_L5_flag_candidates.json")
    ap.add_argument("--out", default="prepA_L5_flag_search.json")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--no-pair", action="store_true")
    args = ap.parse_args()
    cpath = HERE / args.candidates
    candidates = json.loads(cpath.read_text())[:args.limit]
    result = run(candidates, HERE / args.out, args.workers, not args.no_pair)
    print(json.dumps({"candidates": result["candidates"],
                      "placements": result["placements"],
                      "pareto": len(result["pareto"])}))


if __name__ == "__main__":
    main()
