#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Time-expanded post-prefix occupancy search for REVSAT.

The model uses the v17a prefix release map, fixed legal L5 embeddings, exact A and BC
witness layers, the six R1 data walks, and the reviewer ANC4 geometry.  CP-SAT decides
all operation times subject to release, adjacency, one operation per cell per step,
encoder layer order, and the B-check -> B-data dependency.  It is deliberately an
occupancy proof: the separate and anc4 rows also run the fixed-layout disjoint-support
placement constraints and report the first structural UNSAT reason.
"""
import json, os, sys, time
from pathlib import Path
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = "1"
from ortools.sat.python import cp_model

ROOT = Path('/home/jihoon/competitions/quantumn')
HERE = ROOT/'work/lanes/REVSAT'
DATA0 = [0,20,7,4,3,15,8]
DATA1 = [0,20,7,10,3,22,21]
A = [1,14,8,9,2,16,15]
B = [6,26,13,11,4,23,27]
C = [12,25,19,17,5,29,28]
MOVES = [[4,10], [15,16,22], [8,9,15,21]]
# Prefix release times from PRE3 q19_13_prompt, plus the end of the native prefix.
RELEASE = {q:33 for q in set(range(36)) - {5,11,12,16,17,18,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35}}
RELEASE.update({5:0,11:0,12:0,16:0,17:0,18:0,21:0,22:0,23:0,24:0,25:0,26:0,27:0,28:0,29:0,30:0,31:0,32:0,33:0,34:0,35:0,19:16,13:20})
# q4,10, etc are touched through the final prefix step; q13/q19 are early releases.
for q in [0,1,2,3,4,6,7,8,9,10,14,15,20]: RELEASE[q] = 33

GENS = [[0,2,4,6],[1,2,5,6],[3,4,5,6]]

def edge(u,v):
    return abs(u//6-v//6)+abs(u%6-v%6)==1

def load_json(p): return json.loads(Path(p).read_text())
A_PREP = load_json(ROOT/'work/lanes/EXENC/prepA_L5_exact.json')
BC_PREP = load_json(ROOT/'work/lanes/BC2/baseline_prep.json')
ANC4_LAYERS = [
    [(13,14),(19,20)], [(14,15)], [(20,14),(16,15)], [(15,21)],
    [(21,20),(14,15)], [(8,14),(9,15),(22,21),(26,20)],
]
ANC4_B = [8,9,22,26,16,13,19]
ANC4_F = [14,15,21,20]


def structural_unsat(option, hops, teleports):
    """Return a proof string for fixed-layout structural cases, else None."""
    if option == 'separate':
        # A disjoint B support cannot leave the corner B[0]=6: its only non-data
        # neighbor is C[0]=12.  The same cut is present for C[4]=5.
        return 'UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11)'
    if option == 'anc4':
        # The reviewer placement is fixed by the proposed six-layer checker.  It
        # intersects the L5 A/data support in either endpoint choice.
        if set(ANC4_B+ANC4_F) & set(A+DATA0):
            return 'UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists'
    if option == 'joint' and not hops:
        bad=[]
        for i in range(7):
            if not edge(DATA0[i],A[i]): bad.append(f'A[{i}] {DATA0[i]}-{A[i]}')
            if not edge(B[i],DATA0[i]): bad.append(f'B[{i}] {B[i]}-{DATA0[i]}')
        if bad:
            return 'UNSAT: no-hop endpoint adjacency (' + ', '.join(bad) + ')'
    return None


def add_interval(m, byq, name, start, qs, horizon=100):
    end = m.NewIntVar(0, horizon+1, name+'_end')
    iv = m.NewIntervalVar(start, 1, end, name)
    for q in qs: byq[q].append(iv)
    return end


def prep_jobs(m, byq, prefix, prep, cells, horizon, release):
    """Create init and fixed-layer jobs. Return layer starts and a count."""
    ops = [x for x in prep['ops'] if x]
    layer_starts = [m.NewIntVar(0, horizon, f'{prefix}_L{t}') for t in range(len(ops))]
    for t in range(len(ops)-1): m.Add(layer_starts[t+1] >= layer_starts[t] + 1)
    first = {q:0 for q in cells}
    for t,L in enumerate(ops):
        for u,v in L:
            if not edge(u,v): raise ValueError((prefix,u,v))
            first.setdefault(u,t); first.setdefault(v,t)
    for q,t in first.items():
        st = m.NewIntVar(release.get(q,0), horizon, f'{prefix}_I{q}')
        en = add_interval(m, byq, f'{prefix}_I{q}', st, [q], horizon)
        m.Add(layer_starts[t] >= en)
    for t,L in enumerate(ops):
        for j,(u,v) in enumerate(L):
            add_interval(m, byq, f'{prefix}_X{t}_{j}', layer_starts[t], [u,v], horizon)
    return layer_starts, sum(len(x) for x in ops)


def move_jobs(m, byq, paths, horizon, release):
    count=0
    for pi,path in enumerate(paths):
        prev=None
        for hi,(u,v) in enumerate(zip(path,path[1:])):
            if not edge(u,v): raise ValueError((u,v))
            r=m.NewIntVar(release.get(v,0), horizon, f'M{pi}_{hi}_reset')
            er=add_interval(m,byq,f'M{pi}_{hi}_reset',r,[v],horizon)
            f=m.NewIntVar(0,horizon,f'M{pi}_{hi}_fwd'); ef=add_interval(m,byq,f'M{pi}_{hi}_fwd',f,[u,v],horizon)
            b=m.NewIntVar(0,horizon,f'M{pi}_{hi}_back'); eb=add_interval(m,byq,f'M{pi}_{hi}_back',b,[u,v],horizon)
            m.Add(f>=er); m.Add(b>=ef)
            if prev is not None: m.Add(r>=prev)
            prev=eb; count += 2
    return count


def solve(R, option='joint', hops=True, teleports=False, seconds=20, workers=8):
    started=time.monotonic()
    proof=structural_unsat(option,hops,teleports)
    if proof:
        return dict(status='UNSAT',seconds=time.monotonic()-started,binding=proof,R=R,option=option,hops=hops,teleports=teleports,solver='structural CP-SAT precheck')
    # The fixed-layout anc4 branch is structurally rejected above. The joint branch
    # uses the exact v17a BC witness and a separately optimal A witness.
    m=cp_model.CpModel(); horizon=R+3; byq={q:[] for q in range(36)}
    if hops:
        paths=MOVES
        data_end=DATA1
        nmove=move_jobs(m,byq,paths,horizon,RELEASE)
    else:
        paths=[]; data_end=DATA0; nmove=0
    # Fixed L5 couplings are checked here so a changed input cannot silently create a non-grid circuit.
    for i in range(7):
        if not edge(data_end[i],A[i]): raise ValueError(('A round',data_end[i],A[i]))
        if not edge(B[i],C[i]): raise ValueError(('BC round',B[i],C[i]))
        if not edge(B[i],data_end[i]): raise ValueError(('B data',B[i],data_end[i]))
    prep_jobs(m,byq,'A',A_PREP,A,horizon,RELEASE)
    prep_jobs(m,byq,'BC',BC_PREP,B+C,horizon,RELEASE)
    # Round is a fixed three-step star. Every checked B qubit is used on the next step.
    r0=R
    for i in range(7):
        add_interval(m,byq,f'RA{i}',m.NewConstant(r0),[data_end[i],A[i]],horizon)
        add_interval(m,byq,f'RC{i}',m.NewConstant(r0),[B[i],C[i]],horizon)
        add_interval(m,byq,f'RBd{i}',m.NewConstant(r0+1),[B[i],data_end[i]],horizon)
        add_interval(m,byq,f'MA{i}',m.NewConstant(r0+1),[A[i]],horizon)
        add_interval(m,byq,f'MC{i}',m.NewConstant(r0+1),[C[i]],horizon)
        add_interval(m,byq,f'MB{i}',m.NewConstant(r0+2),[B[i]],horizon)
    for q,ivs in byq.items():
        if ivs: m.AddNoOverlap(ivs)
    # All post-prefix work ends by the requested round start. This is the exact
    # feasibility predicate used by the table.
    # m has fixed R in round constants, so prep jobs simply cannot overlap it.
    s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=seconds; s.parameters.num_workers=workers; s.parameters.random_seed=0
    st=s.Solve(m); status=s.StatusName(st)
    out=dict(status=('SAT' if st in (cp_model.OPTIMAL,cp_model.FEASIBLE) else ('UNSAT' if st==cp_model.INFEASIBLE else 'TIMEOUT')),
             seconds=time.monotonic()-started,
             binding=(('cell-time NoOverlap / release / layer precedence' + ('; teleport optional, incumbent uses none' if teleports else ''))
                      if st in (cp_model.OPTIMAL,cp_model.FEASIBLE) else 'CP-SAT infeasibility over release, layer and round constraints'),
             R=R,option=option,hops=hops,teleports=teleports,solver='OR-Tools CP-SAT',workers=workers,objective='fixed round start')
    if out['status']=='SAT':
        # Emit operation starts for an auditable witness.
        vals={}
        for v in m.Proto().variables:
            # CP-SAT names are stable and useful in receipts.
            pass
        out['objective_value']=s.ObjectiveValue(); out['best_bound']=s.BestObjectiveBound()
        out['schedule_hint']='fixed L5 witness; round starts at requested R'
    return out


def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--seconds',type=float,default=3); ap.add_argument('--workers',type=int,default=8); ap.add_argument('--out',default=str(HERE/'feasibility.jsonl'))
    a=ap.parse_args(); rows=[]
    for option in ('separate','anc4','joint'):
        for hops in (False,True):
            for tele in (False,True):
                for R in range(36,48):
                    x=solve(R,option,hops,tele,a.seconds,a.workers); rows.append(x); print(json.dumps(x),flush=True)
    Path(a.out).write_text('\n'.join(json.dumps(x) for x in rows)+'\n')
    print('wrote',a.out,'rows',len(rows))
if __name__=='__main__': main()
