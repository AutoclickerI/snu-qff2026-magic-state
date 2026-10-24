"""Exact fault model of a submission circuit: judge noise channels as Pauli faults on the
deferred-measurement wire picture of tprep.exact, in the start frame |Psi> = C R_k..R_1 |0>.

A Pauli fault F inserted after m rotations equals, up to the output Pauli C F~ C^-1, a flip of the
sign of every later rotation whose axis anticommutes with F~ = (C_t)^-1 F C_t.  So a fault is fully
described by  s (which rotations flip)  and  sig (which output observables it anticommutes with);
a set of faults has s = XOR s_f, sig = XOR sig_f.  Everything the judge scores follows from
(s, sig) by Pauli expectations on the sparse state phi_s = R^s_k..R^s_1 |0>.
"""
import math
import os
import sys
import warnings

import numpy as np
import stim

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "upstream", "snu-qff2026-problem"))

import tprep  # noqa: E402
import tprep.check  # noqa: E402,F401
from tprep.exact import CLIFFORD, ROTATIONS, ExactError, verify  # noqa: E402
from tprep.grid import N_QUBITS, SUPPORTS  # noqa: E402
from tprep.noise import STANDARD, noise_blocks, schedule  # noqa: E402
from tprep.parse import count_measurements, declarations, parse  # noqa: E402
from tprep.qasm import convert  # noqa: E402

tc = sys.modules["tprep.check"]

P = 1e-3
PAULI1 = ["X", "Y", "Z"]
PAULI2 = [a + b for a in "IXYZ" for b in "IXYZ" if a + b != "II"]


def masks(ps):
    xs, zs = ps.to_numpy()
    x = int.from_bytes(np.packbits(xs, bitorder="little").tobytes(), "little")
    z = int.from_bytes(np.packbits(zs, bitorder="little").tobytes(), "little")
    return x, z, complex(ps.sign) * 1j ** (x & z).bit_count()


def comm(x1, z1, x2, z2):
    return ((x1 & z2).bit_count() + (z1 & x2).bit_count()) & 1


class Basis:
    """GF(2) span of the rotations' X parts; coordinates c <-> basis state b(c)."""

    def __init__(self):
        self.vecs = []
        self.piv = {}

    def express(self, x):
        combo = 0
        while x:
            h = x.bit_length() - 1
            if h not in self.piv:
                return None
            v, c = self.piv[h]
            x ^= v
            combo ^= c
        return combo

    def add(self, x):
        combo = 0
        orig = x
        while x:
            h = x.bit_length() - 1
            if h not in self.piv:
                idx = len(self.vecs)
                self.vecs.append(orig)
                self.piv[h] = (x, combo ^ (1 << idx))
                return 1 << idx
            v, c = self.piv[h]
            x ^= v
            combo ^= c
        return combo


