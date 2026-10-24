"""Exact boundary decomposition of block A's encoder on a fixed exterior (v36c family).

The A encoder region (every noise channel on A cells after each cell's release measurement and before
its D->A CX) talks to the rest of the circuit only through the Pauli error on A at the cut just before
D->A. Modulo the stabilizers of |+_L> that error has 7 bits:
    class = sx | sz << 3 | l << 6     (X syndrome, Z syndrome, Z_L bit = parity of Z on code positions {0,1,2}).
In-region check records (q16's MX known-X check) are flipped only by region faults, so a region fault
distribution P(class, side) enters the all-orders expectation only through P~(c) = P(c, side = 0):
    acceptance = sum_c P~(c) A_c,  loss = sum_c P~(c) N_c / sum_c P~(c) A_c
with A_c, N_c = all-orders acceptance / loss numerator of the rest with class c injected deterministically.
Rest faults that flip a measured-input record (c57 on q15, c64 on q1) are written in the compensated detector
basis (A rows XOR that record), which is encoder independent and spans the same detector group.
"""
import sys, json, math, re
from pathlib import Path
from collections import defaultdict
import numpy as np

ROOT = Path('/home/jihoon/competitions/quantumn')
SP = ROOT / 'work/lanes/MAIN/sparse'
sys.path.insert(0, str(SP))
import frontend as fa
import sparse_walsh as sw
from judge_subset.noise import noise_blocks, schedule

A = [1, 14, 8, 9, 2, 16, 15]          # code order
DATA = [0, 20, 7, 10, 3, 22, 21]
POS = {q: i for i, q in enumerate(A)}
HAM = [[0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6]]
XL = [0, 1, 2]                          # X_L / Z_L representative support
FLAG = [2, 3, 6]                        # X8 X9 X15


def syn(bits):
    return sum(1 << k for k, S in enumerate(HAM) if sum((bits >> i) & 1 for i in S) & 1)


def cls(ex, ez):
    """7-bit class of a Pauli (ex, ez as 7-bit masks over code positions)."""
    l = sum((ez >> i) & 1 for i in XL) & 1
    return syn(ex) | (syn(ez) << 3) | (l << 6)


def rep(c):
    """Canonical representative (ex, ez) of class c."""
    sx, sz, l = c & 7, (c >> 3) & 7, c >> 6
    ex = (1 << (sx - 1)) if sx else 0
    ez = (1 << (sz - 1)) if sz else 0
    if (sum((ez >> i) & 1 for i in XL) & 1) != l:
        ez ^= sum(1 << i for i in XL)
    assert cls(ex, ez) == c
    return ex, ez


def flag_bit(c):
    ex, ez = rep(c)
    return sum((ez >> i) & 1 for i in FLAG) & 1


