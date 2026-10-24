"""Block-A encoder specs, their judge noise, and the exact boundary class distribution.

spec = dict(init={cell: (kind, t)}, cx=[(t, c, t)], checks=[(t, cell)] optional)
  kind 'R'  : reset |0> at t (X_ERROR p after)              -> Z input
  kind 'RX' : reset |+> at t (Z_ERROR p after)              -> X pivot
  kind 'MR' : reuse the release Z measurement at REL[cell] (DEPOLARIZE1 p after it; idle charged) -> Z input
  checks    : MX known-X check of a pivot at t (Z_ERROR p before: record flip, DEPOLARIZE1 p after)
The cut is just before each cell's D->A CX at DA[cell]. Group element = class | side << 7 (side bit k = check k).
"""
import numpy as np
from bmodel import A, POS, HAM, REL, DA, cls

P = 1e-3
EDGES = {(1, 2), (2, 8), (8, 9), (8, 14), (9, 15), (14, 15), (15, 16)}
EDGES |= {(b, a) for a, b in EDGES}
TARGET_X = None
UREL = {8: 34, 9: 36, 15: 38, 16: 36}      # last hop CX on each hop source (source check dropped)


def idle_q(n, p=P):
    return 0.75 * (1 - (1 - 4 * p / 3) ** n)


def xspace_ok(spec):
    """Noiseless check: the encoder prepares |+_L> (CSS: X space = span(HAM rows, X_L))."""
    vecs = []
    for q, (k, t) in spec['init'].items():
        if k == 'RX':
            vecs.append(1 << POS[q])
    for t, c, tg in sorted(spec['cx']):
        for i, v in enumerate(vecs):
            if v >> POS[c] & 1:
                vecs[i] = v ^ (1 << POS[tg])
    want = [sum(1 << i for i in S) for S in HAM] + [0b111]

    def rank(vs):
        vs = list(vs); r = 0
        for b in range(7):
            piv = next((i for i in range(r, len(vs)) if vs[i] >> b & 1), None)
            if piv is None: continue
            vs[r], vs[piv] = vs[piv], vs[r]
            for i in range(len(vs)):
                if i != r and vs[i] >> b & 1: vs[i] ^= vs[r]
            r += 1
        return r
    return len(vecs) == 4 and rank(vecs) == 4 and rank(vecs + want) == 4


def legal(spec):
    """Timing / adjacency / window checks. Returns None or a reason."""
    busy = {}
    def use(q, t):
        if (q, t) in busy: return f'two ops on {q} at {t}'
        busy[(q, t)] = 1
    for q, (k, t) in spec['init'].items():
        if k in ('MR', 'U'):
            if t != (REL[q] if k == 'MR' else UREL[q]): return f'{k} at wrong tick {q}'
        else:
            if t <= (UREL[q] if q in spec.get('drop', ()) else REL[q]): return f'init before release {q}'
            use(q, t)
    for t, q in spec.get('checks', []):
        use(q, t)
        if spec['init'][q][0] != 'RX': return 'check on non-pivot'
    first = {}
    for t, c, tg in spec['cx']:
        if (c, tg) not in EDGES: return f'non-edge {c}-{tg}'
        for q in (c, tg):
            use(q, t)
            if t >= DA[q]: return f'gate after D->A on {q}'
            if t <= spec['init'][q][1]: return f'gate before init on {q}'
            if spec['init'][q][0] in ('R', 'RX') and spec['init'][q][1] <= (UREL[q] if q in spec.get('drop', ()) else REL[q]):
                return f'reset before release {q}'
    for t, q in spec.get('checks', []):
        if any(tt <= t for tt, c, tg in spec['cx'] if q in (c, tg)): return 'check after a gate'
        if t <= spec['init'][q][1]: return 'check before init'
    if not xspace_ok(spec): return 'wrong state'
    return None


