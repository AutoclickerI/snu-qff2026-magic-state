#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Exact first-order danger scorer for block-A encoders with X-basis flags.

This is a private extension of :func:`work.lanes.DR.synth.dangerous_z`; the
DR source is deliberately not imported or edited.  ``layers`` is the final
CX-only timeline (one matching per layer), including flag CNOTs.  A flag is a
dict ``{"cell": f, "q": q, "t1": s1, "t2": s2}``, where ``t1``/``t2`` are
physical slots including the one RX-preparation slot.  Thus the corresponding
CX layers are ``t1-1`` and ``t2-1``.  FLAG's ``build_flagged_layers`` emits
this convention and appends a one-step MX after the CX timeline.

The score is a sum over one fault.  CX Pauli faults have weight p/15, idle
Paulis p/3, and pivot/flag RX faults p.  A fault is removed from danger when
any flag's final X-basis record flips (a Z/Y on that flag immediately before
MX); measurement flips are likewise detected.  Data danger is the same
``Z_L x (weight <= 1)`` class and invisible X syndrome used by
``synth.dangerous_z``.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any


# The seven code cells are supplied by callers.  These are Steane parity
# checks in code-position order, matching DR/synth.py.
HAM_POS = ((0, 2, 4, 6), (1, 2, 5, 6), (3, 4, 5, 6))


def z_class(zset: Iterable[int], cells: Sequence[int]) -> int:
    """Return 1 exactly for a Z_L times a weight-at-most-one class."""
    zset = set(zset)
    e = [int(q in zset) for q in cells]
    syn = sum(1 << k for k, S in enumerate(HAM_POS) if sum(e[i] for i in S) & 1)
    w = sum(e)
    w_min = 0 if syn == 0 else 1
    return (w - w_min) & 1


def x_syndrome(xset: Iterable[int], cells: Sequence[int]) -> int:
    xset = set(xset)
    e = [int(q in xset) for q in cells]
    return sum(1 << k for k, S in enumerate(HAM_POS) if sum(e[i] for i in S) & 1)


def _danger_bin(zset: set[int], xset: set[int], cells: Sequence[int]) -> int | None:
    """Return the EXENC danger-vector bin, or None.

    For a dangerous Z class, the syndrome is the Hamming column of the
    residual weight-one error.  Columns are 1..7, with 0 the pure logical
    class.  This is exactly the integer ``zz & 7`` used by EXENC's independent
    scorer, while avoiding any signature assumptions for flag ancillas.
    """
    cset = set(cells)
    if x_syndrome(xset & cset, cells):
        return None
    if not z_class(zset & cset, cells):
        return None
    syn = 0
    e = [int(q in zset) for q in cells]
    for k, S in enumerate(HAM_POS):
        if sum(e[i] for i in S) & 1:
            syn |= 1 << k
    return syn