# ---------------------------------------------------------------- instrumented frontend model
def make_model_snap(ops, dets, snaps):
    """frontend.make_model with snapshots: snaps = {(ii, 'pre'|'post'): [(q, 'X'|'Z'), ...]} returns pulled-back
    Paulis (x, z, coef, m) at those points (m = number of rotations before)."""
    text, labels = fa.native_text(ops)
    prog, blocks = noise_blocks(text, .001, first_order=False)
    n = 36 + sum(len(ins.qubits) for ins in prog if ins.name in ('R', 'RX', 'M', 'MX'))
    mul, comm = fa.mul, fa.comm
    xs = [(1 << i, 0, 1) for i in range(n)]; zs = [(0, 1 << i, 1) for i in range(n)]
    wire = list(range(36)); nxt = 36; records = {}; rots = []; faults = []; chans = []
    got = {}

    def cx(c, t):
        xs[c] = mul(xs[c], xs[t]); zs[t] = mul(zs[c], zs[t])

    def pull(P):
        x, z, coef = P; out = (0, 0, coef)
        while x:
            bit = x & -x; x ^= bit; out = mul(out, xs[bit.bit_length() - 1])
        while z:
            bit = z & -z; z ^= bit; out = mul(out, zs[bit.bit_length() - 1])
        return out

    def physical(qs, pauli):
        x = z = 0; co = 1
        for q, P in zip(qs, pauli):
            if P in 'XY': x |= 1 << wire[q]
            if P in 'YZ': z |= 1 << wire[q]
            if P == 'Y': co *= 1j
        return x, z, co

    def snap(key):
        for q, P in snaps.get(key, []):
            got[(key, q, P)] = pull(physical([q], P)) + (len(rots),)

    def channel(line, ii, jl):
        if '(' not in line: return
        head, rest = line.split(')', 1); name, pr = head.split('('); pr = float(pr)
        qs = list(map(int, rest.split())); arity = 2 if name == 'DEPOLARIZE2' else 1
        comps = {'X_ERROR': ['X'], 'Z_ERROR': ['Z'], 'DEPOLARIZE1': list('XYZ'),
                 'DEPOLARIZE2': [a + b for a in 'IXYZ' for b in 'IXYZ' if a + b != 'II']}[name]
        for k in range(0, len(qs), arity):
            grp = qs[k:k + arity]; cid = len(chans)
            chans.append(dict(name=name, p=pr, qs=grp, ins=ii, jl=jl))
            for pauli in comps:
                x, z, co = pull(physical(grp, pauli))
                faults.append(dict(x=x, z=z, p=pr / len(comps), m=len(rots), chan=cid, pauli=pauli, qs=grp, ins=ii, jl=jl))
    for ii, (ins, block) in enumerate(zip(prog, blocks)):
        k = block.index(ins.text)
        snap((ii, 'pre'))
        for jl, line in enumerate(block[:k]): channel(line, ii, jl)
        name = ins.name; qs = ins.qubits
        if name in ('R', 'RX'):
            for q in qs:
                wire[q] = nxt; nxt += 1
                if name == 'RX': xs[wire[q]], zs[wire[q]] = zs[wire[q]], xs[wire[q]]
        elif name in ('M', 'MX'):
            q = qs[0]; w = nxt; nxt += 1
            if name == 'MX': xs[wire[q]], zs[wire[q]] = zs[wire[q]], xs[wire[q]]
            cx(wire[q], w)
            if name == 'MX': xs[wire[q]], zs[wire[q]] = zs[wire[q]], xs[wire[q]]
            records[labels[ii].bit] = w
        elif name == 'CX': cx(*[wire[q] for q in qs])
        elif name == 'H':
            for q in qs: xs[wire[q]], zs[wire[q]] = zs[wire[q]], xs[wire[q]]
        elif name in ('T', 'T_DAG'):
            for q in qs:
                x, z, co = zs[wire[q]]
                rots.append((x, z, co, (-1 if name == 'T' else 1) * math.pi / 8, ii))
        elif name != 'I': raise ValueError(name)
        snap((ii, 'post'))
        for jl in range(k + 1, len(block)): channel(block[jl], ii, jl)
    assert nxt == n

    def par(bits):
        z = 0
        for bit in bits: z ^= 1 << records[bit]
        return 0, z, 1
    proj = [pull(par(row)) for row in dets]
    gens = [physical([fa.DATA[i] for i in sorted(S)], P * len(S)) for P in 'XZ' for S in fa.SUPPORTS]
    X7 = physical(fa.DATA, 'X' * 7); Z7 = physical(fa.DATA, 'Z' * 7); Y7 = physical(fa.DATA, 'Y' * 7)
    sig = [pull(g) for g in gens] + [pull(X7), pull(Z7), (0, 0, 1), (0, 0, 1)]
    Q = {}
    for T, L in [('X', X7), ('Y', Y7)]:
        for a in range(8):
            for b in range(8):
                if T == 'X' and b: continue
                ps = (0, 0, 1)
                for i, g in enumerate(gens):
                    if (a | (b << 3)) >> i & 1: ps = mul(ps, g)
                Q[T, a, b] = pull(mul(ps, L))

    def signature(F, m):
        Fx = (F[0], F[1])
        return dict(s=sum(comm(Fx, r) << j for j, r in enumerate(rots) if j >= m),
                    d=sum(comm(Fx, v) << j for j, v in enumerate(proj)),
                    e=sum(comm(Fx, v) << j for j, v in enumerate(sig)))
    for f in faults:
        f.update(signature((f['x'], f['z']), f['m']))
    from types import SimpleNamespace
    model = SimpleNamespace(rots=rots, proj_m=proj, Q=Q, cz=0, cxz=0, proj_v=[None] * len(proj), n_post=0,
                            faults=faults, chans=chans)
    model.gen_m = [pull(g) for g in gens]; model.native = text; model.labels = labels; model.dets = dets
    model.record_ps = {bit: pull((0, 1 << w, 1)) for bit, w in records.items()}
    for f in faults:
        F = (f['x'], f['z'])
        f['record_flips'] = [bit for bit, P in model.record_ps.items() if comm(F, P)]
    model.snaps = {k: dict(signature(v, v[3]), x=v[0], z=v[1]) for k, v in got.items()}
    model.prog, model.blocks = prog, blocks
    return model


def channel_meta(m):
    """Per channel: kind (pre/post/idle), t0, n, qs, op name."""
    prog, blocks = m.prog, m.blocks
    _, steps, gaps = schedule(m.native)
    gaps_by_ins = defaultdict(list)
    for g in gaps: gaps_by_ins[g[0]].append(g)
    out = []
    for c in m.chans:
        ii, jl = c['ins'], c['jl']
        block = blocks[ii]; ins = prog[ii]; k = block.index(ins.text)
        nidle = len(gaps_by_ins.get(ii, []))
        lab = m.labels[ii]
        d = dict(qs=tuple(c['qs']), op=ins.name, t0=lab.time, n=1, ins=ii)
        if jl >= len(block) - nidle:
            g = gaps_by_ins[ii][jl - (len(block) - nidle)]
            d.update(kind='idle', t0=g[2], n=g[3])
        elif jl < k:
            d['kind'] = 'pre'
        else:
            d['kind'] = 'post'
        out.append(d)
    return out


