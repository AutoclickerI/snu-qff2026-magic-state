"""Stage-1 phantom builds of the partially coherent C resources on v36h.

A noiseless phantom map tick T_INS is inserted between old ticks 43 and 44.  At T_INS a phantom block M (one qubit per
site of supp(V), prepared in |V>) applies CX M_i -> C_i: this turns r3's |R_0> into |R_V> exactly (M is then read in X;
its records join the X(V) detectors as a Pauli frame).  The evaluator driver (ev/pcc_eval.py) drops every channel of
T_INS and of M and shortens idle runs that span T_INS by one step, so the build equals v36h + an ideal instantaneous map.

Readout (old tick 45 -> new 46, measurements at 47): on each site i of supp(V) the v36h op (copy edge C_i -> helper,
early M, or C17 -> A16) is replaced by CX R_i -> C_i from a phantom readout block R in |V>, prepared on phantom qubits
in ticks <= 45 (never at T_INS); R is read in X at 47 and C_i in Z at 47.  Sites outside supp(V) keep v36h's ops.
Detectors: C's seven Z rows become a basis of Z(V-perp); copy rows of removed copies are deleted; X(w) rows for a basis
of V = XOR of R and M records over w.  usage: build1.py <V basis masks comma-separated or 0> <out stem>
"""
import sys, json, re, itertools
from pathlib import Path
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/PCC')
from qedit import Circ

BASE = '/home/jihoon/competitions/quantumn/work/lanes/PCC/base/v36h'
C = [12, 25, 19, 17, 5, 29, 28]
CREC = {0: 21, 1: 22, 2: 23, 3: 24, 4: 25, 5: 26, 6: 27}           # C site code index -> its final Z record
COPY = {2: (18, 265), 1: (31, 266), 5: (35, 267), 6: (34, 268)}   # site -> (copy helper, helper record)
A16REC, C17REC = 19, 24
T_INS = 44
MAPQ = [36, 37, 38, 39, 40, 41]
RDQ = [42, 43, 44, 45, 46, 47]
QRE = re.compile(r"q\[(\d+)\]")
CRE = re.compile(r"c\[(\d+)\]")


def span(basis):
    out = {0}
    for b in basis:
        out |= {x ^ b for x in out}
    return sorted(out)


def perp_basis(V):
    """basis of V-perp inside F2^7 (row-reduced)"""
    vs = [x for x in range(128) if all(bin(x & v).count('1') % 2 == 0 for v in V)]
    basis, piv = [], {}
    for x in sorted(vs, key=lambda x: (bin(x).count('1'), x)):
        y = x
        while y:
            h = y.bit_length() - 1
            if h not in piv:
                piv[h] = y
                basis.append(x)
                break
            y ^= piv[h]
    return basis


def block_layers(basis, sites):
    """CX layers preparing |V> on `sites` (code indices) from RX pivots; returns (pivots, [[(src, dst), ...], ...])"""
    k = len(basis)
    if k == 1:
        s = sorted(sites)
        p, a, b, c = s
        return [p], [[(p, a)], [(p, b), (a, c)]]
    w1, w2 = basis
    only1 = sorted(i for i in sites if (w1 >> i & 1) and not (w2 >> i & 1))
    only2 = sorted(i for i in sites if (w2 >> i & 1) and not (w1 >> i & 1))
    both = sorted(i for i in sites if (w1 >> i & 1) and (w2 >> i & 1))
    s1, a1 = only1
    s2, a2 = only2
    r, r2 = both
    return [s1, s2], [[(s1, r)], [(s2, r), (s1, a1)], [(s2, a2), (r, r2)]]


def strip_sites(c, sites, rq, rrec, nb):
    """remove v36h's readout ops of these C sites (ticks 45..47: copy CX, C17->A16, early M, copy helper window), then
    measure each site in Z at 47; with a readout block rq add CX rq_i -> C_i at 46 and MX rq_i at 47 (records from nb)"""
    for i in sites:
        q = C[i]
        for t in (45, 46, 47):
            keep = []
            for g in c.segs[t]:
                qs = set()
                for ln in g:
                    qs.update(map(int, QRE.findall(ln)))
                hit = (q in qs and t >= 46) or (i in COPY and COPY[i][0] in qs and t >= 45)
                if not hit:
                    keep.append(g)
            c.segs[t] = keep
        c.segs[47].append([f'measure q[{q}] -> c[{CREC[i]}];'])
        if rq is not None:
            c.segs[46].append([f'cx q[{rq[i]}],q[{q}];'])
            c.segs[47].append([f'h q[{rq[i]}];', f'measure q[{rq[i]}] -> c[{nb}];'])
            rrec[i] = nb; nb += 1