def _normalise_flags(flags: Iterable[Mapping[str, Any]] | None,
                     cells: Sequence[int], T: int) -> list[dict[str, int]]:
    out: list[dict[str, int]] = []
    seen: set[int] = set()
    for raw in flags or ():
        try:
            f = int(raw["cell"])
            q = int(raw["q"])
            t1 = int(raw["t1"])
            t2 = int(raw["t2"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid flag specification: {raw!r}") from exc
        # t1/t2 include prep at physical slot 0.  FLAG's builder always emits
        # 1 <= t1 < t2 <= T+1; requiring the same here catches stale windows.
        if t1 < 1 or t2 <= t1 or t2 > T:
            raise ValueError(f"flag window must satisfy 1 <= t1 < t2 <= {T}: {raw!r}")
        if f in seen:
            raise ValueError(f"flag cells must be distinct: {f}")
        if f in cells:
            raise ValueError(f"flag cell {f} is a block cell")
        seen.add(f)
        out.append({"cell": f, "q": q, "t1": t1, "t2": t2,
                    "layer_t1": t1 - 1, "layer_t2": t2 - 1})
    return out


def score_flagged(layers: Sequence[Sequence[Sequence[int]]],
                  pivots: Sequence[int], cells: Sequence[int],
                  avail: Iterable[int] = (),
                  flags: Iterable[Mapping[str, Any]] | None = None,
                  p: float = 1e-3, *, return_events: bool = False) -> dict[str, Any]:
    """Score all single faults in a final encoder/flag CX timeline.

    ``layers`` contains only CX layers.  Flag prep and MX are one-step events
    outside this list; the former is immediately before physical slot 1, and
    the latter immediately after the final CX layer.  This convention gives
    exactly the baseline ``synth.dangerous_z`` result when ``flags=[]``.
    """
    cells = tuple(int(q) for q in cells)
    if len(cells) != 7 or len(set(cells)) != 7:
        raise ValueError("cells must contain seven distinct code cells")
    L = [[(int(e[0]), int(e[1])) for e in layer] for layer in layers]
    if any(not layer for layer in L):
        raise ValueError("layers must contain no empty layers")
    T = len(L)
    fs = _normalise_flags(flags, cells, T) if flags else []
    f_cells = {f["cell"] for f in fs}
    all_avail = set(int(q) for q in avail) | set(cells) | f_cells
    all_avail |= {q for layer in L for e in layer for q in e}
    # Presence/topology validation is intentionally lightweight; the search
    # builder performs grid checks.  Keeping this scorer generic lets Stim
    # validation feed the exact same timeline.
    all_avail = sorted(all_avail)

    first: dict[int, int] = {}
    last: dict[int, int] = {}
    for t, layer in enumerate(L):
        used: set[int] = set()
        for u, v in layer:
            if u == v:
                raise ValueError("CX cannot have equal endpoints")
            if used & {u, v}:
                raise ValueError(f"layer {t} is not a matching")
            used.update((u, v))
            for q in (u, v):
                first.setdefault(q, t)
                last[q] = t
    # As in synth.dangerous_z, code cells are available from the encoder's
    # initial reset even if they have no CX in a particular schedule.
    for q in cells:
        first.setdefault(q, 0)
    # A flag is prepared before layer 0 and is live until MX after layer T-1.
    # Setting first=0 makes its wait before t1 receive the judge's idle noise;
    # its last operation is intentionally not used to truncate waits because
    # the flag is still live until the final MX event.
    for f in f_cells:
        first.setdefault(f, 0)

    def propagate(z: set[int], x: set[int], t0: int) -> tuple[set[int], set[int]]:
        z, x = set(z), set(x)
        for layer in L[t0:]:
            for u, v in layer:
                if u in x:
                    x ^= {v}
                if v in z:
                    z ^= {u}
        return z, x

    # We record integer weights in p/15 units, exactly as EXENC's score().
    weights = [0] * 8
    detected_units = 0
    event_rows: list[dict[str, Any]] = []

    def add(z: set[int], x: set[int], weight: int, label: str,
            *, explicit_detected: bool = False) -> None:
        nonlocal detected_units
        detect = explicit_detected or any(f in z for f in f_cells)
        b = _danger_bin(z, x, cells)
        dangerous = b is not None
        if detect:
            detected_units += weight
        if dangerous and not detect:
            weights[b] += weight
        if return_events:
            event_rows.append({"label": label, "weight_units": weight,
                               "detected": detect, "dangerous": dangerous,
                               "bin": b})

    # Encoder and flag CX depolarizing faults.  Faults occur immediately after
    # the gate, hence propagation starts at the following layer.
    for t, layer in enumerate(L):
        for gi, (u, v) in enumerate(layer):
            for pu in "IXYZ":
                for pv in "IXYZ":
                    if pu == pv == "I":
                        continue
                    z = {q for q, P in ((u, pu), (v, pv)) if P in "YZ"}
                    x = {q for q, P in ((u, pu), (v, pv)) if P in "XY"}
                    zz, xx = propagate(z, x, t + 1)
                    add(zz, xx, 1, f"cx@{t}:{gi}:{pu}{pv}")

    # Idle DEPOLARIZE1 before every CX layer.  For ordinary helper qubits we
    # retain synth.dangerous_z's deliberate truncation after their last gate;
    # flags are exceptions because MX happens only after the whole timeline.
    busy_by_t = [set(q for e in layer for q in e) for layer in L]
    for t, busy in enumerate(busy_by_t):
        for q in all_avail:
            if q in busy or first.get(q, T) >= t:
                continue
            if q not in cells and q not in f_cells and t > last.get(q, -1):
                continue
            for P in "XYZ":
                z = {q} if P in "YZ" else set()
                x = {q} if P in "XY" else set()
                zz, xx = propagate(z, x, t)
                add(zz, xx, 5, f"idle@{t}:{q}:{P}")

    # Pivot reset/RX faults.  Existing synth/exenc semantics charge only the
    # pivots (the |+> inputs), with a Z error of probability p immediately
    # before their first layer.  Empty circuits still charge each pivot.
    for q in pivots:
        t0 = first.get(int(q), 0)
        zz, xx = propagate({int(q)}, set(), t0)
        add(zz, xx, 15, f"pivot_prep:{q}")

    # Every flag RX carries one Z_ERROR(p).  It is immediately before layer 0;
    # a Z on a control remains on the flag and therefore fires MX unless it is
    # cancelled by a later error (there is no second fault in this model).
    for f in f_cells:
        zz, xx = propagate({f}, set(), 0)
        add(zz, xx, 15, f"flag_prep:{f}")

    # MX record flips are faults of probability p.  They are detected by the
    # very flag whose record is flipped and cannot create a data danger with a
    # single fault.  Keep them in the optional event stream for end-to-end
    # fault audits; they do not contribute to ``danger_units``.
    if return_events:
        for f in f_cells:
            add(set(), set(), 15, f"flag_measure:{f}", explicit_detected=True)

    danger_units = sum(weights)
    out: dict[str, Any] = {
        "danger_units": danger_units,
        "danger_vector_units": weights,
        "danger": danger_units * p / 15.0,
        "danger_pure_logical": weights[0] * p / 15.0,
        "danger_per_qubit": [w * p / 15.0 for w in weights[1:]],
        "detected_units": detected_units,
        "flags": [{k: f[k] for k in ("cell", "q", "t1", "t2")} for f in fs],
    }
    if return_events:
        out["events"] = event_rows
    return out


# Alias used by a few local scripts.
dangerous_z = score_flagged


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) not in (3, 4):
        raise SystemExit("usage: flag_scorer.py <circuit.json> <cells csv> [flags.json]")
    circ = json.loads(open(sys.argv[1]).read())
    cells = [int(x) for x in sys.argv[2].replace(",", " ").split()]
    fs = json.loads(open(sys.argv[3]).read()) if len(sys.argv) == 4 else []
    print(json.dumps(score_flagged(circ["ops"], circ["pivots"], cells, cells, fs), indent=2))
