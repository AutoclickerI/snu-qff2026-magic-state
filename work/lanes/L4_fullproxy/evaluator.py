"""Fast full-circuit loss proxies for QFF2026 schedules.

The recommended evaluator accepts the complete submitted circuit, extracts the final
Clifford cycle after the fourteen cultivation records, and applies the existing Stim
detector-error-model pair calculation with a calibrated accepted pre-cycle depolarizing
mass.  This avoids pretending that the non-Clifford cultivation stages have a valid
ordinary detector error model.  The file also retains an experimental T-to-S surrogate
helper for reproducibility; it is not used by :func:`evaluate` because its output
observables are non-deterministic on the full circuit.

This module intentionally imports the work-tree builders read-only.  The public entry
point is ``evaluate(text, data_qubits)`` and accepts the same QASM text as ``tprep.check``.
"""

from __future__ import annotations

import functools
import re
import time

import stim

from tprep.noise import STANDARD, apply_noise
from tprep.qasm import to_stim

import cultiv_port as cp
import proxy2


_T = re.compile(r"^(T|T_DAG)(?:\s|\()")


def _s_surrogate(stim_text: str, inverse: bool = False) -> str:
    """Replace non-Clifford T gates in Stim text by Clifford S gates.

    ``inverse`` is useful for ports whose source S/S_DAG convention was mapped to
    T/T_DAG with the opposite direction (the QFF cultivation port does this for
    ``s_to='Tswap'``).
    """
    out = []
    for line in stim_text.splitlines():
        if line.startswith("T ") or line.startswith("T("):
            out.append(("S_DAG" if inverse else "S") + line[1:])
        elif line.startswith("T_DAG ") or line.startswith("T_DAG("):
            out.append(("S" if inverse else "S_DAG") + line[5:])
        else:
            out.append(line)
    return "\n".join(out) + ("\n" if stim_text.endswith("\n") else "")


def _mpp(basis, qs):
    return "MPP " + "*".join(f"{basis}{q}" for q in qs)


def _wrapped(full_noisy: str, logical: str) -> tuple[stim.Circuit, int]:
    """Add final code stabilizer/single logical measurements to a noisy full circuit.

    Existing circuit DETECTOR lines are retained in place.  The six final stabilizer
    records are direct detectors and are the lookup syndrome; the final logical record is
    observable 0.  The returned integer is the number of final detectors.
    """
    stabs = [("X", s) for s in proxy2.SUPPORT] + [("Z", s) for s in proxy2.SUPPORT]
    body = [l for l in full_noisy.splitlines() if not l.startswith("OBSERVABLE")]
    body.extend(_mpp(b, s) for b, s in stabs)
    body.append(_mpp(logical, proxy2.DATA))
    # Final stabilizer detectors are direct records.  Their order is X0..X2,Z0..Z2.
    body.extend("DETECTOR rec[-%d]" % (6 - i) for i in range(6))
    body.append("OBSERVABLE_INCLUDE(0) rec[-1]")
    return stim.Circuit("\n".join(body)), 6


