"""CP-SAT layer scheduler for LayoutModel.

The model enumerates all integer layer assignments in a bounded depth, with
resource no-overlap, move precedence, GHZ-tree preparation, and orientation/readout
constraints.  Stim's exact second-order DEM proxy is evaluated on each returned
schedule; CP-SAT is only the candidate generator/feasibility certificate.
"""
from __future__ import annotations
import random
from ortools.sat.python import cp_model
from layout_model import LayoutModel


def make(model: LayoutModel, orient, lmax=9, seed=None, objective='weighted', order_hint=None):
    m = cp_model.CpModel()
    v = {k: m.new_int_var(2, lmax, f'v_{i}') for i, k in enumerate(model.keys)}
    # Every operation uses a physical qubit resource.  No same-layer overlap.
    perq = {}
    for k in model.keys:
        for q in model.qubits_of(k, orient):
            perq.setdefault(q, []).append(k)
    for ks in perq.values():
        m.add_all_different([v[k] for k in ks])
        if order_hint is not None:
            seq = sorted(ks, key=lambda k: order_hint[k])
            for ka, kb in zip(seq, seq[1:]):
                m.add(v[ka] < v[kb])
    # Moves are ordered; data service starts after its final hop.
    for d, path in model.moves.items():
        mk = [v[("M", d, j)] for j in range(2*len(path))]
        for a, b in zip(mk, mk[1:]): m.add(a + 1 < b)
        last = mk[-1]
        for k in model.keys:
            if isinstance(k[0], int) and k[1] == d:
                m.add(v[k] > last)
    # Extra GHZ prep before child prep/service, and vacated source after move.
    for e in model.extras:
        a = v[(e.tile, 'A', e.coord)]
        for d in e.served: m.add(a < v[(e.tile, d, 'X')])
        if e.parent in model._extra_by_coord:
            p = model._extra_by_coord[e.parent]
            m.add(v[(p.tile, 'A', p.coord)] < a)
        if e.coord in model.DATA0 if hasattr(model, 'DATA0') else False:
            pass
        # model.DATA0 is module-level; coordinate lookup avoids extra import.
        from layout_model import DATA0
        if e.coord in DATA0:
            owner = DATA0.index(e.coord)
            if owner not in model.moves: return None
            m.add(v[("M", owner, 2*len(model.moves[owner])-1)] < a)
    # Late Bell preparation is a scheduled operation after all moves vacating
    # either member and before any tile interaction.
    from layout_model import DATA0
    for t in model.late_bell:
        b = v[("B", t, "")]
        for q in model.bells[t]:
            if q in DATA0:
                owner = DATA0.index(q)
                m.add(b > v[("M", owner, 2*len(model.moves[owner])-1)])
        for k in model.keys:
            if k[0] == t and k[1] != "U" and k != ("B",t,""):
                m.add(b < v[k])
    # After unbell only matching-basis work on the corresponding Bell member is legal.
    for t in range(3):
        u = v[(t, 'U', '')]
        ax, az = model.readers(t, orient)
        for k in model.keys:
            if k[0] != t or k[1] == 'U': continue
            qs = model.qubits_of(k, orient)
            if k[1] == 'A':
                if qs[0] == az: m.add(v[k] < u)
                continue
            anc = model.xmem[(t, k[1])] if k[2] == 'X' else model.zmem[(t, k[1])]
            if anc == ax and k[2] != 'X': m.add(v[k] < u)
            if anc == az and k[2] != 'Z': m.add(v[k] < u)
    # Correctness parity constraints: for every ordered tile pair, the number
    # of shared-data crossings X(tile-a) before Z(tile-b) must be even.  This is
    # the standard CNOT commute invariant used by the existing gen2 search.
    from layout_model import PLAQ
    for ta, da in enumerate(PLAQ):
        for tb, db in enumerate(PLAQ):
            terms = []
            for d in set(da) & set(db):
                b = m.new_bool_var(f"par_{ta}_{tb}_{d}")
                m.add(v[(ta, d, 'X')] < v[(tb, d, 'Z')]).only_enforce_if(b)
                m.add(v[(ta, d, 'X')] >= v[(tb, d, 'Z')]).only_enforce_if(~b)
                terms.append(b)
            if terms:
                ev = m.new_int_var(0, len(terms)//2, f"even_{ta}_{tb}")
                m.add(sum(terms) == 2*ev)
    # Randomized linear objectives give distinct certified schedules while staying
    # deterministic for a recorded seed.
    rng = random.Random(seed)
    if objective == 'weighted':
        weights = {k: rng.randint(1, 1000) for k in model.keys}
        # prioritize short depth, then late data/ancilla operations only weakly.
        end = m.new_int_var(2, lmax, 'end')
        m.add_max_equality(end, list(v.values()))
        m.minimize(100000*end + sum(weights[k]*v[k] for k in model.keys))
    elif objective == 'depth':
        end = m.new_int_var(2, lmax, 'end'); m.add_max_equality(end, list(v.values())); m.minimize(end)
    return m, v


def solve(model, orient, lmax=9, seed=0, seconds=2.0, order_hint=None):
    out = make(model, orient, lmax=lmax, seed=seed, order_hint=order_hint)
    if out is None: return None
    m, v = out
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_search_workers = 1
    s.parameters.random_seed = seed
    s.parameters.cp_model_presolve = True
    status = s.solve(m)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    return {k: s.value(var) for k, var in v.items()}, {'status': s.status_name(status), 'objective': s.objective_value, 'bound': s.best_objective_bound}

def cegar(model, orient, lmax=9, seed=0, seconds=1.0, tries=100, hint=None, order_hint=None):
    """CP-SAT + Stim CEGAR: reject schedules whose exact DEM is invalid."""
    out = make(model, orient, lmax=lmax, seed=seed, order_hint=order_hint)
    if out is None: return None
    m, v = out
    if hint:
        for k,val in hint.items():
            if k in v: m.add_hint(v[k], val)
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds=seconds; s.parameters.num_search_workers=1; s.parameters.random_seed=seed
    for j in range(tries):
        status=s.solve(m)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
        a={k:s.value(var) for k,var in v.items()}
        try:
            cost=model.proxy(a,orient)
        except ValueError:
            cost=None
        if cost is not None:
            return a, cost, {'status':s.status_name(status),'objective':s.objective_value,'bound':s.best_objective_bound,'cegar_rejects':j}
        neq=[]
        for i,k in enumerate(model.keys):
            b=m.new_bool_var(f'neq_{j}_{i}')
            m.add(v[k] != a[k]).only_enforce_if(b)
            m.add(v[k] == a[k]).only_enforce_if(~b)
            neq.append(b)
        m.add(sum(neq) >= 1)
    return None
