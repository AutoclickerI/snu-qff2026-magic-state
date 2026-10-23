"""Layouts with relocated Bell pairs (lane L2): data hop first, then each tile's Bell pair (possibly on
a vacated data site) is entangled by a scheduled key ("B", t, "") = CX(a -> b); a is prepared in |+>,
b in |0>. A Bell member on a vacated site takes its state from the hop (normal hop -> |0>, so it must
be b; mirrored hop (zhops) -> |+>, so it must be a). Everything else as gmodel/zmodel."""
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/L2_layout_cpsat")
import zmodel as Z  # noqa: E402

G, P, DATA0, adj = Z.G, Z.P, Z.DATA0, Z.adj


class LModel(Z.ZModel):
    def __init__(self, moves=(), bells=None, extras=(), xmem=None, zmem=None, zext=(), zhops=()):
        self.bells = [tuple(p) for p in bells]
        save = G.BELL
        G.BELL = self.bells           # GModel.__init__ reads the module-level BELL for member defaults
        try:
            Z.ZModel.__init__(self, moves, extras, xmem, zmem, zext, zhops)
        finally:
            G.BELL = save
        self.keys += [("B", t, "") for t in range(3)]
        self.vac = {}
        for d, path in self.moves.items():
            for q in [DATA0[d]] + path[:-1]:
                self.vac[q] = d
        for a, b in self.bells:
            assert adj(a, b)
            if a in self.vac:
                assert self.vac[a] in self.zhops, a
            if b in self.vac:
                assert self.vac[b] not in self.zhops, b
            assert a not in self.pos and b not in self.pos
        self.member_tile = {q: t for t, p in enumerate(self.bells) for q in p}

    def readers(self, t, orient):
        a, b = self.bells[t]
        return (a, b) if orient[t] == 0 else (b, a)

    def qubits_of(self, key, orient):
        if key[0] == "B":
            return self.bells[key[1]]
        return Z.ZModel.qubits_of(self, key, orient)

    def feasible(self, assign, orient):
        for t, (a, b) in enumerate(self.bells):
            lb = assign[("B", t, "")]
            for q in (a, b):
                if q in self.vac:
                    d = self.vac[q]
                    if lb <= max(assign[("M", d, k)] for k in range(2 * len(self.moves[d]))):
                        return False
            for k, L in assign.items():
                if k[0] != "B" and L <= lb and set(self.qubits_of(k, orient)) & {a, b}:
                    if k[0] == "M":
                        continue
                    return False
        return Z.ZModel.feasible(self, {k: v for k, v in assign.items() if k[0] != "B"} | {}, orient) and \
            self._qubit_ok(assign, orient)

    def _qubit_ok(self, assign, orient):
        used = set()
        for k, L in assign.items():
            for q in self.qubits_of(k, orient):
                if (L, q) in used:
                    return False
                used.add((L, q))
        return True

    def emit(self, c, assign, orient):
        lmax = max(assign.values())
        bell = [q for pair in self.bells for q in pair]
        ex = [cc for _, cc, _ in self.extras]
        dests = [q for path in self.moves.values() for q in path]
        involved = sorted({P(q) for q in bell + ex + dests + DATA0 + self.pos})
        c.barrier(*involved)
        zd = {q for d in self.zhops for q in self.moves[d]}
        plus = sorted(q for q in (self.zext | zd | {a for a, _ in self.bells}) if q not in DATA0)
        zero = sorted(q for q in set(ex + dests + [b for _, b in self.bells]) if q not in DATA0 and q not in plus)
        if zero:
            c.reset(*[P(q) for q in zero])
        if plus:
            c.rx(*[P(q) for q in plus])
        c.barrier(*involved)
        lastq = {}
        for k, L in assign.items():
            for q in self.qubits_of(k, orient):
                lastq[q] = max(lastq.get(q, 0), L)
        readers = {}
        for t in range(3):
            ax, az = self.readers(t, orient)
            readers[ax], readers[az] = (t, "X"), (t, "Z")
        for t, cc, _ in self.extras:
            readers[cc] = (t, "Z" if cc in self.zext else "X")
        self.checks = {}
        for L in range(2, lmax + 2):
            c.barrier(*involved)
            for q, (t, B) in readers.items():
                if lastq.get(q, 1) == L - 1:
                    bit = c.mx(P(q)) if B == "X" else c.measure(P(q))
                    self.checks.setdefault((t, B), []).append(bit)
            for k, LL in sorted(assign.items(), key=lambda kv: str(kv[0])):
                if LL == L:
                    a, b = self.qubits_of(k, orient)
                    c.cx(P(a), P(b))
        for _, bits in sorted(self.checks.items()):
            c.detector(*bits)
