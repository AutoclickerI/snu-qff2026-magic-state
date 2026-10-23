"""Cycle-only direct single-basis readout prototypes.

This module is lane-local.  It imports the shared QASM/Stim helpers read-only and keeps the
prototype detector construction explicit: cat readout parities are stabilizer detectors, while
cat-verification records (when present) are zero-valued detectors.
"""
from __future__ import annotations

import itertools
import random
import sys
from dataclasses import dataclass

import stim

WORK = "/home/jihoon/competitions/quantumn/work"
if WORK not in sys.path:
    sys.path.insert(0, WORK)
import cultiv_port as cp
import proxy2
from qcirc import Circ, allow_any_coupling
from tprep.noise import STANDARD, apply_noise
from tprep.qasm import to_stim


DATA = list(proxy2.DATA)
TILES = proxy2.TILES
P = cp.phys
SUPPORT = proxy2.SUPPORT
allow_any_coupling()  # cycle-only prototypes deliberately ignore the grid.


@dataclass(frozen=True)
class Check:
    basis: str
    tile: int
    support: tuple[int, ...]


CHECKS = tuple([Check("X", t, tuple(ds)) for t, (_, ds) in enumerate(TILES)]
               + [Check("Z", t, tuple(ds)) for t, (_, ds) in enumerate(TILES)])


class DirectRound:
    """Construct one direct-readout final round on arbitrary coupling.

    ``kind='bare'`` uses one syndrome ancilla per check. ``kind='shor'`` uses four cat
    members, each touching one data qubit.  The default schedule is interleaved by time slot;
    all operations are separated by barriers so proxy idle noise is measured consistently.
    """

    def __init__(self, kind="shor", order=None, verify=False, cat_order=None):
        self.kind = kind
        self.verify = verify
        self.order = tuple(order or range(6))
        self.cat_order = cat_order or {}
        if sorted(self.order) != list(range(6)):
            raise ValueError("order must permute six checks")
        # use high-numbered free wires.  cp.DATA occupies seven of 0..35.
        free = [q for q in range(36) if q not in DATA]
        self.members = {}
        self.flags = {}
        self._alloc = iter(free)
        for ci in self.order:
            ch = CHECKS[ci]
            if kind == "bare":
                self.members[ci] = (next(self._alloc),)
            elif kind in ("shor", "flag2"):
                n = 4 if kind == "shor" else 2
                self.members[ci] = tuple(next(self._alloc) for _ in range(n))
                if verify:
                    # verification ancillas are allocated lazily below, after members.
                    self.flags[ci] = tuple()
            else:
                raise ValueError(kind)
        if verify and kind == "shor":
            # Three verifier wires are reset and reused for each check.  The direction/basis is
            # selected in emit; reuse keeps the prototype within the 36-wire judge model.
            verifiers = tuple(next(self._alloc) for _ in range(3))
            for ci in self.order:
                self.flags[ci] = verifiers
        self.groups = []                 # (cycle bits, reference syndrome or None)
        self.verify_groups = []          # direct zero detectors, for reporting

    def _barrier(self, c, used):
        c.barrier(*sorted(used))

    def _cat_prep(self, c, ch, qs, used):
        if self.kind == "bare":
            if ch.basis == "X":
                c.rx(qs[0])
            else:
                c.reset(qs[0])
            return
        # Prepare a four-member GHZ cat in the basis needed by the check.  Z checks use the
        # computational cat and Z readout; X checks use its Hadamard-rotated form and X readout.
        c.reset(*qs)
        c.h(qs[0])
        for q in qs[1:]:
            c.cx(qs[0], q)
        if ch.basis == "X":
            c.h(*qs)

    def _verify_cat(self, c, ch, qs, vs):
        if not self.verify:
            return
        for a, b, v in zip(qs[:-1], qs[1:], vs):
            if ch.basis == "X":
                # Measure Z_a Z_b with a target verifier in |0>.
                c.reset(v); c.cx(a, v); c.cx(b, v)
                bit = c.measure(v)
            else:
                # Measure X_a X_b with a control verifier in |+>.
                c.rx(v); c.cx(v, a); c.cx(v, b)
                bit = c.mx(v)
            self.verify_groups.append(bit)

    def emit(self, c: Circ, schedule=None):
        """Append the round and return ``(groups, used)``.

        A schedule is a list of check indices; with no schedule checks run as six consecutive
        blocks.  The explicit barriers make the result deterministic under judge idling.
        """
        self.groups = []
        self.verify_groups = []
        used = set(DATA)
        for qs in self.members.values():
            used.update(qs)
        for vs in self.flags.values():
            used.update(vs)
        self._barrier(c, used)
        schedule = tuple(self.order if schedule is None else schedule)
        if sorted(schedule) != list(range(6)):
            raise ValueError("schedule must permute six checks")
        for ci in schedule:
            ch = CHECKS[ci]
            qs = self.members[ci]
            self._cat_prep(c, ch, qs, used)
            self._barrier(c, used)
            self._verify_cat(c, ch, qs, self.flags.get(ci, ()))
            self._barrier(c, used)
            # each cat member takes at most one data CNOT.
            ds = [P(x) for x in ch.support]
            pairs = ((qs[0], d) for d in ds) if self.kind == "bare" else zip(qs, ds)
            for q, d in pairs:
                if ch.basis == "X":
                    c.cx(q, d)
                else:
                    c.cx(d, q)
            self._barrier(c, used)
            bits = []
            for q in qs:
                bits.append(c.mx(q) if ch.basis == "X" else c.measure(q))
            self.groups.append((tuple(bits), ch.tile if ch.basis == "X" else 3 + ch.tile))
            # The raw verifier outcomes are direct deterministic detectors.  They are not part
            # of the stabilizer parity because they certify cat preparation.
            for b in self.verify_groups[-(len(self.flags.get(ci, ()))):]:
                self.groups.append(((b,), None))
            # The stabilizer parity and any verifier parity are deterministic checks used by the
            # judge.  Keep these on the Circ as well as in the proxy metadata.
            c.detector(*bits)
            for b in self.verify_groups[-(len(self.flags.get(ci, ()))):]:
                c.detector(b)
            self._barrier(c, used)
        return self.groups, used

    def proxy(self, q_in=0.003, lazy=True):
        c = Circ(); c.g("id", *DATA)
        groups, _ = self.emit(c)
        c.detectors = []
        if lazy:
            c = c.rescheduled(lazy_init=True)
        s, err = to_stim(c.text())
        if err:
            raise ValueError("; ".join(err))
        noisy = apply_noise(s, 1e-3, STANDARD)
        bits = [b for kind, qs, b in c.sops if kind in ("M", "MX")]
        return direct_loss(noisy, bits, groups, q_in=q_in)


