"""Lane-local generalized final-round model.

A final round is described by data positions after optional one-hop/two-CNOT moves,
three arbitrary Bell pairs, and arbitrary X-only cat members.  Every extra member
has a grid-adjacent parent, so the preparation graph is a connected GHZ tree.  The
Bell members may each take X and Z data CNOTs; extras take X CNOTs only and are read
with MX.  A CP-SAT/exhaustive schedule is represented by integer layer assignments,
then Stim's DEM is the cost oracle.

The injection and double-cat check are imported read-only from cultiv_port.  All
writes/results for this lane are made by search.py and verify.py in this directory.
"""
from __future__ import annotations
import ast
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import stim
import cultiv_port as cp
import proxy2
from qcirc import Circ
from tprep.noise import STANDARD, apply_noise
from tprep.qasm import to_stim

P = cp.phys
DATA0 = tuple(cp.DATA_XY[i] for i in range(7))
TILES = tuple(tuple(ds) for _, ds in proxy2.TILES)
PLAQ = tuple(tuple(DATA0.index(xy) for xy in ds) for ds in TILES)
BELL0 = tuple((m, (m[0] + 1, m[1])) for m, _ in proxy2.TILES)
GRID = tuple((x, y) for y in range(6) for x in range(6))


def adj(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


@dataclass(frozen=True)
class Extra:
    tile: int
    coord: tuple[int, int]
    parent: tuple[int, int]
    served: tuple[int, ...] = ()


class LayoutModel:
    """Exact second-order proxy plus full-grid circuit emitter.

    ``moves`` maps a data index to a list of destination coordinates.  Each hop is
    emitted as CX(src,dst), CX(dst,src), and hops are ordered.  ``bells`` contains
    one adjacent Bell pair per tile.  ``extras`` contains arbitrary tree members;
    the X member map selects the Bell/extra coordinate serving each X CNOT, while
    Z members are necessarily Bell coordinates (Bell-read parity).
    """
    def __init__(self, moves=None, bells=None, extras=(), xmem=None, zmem=None):
        self.moves = {int(d): tuple(path) for d, path in (moves or {}).items()}
        self.pos = list(DATA0)
        for d, path in self.moves.items():
            if not path:
                raise ValueError("empty move path")
            self.pos[d] = path[-1]
        self.pos = tuple(self.pos)
        self.bells = tuple(tuple(pair) for pair in (bells or BELL0))
        self.extras = tuple(e if isinstance(e, Extra) else Extra(*e) for e in extras)
        self._extra_by_coord = {e.coord: e for e in self.extras}
        self.xmem = dict(xmem or {})
        self.zmem = dict(zmem or {})
        self._validate_layout()
        for t, ds in enumerate(PLAQ):
            for d in ds:
                # Defaults choose either Bell member that is adjacent.  X can be
                # overridden by an extra; Z remains Bell-only.
                pair = self.bells[t]
                zs = [q for q in pair if adj(q, self.pos[d])]
                if (t, d) not in self.zmem:
                    if not zs:
                        raise ValueError(f"no Bell Z member for tile {t} data {d}")
                    self.zmem[(t, d)] = zs[0]
                if (t, d) not in self.xmem:
                    xs = [q for q in pair if adj(q, self.pos[d])]
                    if not xs:
                        xs = [e.coord for e in self.extras if e.tile == t and d in e.served and adj(e.coord, self.pos[d])]
                    if not xs:
                        raise ValueError(f"no X member for tile {t} data {d}")
                    self.xmem[(t, d)] = xs[0]
        self.keys = [(t, d, typ) for t, ds in enumerate(PLAQ) for d in ds for typ in "XZ"]
        self.keys += [(t, "U", "") for t in range(3)]
        self.keys += [(e.tile, "A", e.coord) for e in self.extras]
        self.keys += [("M", d, k) for d, path in self.moves.items() for k in range(2 * len(path))]
        self.late_bell = tuple(t for t,pair in enumerate(self.bells) if any(q in DATA0 for q in pair))
        self.keys += [("B", t, "") for t in self.late_bell]

    def _validate_layout(self):
        if len(set(self.pos)) != 7:
            raise ValueError("data positions overlap")
        if any(q not in GRID for q in self.pos):
            raise ValueError("data outside grid")
        if len(self.bells) != 3 or any(len(p) != 2 or not adj(*p) for p in self.bells):
            raise ValueError("Bell pair is not a grid edge")
        if len({q for p in self.bells for q in p}) != 6:
            raise ValueError("Bell members overlap")
        for e in self.extras:
            if e.coord in self.bells[e.tile] or not adj(e.coord, e.parent):
                raise ValueError("invalid extra tree edge")
            if e.parent not in self.bells[e.tile] and e.parent not in self._extra_by_coord:
                raise ValueError("extra parent is not in its tile cat")
        # A Bell node on an old data site is allowed only when that data is moved;
        # its GHZ preparation is then emitted after the move.
        for pair in self.bells:
            for q in pair:
                if q in DATA0 and DATA0.index(q) not in self.moves:
                    raise ValueError("Bell pair on an unmoved data site")
        # A final data site may coincide with an old data site only if that old
        # site is vacated by a move; this is the fresh-|0> move invariant.
        old_to_moved = {DATA0[d] for d in self.moves}
        for q in self.pos:
            if q in DATA0 and q not in old_to_moved:
                # unchanged data is expected; it is not an ancilla location
                continue
        for q in [q for p in self.bells for q in p] + [e.coord for e in self.extras]:
            if q in self.pos:
                raise ValueError("ancilla overlaps final data")
        for t, ds in enumerate(PLAQ):
            for d in ds:
                zm = self.zmem.get((t, d))
                xm = self.xmem.get((t, d))
                if zm is not None and zm not in self.bells[t]:
                    raise ValueError("Z interaction must use Bell member")
                if xm is not None and xm not in self.bells[t] and xm not in self._extra_by_coord:
                    raise ValueError("X interaction member is not in cat")
                if zm is not None and not adj(zm, self.pos[d]):
                    raise ValueError("non-adjacent Z interaction")
                if xm is not None and not adj(xm, self.pos[d]):
                    raise ValueError("non-adjacent X interaction")
        for d, path in self.moves.items():
            chain = [DATA0[d], *path]
            if len(set(chain)) != len(chain):
                raise ValueError("move path revisits site")
            for a, b in zip(chain, chain[1:]):
                if not adj(a, b):
                    raise ValueError("move hop is not a grid edge")

    def readers(self, t, orient):
        a, b = self.bells[t]
        return (a, b) if not orient[t] else (b, a)

    def qubits_of(self, key, orient):
        a, b, c = key
        if a == "M":
            path = [DATA0[b], *self.moves[b]]
            src, dst = path[c // 2], path[c // 2 + 1]
            return (src, dst) if c % 2 == 0 else (dst, src)
        if a == "B":
            return self.bells[b]
        if b == "U":
            return self.readers(a, orient)
        if b == "A":
            e = self._extra_by_coord[c]
            return (e.parent, c)
        anc = self.xmem[(a, b)] if c == "X" else self.zmem[(a, b)]
        return (anc, self.pos[b]) if c == "X" else (self.pos[b], anc)

    def _move_last(self, d, assign):
        return max(assign[("M", d, k)] for k in range(2 * len(self.moves[d])))

    def feasible(self, assign, orient):
        if set(assign) != set(self.keys) or any(assign[k] < 2 for k in self.keys):
            return False
        used = set()
        for k in self.keys:
            L = assign[k]
            for q in self.qubits_of(k, orient):
                if (L, q) in used:
                    return False
                used.add((L, q))
        # Moves are ordered and all operations on relocated data happen after the move.
        for d, path in self.moves.items():
            ms = [assign[("M", d, k)] for k in range(2 * len(path))]
            if ms != sorted(ms) or len(set(ms)) != len(ms):
                return False
            last = ms[-1]
            for k, L in assign.items():
                if isinstance(k[0], int) and k[1] == d and L <= last:
                    return False
        # A destination that was an old data site is fresh only after its owner moves.
        for d, path in self.moves.items():
            for dst in path:
                for e in self.extras:
                    if e.coord == dst and e.coord in DATA0:
                        owner = DATA0.index(e.coord)
                        if owner in self.moves and self._move_last(owner, assign) >= assign[("M", d, 2 * path.index(dst))]:
                            return False
        # Tree preparation and X service must precede the relevant readout/operation.
        for e in self.extras:
            la = assign[(e.tile, "A", e.coord)]
            for d in e.served:
                if assign[(e.tile, d, "X")] <= la:
                    return False
            if e.parent in self._extra_by_coord:
                p = self._extra_by_coord[e.parent]
                if assign[(p.tile, "A", p.coord)] >= la:
                    return False
            # A cat member at a vacated data site only exists after its move.
            if e.coord in DATA0:
                owner = DATA0.index(e.coord)
                if owner not in self.moves or la <= self._move_last(owner, assign):
                    return False
        # Late Bell preparation occurs only after every move vacating one of its
        # nodes, and before all tile interactions/readout.
        from layout_model import DATA0
        for t in self.late_bell:
            bl = assign[("B", t, "")]
            for q in self.bells[t]:
                if q in DATA0:
                    owner = DATA0.index(q)
                    if owner not in self.moves or bl <= self._move_last(owner, assign):
                        return False
            for k,L in assign.items():
                if k[0] == t and k != ("B",t,"") and k[1] != "U" and L <= bl:
                    return False

        # Unbell can overlap late matching-basis work, but never a wrong-basis
        # operation or extra preparation on the readout-Z parent.
        for t in range(3):
            u = assign[(t, "U", "")]
            ax, az = self.readers(t, orient)
            for k, L in assign.items():
                if k[0] != t or L < u or k[1] == "U":
                    continue
                if k[1] == "A":
                    if self.qubits_of(k, orient)[0] == az:
                        return False
                    continue
                q = self.xmem[(t, k[1])] if k[2] == "X" else self.zmem[(t, k[1])]
                if q == ax and k[2] != "X":
                    return False
                if q == az and k[2] != "Z":
                    return False
        return True

    def emit(self, c, assign, orient):
        lmax = max(assign.values())
        bell = [q for pair in self.bells for q in pair]
        ex = [e.coord for e in self.extras]
        dests = [q for path in self.moves.values() for q in path]
        involved = sorted({P(q) for q in bell + ex + dests + list(DATA0) + list(self.pos)})
        c.barrier(*involved)
        early = [pair for t,pair in enumerate(self.bells) if t not in self.late_bell]
        c.rx(*[P(pair[0]) for pair in early])
        c.reset(*[P(pair[1]) for pair in early])
        # A destination must be fresh |0>.  Vacated old data sites are already
        # zero after their move and X-only extras there need no initial reset.
        fresh = set(q for q in ex + dests if q not in DATA0)
        if fresh:
            c.reset(*sorted(P(q) for q in fresh))
        c.barrier(*involved)
        for a, b in self.bells:
            c.cx(P(a), P(b))
        lastq = {}
        for k, L in assign.items():
            for q in self.qubits_of(k, orient):
                lastq[q] = max(lastq.get(q, 0), L)
        readers = {}
        for t in range(3):
            ax, az = self.readers(t, orient)
            readers[ax], readers[az] = (t, "X"), (t, "Z")
        for e in self.extras:
            readers[e.coord] = (e.tile, "X")
        self.checks = {}
        for L in range(2, lmax + 2):
            c.barrier(*involved)
            for q, (t, B) in readers.items():
                if lastq.get(q, 1) == L - 1:
                    bit = c.mx(P(q)) if B == "X" else c.measure(P(q))
                    self.checks.setdefault((t, B), []).append(bit)
            for k, LL in sorted(assign.items(), key=lambda kv: (0 if kv[0][0] == 'B' else 1, str(kv[0]))):
                if LL != L:
                    continue
                if k[0] == 'B':
                    pair = self.bells[k[1]]
                    c.rx(P(pair[0])); c.reset(P(pair[1])); c.cx(P(pair[0]), P(pair[1]))
                else:
                    a, b = self.qubits_of(k, orient)
                    c.cx(P(a), P(b))
        for _, bits in sorted(self.checks.items()):
            c.detector(*bits)

    def _full(self, noisy, bits, bit_check, logical):
        sup0 = [sorted(P(DATA0[d]) for d in ds) for ds in PLAQ]
        sup1 = [sorted(P(self.pos[d]) for d in ds) for ds in PLAQ]
        d0 = sorted(P(q) for q in DATA0)
        d1 = sorted(P(q) for q in self.pos)
        lines = [proxy2._mpp(B, s) for B in "XZ" for s in sup0] + [proxy2._mpp(logical, d0)]
        lines += [l for l in noisy.splitlines() if not l.startswith(("DETECTOR", "OBSERVABLE"))]
        lines += [proxy2._mpp(B, s) for B in "XZ" for s in sup1] + [proxy2._mpp(logical, d1)]
        n = len(bits); total = 7 + n + 7
        rec = lambda i: f"rec[{i-total}]"
        pos = {b: j for j, b in enumerate(bits)}
        per = {}
        for b, k in bit_check.items():
            per.setdefault(k, []).append(pos[b])
        for k, js in sorted(per.items()):
            lines.append("DETECTOR " + " ".join(rec(7+j) for j in js) + f" {rec(k)}")
        for k in range(6):
            lines.append(f"OBSERVABLE_INCLUDE({k}) {rec(7+n+k)} {rec(k)}")
        lines.append(f"OBSERVABLE_INCLUDE(6) {rec(7+n+6)} {rec(6)}")
        return stim.Circuit("\n".join(lines))

    def proxy(self, assign, orient):
        if not self.feasible(assign, orient):
            return None
        c = Circ(); c.g("id", *[P(q) for q in DATA0]); self.emit(c, assign, orient)
        bit_check = {b: (t if B == "X" else 3+t) for (t, B), bits in self.checks.items() for b in bits}
        c.detectors = []; c = c.rescheduled(lazy_init=True)
        s, err = to_stim(c.text())
        if err:
            return None
        noisy = apply_noise(s, 1e-3, STANDARD)
        bits = [b for kind, qs, b in c.sops if kind in ("M", "MX")]
        cx, cz = (self._full(noisy, bits, bit_check, L) for L in "XZ")
        return proxy2.joint_loss(cx, cz)

    def full_circuit(self, assign, orient, lazy=True):
        c = Circ()
        cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_init_unitary", cp.UP + "_injection_stage.py"), s_to="Tswap")
        cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_double_cat_check", cp.UP + "_cultivation_stage.py"), s_to="Tswap")
        self.emit(c, assign, orient)
        if lazy:
            c = c.rescheduled(lazy_init=True)
        return c, [P(q) for q in self.pos]


def default_layout(move_d1=True):
    moves = {1: [(1, 3)]} if move_d1 else {}
    extras = [Extra(1, (2, 3), (2, 2), (1,))]
    extras.append(Extra(2, (4, 2), (4, 1), (5,)))
    xmem = {(1, 1): (2, 3), (2, 5): (4, 2)}
    return LayoutModel(moves=moves, extras=extras, xmem=xmem)
