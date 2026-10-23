"""Final superdense cycle with extra cat members (GHZ extension of a tile's Bell pair).

An extra member c starts in |0>, joins its tile's cat with CX parent -> c, and does only X-part
CNOTs (c -> data); it is read with MX, and its result joins the tile's X-check parity. Data whose
X-part CNOT moves to c can then do it while the Bell pairs are being read out. Annealed against the
same second-order proxy as gen_cycle (proxy2, with checks given as parities of several records).
"""
import json
import random
import sys

import stim

import cultiv_port as cp
import gen_cycle as g1
import proxy2

TILES = proxy2.TILES
P = cp.phys
ancilla_of = g1.ancilla_of

# tile -> list of (member, parent, data whose X-part it takes)
EXTRAS_ALL = {
    "t1c13": (1, (1, 3), (1, 2), [(2, 3)]),
    "t2c42": (2, (4, 2), (4, 1), [(3, 2)]),
    "t2c51": (2, (5, 1), (4, 1), []),
    "t2c50": (2, (5, 0), (5, 1), [(4, 0)]),
    "t1c02": (1, (0, 2), (1, 2), []),
    "t1c01": (1, (0, 1), (0, 2), [(1, 1)]),
}


UMAX = None   # if set: penalize unbells after this layer (forces post-unbell data ops)
JOINT = True   # cost Y_L as 1/2 (joint X_L/Z_L flips); False = old proxy (Y_L counted 1.5)


