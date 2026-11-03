"""Joint native ABC CSS preparation, with two-axis first-order contracts.

Initial plus locations and their GL(11,2) basis are free. Every resource cell
can carry another block's information during preparation. Optional zero-output
helpers supply literal terminal flags. No shared evaluator code is changed.
"""
import argparse
import json
import os
import time
from pathlib import Path
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
from ortools.sat.python import cp_model
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
from partial_contract import A, B, C, D, CELLS, HELPERS, COLS, ROWS, fault_signature, make_contract, make_four_square_contract, make_partial_contract
HERE=Path(__file__).resolve().parent
(HERE/'sol').mkdir(exist_ok=True)
GEOMETRY=json.loads((ROOT/'work/lanes/SOTA_SOURCE_20261028/geometry_both_borrow_7_opt.json').read_text())
ROLES=GEOMETRY['roles']
BLOCKED=set()

def solve(name, depth=18, t0=0, seconds=120, helpers=True, release=None,
          hint=None, seed=1, f1=True, wbad=10, wunflag=10, cap=None,
          known_initial=None, fix_initial=False, late_c14=False, orientation=0,
          four_square=False,dual_a=False):
    contract=make_partial_contract(ROLES,127,True,dual_a)
    assert not dual_a or not(f1 or wbad or wunflag), 'Dual-A F1 needs general Pauli audit; this mode is state-only.'
    assert four_square and dual_a
    assert not(f1 or wbad or wunflag), 'Measured-helper fault model must be audited in complete circuit.'
    cells = sorted(contract.CELLS + contract.HELPERS)
    hs = [q for q in cells if q in contract.HELPERS]
    release = {int(q): int(t) for q,t in (release or {}).items()}
    known_initial={int(q):v for q,v in (known_initial or {}).items()}
    target={q:contract.COLS[q] for q in cells}
    rank=contract.rank
    edges = [(a,b) for a in cells for b in cells if abs(a//6-b//6)+abs(a%6-b%6)==1]
    m = cp_model.CpModel()
    sel = [{e: m.NewBoolVar(f'cx{t}_{e[0]}_{e[1]}') for e in edges} for t in range(depth)]
    use = []
    for t in range(depth):
        row = {}
        for q in cells:
            vv = [v for e,v in sel[t].items() if q in e]
            m.AddAtMostOne(vv)
            row[q] = m.NewBoolVar(f'use{t}_{q}')
            m.AddMaxEquality(row[q], vv)
            # R/RX immediately before first CX is itself a physical operation.
            if (t0+t,q) in BLOCKED or t0+t < release.get(q, -1) or (t0+t == release.get(q,-1) and q not in known_initial):
                m.Add(row[q] == 0)
        use.append(row)
    for q in contract.late_plus+contract.post_h:
        m.Add(use[-1][q]==0)  # Final reset/H operation shares the last main tick.
    alive = []
    for t in range(depth+1):
        row = {q: m.NewBoolVar(f'alive{t}_{q}') for q in cells}
        for q in cells:
            if t:
                m.AddMaxEquality(row[q], [use[k][q] for k in range(t)])
            else:
                m.Add(row[q] == 0)
        alive.append(row)
    def variables(width, label):
        return [{q: [m.NewBoolVar(f'{label}{t}_{q}_{k}') for k in range(width)] for q in cells}
                for t in range(depth+1)]
    state = variables(rank, 'x')
    hx = variables(7+len(hs), 'hx') if f1 or wbad or wunflag else []
    hz = variables(11, 'hz') if f1 or wbad or wunflag else []
    axes=[('X',hx),('Z',hz)] if hx else []
    nz = {q: m.NewBoolVar(f'piv{q}') for q in cells}
    for q in cells:
        m.AddMaxEquality(nz[q], state[0][q])
        if q in contract.CELLS:
            for k,v in enumerate(state[-1][q]):
                m.Add(v == (target[q] >> k & 1))
        for axis,arr in axes:
            end = contract.fault_signature(q, axis, hs)
            for k,v in enumerate(arr[-1][q]):
                m.Add(v == (end >> k & 1))
        at=release.get(q,-1)-t0
        if q in known_initial and 0<=at<depth:
            m.Add(nz[q] == int(known_initial[q]=='X')).OnlyEnforceIf(use[at][q])
        if fix_initial:
            assert hint is not None
            value=int(hint['pivots'].get(str(q),hint['pivots'].get(q,0)))
            for k,v in enumerate(state[0][q]):m.Add(v == (value>>k&1))
    m.Add(sum(nz.values()) == rank)
    def xor(z,a,b,lit):
        aux = m.NewIntVar(0,1,'')
        m.Add(z+a+b == 2*aux).OnlyEnforceIf(lit)
    for t in range(depth):
        for q in cells:
            incoming = [(a,b) for a,b in edges if b==q]
            outgoing = [(a,b) for a,b in edges if a==q]
            for arr, es, control in [(state,incoming,0)]+([(hx,outgoing,1),(hz,incoming,0)] if hx else []):
                on = m.NewBoolVar('')
                m.AddMaxEquality(on, [sel[t][e] for e in es])
                for k in range(len(arr[t][q])):
                    m.Add(arr[t][q][k] == arr[t+1][q][k]).OnlyEnforceIf(on.Not())
                    for e in es:
                        xor(arr[t][q][k], arr[t+1][q][k], arr[t+1][e[control]][k], sel[t][e])
    badterms, riskterms = [], []
    def safety(sig, lit, weight=1):
        syn,parity,det = sig[:3],sig[3],sig[4:]
        # Bad class: syndrome 000/parity1, or nonzero syndrome/parity0.
        if f1:
            m.AddBoolOr(det+[lit.Not(),parity.Not()]+syn)
            for b in syn:
                m.AddBoolOr(det+[lit.Not(),b.Not(),parity])
        if wbad:
            bad = m.NewBoolVar('badclass')
            m.AddBoolOr([lit.Not(),bad,parity.Not()]+syn)
            for b in syn:
                m.AddBoolOr([lit.Not(),bad,b.Not(),parity])
            badterms.append(weight*bad)
        if wunflag:
            risk = m.NewBoolVar('unflagged')
            for b in sig[:4]:
                m.AddBoolOr([lit.Not(),risk,b.Not()]+det)
            riskterms.append(weight*risk)
    for t in range(1,depth+1):
        for q in cells:
            for _,arr in axes:
                safety(arr[t][q],alive[t][q],2)
    for t in range(depth):
        for a,b in edges:
            if a>b:
                continue
            on = m.NewBoolVar('gatepair')
            m.AddMaxEquality(on,[sel[t][a,b],sel[t][b,a]])
            for _,arr in axes:
                sig = [m.NewBoolVar('pair_signature') for _ in arr[t+1][a]]
                for k,v in enumerate(sig):
                    xor(v,arr[t+1][a][k],arr[t+1][b][k],on)
                safety(sig,on,1)
        for q in cells:
            first = m.NewBoolVar('first')
            m.AddBoolAnd([use[t][q],alive[t][q].Not()]).OnlyEnforceIf(first)
            m.AddBoolOr([use[t][q].Not(),alive[t][q],first])
            for _,arr in axes:
                safety(arr[t][q],first,3)
    # A product target cell can be prepared immediately before the terminal
    # without any resource CX. C_6 is exactly such a free |+> factor.
    for q in contract.CELLS:
        for _,arr in axes:
            safety(arr[-1][q],alive[-1][q].Not(),3)
    ncx = sum(v for row in sel for v in row.values())
    if cap is not None:
        m.Add(ncx <= cap)
    badcount, riskcount = sum(badterms), sum(riskterms)
    m.Minimize(10*ncx+sum(v for row in alive for v in row.values())+wbad*badcount+wunflag*riskcount)
    if hint and not hint.get('initial_only'):
        ops = hint['ops']
        # Flat lists are interpreted as already layered by the seed owner.
        initial = {int(q):int(v) for q,v in hint['pivots'].items()}
        for t,row in enumerate(sel):
            used = {tuple(e) for e in ops[t]} if t<len(ops) else set()
            for e,v in row.items():
                m.AddHint(v,int(e in used))
        forward = {q: initial.get(q,0) for q in cells}
        for t in range(depth+1):
            for q in cells:
                for k,v in enumerate(state[t][q]):
                    m.AddHint(v,forward[q]>>k&1)
            if t<depth:
                for a,b in ops[t] if t<len(ops) else []:
                    if (a,b) in edges:
                        forward[b] ^= forward[a]
        for axis,arr in axes:
            back = {q:contract.fault_signature(q,axis,hs) for q in cells}
            for t in range(depth,-1,-1):
                for q in cells:
                    for k,v in enumerate(arr[t][q]):
                        m.AddHint(v,back[q]>>k&1)
                if t:
                    for a,b in ops[t-1] if t-1<len(ops) else []:
                        if (a,b) in edges:
                            if axis=='X': back[a] ^= back[b]
                            else: back[b] ^= back[a]
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = seed
    status = solver.Solve(m)
    out = dict(status=solver.StatusName(status),seconds=solver.WallTime(),T0=t0,depth=depth,
               cells=cells,helpers=hs,release=release,seed=seed,f1=f1,wbad=wbad,wunflag=wunflag,
               known_initial=known_initial,fix_initial=fix_initial,
               late_c14=late_c14,state_rank=rank,target_columns=target,
               orientation=orientation,roles=contract.roles,
               contract_kind=contract.kind,square_mask=contract.square_mask,dual_a=dual_a,post_h=contract.post_h,
               contract_file='work/lanes/END2_20261027/partial_resource_contract.json')
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        out.update(ops=[[list(e) for e,v in row.items() if solver.Value(v)] for row in sel],
            pivots={q:sum(solver.Value(b)<<k for k,b in enumerate(state[0][q])) for q in cells},
            cx=solver.Value(ncx),bad=solver.Value(badcount),unflagged=solver.Value(riskcount),
            objective=solver.ObjectiveValue(),bound=solver.BestObjectiveBound(),
            final_rows={q:sum(solver.Value(v)<<k for k,v in enumerate(state[-1][q])) for q in cells}, measured_helpers=True)
        out['reuse']={q:known_initial[q] for q in known_initial if any(q in e for layer in out['ops'] for e in layer)
                      and min(t0+t for t,layer in enumerate(out['ops']) if any(q in e for e in layer))==release[q]}
        out['late_initializations']=[dict(qubit=q,time=t0+depth-1,kind='RX') for q in contract.late_plus]
        out['late_cliffords']=[dict(qubit=q,time=t0+depth-1,kind='H') for q in contract.post_h]
    (HERE/'sol'/f'{name}.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)
    return out


if __name__=='__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('name');ap.add_argument('--depth',type=int,default=18)
    ap.add_argument('--t0',type=int,default=0);ap.add_argument('--seconds',type=float,default=120)
    ap.add_argument('--no-helpers',action='store_true');ap.add_argument('--no-f1',action='store_true')
    ap.add_argument('--release');ap.add_argument('--hint');ap.add_argument('--seed',type=int,default=1)
    ap.add_argument('--wbad',type=int,default=10);ap.add_argument('--wunflag',type=int,default=10)
    ap.add_argument('--cap',type=int)
    ap.add_argument('--known-initial');ap.add_argument('--fix-initial',action='store_true')
    ap.add_argument('--late-c14',action='store_true')
    ap.add_argument('--orientation',type=int,default=0)
    ap.add_argument('--four-square',action='store_true');ap.add_argument('--dual-a',action='store_true')
    a=ap.parse_args()
    release=json.loads(Path(a.release).read_text()) if a.release else None
    if release and 'release' in release:release=release['release']
    hint=json.loads(Path(a.hint).read_text()) if a.hint else None
    known=json.loads(Path(a.known_initial).read_text()) if a.known_initial else None
    solve(a.name,a.depth,a.t0,a.seconds,not a.no_helpers,release,hint,a.seed,not a.no_f1,a.wbad,a.wunflag,a.cap,known,a.fix_initial,a.late_c14,a.orientation,a.four_square,a.dual_a)