class Model:
    def __init__(self, qasm_text, data_qubits, p=P, log=print):
        self.p = p
        text, labels, errors = convert(qasm_text, N_QUBITS, STANDARD)
        if errors:
            raise ValueError("; ".join(errors))
        import xtim
        frame, post = declarations(text)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            clean = xtim.Circuit(tprep.apply_noise(text, 0.0, STANDARD))
            if frame is None:
                frame = tc.auto_frame(clean, list(data_qubits))
            ex = verify(text, list(data_qubits), frame=frame, postselect=post)
        if ex["errors"]:
            raise ValueError("circuit fails the judge's correctness check: " + ex["errors"][0])
        text, post = tc.conditional(text, post, ex["conditional_detectors"])
        self.text, self.labels, self.frame, self.post = text, labels, frame, post
        self.data = list(data_qubits)
        self.A0 = ex["acceptance"]
        self._walk()

    # ------------------------------------------------------------------ walk
    def _walk(self):
        text = self.text
        prog, blocks = noise_blocks(text, self.p, STANDARD)
        _, steps, gaps = schedule(text)
        idle_of = {}
        for i, q, first, n in gaps:
            idle_of.setdefault(i, []).append((q, first, n))
        fresh = sum(len(i.qubits) for i in prog if i.name in ("M", "MX", "R", "RX"))
        n = N_QUBITS + fresh
        sim = stim.TableauSimulator()
        sim.set_num_qubits(n)
        wire = list(range(N_QUBITS))
        nxt = N_QUBITS
        records, dets = [], []
        rots = []          # (x, z, coef, theta) in the start frame
        faults = []        # dict per Pauli component
        chans = []         # dict per channel instance
        for ii, (ins, block) in enumerate(zip(prog, blocks)):
            k = block.index(ins.text)
            nidle = len(idle_of.get(ii, []))
            tail = len(block) - nidle
            for jl, line in enumerate(block[:k]):
                self._channel(line, ii, ins, sim, wire, len(rots), chans, faults, None, "before", jl)
            name, qs = ins.name, ins.qubits
            if name == "DETECTOR":
                dets.append([len(records) - int(t[5:-1]) for t in ins.targets])
            elif name in ("TICK", "QUBIT_COORDS", "SHIFT_COORDS") or (not qs and name not in ROTATIONS):
                pass
            elif name in ("M", "MX"):
                for q in qs:
                    w, nxt = nxt, nxt + 1
                    if name == "MX":
                        sim.h(wire[q])
                    sim.cx(wire[q], w)
                    if name == "MX":
                        sim.h(wire[q])
                    records.append(w)
            elif name in ("R", "RX"):
                for q in qs:
                    wire[q], nxt = nxt, nxt + 1
                    if name == "RX":
                        sim.h(wire[q])
            elif name in CLIFFORD:
                if name != "I":
                    sim.do(stim.CircuitInstruction(name, [wire[q] for q in qs]))
            elif name in ROTATIONS and name in ("T", "T_DAG"):
                for q in qs:
                    for axis, theta in ROTATIONS[name]:
                        ps = stim.PauliString(n)
                        ps[wire[q]] = "Z"
                        x, z, coef = masks(sim.current_inverse_tableau()(ps))
                        rots.append((x, z, coef, theta, ii))
            else:
                raise ExactError(f"line {ins.line_no}: {name} unsupported")
            for j in range(k + 1, len(block)):
                idl = idle_of[ii][j - tail] if j >= tail else None
                self._channel(block[j], ii, ins, sim, wire, len(rots), chans, faults, idl, "after", j)
        self.n, self.wire, self.records, self.rots = n, wire, records, rots
        self.chans, self.faults = chans, faults
        inv = sim.current_inverse_tableau()
        self.inv = inv
        self.prog = prog
        self.steps = steps
        # observables in the start frame
        def pull(ps):
            return masks(inv(ps))
        def par(recs):
            ps = stim.PauliString(n)
            for r in recs:
                w = records[r]
                ps[w] = "Z" if ps[w] == 0 else "I"
            return ps
        self.par = par
        self.pull = pull
        # projectors: postselects then detectors (values filled in by the dense engine)
        self.proj_ps = [par(r) for v, r in self.post] + [par(d) for d in dets]
        self.proj_v = [v for v, r in self.post] + [None] * len(dets)
        self.n_post = len(self.post)
        self.proj_m = [pull(ps) for ps in self.proj_ps]
        # data stabilizers and logicals
        dw = [wire[q] for q in self.data]
        def op(pauli, idxs):
            ps = stim.PauliString(n)
            for i in idxs:
                ps[dw[i]] = pauli
            return ps
        self.gen = [op("X", sorted(s)) for s in SUPPORTS] + [op("Z", sorted(s)) for s in SUPPORTS]
        X7, Z7, Y7 = op("X", range(7)), op("Z", range(7)), op("Y", range(7))
        (cx, sx), (cz, sz) = self.frame["X"], self.frame["Z"]
        self.cz, self.cxz = cz, cx ^ cz
        parZ, parXZ = par(sz), par(list(sx) + list(sz))
        # signature observables for faults: 6 stabs, X7, Z7, parZ, parXZ  (bits of e) ; detectors separate
        self.sig_e = [pull(g) for g in self.gen] + [pull(X7), pull(Z7), pull(parZ), pull(parXZ)]
        # Q operators g*T: index (T, a, b)
        def mul(*pss):
            out = stim.PauliString(n)
            for p_ in pss:
                out = out * p_
            return out
        self.Q = {}
        for T, logical, parity in (("X", X7, parZ), ("Y", Y7, parXZ)):
            for a in range(8):
                for b in range(8):
                    if T == "X" and b:
                        continue
                    gs = [self.gen[i] for i in range(3) if a >> i & 1] + [self.gen[3 + i] for i in range(3) if b >> i & 1]
                    self.Q[(T, a, b)] = pull(mul(*gs, logical, parity))
        # fault signatures
        for f in faults:
            fx, fz = f["x"], f["z"]
            f["s"] = sum(comm(fx, fz, r[0], r[1]) << j for j, r in enumerate(rots) if j >= f["m"])
            f["d"] = sum(comm(fx, fz, m_[0], m_[1]) << j for j, m_ in enumerate(self.proj_m))
            f["e"] = sum(comm(fx, fz, m_[0], m_[1]) << j for j, m_ in enumerate(self.sig_e))
        self.n_det = len(dets)

    def _channel(self, line, ii, ins, sim, wire, m, chans, faults, idle, when, jl):
        head, _, rest = line.partition(")")
        name, _, pr = head.partition("(")
        if name not in ("X_ERROR", "Z_ERROR", "DEPOLARIZE1", "DEPOLARIZE2"):
            return
        prob = float(pr)
        qs = [int(t) for t in rest.split()]
        arity = 2 if name == "DEPOLARIZE2" else 1
        tab = sim.current_inverse_tableau()
        for g in range(0, len(qs), arity):
            grp = qs[g:g + arity]
            img = []
            for q in grp:
                w = wire[q]
                img.append((masks(tab.x_output(w))[:2], masks(tab.z_output(w))[:2]))
            if name == "X_ERROR":
                comps = [("X",)]
                pc = [prob]
            elif name == "Z_ERROR":
                comps = [("Z",)]
                pc = [prob]
            elif name == "DEPOLARIZE1":
                comps = [(a,) for a in PAULI1]
                pc = [prob / 3] * 3
            else:
                comps = [tuple(s) for s in PAULI2]
                pc = [prob / 15] * 15
            cid = len(chans)
            kind = "idle" if idle is not None else {"X_ERROR": "flip", "Z_ERROR": "flip", "DEPOLARIZE1": "gate1", "DEPOLARIZE2": "gate2"}[name]
            chans.append({"id": cid, "ins": ii, "name": name, "qubits": grp, "prob": prob, "kind": kind,
                          "when": when, "gap": idle, "jl": jl, "grp": g, "blk": ii})
            for comp, pp in zip(comps, pc):
                x = z = 0
                for (xi, zi), pa in zip(img, comp):
                    if pa in ("X", "Y"):
                        x ^= xi[0]
                        z ^= xi[1]
                    if pa in ("Z", "Y"):
                        x ^= zi[0]
                        z ^= zi[1]
                faults.append({"chan": cid, "p": pp, "pauli": "".join(comp), "qubits": grp, "x": x, "z": z, "m": m})


def n_rot_span(model):
    b = Basis()
    for r in model.rots:
        b.add(r[0])
    return len(b.vecs)
