"""Low-weight Z-type and X-type stabilizers of the T->I surrogate state after each tick of a full-barrier circuit.
usage: stabt.py <stem> t0 t1 [maxw]"""
import sys, re, itertools
import numpy as np, stim
sys.path.insert(0, '.')
from qedit import load
c = load(sys.argv[1]); t0, t1 = int(sys.argv[2]), int(sys.argv[3]); MW = int(sys.argv[4]) if len(sys.argv) > 4 else 4
QRE = re.compile(r'q\[(\d+)\]')
sim = stim.TableauSimulator()
sim.set_num_qubits(36)
def run_seg(seg):
    for g in seg:
        for ln in g:
            s = ln.strip(); n = s.split()[0]; qs = [int(x) for x in QRE.findall(s)]
            if n == 'reset': sim.reset(*qs)
            elif n == 'h': sim.h(*qs)
            elif n == 'cx': sim.cnot(*qs)
            elif n == 'measure': sim.measure(qs[0])
            elif n in ('t', 'tdg', 'id'): pass
            else: raise ValueError(s)
def gf2_basis(rows):
    piv = {}
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in piv: v ^= piv[h]
            else: piv[h] = v; break
    return list(piv.values())
for t in range(len(c.segs)):
    run_seg(c.segs[t])
    if t < t0 or t > t1: continue
    st = sim.canonical_stabilizers()
    rows = []
    for p in st:
        xs, zs = p.to_numpy()
        rows.append((int(''.join('1' if b else '0' for b in xs[::-1]), 2), int(''.join('1' if b else '0' for b in zs[::-1]), 2)))
    # Z-type subgroup: combos with x == 0; solve via elimination on x part (append z as payload)
    def subgroup(rows, sel):
        # sel=0: Z-type (x==0), sel=1: X-type (z==0)
        comb = [((a << 64) | b) if sel == 0 else ((b << 64) | a) for a, b in rows]
        piv = {}
        out = []
        for v in comb:
            while v >> 64:
                h = v.bit_length() - 1
                if h in piv: v ^= piv[h]
                else: piv[h] = v; v = None; break
            if v is not None and v:
                out.append(v & ((1 << 64) - 1))
        return gf2_basis(out)
    for sel, name in ((0, 'Z'), (1, 'X')):
        B = subgroup(rows, sel)
        singles = {v.bit_length() - 1 for v in B if v.bit_count() == 1}
        # reduce: enumerate combos of basis vectors is exponential; instead search low weight via supports
        span = {}
        for v in B:
            vv = v
            while vv:
                h = vv.bit_length() - 1
                if h in span: vv ^= span[h]
                else: span[h] = vv; break
        def inspan(v):
            while v:
                h = v.bit_length() - 1
                if h not in span: return False
                v ^= span[h]
            return True
        cand = [q for q in range(36) if q not in singles]
        found = []
        for w in range(2, MW + 1):
            for sup in itertools.combinations(cand, w):
                v = sum(1 << q for q in sup)
                if inspan(v) and not any(set(f) <= set(sup) for f in found):
                    found.append(sup)
        print(t, name, ' '.join('{' + ','.join(map(str, f)) + '}' for f in found))
