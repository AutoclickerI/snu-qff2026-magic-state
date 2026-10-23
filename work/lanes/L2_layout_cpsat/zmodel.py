"""GModel with Z-only extra cat members, the mirror of gmodel's X-only extras: a Z extra starts in |+>,
joins by CX(extra -> parent) (a Z-type GHZ extension of the Bell pair), takes Z-part CNOTs
CX(data -> extra) and is read with M; the tile's Z check is the Bell ZZ readout xor these bits."""
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/me_layout")
import gmodel as G  # noqa: E402

P, DATA0, BELL, adj = G.P, G.DATA0, G.BELL, G.adj


class ZModel(G.GModel):
    def __init__(self, moves=(), extras=(), xmem=None, zmem=None, zext=(), zhops=()):
        # zhops: data whose hops use a |+> destination, CX(dst->src) then CX(src->dst); the vacated
        # site is left in |+> (usable as a Z extra) instead of |0>
        self.zext = set(zext)
        self.zhops = set(zhops)
        G.GModel.__init__(self, moves, extras, xmem)
        for (t, d), mm in (zmem or {}).items():
            assert mm in self.zext and adj(mm, self.pos[d]), (t, d, mm)
            self.zmem[(t, d)] = mm
        for (t, d), mm in self.xmem.items():
            assert mm not in self.zext, (t, d, mm)
        ex = {c: p for _, c, p in self.extras}
        for c, p in ex.items():
            if p in ex:
                assert (p in self.zext) == (c in self.zext), (c, p)
            for d, path in self.moves.items():
                if c in [DATA0[d]] + path[:-1]:
                    assert (c in self.zext) == (d in self.zhops), (c, d)

    def qubits_of(self, key, orient):
        a, b, c = key
        if a == "M" and b in self.zhops:
            return G.GModel.qubits_of(self, key, orient)[::-1]
        if b == "A" and c in self.zext:
            parent = next(p for t, cc, p in self.extras if cc == c)
            return (c, parent)
        return G.GModel.qubits_of(self, key, orient)

    def parent(self, c):
        return next(p for t, cc, p in self.extras if cc == c)

    def feasible(self, assign, orient):
        used = set()
        for k, L in assign.items():
            for q in self.qubits_of(k, orient):
                if (L, q) in used:
                    return False
                used.add((L, q))
        for d, path in self.moves.items():
            ms = [assign[("M", d, k)] for k in range(2 * len(path))]
            if ms != sorted(ms) or len(set(ms)) != len(ms):
                return False
            for k, L in assign.items():
                if k[0] != "M" and k[1] == d and L <= ms[-1]:
                    return False
        extra_set = {c for _, c, _ in self.extras}
        for t in range(3):
            u = assign[(t, "U", "")]
            ax, az = self.readers(t, orient)
            for k, L in assign.items():
                if k[0] != t or L < u or k[1] == "U":
                    continue
                if k[1] == "A":
                    par = self.parent(k[2])
                    if par == (ax if k[2] in self.zext else az):
                        return False
                    continue
                q = self.xmem[(t, k[1])] if k[2] == "X" else self.zmem[(t, k[1])]
                if q in extra_set:
                    continue
                if (q == ax and k[2] != "X") or (q == az and k[2] != "Z"):
                    return False
        for t, c, parent in self.extras:
            la = assign[(t, "A", c)]
            mem, typ = (self.zmem, "Z") if c in self.zext else (self.xmem, "X")
            for (tt, d), m in mem.items():
                if m == c and assign[(tt, d, typ)] <= la:
                    return False
            if parent in extra_set:
                tp = next(tt for tt, cc, _ in self.extras if cc == parent)
                if assign[(tp, "A", parent)] >= la:
                    return False
            for d, path in self.moves.items():
                srcs = [DATA0[d]] + path[:-1]
                if c in srcs and la <= max(assign[("M", d, k)] for k in range(2 * len(path))):
                    return False
        return True

    def emit(self, c, assign, orient):
        lmax = max(assign.values())
        bell = [q for pair in BELL for q in pair]
        ex = [cc for _, cc, _ in self.extras]
        dests = [q for path in self.moves.values() for q in path]
        involved = sorted({P(q) for q in bell + ex + dests + DATA0 + self.pos})
        c.barrier(*involved)
        c.rx(*[P(a) for a, _ in BELL]); c.reset(*[P(b) for _, b in BELL])
        zd = {q for d in self.zhops for q in self.moves[d]}
        plus = sorted(q for q in (self.zext | zd) if q not in DATA0)
        fresh = [P(q) for q in ex + dests if q not in DATA0 and q not in plus]
        if fresh:
            c.reset(*fresh)
        if plus:
            c.rx(*[P(q) for q in plus])
        c.barrier(*involved)
        for a, b in BELL:
            c.cx(P(a), P(b))
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
