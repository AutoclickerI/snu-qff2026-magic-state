"""Search per-tile orderings of the superdense cycle's three CX sub-layers (each part) so data
qubits' last X-part and Z-part CNOTs land as late as possible; score the best with the judge."""
import itertools
import sys

import cultiv_port as cp
from qcirc import Circ, evaluate

TILES = [((1, 0), [(3, 0), (0, 0), (1, 1), (2, 1)]),
         ((1, 2), [(3, 2), (1, 1), (2, 3), (2, 1)]),
         ((3, 1), [(2, 1), (3, 2), (3, 0), (4, 0)])]


def groups(m):
    mx, my = m
    # each group: list of (ancilla, data) pairs; ancilla m or m+1
    return [[((mx, my), (mx - 1, my)), ((mx + 1, my), (mx + 2, my))],
            [((mx, my), (mx, my + 1)), ((mx + 1, my), (mx + 1, my + 1))],
            [((mx, my), (mx, my - 1)), ((mx + 1, my), (mx + 1, my - 1))]]


def plan(perms_first, perms_second, first="Z"):
    """layers 2..4: first part, 5..7: second part. perms_*[t] = order of groups for tile t."""
    layers = {L: [] for L in range(2, 8)}
    for t, (m, data) in enumerate(TILES):
        dset = set(data)
        for part, perms, base in ((first, perms_first[t], 2), ("X" if first == "Z" else "Z", perms_second[t], 5)):
            for k, g in enumerate(perms):
                for anc, d in groups(m)[g]:
                    if d in dset:
                        layers[base + k].append((part, anc, d))
    for L, ops in layers.items():
        ds = [d for _, _, d in ops]
        if len(ds) != len(set(ds)):
            return None
    return layers


def tail_cost(layers):
    lastX, lastZ = {}, {}
    for L, ops in layers.items():
        for part, _, d in ops:
            (lastX if part == "X" else lastZ)[d] = max(L, (lastX if part == "X" else lastZ).get(d, 0))
    return sum(2 * (8 - lastX[d]) + (8 - lastZ[d]) for d in lastX)


def emit(c, layers):
    P = lambda xy: cp.phys(xy)
    xm = [P(m) for m, _ in TILES]
    zm = [P((m[0] + 1, m[1])) for m, _ in TILES]
    involved = sorted(set(xm) | set(zm) | set(cp.DATA))
    c.barrier(*involved)
    c.rx(*xm); c.reset(*zm)
    c.barrier(*involved)
    for a, b in zip(xm, zm):
        c.cx(a, b)
    for L in range(2, 8):
        c.barrier(*involved)
        for part, anc, d in layers[L]:
            if part == "X":
                c.cx(P(anc), P(d))
            else:
                c.cx(P(d), P(anc))
    c.barrier(*involved)
    for a, b in zip(xm, zm):
        c.cx(a, b)
    for q in xm:
        c.detector(c.mx(q))
    for q in zm:
        c.detector(c.measure(q))


def build_with(layers):
    c = Circ()
    cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_init_unitary", cp.UP + "_injection_stage.py"), s_to="Tswap")
    cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_double_cat_check", cp.UP + "_cultivation_stage.py"), s_to="Tswap")
    emit(c, layers)
    return c


if __name__ == "__main__":
    shots = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10**6
    top = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    perms = list(itertools.permutations(range(3)))
    cands = []
    for first in ("Z", "X"):
        for pf in itertools.product(perms, repeat=3):
            for ps in itertools.product(perms, repeat=3):
                lay = plan(pf, ps, first)
                if lay:
                    cands.append((tail_cost(lay), first, pf, ps, lay))
    cands.sort(key=lambda x: x[0])
    print(len(cands), "valid orderings; best tail costs", [x[0] for x in cands[:10]])
    seen = set()
    shown = 0
    for cost, first, pf, ps, lay in cands:
        key = (cost, first)
        if key in seen:
            continue
        seen.add(key)
        c = build_with(lay)
        r = evaluate(c.text(), cp.DATA, shots=shots, quiet=True)
        print(f"tail {cost} first={first} pf={pf} ps={ps}: 1-F={r['score']:.4g} ± {r['sem']:.2g} acc={r['acc']:.3f} c1={r.get('c1')}", flush=True)
        shown += 1
        if shown >= top:
            break