class Model:
    def __init__(self, extras):
        self.extras = [EXTRAS_ALL[e] for e in extras]
        self.xanc = {}
        for t, c, parent, ds in self.extras:
            for d in ds:
                self.xanc[(t, d)] = c
        self.keys = [(t, d, typ) for t, (m, ds) in enumerate(TILES) for d in ds for typ in "XZ"]
        self.keys += [(t, "U", "") for t in range(3)]
        self.keys += [(t, "A", c) for t, c, _, _ in self.extras]

    def anc(self, t, d, typ):
        if typ == "X" and (t, d) in self.xanc:
            return self.xanc[(t, d)]
        return ancilla_of(TILES[t][0], d)

    def qubits_of(self, key, orient):
        t, d, typ = key
        m = TILES[t][0]
        if d == "U":
            return (m, (m[0] + 1, m[1]))
        if d == "A":
            parent = next(p for tt, c, p, _ in self.extras if c == typ)
            return (parent, typ)
        return (self.anc(t, d, typ), d)

    def feasible(self, assign, orient):
        used = set()
        for k, L in assign.items():
            for q in self.qubits_of(k, orient):
                if (L, q) in used:
                    return False
                used.add((L, q))
        for t in range(3):
            u = assign[(t, "U", "")]
            ax, az = g1.readers(t, orient)
            for k, L in assign.items():
                if k[0] != t or k[1] == "U" or L < u:
                    continue
                qs = self.qubits_of(k, orient)
                if k[1] == "A":
                    if qs[0] == az:
                        return False
                    continue
                q = qs[0]
                if (q == ax and k[2] != "X") or (q == az and k[2] != "Z"):
                    return False
        for t, c, parent, ds in self.extras:
            a_l = assign[(t, "A", c)]
            for d in ds:
                if assign[(t, d, "X")] <= a_l:
                    return False
            for t2, c2, p2, _ in self.extras:
                if p2 == c and assign[(t2, "A", c2)] <= a_l:
                    return False
            if parent not in (TILES[t][0], (TILES[t][0][0] + 1, TILES[t][0][1])):
                pa = next(tt for tt in self.extras if tt[1] == parent)
                if assign[(t, "A", parent)] >= a_l:
                    return False
        return True

    def emit(self, c, assign, orient):
        lmax = max(assign.values())
        xm = [P(m) for m, _ in TILES]
        zm = [P((m[0] + 1, m[1])) for m, _ in TILES]
        ex = [P(cc) for _, cc, _, _ in self.extras]
        involved = sorted(set(xm) | set(zm) | set(ex) | set(cp.DATA))
        c.barrier(*involved)
        c.rx(*xm); c.reset(*zm, *ex)
        c.barrier(*involved)
        for a, b in zip(xm, zm):
            c.cx(a, b)
        lastq = {}
        for k, L in assign.items():
            for q in self.qubits_of(k, orient):
                lastq[q] = max(lastq.get(q, 0), L)
        readers = {}
        for t in range(3):
            ax, az = g1.readers(t, orient)
            readers[ax], readers[az] = (t, "X"), (t, "Z")
        for t, cc, _, _ in self.extras:
            readers[cc] = (t, "X")
        self.checks = {}
        for L in range(2, lmax + 2):
            c.barrier(*involved)
            for q, (t, B) in readers.items():
                if lastq.get(q, 1) == L - 1:
                    bit = c.mx(P(q)) if B == "X" else c.measure(P(q))
                    self.checks.setdefault((t, B), []).append(bit)
            for k, LL in sorted(assign.items(), key=lambda kv: str(kv[0])):
                if LL != L:
                    continue
                t, d, typ = k
                if d == "U":
                    ax, az = g1.readers(t, orient)
                    c.cx(P(ax), P(az))
                elif d == "A":
                    parent, cc = self.qubits_of(k, orient)
                    c.cx(P(parent), P(cc))
                elif typ == "X":
                    c.cx(P(self.anc(t, d, typ)), P(d))
                else:
                    c.cx(P(d), P(self.anc(t, d, typ)))
        for (t, B), bits in self.checks.items():
            c.detector(*bits)

    def proxy(self, assign, orient):
        from qcirc import Circ
        from tprep.noise import STANDARD, apply_noise
        from tprep.qasm import to_stim
        c = Circ()
        c.g("id", *proxy2.DATA)
        self.emit(c, assign, orient)
        dets = [d for d in c.detectors]
        nb = c.nbits
        bit_check = {}
        for (t, B), bits in self.checks.items():
            for b in bits:
                bit_check[b] = t if B == "X" else 3 + t
        c.detectors = []
        c = c.rescheduled(lazy_init=True)
        s, err = to_stim(c.text())
        assert not err, err
        noisy = apply_noise(s, 1e-3, STANDARD)
        # records come out in bit order (rescheduling keeps bit numbers; to_stim keeps measure order)
        order = []
        for line in noisy.splitlines():
            if line.startswith(("M ", "MX ")):
                order += [None] * len(line.split()[1:])
        # map record index -> bit: rescheduled ops carry bits in emission order
        bits_in_order = [b for kind, qs, b in c.sops if kind in ("M", "MX")]
        assert len(bits_in_order) == len(order) == nb
        cx = self._full(noisy, bits_in_order, bit_check, "X")
        cz = self._full(noisy, bits_in_order, bit_check, "Z")
        if JOINT:
            return proxy2.joint_loss(cx, cz), None
        out = {}
        for logical, circ, syn in (("X", cx, 0b000111), ("Z", cz, 0b111000)):
            out[logical] = proxy2.loss(circ, syn)
        return out["X"][0] + 0.5 * out["Z"][0] + out["X"][1] + 0.5 * out["Z"][1], out

    def _full(self, noisy, bits_in_order, bit_check, logical):
        stabs = [("X", s) for s in proxy2.SUPPORT] + [("Z", s) for s in proxy2.SUPPORT]
        lines = [proxy2._mpp(B, s) for B, s in stabs] + [proxy2._mpp(logical, proxy2.DATA)]
        lines += [l for l in noisy.splitlines() if not l.startswith(("DETECTOR", "OBSERVABLE"))]
        lines += [proxy2._mpp(B, s) for B, s in stabs] + [proxy2._mpp(logical, proxy2.DATA)]
        nm = len(bits_in_order)
        n = 7 + nm + 7
        rec = lambda i: f"rec[{i - n}]"
        pos = {b: j for j, b in enumerate(bits_in_order)}
        per = {}
        for b, k in bit_check.items():
            per.setdefault(k, []).append(pos[b])
        for k, js in sorted(per.items()):
            lines.append("DETECTOR " + " ".join(rec(7 + j) for j in js) + f" {rec(k)}")
        for k in range(6):
            lines.append(f"OBSERVABLE_INCLUDE({k}) {rec(7 + nm + k)} {rec(k)}")
        lines.append(f"OBSERVABLE_INCLUDE(6) {rec(7 + nm + 6)} {rec(6)}")
        return stim.Circuit("\n".join(lines))

    def cost(self, assign, orient):
        if not self.feasible(assign, orient):
            return None
        try:
            v = self.proxy(assign, orient)[0]
        except ValueError:
            return None
        if UMAX is not None:
            v += 2e-5 * sum(max(0, assign[(t, "U", "")] - UMAX) for t in range(3))
        return v