def _mpp(B, qs):
    return "MPP " + "*".join(f"{B}{q}" for q in qs)


def _full(noisy, bits, groups, logical, q_in):
    stabs = [("X", s) for s in SUPPORT] + [("Z", s) for s in SUPPORT]
    lines = [_mpp(B, s) for B, s in stabs] + [_mpp(logical, DATA)]
    if q_in:
        lines.append("DEPOLARIZE1(%g) %s" % (q_in, " ".join(map(str, DATA))))
    lines += [x for x in noisy.splitlines() if not x.startswith(("DETECTOR", "OBSERVABLE"))]
    lines += [_mpp(B, s) for B, s in stabs] + [_mpp(logical, DATA)]
    nm = len(bits); n = 7 + nm + 7
    rec = lambda i: f"rec[{i - n}]"
    pos = {b: j for j, b in enumerate(bits)}
    for refs, ref in groups:
        js = [pos[b] for b in refs]
        terms = [rec(7 + j) for j in js]
        if ref is not None:
            terms.append(rec(ref))
        lines.append("DETECTOR " + " ".join(terms))
    for k in range(6):
        # rec(k) is the initial stabilizer; the judge's initial six records precede the logical
        # record at rec[6].  The cycle body begins after those seven records.
        lines.append(f"OBSERVABLE_INCLUDE({k}) {rec(7 + nm + k)} {rec(k)}")
    # Logical X^7 is compared with its initial record (rec[6]); the leading 7 records are
    # six checks plus the initial logical observable.
    lines.append(f"OBSERVABLE_INCLUDE(6) {rec(7 + nm + 6)} {rec(6)}")
    return stim.Circuit("\n".join(lines))


def direct_loss(noisy, bits, groups, q_in=0.003):
    cx = _full(noisy, bits, groups, "X", q_in)
    cz = _full(noisy, bits, groups, "Z", q_in)
    return proxy2.joint_loss(cx, cz)


def evaluate(kind="shor", verify=False, order=None, q_in=0.003):
    m = DirectRound(kind=kind, verify=verify, order=order)
    return m.proxy(q_in=q_in)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="shor", choices=("bare", "shor"))
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    print(args, evaluate(args.kind, args.verify))