# ---------------------------------------------------------------- the v36c exterior
REL = {1: 37, 2: 35, 8: 35, 9: 37, 14: 36, 15: 39, 16: 37}     # release measurement tick per A cell
DA = {q: 44 for q in A}; DA[9] = 43; DA[15] = 43                  # D->A tick per A cell
MREUSE = {15: 57, 1: 64}                                          # measured inputs used by v36c's encoder (record)


def region_channel(md, rel=REL):
    qs = md['qs']
    if not all(q in POS for q in qs): return False
    for q in qs:
        if not (rel[q] <= md['t0'] < DA[q]): return False
        if md['t0'] == rel[q] and md['kind'] == 'pre': return False     # the release measurement's flip
    return True


class Exterior:
    """Rest-of-circuit model with the A region removed, in the compensated basis, plus boundary signatures."""

    def __init__(self, stem, check_rows=(64,), rel=None, mreuse=None):
        stem = Path(stem)
        self.rel = dict(REL) if rel is None else rel
        self.mreuse = dict(MREUSE) if mreuse is None else mreuse
        MR_ = self.mreuse
        text = stem.with_suffix('.qasm').read_text()
        fa.DATA = json.loads(stem.with_suffix('.json').read_text())['data_qubits']
        ops, dets = fa.parse_current(text)
        self.ops, self.dets = ops, dets
        # snapshot points
        snaps = defaultdict(list)
        self.cut = {}
        for ii, op in enumerate(ops):
            if op.kind == 'CX' and op.qs[1] in POS and op.qs[0] == DATA[POS[op.qs[1]]] and op.time == DA[op.qs[1]]:
                for P in 'XZ': snaps[(ii, 'pre')].append((op.qs[1], P))
                self.cut[op.qs[1]] = ii
            if op.kind == 'M' and op.qs[0] in MR_ and op.bit == MR_[op.qs[0]]:
                for P in 'XZ': snaps[(ii, 'post')].append((op.qs[0], P))
                self.cut[('in', op.qs[0])] = ii
        assert len([k for k in self.cut if not isinstance(k, tuple)]) == 7, self.cut
        m = make_model_snap(ops, dets, snaps)
        eng = fa.Engine(m)
        changes = sw.canonicalize_detector_rows(m, eng)
        if changes: eng = fa.Engine(m)
        m.detector_row_changes = changes
        self.changes = changes
        self.m, self.eng = m, eng
        # boundary basis signatures: X / Z on each code position at the cut
        def sg(key):
            s = m.snaps[key]
            d = s['d']
            # apply canonicalisation row changes to snapshot signatures too
            for i, mask in changes.items():
                d = (d & ~(1 << i)) | (((s['d'] & mask).bit_count() % 2) << i)
            return d, s['s'], s['e']
        self.bx, self.bz = [], []
        for q in A:
            ii = self.cut[q]
            self.bx.append(sg(((ii, 'pre'), q, 'X')))
            self.bz.append(sg(((ii, 'pre'), q, 'Z')))
        self.inx = {q: sg(((self.cut[('in', q)], 'post'), q, 'X')) for q in MR_}
        self.inz = {q: sg(((self.cut[('in', q)], 'post'), q, 'Z')) for q in MR_}
        self.meta = channel_meta(m)
        self.region = {c for c, md in enumerate(self.meta) if region_channel(md, self.rel)}
        self.check_rows = set(check_rows)

    def sig_of(self, ex, ez):
        d = s = e = 0
        for i in range(7):
            if ex >> i & 1:
                d ^= self.bx[i][0]; s ^= self.bx[i][1]; e ^= self.bx[i][2]
            if ez >> i & 1:
                d ^= self.bz[i][0]; s ^= self.bz[i][1]; e ^= self.bz[i][2]
        return d, s, e

    def rest_groups(self):
        """Fault groups of the rest: region channels removed, measured-input record flips compensated."""
        groups = defaultdict(list)
        nflip = 0
        for f in self.m.faults:
            if f['chan'] in self.region: continue
            g = dict(f)
            for q, bit in self.mreuse.items():
                if bit in f['record_flips']:
                    d, s, e = self.inx[q]
                    g['d'] ^= d; g['s'] ^= s; g['e'] ^= e
                    nflip += 1
            assert not any((g['d'] >> r) & 1 for r in self.check_rows), ('rest fault flips an in-region check row', f)
            groups[f['chan']].append(g)
        self.nflip = nflip
        return groups