def start_from(model, base_file, lmax=9, seed=0):
    """Base schedule plus attach layers (and, if needed, served X-ops moved) chosen at random
    until the cycle is feasible and valid."""
    rng = random.Random(seed)
    if base_file.startswith("gen2_"):
        import ast
        _, a, o, _, _ = json.load(open(base_file))[0]
        def key(k):
            t, d, typ = k
            if d in ("U", "A"):
                return (int(t), d, ast.literal_eval(typ) if d == "A" else typ)
            return (int(t), ast.literal_eval(d), typ)
        return {key(k): L for k, L in a}, list(o)
    a0, o = g1.load(base_file)
    for _ in range(20000):
        a = dict(a0)
        for t, c, parent, ds in model.extras:
            a[(t, "A", c)] = rng.randint(2, lmax - 1)
            for d in ds:
                if rng.random() < 0.5:
                    a[(t, d, "X")] = rng.randint(a[(t, "A", c)] + 1, lmax)
        if model.cost(a, o) is not None:
            return a, o
    raise RuntimeError("no feasible start")


def anneal(model, a0, o0, seed, steps, lmax, T0=4e-6, T1=2e-7):
    rng = random.Random(seed)
    assign, orient = dict(a0), list(o0)
    cur = model.cost(assign, orient)
    best = (cur if cur is not None else 1.0, dict(assign), list(orient))
    if cur is None:
        cur = 1.0
    for s in range(steps):
        T = T0 * (T1 / T0) ** (s / steps)
        a2, o2 = dict(assign), list(orient)
        r = rng.random()
        if r < 0.08:
            o2[rng.randrange(3)] ^= 1
        elif r < 0.4:
            k = rng.choice(model.keys)
            a2[k] = rng.randint(2, lmax)
        elif r < 0.6:
            k1, k2 = rng.sample(model.keys, 2)
            a2[k1], a2[k2] = a2[k2], a2[k1]
        else:
            k = rng.choice(model.keys)
            old, L = a2[k], rng.randint(2, lmax)
            qs = set(model.qubits_of(k, o2))
            for k2, L2 in list(a2.items()):
                if k2 != k and L2 == L and qs & set(model.qubits_of(k2, o2)):
                    a2[k2] = old
            a2[k] = L
        c2 = model.cost(a2, o2)
        if c2 is None:
            continue
        if c2 < cur or rng.random() < pow(2.718281828, -(c2 - cur) / T):
            assign, orient, cur = a2, o2, c2
            if cur < best[0]:
                best = (cur, dict(assign), list(orient))
    return best


def _job(args):
    extras, base, seed, steps, lmax = args
    m = Model(extras)
    a0, o0 = start_from(m, base, lmax, seed)
    c, a, o = anneal(m, a0, o0, seed, steps, lmax)
    return c, [[list(map(str, k)), v] for k, v in a.items()], o, seed, extras


if __name__ == "__main__":
    import multiprocessing as mp
    import time
    extras = sys.argv[1].split(",")
    steps, lmax, nch = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    base = sys.argv[5] if len(sys.argv) > 5 else "gen_10_1792739112.json"
    if len(sys.argv) > 7:
        UMAX = int(sys.argv[7])
    with mp.get_context("fork").Pool(nch) as pool:
        seed0 = int(sys.argv[6]) if len(sys.argv) > 6 else 200
        res = pool.map(_job, [(extras, base, seed0 + s, steps, lmax) for s in range(nch)])
    res.sort(key=lambda r: r[0])
    for r in res[:8]:
        print(r[0], r[2], r[3], flush=True)
    json.dump(res, open(f"gen2_{'+'.join(extras)}_{lmax}_{int(time.time())}.json", "w"))
