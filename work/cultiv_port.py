"""Port of the d=3 injection + double cat check from Gidney, Shutty & Jones, "Magic state
cultivation" (arXiv:2409.17595; code: github.com/Strilanc/magic-state-cultivation, Apache-2.0),
onto the QFF2026 6x6 grid, followed by a superdense color-code cycle on the same layout.

Their Stim chunks are parsed (MPP boundary lines and the noise-free observable bookkeeping
dropped; S/S_DAG on the injection and check replaced by T/T_DAG). DETECTORs are rebuilt by
dropping references to the dropped MPP records; the judge finds their reference values.
"""
import re
import sys

UP = "/home/jihoon/competitions/quantumn/upstream/magic-state-cultivation/src/cultiv/_construction/"

from qcirc import Circ  # noqa: E402

# Steane labels on their coordinates (x, y): S1=T1, S2=T2, S3=T3 (see work notes)
DATA_XY = {0: (0, 0), 1: (2, 3), 2: (1, 1), 3: (4, 0), 4: (3, 0), 5: (3, 2), 6: (2, 1)}


def phys(xy, r0=0, c0=0):
    x, y = xy
    return 6 * (y + r0) + (x + c0)


DATA = [phys(DATA_XY[i]) for i in range(7)]


def extract_chunk(fn_name, path):
    src = open(path).read()
    body = src[src.index(f"def {fn_name}("):]
    body = body[body.index('stim.Circuit("""') + len('stim.Circuit("""'):]
    return body[:body.index('"""')]


def run_chunk(c, text, *, s_to="T", qubits_seen=None, keep_detectors=True):
    """Append a Stim chunk to Circ c. Returns list of (bit) for each measurement in order."""
    coords = {}
    recs = []          # per Stim record: our bit index, or None for dropped MPP records
    for raw in text.splitlines():
        line = raw.split("#")[0].strip()
        if not line or line.startswith("TICK"):
            continue
        m = re.match(r"QUBIT_COORDS\(([\d.]+),\s*([\d.]+)\)\s+(\d+)", line)
        if m:
            coords[int(m.group(3))] = (int(float(m.group(1))), int(float(m.group(2))))
            continue
        name, *args = line.split()
        name = name.split("(")[0]
        if name in ("MPP",):
            recs.append(None)
            continue
        if name == "OBSERVABLE_INCLUDE":
            continue
        if name == "DETECTOR":
            if not keep_detectors:
                continue
            bits = []
            for a in re.findall(r"rec\[-\d+\]", line):
                k = int(a[len("rec[-"):-1])
                b = recs[len(recs) - k]
                if b is not None:
                    bits.append(b)
            if bits:
                c.detector(*bits)
            continue
        qs = [phys(coords[int(a)]) for a in args]
        if name == "R":
            c.reset(*qs)
        elif name == "RX":
            c.rx(*qs)
        elif name == "CX":
            for i in range(0, len(qs), 2):
                c.cx(qs[i], qs[i + 1])
        elif name in ("S_DAG", "S"):
            dag = name == "S_DAG"
            gate = {"T": (c.tdg if dag else c.t), "Tswap": (c.t if dag else c.tdg)}[s_to]
            gate(*qs)
        elif name == "M":
            for q in qs:
                recs.append(c.measure(q))
        elif name == "MX":
            for q in qs:
                recs.append(c.mx(q))
        elif name == "H":
            c.h(*qs)
        else:
            raise ValueError(f"unhandled {name}")
    return recs


def superdense_cycle(c, z_first=True, lockstep=False):
    """Superdense d=3 color code cycle (Gidney & Jones 2023 as built in make_chunk_color_code_
    superdense_cycle): Bell pair per tile (m: X-measure, m+1: Z-measure), X part, Z part, unbell."""
    tiles = [((1, 0), [(3, 0), (0, 0), (1, 1), (2, 1)]),
             ((1, 2), [(3, 2), (1, 1), (2, 3), (2, 1)]),
             ((3, 1), [(2, 1), (3, 2), (3, 0), (4, 0)])]
    P = lambda x, y: phys((x, y))
    xm = [P(*m) for m, _ in tiles]
    zm = [P(m[0] + 1, m[1]) for m, _ in tiles]
    involved = sorted(set(xm) | set(zm) | set(DATA))
    if lockstep:
        c.barrier(*involved)
    c.rx(*xm)
    c.reset(*zm)
    layers = {k: [] for k in range(1, 9)}
    for (mx, my), data in tiles:
        m = (mx, my)
        dset = set(data)
        add = lambda L, a, b, rev=False: (a in dset or b in dset) and layers[L].append((b, a) if rev else (a, b))
        layers[1].append((m, (mx + 1, my)))
        layers[8].append((m, (mx + 1, my)))
        xl, zl = ((5, 6, 7), (2, 3, 4)) if z_first else ((2, 3, 4), (5, 6, 7))
        # X part: ancillas control data
        add(xl[0], (mx, my), (mx - 1, my)); add(xl[0], (mx + 1, my), (mx + 2, my))
        add(xl[1], (mx, my), (mx, my + 1)); add(xl[1], (mx + 1, my), (mx + 1, my + 1))
        add(xl[2], (mx, my), (mx, my - 1)); add(xl[2], (mx + 1, my), (mx + 1, my - 1))
        # Z part: data control ancillas
        add(zl[0], (mx, my), (mx - 1, my), True); add(zl[0], (mx + 1, my), (mx + 2, my), True)
        add(zl[1], (mx, my), (mx, my + 1), True); add(zl[1], (mx + 1, my), (mx + 1, my + 1), True)
        add(zl[2], (mx, my), (mx, my - 1), True); add(zl[2], (mx + 1, my), (mx + 1, my - 1), True)
    for L in range(1, 9):
        if lockstep:
            c.barrier(*involved)
        for a, b in layers[L]:
            c.cx(P(*a), P(*b))
    for q in xm:
        c.detector(c.mx(q))
    for q in zm:
        c.detector(c.measure(q))


def build(stages=("inject", "check", "cycle"), s_to="T", z_first=True, lockstep=False):
    c = Circ()
    if "inject" in stages:
        run_chunk(c, extract_chunk("make_chunk_d3_init_unitary", UP + "_injection_stage.py"), s_to=s_to)
    if "check" in stages:
        run_chunk(c, extract_chunk("make_chunk_d3_double_cat_check", UP + "_cultivation_stage.py"), s_to=s_to)
    if "cycle" in stages:
        superdense_cycle(c, z_first=z_first, lockstep=lockstep)
    return c


if __name__ == "__main__":
    from qcirc import evaluate
    stages = tuple(sys.argv[1].split(",")) if len(sys.argv) > 1 else ("inject", "check", "cycle")
    s_to = sys.argv[2] if len(sys.argv) > 2 else "Tswap"
    shots = int(float(sys.argv[3])) if len(sys.argv) > 3 else 10**6
    z_first = (sys.argv[4] != "xfirst") if len(sys.argv) > 4 else True
    c = build(stages, s_to, z_first=z_first)
    print("stages", stages, "s_to", s_to, "n_2q", c.n_2q(), "data_qubits", DATA)
    evaluate(c.text(), DATA, shots=shots)