def channels(spec, p=P):
    """List of channels; each a list of (pauli dict {cell: 'X'|'Y'|'Z'}, time, prob, side_flip_before) where the
    Pauli sits just after `time` (side_flip_before: record bits flipped directly)."""
    chans = []
    checks = sorted(spec.get('checks', []))
    for q, (k, t) in spec['init'].items():
        if k == 'R': chans.append([({q: 'X'}, t, p)])
        elif k == 'RX': chans.append([({q: 'Z'}, t, p)])
        elif k == 'MR': chans.append([({q: P_}, t, p / 3) for P_ in 'XYZ'])
        elif k == 'U': pass                                  # hop source used unmeasured: its noise is outside
    for t, q in checks:
        chans.append([({q: 'Z'}, t - 0.5, p)])            # Z_ERROR before the MX (flips it, persists)
        chans.append([({q: P_}, t, p / 3) for P_ in 'XYZ'])
    for t, c, tg in spec['cx']:
        ch = []
        for a in 'IXYZ':
            for b in 'IXYZ':
                if a + b == 'II': continue
                d = {}
                if a != 'I': d[c] = a
                if b != 'I': d[tg] = b
                ch.append((d, t, p / 15))
        chans.append(ch)
    # idles: ops per cell
    for q in A:
        k, t0 = spec['init'][q]
        ops = [(t0, k)]
        ops += [(t, 'C') for t, c, tg in spec['cx'] if q in (c, tg)]
        ops += [(t, 'MX') for t, qq in checks if qq == q]
        ops.append((DA[q], 'DA'))
        ops.sort()
        for (ta, ka), (tb, kb) in zip(ops, ops[1:]):
            n = tb - ta - 1
            if n > 0:
                chans.append([({q: P_}, ta, idle_q(n, p) / 3) for P_ in 'XYZ'])
    return chans


def propagate(spec):
    """Function (pauli dict, time) -> group element (class | side << 7)."""
    cx = sorted(spec['cx'])
    checks = sorted(spec.get('checks', []))
    events = [(t, 0, ('C', c, tg)) for t, c, tg in cx] + [(t, 1, ('M', q, i)) for i, (t, q) in enumerate(checks)]
    events.sort()

    def f(pauli, time):
        ex = ez = 0
        for q, P_ in pauli.items():
            if P_ in 'XY': ex |= 1 << POS[q]
            if P_ in 'YZ': ez |= 1 << POS[q]
        side = 0
        for t, _, ev in events:
            if t <= time: continue
            if ev[0] == 'C':
                _, c, tg = ev
                ic, it = POS[c], POS[tg]
                if ex >> ic & 1: ex ^= 1 << it
                if ez >> it & 1: ez ^= 1 << ic
            else:
                _, q, i = ev
                if ez >> POS[q] & 1: side ^= 1 << i
        return cls(ex, ez) | (side << 7)
    return f


def distribution(spec, p=P):
    """Exact distribution over group elements (class | side << 7) of all region faults (XOR convolution)."""
    k = len(spec.get('checks', []))
    G = 1 << (7 + k)
    f = propagate(spec)
    # Walsh-Hadamard: characteristic function of each channel, multiplied
    y = np.arange(G)
    logabs = np.zeros(G)
    sign = np.ones(G)
    for ch in channels(spec, p):
        tot = sum(pr for _, _, pr in ch)
        chi = np.full(G, 1 - tot)
        for pauli, t, pr in ch:
            g = f(pauli, t)
            chi += pr * (1 - 2 * (np.bitwise_count(y & g) & 1).astype(np.int64))
        sign *= np.sign(chi)
        logabs += np.log(np.abs(chi))
    prod = sign * np.exp(logabs)
    # inverse WHT
    a = prod.copy(); h = 1
    while h < G:
        a = a.reshape(-1, 2 * h); l = a[:, :h].copy(); r = a[:, h:].copy()
        a[:, :h] = l + r; a[:, h:] = l - r; a = a.reshape(-1); h *= 2
    return a / G


def ptilde(spec, p=P):
    """P~(c) = P(class c, all in-region checks silent)."""
    return distribution(spec, p)[:128]


def first_order(spec, p=P):
    """List of (group element, prob) for every single fault (diagnostics)."""
    f = propagate(spec)
    out = []
    for ch in channels(spec, p):
        for pauli, t, pr in ch:
            out.append((f(pauli, t), pr, pauli, t))
    return out


# v36c's encoder (SEPBC checked16_timing_0 lineage)
V36C = dict(
    init={8: ('RX', 36), 2: ('R', 36), 14: ('RX', 37), 9: ('RX', 38), 1: ('MR', 37), 15: ('MR', 39), 16: ('RX', 39)},
    checks=[(40, 16)],
    cx=[(37, 8, 2), (38, 2, 1), (38, 14, 8), (39, 1, 2), (39, 9, 8), (40, 8, 2), (40, 9, 15), (41, 8, 9),
        (41, 16, 15), (42, 9, 8), (42, 15, 14), (43, 14, 8)])