def _cycle_only_from_full(text: str, q_in: float):
    """Build the existing cycle DEM wrapper from the suffix after the fourteen prep records.

    The cultivation port writes fourteen measurements before the final cycle.  Cutting after
    their detector lines leaves the cycle's own measurements/detectors and avoids pretending
    that the non-Clifford preparation is a stabilizer circuit.  ``q_in`` is a uniform input
    depolarizing mass standing for accepted pre-cycle faults.
    """
    clean, errors = to_stim(text)
    if errors:
        raise ValueError("QASM conversion failed: " + "; ".join(errors))
    lines = clean.splitlines()
    seen = 0
    cut = None
    for i, line in enumerate(lines):
        raw = line.split("#", 1)[0].strip()
        if raw.startswith(("M ", "MX ")):
            # Stim's measurement lines can contain multiple targets; these circuits use one.
            seen += len(raw.split()) - 1
            if seen >= 14:
                cut = i + 1
                while cut < len(lines) and lines[cut].startswith("DETECTOR"):
                    cut += 1
                break
    if cut is None:
        raise ValueError("expected fourteen cultivation measurements before the cycle")
    suffix = lines[cut:]
    # Drop any OBSERVABLE declarations from the submission; the proxy supplies its own.
    suffix = [l for l in suffix if not l.startswith("OBSERVABLE")]
    # Parse the cycle measurements and its six parity detectors before adding noise.
    # Extra cat members are assigned to a tile by the qubit they read.
    qtile = {1: 0, 2: 0, 13: 1, 14: 1, 9: 2, 10: 2, 19: 1, 16: 2}
    rec_meta = []
    detector_groups = []
    nrec = 0
    for line in suffix:
        raw = line.split("#", 1)[0].strip()
        if raw.startswith(("M ", "MX ")):
            name, *args = raw.split()
            for a in args:
                rec_meta.append((int(a), name))
            nrec += len(args)
        elif raw.startswith("DETECTOR"):
            refs = []
            for tok in raw.split()[1:]:
                if tok.startswith("rec[-"):
                    refs.append(nrec - int(tok[5:-1]))
            detector_groups.append(refs)
    if len(detector_groups) < 6:
        raise ValueError(f"expected six cycle detectors, found {len(detector_groups)}")
    # Classify each parity by tile and readout basis, then order X0..X2,Z0..Z2.
    by_syndrome = {}
    for refs in detector_groups[-6:]:
        if not refs:
            continue
        qs = [rec_meta[j][0] for j in refs]
        names = [rec_meta[j][1] for j in refs]
        t = qtile.get(qs[0])
        if t is None:
            raise ValueError(f"unmapped cycle readout qubit(s): {qs}")
        basis = "X" if names[0] == "MX" else "Z"
        syn = t if basis == "X" else 3 + t
        by_syndrome[syn] = refs
    if set(by_syndrome) != set(range(6)):
        raise ValueError(f"cycle detector classification incomplete: {sorted(by_syndrome)}")
    suffix_body = [l for l in suffix if not l.split("#", 1)[0].strip().startswith("DETECTOR")]
    data = proxy2.DATA
    prefix = ["I " + " ".join(map(str, data))]
    body = prefix + suffix_body
    noisy = apply_noise("\n".join(body), 1e-3, STANDARD)
    meas = []
    for line in noisy.splitlines():
        name, *args = line.split("#", 1)[0].split()
        if name in ("M", "MX"):
            meas.extend((int(a), name) for a in args)
    stabs = [("X", s) for s in proxy2.SUPPORT] + [("Z", s) for s in proxy2.SUPPORT]
    initial = [_mpp(B, s) for B, s in stabs] + [_mpp("X", data)]
    final_x = [_mpp(B, s) for B, s in stabs] + [_mpp("X", data)]
    final_z = [_mpp(B, s) for B, s in stabs] + [_mpp("Z", data)]
    total = 7 + nrec + 7

    def ref_mid(j):
        return f"rec[-{total - (7 + j)}]"

    def ref_initial(j):
        return f"rec[-{total - j}]"

    def make(final, initial_logical):
        out = [_mpp(B, s) for B, s in stabs] + [_mpp(initial_logical, data)]
        if q_in:
            out.append(f"DEPOLARIZE1({q_in}) " + " ".join(map(str, data)))
        out += noisy.splitlines()
        out += final
        for syn in range(6):
            out.append("DETECTOR " + " ".join([*(ref_mid(j) for j in by_syndrome[syn]), ref_initial(syn)]))
        # Match proxy2's convention: observables 0..5 are the final stabilizer
        # parities used by lookup correction, and observable 6 is the logical
        # parity.  proxy2.loss then applies the syndrome to the logical bit.
        for k in range(6):
            out.append(f"OBSERVABLE_INCLUDE({k}) rec[-{7-k}] {ref_initial(k)}")
        out.append(f"OBSERVABLE_INCLUDE(6) rec[-1] {ref_initial(6)}")
        return stim.Circuit("\n".join(out))

    return make(final_x, "X"), make(final_z, "Z")


