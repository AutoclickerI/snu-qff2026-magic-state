"""Schedules for a final round of single-ancilla flagged checks, found by CP-SAT and ranked by the
exact data-side second-order loss (relaxed.loss).

Each check (type X or Z, any weight-4 stabilizer) uses one fresh ancilla that couples to its four
data in four distinct steps; a flag CNOT needs a free ancilla step between the 1st and 2nd and
between the 3rd and 4th couplings. Data do at most one coupling per step. Every X-check / Z-check
pair crosses an even number of times on shared data (commutation). The round has T coupling steps;
all ancillas are read at step T (data idle then).

    python flagsched.py <T> <X check ids> <Z check ids> [solutions]
    check ids index relaxed.W4, e.g. 012 = {0246,1256,3456}
"""
import itertools
import sys

from ortools.sat.python import cp_model

import relaxed as R


def model(T, xs, zs, rng_seed=0):
    m = cp_model.CpModel()
    checks = [("X", k) for k in xs] + [("Z", k) for k in zs]
    tau = {}
    for c in checks:
        for q in sorted(R.W4[c[1]]):
            tau[(q, c)] = m.NewIntVar(0, T - 1, f"t{q}{c}")
    for q in range(7):
        vs = [tau[(q, c)] for c in checks if q in R.W4[c[1]]]
        m.AddAllDifferent(vs)
    for c in checks:
        qs = sorted(R.W4[c[1]])
        s = [m.NewIntVar(0, T - 1, f"s{c}{k}") for k in range(4)]
        m.Add(s[1] >= s[0] + 2)
        m.Add(s[2] >= s[1] + 1)
        m.Add(s[3] >= s[2] + 2)
        x = {(q, k): m.NewBoolVar(f"x{q}{k}{c}") for q in qs for k in range(4)}
        for q in qs:
            m.AddExactlyOne(x[(q, k)] for k in range(4))
            for k in range(4):
                m.Add(tau[(q, c)] == s[k]).OnlyEnforceIf(x[(q, k)])
        for k in range(4):
            m.AddExactlyOne(x[(q, k)] for q in qs)
    for cx in [c for c in checks if c[0] == "X"]:
        for cz in [c for c in checks if c[0] == "Z"]:
            shared = sorted(R.W4[cx[1]] & R.W4[cz[1]])
            bs = []
            for q in shared:
                b = m.NewBoolVar("")
                m.Add(tau[(q, cx)] < tau[(q, cz)]).OnlyEnforceIf(b)
                m.Add(tau[(q, cx)] > tau[(q, cz)]).OnlyEnforceIf(b.Not())
                bs.append(b)
            if len(bs) == 2:
                m.Add(bs[0] == bs[1])
            elif bs:
                par = m.NewIntVar(0, len(bs) // 2, "")
                m.Add(sum(bs) == 2 * par)
    # surrogate: every data qubit's last coupling late (short tails)
    last = []
    for q in range(7):
        lq = m.NewIntVar(0, T - 1, "")
        m.AddMaxEquality(lq, [tau[(q, c)] for c in checks if q in R.W4[c[1]]])
        last.append(lq)
    m.Maximize(sum(last))
    return m, tau, checks


class Collect(cp_model.CpSolverSolutionCallback):
    def __init__(self, tau, checks, limit):
        super().__init__()
        self.tau, self.checks, self.limit, self.sols = tau, checks, limit, []

    def on_solution_callback(self):
        sched = {q: [] for q in range(7)}
        for (q, c), v in self.tau.items():
            sched[q].append((self.Value(v), c, c[0]))
        self.sols.append(sched)
        if len(self.sols) >= self.limit:
            self.StopSearch()


def search(T, xs, zs, n=400, seconds=60):
    m, tau, checks = model(T, xs, zs)
    # first the best surrogate, then enumerate near-optimal solutions
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_workers = 8
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, []
    best_last = int(s.ObjectiveValue())
    m.ClearObjective()
    lastsum = []
    for q in range(7):
        lq = m.NewIntVar(0, T - 1, "")
        m.AddMaxEquality(lq, [tau[(q, c)] for c in checks if q in R.W4[c[1]]])
        lastsum.append(lq)
    m.Add(sum(lastsum) >= best_last - 2)
    s2 = cp_model.CpSolver()
    s2.parameters.enumerate_all_solutions = True
    s2.parameters.max_time_in_seconds = seconds
    cb = Collect(tau, checks, n)
    s2.Solve(m, cb)
    scored = []
    for sched in cb.sols:
        v = R.loss(sched, T, [0] * 7)
        scored.append((v, sched))
    scored.sort(key=lambda r: r[0])
    return best_last, scored


if __name__ == "__main__":
    T = int(sys.argv[1])
    xs = tuple(int(c) for c in sys.argv[2])
    zs = tuple(int(c) for c in sys.argv[3])
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 400
    best_last, scored = search(T, xs, zs, n)
    if not scored:
        print(f"T {T} X {xs} Z {zs}: infeasible")
        sys.exit()
    v, sched = scored[0]
    print(f"T {T} X {xs} Z {zs}: surrogate {best_last}, {len(scored)} solutions, best data-side loss {v:.4e}")
    for q in range(7):
        print(f"  d{q}: " + " ".join(f"t{t}:{typ}{sorted(R.W4[c[1]])}" for t, c, typ in sorted(sched[q])))
