"""Small QASM builder for the QFF2026 judge, plus an evaluation helper.

Circuits are written as OpenQASM 2.0 with the judge's comment lines (problem.md 1.3). X-basis
preparation/readout are written as reset+h / h+measure, which the judge runs natively.
`allow_any_coupling()` switches off the grid-adjacency check for prototyping only; anything
submitted must pass the real check.
"""

import tprep

HEADER = 'OPENQASM 2.0;\ninclude "qelib1.inc";\n'


class Circ:
    def __init__(self, n_qubits=36):
        self.n = n_qubits
        self.ops = []
        self.nbits = 0
        self.detectors = []      # lists of bit indices
        self.postselect = []     # (value, [bits])
        self.frame = None        # {"X": (c, bits), "Z": (c, bits)}
        self.sops = []           # structured ops (kind, qubits, bit) mirroring self.ops

    # single-qubit gates
    def g(self, name, *qs):
        for q in qs:
            self.ops.append(f"{name} q[{q}];")
            self.sops.append(("R" if name == "reset" else "g:" + name, (q,), None))
        return self

    def h(self, *qs): return self.g("h", *qs)
    def t(self, *qs): return self.g("t", *qs)
    def tdg(self, *qs): return self.g("tdg", *qs)
    def s(self, *qs): return self.g("s", *qs)
    def sdg(self, *qs): return self.g("sdg", *qs)
    def x(self, *qs): return self.g("x", *qs)
    def z(self, *qs): return self.g("z", *qs)
    def reset(self, *qs): return self.g("reset", *qs)

    def rx(self, *qs):
        for q in qs:
            self.ops.append(f"reset q[{q}];")
            self.ops.append(f"h q[{q}];")
            self.sops.append(("RX", (q,), None))
        return self

    def cx(self, c, t):
        self.ops.append(f"cx q[{c}],q[{t}];")
        self.sops.append(("cx", (c, t), None))
        return self

    def cxs(self, pairs):
        for c, t in pairs:
            self.cx(c, t)
        return self

    def barrier(self, *qs):
        self.ops.append("barrier " + ",".join(f"q[{q}]" for q in qs) + ";")
        self.sops.append(("barrier", tuple(qs), None))
        return self

    def measure(self, q, _kind="M"):
        b = self.nbits
        self.nbits += 1
        self.ops.append(f"measure q[{q}] -> c[{b}];")
        self.sops.append((_kind, (q,), b))
        return b

    def mx(self, q):
        self.ops.append(f"h q[{q}];")
        return self.measure(q, _kind="MX")

    def detector(self, *bits):
        self.detectors.append(list(bits))

    def text(self):
        lines = [HEADER.rstrip(), f"qreg q[{self.n}];"]
        if self.nbits:
            lines.append(f"creg c[{self.nbits}];")
        lines += self.ops
        lines += ["// DETECTOR " + " ".join(f"c[{b}]" for b in d) for d in self.detectors]
        lines += [f"// POSTSELECT({v}) " + " ".join(f"c[{b}]" for b in bits) for v, bits in self.postselect]
        if self.frame is not None:
            for P in "XZ":
                c, bits = self.frame[P]
                lines.append((f"// FRAME_{P}({c}) " + " ".join(f"c[{b}]" for b in bits)).rstrip())
        return "\n".join(lines) + "\n"

    def layers(self, lazy_init=True):
        """ASAP schedule like the judge's (barriers honoured), then inits (R/RX) moved as late as
        possible, i.e. into the step right before the qubit's next operation."""
        free, steps = {}, []
        for kind, qs, b in self.sops:
            if kind == "barrier":
                t = max((free.get(q, 0) for q in qs), default=0)
                for q in qs:
                    free[q] = t
                steps.append(None)
                continue
            t = max(free.get(q, 0) for q in qs)
            for q in qs:
                free[q] = t + 1
            steps.append(t)
        if lazy_init:
            per_q = {}
            for i, (kind, qs, b) in enumerate(self.sops):
                if steps[i] is not None:
                    for q in qs:
                        per_q.setdefault(q, []).append(i)
            for q, idx in per_q.items():
                for a, bnext in zip(idx, idx[1:]):
                    if self.sops[a][0] in ("R", "RX"):
                        steps[a] = steps[bnext] - 1
        out = {}
        for i, t in enumerate(steps):
            if t is not None:
                out.setdefault(t, []).append(self.sops[i])
        return [out.get(t, []) for t in range(max(out) + 1)] if out else []

    def rescheduled(self, lazy_init=True):
        """A copy emitted layer by layer with a barrier over every used qubit between layers, so
        the judge runs exactly this schedule."""
        new = Circ(self.n)
        new.nbits = self.nbits
        new.detectors = [list(d) for d in self.detectors]
        new.postselect = list(self.postselect)
        new.frame = self.frame
        used = sorted({q for kind, qs, _ in self.sops if kind != "barrier" for q in qs})
        lay = self.layers(lazy_init)
        for k, layer in enumerate(lay):
            for kind, qs, b in layer:
                if kind == "cx":
                    new.ops.append(f"cx q[{qs[0]}],q[{qs[1]}];")
                elif kind == "R":
                    new.ops.append(f"reset q[{qs[0]}];")
                elif kind == "RX":
                    new.ops += [f"reset q[{qs[0]}];", f"h q[{qs[0]}];"]
                elif kind == "M":
                    new.ops.append(f"measure q[{qs[0]}] -> c[{b}];")
                elif kind == "MX":
                    new.ops += [f"h q[{qs[0]}];", f"measure q[{qs[0]}] -> c[{b}];"]
                else:
                    new.ops.append(f"{kind[2:]} q[{qs[0]}];")
                new.sops.append((kind, qs, b))
            if k + 1 < len(lay):
                new.ops.append("barrier " + ",".join(f"q[{q}]" for q in used) + ";")
                new.sops.append(("barrier", tuple(used), None))
        return new

    def n_2q(self):
        return sum(op.startswith("cx ") for op in self.ops)


def allow_any_coupling():
    """Prototype mode: every pair counts as coupled (judge's adjacency check off)."""
    import sys

    # tprep/__init__ rebinds `tprep.parse` to a function, so reach the modules directly.
    for mod in ("tprep.parse", "tprep.qasm"):
        sys.modules[mod].adjacent = lambda a, b: True


def evaluate(text, data_qubits, shots=10**6, seed=0, scan=True, quiet=False):
    rep = tprep.check(text, data_qubits, shots=shots, seed=seed)
    out = {"passed": rep.passed, "score": rep.score, "sem": rep.sem, "acc": rep.acceptance,
           "n_2q": rep.n_2q, "report": rep}
    if not quiet:
        print(rep)
    if scan and rep.passed:
        sc = tprep.fault_scan(text, data_qubits)
        out["c1"] = sc.c1
        out["scan"] = sc
        if not quiet:
            print(sc)
    return out