def _loss(circuit: stim.Circuit, n_final_detectors: int = 6, logical_cost: str = "X"):
    """First/second-order loss from a DEM with full detector signatures."""
    dem = circuit.detector_error_model(decompose_errors=False, approximate_disjoint_errors=True)
    groups = {}
    for inst in dem.flattened():
        if inst.type != "error":
            continue
        p = float(inst.args_copy()[0])
        dets = []
        obs = 0
        for target in inst.targets_copy():
            if target.is_relative_detector_id():
                dets.append(target.val)
            elif target.is_logical_observable_id():
                obs ^= 1 << target.val
        groups.setdefault(frozenset(dets), []).append((p, obs))
    nd = circuit.num_detectors
    # Final X checks correct Z-type (X observable); final Z checks correct X-type
    # (Z observable) in the same convention as proxy2.loss.
    if logical_cost == "X":
        syn_bits = sum(1 << (nd - 6 + i) for i in range(3))
    elif logical_cost == "Z":
        syn_bits = sum(1 << (nd - 3 + i) for i in range(3))
    else:
        raise ValueError(logical_cost)

    def flips(mask):
        return bool((mask & 1) ^ bool(mask & syn_bits))

    first = sum(p for p, m in groups.get(frozenset(), ()) if flips(m))
    second = 0.0
    for vals in groups.values():
        for i, (pi, mi) in enumerate(vals):
            for pj, mj in vals[i + 1:]:
                if flips(mi ^ mj):
                    second += pi * pj
    return first, second, len(groups), sum(len(v) for v in groups.values())


@functools.lru_cache(maxsize=64)
def _cached(text: str):
    """Build both logical DEMs; cache by exact submitted text."""
    clean, errors = to_stim(text)
    if errors:
        raise ValueError("QASM conversion failed: " + "; ".join(errors))
    # Noise is generated from the original circuit, then the Clifford surrogate is
    # applied to the complete noisy circuit.  This preserves the judge's idle schedule.
    noisy = apply_noise(clean, 1e-3, STANDARD)
    surrogate = _s_surrogate(noisy)
    cx, nf = _wrapped(surrogate, "X")
    cz, _ = _wrapped(surrogate, "Z")
    return cx, cz, nf


def evaluate(text, data_qubits, *, details=False):
    """Return the recommended calibrated full-circuit estimate of ``1-F``.

    The input is the complete submission text.  The evaluator extracts its final
    Clifford cycle, retains the judge's schedule-dependent STANDARD noise, and feeds
    a fixed accepted pre-cycle depolarizing mass ``q_in=0.001`` into the cycle DEM.
    This calibration was selected once from the recorded MC schedules; it is not a
    per-circuit fit.  The default return is a float; ``details=True`` returns the
    measured components and runtime.
    """
    return evaluate_cycle_proxy(text, data_qubits, q_in=0.001, details=details)


def evaluate_cycle_proxy(text, data_qubits, *, q_in=3e-3, details=False):
    """Evaluate the final cycle with a uniform accepted pre-cycle error mass.

    This is exposed separately because it is a useful control: it deliberately omits
    non-Clifford cultivation faults and is expected to be biased low on the full score.
    """
    del data_qubits
    t0 = time.perf_counter()
    cx, cz = _cycle_only_from_full(text, q_in)
    ax, bx = proxy2.loss(cx, 0b000111)
    az, bz = proxy2.loss(cz, 0b111000)
    val = ax + 0.5 * az + bx + 0.5 * bz
    if details:
        return {"estimate": val, "first": ax + 0.5 * az,
                "second": bx + 0.5 * bz, "x_first": ax, "x_second": bx,
                "z_first": az, "z_second": bz, "detectors": cx.num_detectors,
                "dem_groups": (None, None), "dem_errors": (None, None),
                "seconds": time.perf_counter() - t0, "q_in": q_in}
    return val


def evaluate_text(text, data_qubits):
    """Alias kept for callers that use the fast_check naming convention."""
    return evaluate(text, data_qubits)

