#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Validate the FLAG single-fault classification with Stim.

The FLAG scorer works on a layered CSS Pauli model.  This file is an independent
check of that model: it builds the encoder and the optional flag CNOTs, injects
each individual prep, CNOT, idle, or measurement fault, and runs a fresh Stim
tableau simulation.  A fault is detected iff one of the final MX outcomes is
different from the noiseless outcome.  The Pauli propagation used for the
dangerous classification is deliberately kept local (``synth.py`` is not
modified).

Usage::

    .venv/bin/python work/lanes/FLAG/validate_stim.py \
        work/lanes/FLAG/prepA_L5_flag1.json

``flags`` entries use the required format ``cell, q, t1, t2``.  ``t1`` and
``t2`` are zero-based encoder-CX layer indices, as in the FLAG scorer.  The
flag prep happens before layer zero and the MX readout after the last layer.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import stim


CELLS = [1, 14, 8, 9, 2, 16, 15]
COLS = 6
HAM_POS = [[0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6]]


def z_class(zset: set[int], cells: list[int]) -> int:
    e = [int(q in zset) for q in cells]
    syn = sum(1 << k for k, s in enumerate(HAM_POS) if sum(e[i] for i in s) & 1)
    return (sum(e) - (0 if syn == 0 else 1)) & 1


def x_syndrome(xset: set[int], cells: list[int]) -> int:
    e = [int(q in xset) for q in cells]
    return sum(1 << k for k, s in enumerate(HAM_POS) if sum(e[i] for i in s) & 1)


def nbrs(q: int) -> set[int]:
    r, c = divmod(q, COLS)
    return {rr * COLS + cc for rr, cc in ((r - 1, c), (r + 1, c),
                                           (r, c - 1), (r, c + 1))
            if 0 <= rr < 6 and 0 <= cc < 6}


@dataclass(frozen=True)
class Event:
    """One deterministic component of one judge noise channel.

    ``start`` is the first encoder layer after the Pauli is applied.  For an
    idle event the Pauli is before that layer; for a CNOT event it is after the
    CNOT's layer.  ``kind`` is used solely for reporting and for fault weights.
    """

    label: str
    kind: str
    start: int
    pauli: tuple[tuple[int, str], ...]
    flags: tuple[int, ...] = ()
    measurement_flip: bool = False


def _propagate(event: Event, layers: list[list[tuple[int, int]]]) -> tuple[set[int], set[int]]:
    z: set[int] = set()
    x: set[int] = set()
    for q, p in event.pauli:
        if p in "ZY":
            z.add(q)
        if p in "XY":
            x.add(q)
    for layer in layers[event.start:]:
        for u, v in layer:
            if u in x:
                x ^= {v}
            if v in z:
                z ^= {u}
    return z, x


def _put_pauli(sim: stim.TableauSimulator, pauli: Iterable[tuple[int, str]]) -> None:
    for q, p in pauli:
        if p == "X":
            sim.x(q)
        elif p == "Y":
            sim.y(q)
        elif p == "Z":
            sim.z(q)
        else:
            raise ValueError(p)


def _layers(circuit: dict) -> tuple[list[list[tuple[int, int]]], list[dict], int]:
    """Return base CX layers with flags overlaid and the final MX layer.

    The JSON's ``t1/t2`` indices refer to the encoder layers (zero based).  A
    flag CNOT is required to occupy a free slot in its block-qubit layer.  The
    scorer inserts/retimes layers before emitting JSON, so an overlap here is a
    malformed candidate and is rejected rather than silently changing it.
    """
    base = [[tuple(map(int, e)) for e in layer] for layer in circuit["ops"]]
    flags = list(circuit.get("flags", []))
    if not flags:
        return base, flags, len(base)
    layers = [list(layer) for layer in base]
    for f in flags:
        for key in ("cell", "q", "t1", "t2"):
            if key not in f:
                raise ValueError(f"flag is missing {key}: {f}")
        q, cell = int(f["q"]), int(f["cell"])
        if cell not in nbrs(q) or cell in CELLS:
            raise ValueError(f"flag cell {cell} is not a free neighbour of q={q}")
        for t in (int(f["t1"]), int(f["t2"])):
            if not (0 <= t < len(layers)):
                raise ValueError(f"flag time {t} outside encoder depth {len(layers)}")
            used = {a for e in layers[t] for a in e}
            if q in used or cell in used:
                raise ValueError(f"flag CX {(cell, q)} collides at layer {t}: {layers[t]}")
            layers[t].append((cell, q))
    for t, layer in enumerate(layers):
        used = [q for e in layer for q in e]
        if len(used) != len(set(used)):
            raise ValueError(f"non-disjoint layer {t}: {layer}")
    return layers, flags, len(layers)


