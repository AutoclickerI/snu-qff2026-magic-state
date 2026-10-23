"""Grid layouts for the Steane-type final round (steane.py) on the 6x6 chip.

Code qubit i uses four cells: data d_i, block cells a_i, b_i, c_i with d_i~a_i, d_i~b_i, b_i~c_i
(nearest neighbours). Each block's seven cells must induce a connected subgraph, so its encoder can be
any nearest-neighbour CNOT circuit inside the block. Optional: prefer data cells near given cells
(e.g. where the pre-stage leaves the data), by total Manhattan distance.

    python steane_layout.py [n solutions] [prefer data cells, comma separated, in code order]
"""
import sys

from ortools.sat.python import cp_model

R = C = 6
N = R * C


def nbrs(q):
    r, c = divmod(q, C)
    return [rr * C + cc for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)) if 0 <= rr < R and 0 <= cc < C]


EDGES = [(q, p) for q in range(N) for p in nbrs(q)]          # directed


def solve(prefer=None, n=5, seconds=60, forbid=(), connect="abc", via_free=False, w_free=0):
    """via_free: block k only needs to be connected through its own cells and cells with no role;
    w_free > 0 then charges w_free per free cell a block's connection uses (shorter routing)."""
    free_cost = []
    m = cp_model.CpModel()
    roles = "dabc"
    x = {(k, i, q): m.NewBoolVar(f"x{k}{i}_{q}") for k in roles for i in range(7) for q in range(N)}
    for k in roles:
        for i in range(7):
            m.AddExactlyOne(x[(k, i, q)] for q in range(N))
    for q in range(N):
        m.AddAtMostOne(x[(k, i, q)] for k in roles for i in range(7))
    for q in forbid:
        for k in roles:
            for i in range(7):
                m.Add(x[(k, i, q)] == 0)

    def adj(k1, k2, i):
        # cell of k1_i adjacent to cell of k2_i
        for q in range(N):
            m.AddBoolOr([x[(k2, i, p)] for p in nbrs(q)]).OnlyEnforceIf(x[(k1, i, q)])
    for i in range(7):
        adj("d", "a", i)
        adj("d", "b", i)
        adj("b", "c", i)
    # block connectivity by single-commodity flow from member 0 of the block
    for k in connect:
        inb = [m.NewBoolVar("") for _ in range(N)]
        for q in range(N):
            m.Add(inb[q] == sum(x[(k, i, q)] for i in range(7)))
        root = [x[(k, 0, q)] for q in range(N)]
        mem = inb
        if via_free:
            mem = [m.NewBoolVar("") for _ in range(N)]
            for q in range(N):
                # member of block k, or a cell with no role at all
                if w_free:
                    use = m.NewBoolVar("")
                    free_cost.append(use)
                    m.Add(mem[q] <= inb[q] + use)
                    m.Add(use <= 1 - sum(x[(kk, i, q)] for kk in roles for i in range(7)))
                    m.Add(mem[q] >= inb[q])
                else:
                    m.Add(mem[q] == 1 - sum(x[(kk, i, q)] for kk in roles if kk != k for i in range(7)))
        f = {e: m.NewIntVar(0, 6, "") for e in EDGES}
        for (u, v), fe in f.items():
            m.Add(fe <= 6 * mem[u])
            m.Add(fe <= 6 * mem[v])
        for q in range(N):
            out = sum(f[(q, p)] for p in nbrs(q))
            inn = sum(f[(p, q)] for p in nbrs(q))
            # root supplies 6 units, every other member absorbs one
            m.Add(out - inn == 7 * root[q] - inb[q])
    if prefer:
        cost = []
        for i, pc in enumerate(prefer):
            pr, pcc = divmod(pc, C)
            cost.append(sum(x[("d", i, q)] * (abs(q // C - pr) + abs(q % C - pcc)) for q in range(N)))
        m.Minimize(sum(cost) + w_free * sum(free_cost))
    elif free_cost:
        m.Minimize(sum(free_cost))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_workers = 8
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    lay = {k: [next(q for q in range(N) if s.Value(x[(k, i, q)])) for i in range(7)] for k in roles}
    return lay, (s.ObjectiveValue() if prefer else 0), s.StatusName(st)


def show(lay):
    g = [["  ." for _ in range(C)] for _ in range(R)]
    for k, cells in lay.items():
        for i, q in enumerate(cells):
            g[q // C][q % C] = f" {k}{i}"
    return "\n".join("".join(row) for row in g)


if __name__ == "__main__":
    prefer = [int(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
    res = solve(prefer)
    if res is None:
        print("infeasible")
    else:
        lay, obj, st = res
        print(st, "data move cost", obj)
        print(lay)
        print(show(lay))