def fix_dets(dets, sites):
    new = []
    for d in dets:
        if any(i in COPY and COPY[i][1] in d for i in sites):
            continue                                     # copy rows of removed copies
        if 3 in sites and A16REC in d:
            d = d - {C17REC}                             # C17 no longer copied into A16
        new.append(d)
    return new


def build(basis, out, strip=()):
    V = span(basis)
    k = len(basis)
    sup = sorted({i for v in V for i in range(7) if v >> i & 1})
    c = Circ(Path(BASE + '.qasm').read_text())
    assert len(c.segs) == 47
    c.segs.insert(T_INS, [])                       # new ticks: 44 = T_INS, 45 = old 44, 46 = old 45, 47 = old 46
    nb = c.max_creg() + 1
    dets = [set(map(int, CRE.findall(d))) for d in c.dets]
    mrec, rrec = {}, {}
    if k:
        mq = {i: MAPQ[j] for j, i in enumerate(sup)}
        rq = {i: RDQ[j] for j, i in enumerate(sup)}
        # map block |V> on mq, ready by tick 43; CX mq_i -> C_i at T_INS; MX mq at 45
        piv, layers = block_layers(basis, sup)
        t0 = T_INS - len(layers)
        for i in sup:
            c.segs[t0 - 1].append([f'reset q[{mq[i]}];'] + ([f'h q[{mq[i]}];'] if i in piv else []))
        for L, layer in enumerate(layers):
            for s, d in layer:
                c.segs[t0 + L].append([f'cx q[{mq[s]}],q[{mq[d]}];'])
        for i in sup:
            c.segs[T_INS].append([f'cx q[{mq[i]}],q[{C[i]}];'])
            c.segs[T_INS + 1].append([f'h q[{mq[i]}];', f'measure q[{mq[i]}] -> c[{nb}];'])
            mrec[i] = nb; nb += 1
        # readout block |V> on rq, layers in ticks <= 45 skipping T_INS, CX rq_i -> C_i at 46, MX rq at 47
        ticks = [t for t in range(46 - 1, 0, -1) if t != T_INS][:len(layers)][::-1]
        first = {}
        for L, layer in enumerate(layers):
            for s, d in layer:
                first.setdefault(s, ticks[L]); first.setdefault(d, ticks[L])
        for i in sup:
            rt = [t for t in range(first[i] - 1, 0, -1) if t != T_INS][0]
            c.segs[rt].append([f'reset q[{rq[i]}];'] + ([f'h q[{rq[i]}];'] if i in piv else []))
        for L, layer in enumerate(layers):
            for s, d in layer:
                c.segs[ticks[L]].append([f'cx q[{rq[s]}],q[{rq[d]}];'])
        strip_sites(c, sup, rq, rrec, nb)
        nb += len(sup)
        # detectors
        crecs = set(CREC.values())
        new = [d for d in fix_dets(dets, sup) if not d <= crecs]   # C rows: rebuilt below
        for z in perp_basis(V):
            new.append({CREC[i] for i in range(7) if z >> i & 1})
        for w in basis:
            new.append({rrec[i] for i in sup if w >> i & 1} | {mrec[i] for i in sup if w >> i & 1})
        dets = new
    else:
        c.segs[T_INS].append([f'reset q[{MAPQ[0]}];'])   # dummy phantom op: makes T_INS a native step (dropped)
        if strip:                                        # control: copies on these sites removed, no X check
            strip_sites(c, sorted(strip), None, {}, nb)
            dets = fix_dets(dets, strip)
    c.dets = ['// DETECTOR ' + ' '.join(f'c[{b}]' for b in sorted(d)) for d in dets]
    c.header = [h if not h.startswith('creg') else f'creg c[{nb}];' for h in c.header]
    c.header = [h if not h.startswith('qreg') else 'qreg q[48];' for h in c.header]
    for t, seg in enumerate(c.segs):
        seen = set()
        for g in seg:
            qs = set()
            for ln in g:
                qs.update(map(int, QRE.findall(ln)))
            assert not (qs & seen), ('conflict', t, g)
            seen |= qs
    Path(out + '.qasm').write_text(c.text())
    meta = json.loads(Path(BASE + '.json').read_text())
    meta = {'data_qubits': meta['data_qubits'], 'source': 'PCC build1', 'V_basis': basis, 'strip': sorted(strip), 'V': V, 'support': sup,
            'T_INS': T_INS, 'map_qubits': [MAPQ[j] for j in range(len(sup))] if k else [MAPQ[0]],
            'readout_qubits': [RDQ[j] for j in range(len(sup))] if k else []}
    Path(out + '.json').write_text(json.dumps(meta, indent=1))
    return meta


if __name__ == '__main__':
    arg = sys.argv[1]
    basis = [] if arg == '0' else [int(x) for x in arg.split(',')]
    strip = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else []
    print(json.dumps(build(basis, sys.argv[2], strip)))
