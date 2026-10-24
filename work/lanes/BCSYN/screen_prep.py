#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Insert a synthesized B+C prep into v18 and reschedule on native steps."""
import argparse,json,os,sys
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/TREP')]
import schedule as S
from ortools.sat.python import cp_model
from util import native_times
B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28]

def make_units(prep):
    cells=prep.get('cells',B+C); piv=set(prep['pivots']); first={}
    for t,lay in enumerate(prep['ops']):
        for u,v in lay:
            first.setdefault(u,t);first.setdefault(v,t)
    for q in cells:first.setdefault(q,0)
    units=[]
    for q,t in sorted(first.items(),key=lambda kv:(kv[1],kv[0])):
        units.append(S.Unit([f'reset q[{q}];']+([f'h q[{q}];'] if q in piv else []),[]))
    for lay in prep['ops']:
        units.append(S.Unit([f'cx q[{u}],q[{v}];' for u,v in lay],[]))
    return units,cells

def build(prep, source=ROOT/'work/lanes/MAIN/v18.qasm', out=None, workers=8):
    text=Path(source).read_text(); meta=json.loads(Path(source).with_suffix('.json').read_text())
    head,raw,suffix=S.qasm_ops(text); old=S.fold_units(raw); ots=native_times(text,old)
    # v18 metadata identifies prefix units exactly; its native round begins at R.
    preids=set(meta.get('prefix_unit_indices',[])); R0=int(meta.get('R',46))
    cand,cells=make_units(prep); footprint=set(cells)
    keep=[]; old_ids=[]
    for i,u in enumerate(old):
        # Remove only the old B+C preparation operations before the round.
        if i not in preids and ots[i] < R0 and set(u.qs) <= footprint and u.name in ('RESET','RX','CX'):
            continue
        old_ids.append(i);keep.append(u)
    all_units=keep+cand; nold=len(keep); cand_ids=list(range(nold,len(all_units)))
    # Per-wire sequence: retain original order and insert the new prep before
    # the first surviving suffix operation on each footprint cell.
    per={}
    for j,u in enumerate(keep):
        oi=old_ids[j]
        for q in u.qs:per.setdefault(q,[]).append(j)
    for j in cand_ids:
        for q in all_units[j].qs:per.setdefault(q,[]).append(j)
    # Rebuild each sequence with candidate units inserted before round suffix.
    for q in footprint:
        orig=[j for j in range(nold) if q in all_units[j].qs]
        cp=[j for j in cand_ids if q in all_units[j].qs]
        # Candidate units must precede the first original operation at/after R0.
        cut=next((k for k,j in enumerate(orig) if ots[old_ids[j]]>=R0),len(orig))
        per[q]=orig[:cut]+cp+orig[cut:]
    m=cp_model.CpModel(); max_t=max(ots)+len(cand)+20
    tv=[m.NewIntVar(0,max_t,f't{i}') for i in range(len(all_units))]
    shift=m.NewIntVar(0,max_t,'round_shift')
    # Prefix timing is held exactly, including the ALAP interleaving decisions.
    for j,oi in enumerate(old_ids):
        if oi in preids:m.Add(tv[j]==ots[oi])
        elif ots[oi]>=R0:m.Add(tv[j]==ots[oi]+shift)
        else:m.Add(tv[j]>=ots[oi])
    for q,seq in per.items():
        for x,y in zip(seq,seq[1:]):m.Add(tv[y]>=tv[x]+1)
    # Respect each cell's release after the fixed prefix.
    for q in footprint:
        p=[j for j,oi in enumerate(old_ids) if oi in preids and q in all_units[j].qs]
        if p:
            rel=max(ots[old_ids[j]] for j in p)+1
            for j in cand_ids:
                if q in all_units[j].qs:m.Add(tv[j]>=rel)
    round_ids=[j for j,oi in enumerate(old_ids) if ots[oi]>=R0]
    rt=m.NewIntVar(0,max_t,'round_start');m.Add(rt==R0+shift)
    m.Minimize(rt)
    s=cp_model.CpSolver();s.parameters.num_search_workers=workers;s.parameters.max_time_in_seconds=120
    st=s.Solve(m);assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE),s.StatusName(st)
    rbest=s.Value(rt)
    # With the earliest feasible round fixed, delay the prep ALAP.  This is
    # the important v18 property: idle before a first use is free, while an
    # early-prepared B/C block accrues idle noise for every intervening step.
    m.Add(rt==rbest)
    m.ClearObjective()
    m.Maximize(sum(tv[j] for j in cand_ids))
    st=s.Solve(m);assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE),s.StatusName(st)
    times=[s.Value(t) for t in tv]
    # Preserve operation ordering within equal native steps as represented by
    # unit IDs; S.emit inserts a full barrier between steps.
    order=sorted(range(len(all_units)),key=lambda j:(times[j],j))
    outtext=S.emit(head,all_units,times,suffix)
    if out is not None:
        out=Path(out);out.with_suffix('.qasm').write_text(outtext)
        md=dict(meta,source_v18=str(source),prep_source=str(prep.get('_source','')),prep_cx=sum(map(len,prep['ops'])),prep_depth=len(prep['ops']),schedule_workers=workers)
        out.with_suffix('.json').write_text(json.dumps(md,indent=2)+'\n')
    return outtext,dict(meta,round_start=s.Value(rt),prep_cx=sum(map(len,prep['ops'])),prep_depth=len(prep['ops']))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('prep');ap.add_argument('out');ap.add_argument('--workers',type=int,default=8);a=ap.parse_args();d=json.loads(Path(a.prep).read_text());d['_source']=a.prep;txt,md=build(d,out=a.out,workers=a.workers);print(json.dumps(md),flush=True)
if __name__=='__main__':main()