def _events(circuit: dict, layers: list[list[tuple[int, int]]], flags: list[dict]) -> list[Event]:
    cells = set(CELLS)
    pivots = {int(q) for q in circuit["pivots"]}
    f_cells = {int(f["cell"]) for f in flags}
    ev: list[Event] = []

    # Native reset+H (RX) has a Z prep flip; ordinary reset has an X flip.
    for q in sorted(cells | f_cells):
        p = "Z" if q in pivots or q in f_cells else "X"
        kind = "flag_prep" if q in f_cells else "prep"
        ev.append(Event(f"{kind}:{q}:{p}", kind, 0, ((q, p),),
                        tuple(sorted(f_cells)) if q in f_cells else ()))

    # CNOT depolarisation: all non-II two-qubit Paulis, one event each.
    for t, layer in enumerate(layers):
        for j, (u, v) in enumerate(layer):
            is_flag = any({u, v} == {int(f["cell"]), int(f["q"])} for f in flags)
            k = "flag_cx" if is_flag else "cx"
            for pu in "IXYZ":
                for pv in "IXYZ":
                    if pu == pv == "I":
                        continue
                    pauli = tuple((q, p) for q, p in ((u, pu), (v, pv)) if p != "I")
                    ev.append(Event(f"{k}:{t}:{j}:{pu}{pv}", k, t + 1, pauli))

    # One DEPOLARIZE1 Pauli per waiting layer.  Block qubits are live from
    # layer zero through the end; flag cells are live from prep through t2.
    last: dict[int, int] = {}
    first: dict[int, int] = {q: 0 for q in cells | f_cells}
    for t, layer in enumerate(layers):
        for u, v in layer:
            last[u] = last[v] = t
    for f in flags:
        last[int(f["cell"])] = max(int(f["t1"]), int(f["t2"]))
    for t, layer in enumerate(layers):
        busy = {q for e in layer for q in e}
        for q in sorted(cells | f_cells):
            if q in busy or first[q] >= t:
                continue
            if q in f_cells and t > last.get(q, -1):
                continue
            for p in "XYZ":
                ev.append(Event(f"idle:{t}:{q}:{p}", "idle", t, ((q, p),)))

    # MX is measured after the last encoder layer.  Its readout flip is a Z
    # before the X measurement; it is represented directly as a flag toggle.
    for f in flags:
        q = int(f["cell"])
        ev.append(Event(f"flag_meas:{q}", "flag_meas", len(layers), (),
                        (q,), measurement_flip=True))
    return ev


def _detected(event: Event, layers: list[list[tuple[int, int]]], flags: list[dict]) -> bool:
    if event.measurement_flip:
        return True
    z, _ = _propagate(event, layers)
    return any(f in z for f in event.flags)


def _dangerous(event: Event, layers: list[list[tuple[int, int]]], detected: bool) -> bool:
    if detected:
        return False
    z, x = _propagate(event, layers)
    return bool(z_class(z & set(CELLS), CELLS)) and x_syndrome(x & set(CELLS), CELLS) == 0


def _stim_flags(circuit: dict, layers: list[list[tuple[int, int]]], flags: list[dict], fault: Event | None) -> tuple[int, ...]:
    """Run one noiseless Stim circuit with exactly ``fault`` injected."""
    sim = stim.TableauSimulator()
    # Every qubit in the 6x6 grid exists, including free flag cells.
    sim.set_num_qubits(36)
    cells = set(CELLS)
    f_cells = {int(f["cell"]) for f in flags}
    pivots = {int(q) for q in circuit["pivots"]}
    prep: list[tuple[int, str]] = []
    for q in sorted(cells | f_cells):
        sim.reset(q)
        if q in pivots or q in f_cells:
            sim.h(q)
        p = "Z" if q in pivots or q in f_cells else "X"
        prep.append((q, p))
    if fault is not None and fault.kind in ("prep", "flag_prep"):
        _put_pauli(sim, fault.pauli)
    for t, layer in enumerate(layers):
        # Idle noise is before this layer.
        if fault is not None and fault.kind == "idle" and fault.start == t:
            _put_pauli(sim, fault.pauli)
        for j, (u, v) in enumerate(layer):
            sim.cnot(u, v)
            if (fault is not None and fault.kind in ("cx", "flag_cx")
                    and fault.start == t + 1 and fault.label.split(":")[2] == str(j)):
                _put_pauli(sim, fault.pauli)
    out = []
    for f in flags:
        q = int(f["cell"])
        if fault is not None and fault.kind == "flag_meas" and fault.pauli == () and q in fault.flags:
            ps = stim.PauliString(36)
            ps[q] = "X"
            out.append(1 ^ int(sim.measure_observable(ps)))
        else:
            ps = stim.PauliString(36)
            ps[q] = "X"
            out.append(int(sim.measure_observable(ps)))
    return tuple(out)


def validate(path: Path) -> dict:
    circuit = json.loads(path.read_text())
    layers, flags, depth = _layers(circuit)
    events = _events(circuit, layers, flags)
    clean = _stim_flags(circuit, layers, flags, None)
    rows = []
    for e in events:
        pred = _detected(e, layers, flags)
        got = tuple(a ^ b for a, b in zip(_stim_flags(circuit, layers, flags, e), clean))
        stim_detected = any(got)
        if pred != stim_detected:
            raise AssertionError(f"Stim mismatch for {e.label}: propagated={pred}, Stim={got}")
        dangerous = _dangerous(e, layers, flags and pred)
        rows.append({"label": e.label, "kind": e.kind, "detected": pred, "dangerous": dangerous})
    units = sum((1 if r["kind"] in ("cx", "flag_cx") else 5 if r["kind"] == "idle" else 15)
                for r in rows if r["dangerous"])
    detected = sum(r["detected"] for r in rows)
    result = {"circuit": str(path), "depth": depth, "flags": flags,
              "events": len(events), "detected": detected,
              "dangerous_events": sum(r["dangerous"] for r in rows),
              "danger_units": units, "stim_clean_flags": clean,
              "rows": rows}
    out = path.with_name(path.stem + "_stim_validation.json")
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("depth", "flags", "events", "detected", "dangerous_events", "danger_units", "stim_clean_flags")}))
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("json", type=Path)
    args = ap.parse_args()
    validate(args.json.resolve())


if __name__ == "__main__":
    main()
