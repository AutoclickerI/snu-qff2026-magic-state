"""Scan tick boundaries for placeable weight-2..4 stabilizer checks with ancillas on non-live cells.
At boundary b (between tick b-1 and b), cells free = status dead/pre/prem at ticks b-1 and b (+ margin m before/after).
For each Z/X stabilizer element (surrogate, weight<=4) of the state after tick b-1, find ancilla sets: each support cell
needs a free neighbour; the chosen ancillas must be connected through free cells (GHZ with relays)."""
import sys, re, itertools
import stim
sys.path.insert(0, '.')
from qedit import load
from gadgets import read, status, ADJ
stem = sys.argv[1]; b0, b1 = int(sys.argv[2]), int(sys.argv[3]); M = int(sys.argv[4]) if len(sys.argv) > 4 else 1
c = load(stem); st = status(read(stem)); T = len(c.segs)
QRE = re.compile(r'q\[(\d+)\]')
sim = stim.TableauSimulator(); sim.set_num_qubits(36)
def gf2(rows):
    piv = {}
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in piv: v ^= piv[h]
            else: piv[h] = v; break
    return piv
def inspan(piv, v):
    while v:
        h = v.bit_length() - 1
        if h not in piv: return False
        v ^= piv[h]
    return True
for t in range(T):
    for g in c.segs[t]:
        for ln in g:
            s = ln.strip(); n = s.split()[0]; qs = [int(x) for x in QRE.findall(s)]
            if n == 'reset': sim.reset(*qs)
            elif n == 'h': sim.h(*qs)
            elif n == 'cx': sim.cnot(*qs)
            elif n == 'measure': sim.measure(qs[0])
    b = t + 1
    if b < b0 or b > b1: continue
    free = {q for q in range(36) if all(st[q][u] in ('dead', 'pre', 'prem') for u in range(max(0, b - M), min(T, b + max(M, 1))))}
    live = {q for q in range(36) if q not in free and st[q][min(b, T - 1)] != 'dead'}
    rows = []
    for p in sim.canonical_stabilizers():
        xs, zs = p.to_numpy()
        rows.append((sum(1 << i for i in range(36) if xs[i]), sum(1 << i for i in range(36) if zs[i])))
    for name, sel in (('Z', 0), ('X', 1)):
        comb = [((a << 64) | bb) if sel == 0 else ((bb << 64) | a) for a, bb in rows]
        piv = {}; sub = []
        for v in comb:
            while v >> 64:
                h = v.bit_length() - 1
                if h in piv: v ^= piv[h]
                else: piv[h] = v; v = None; break
            if v: sub.append(v & ((1 << 64) - 1))
        sp = gf2(sub)
        singles = {q for q in range(36) if inspan(sp, 1 << q)}
        cand = [q for q in sorted(live) if q not in singles]
        found = []
        for w in (2, 3, 4):
            for sup in itertools.combinations(cand, w):
                if any(set(f) <= set(sup) for f in found): continue
                if not inspan(sp, sum(1 << q for q in sup)): continue
                found.append(sup)
                nb = {q: [a for a in ADJ[q] if a in free] for q in sup}
                if not all(nb.values()): continue
                # connectivity of free cells: components
                comp = {}
                for q0 in free:
                    if q0 in comp: continue
                    stack = [q0]; comp[q0] = q0
                    while stack:
                        x = stack.pop()
                        for y in ADJ[x]:
                            if y in free and y not in comp:
                                comp[y] = q0; stack.append(y)
                # need all support cells to have a free neighbour in one common component
                comps = set.intersection(*[{comp[a] for a in nb[q]} for q in sup])
                print(f'b{b} {name} w{w} sup={sup} nb={ {q: nb[q] for q in sup} } onecomp={bool(comps)}')
