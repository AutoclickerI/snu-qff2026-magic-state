"""CP-SAT scheduling of a synthesized prefix with the v17a suffix held rigid.

Per-wire order preserves the exact circuit. A common time shift for every suffix
operation preserves its prep, move, and round spacings. The objective first moves
the suffix early, then delays preparations and advances released-cell readout.
"""
import os,sys,json,argparse
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from exact2 import Eval
from ortools.sat.python import cp_model

def main():
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--mode',choices=['alap','asap','idle'],default='idle');ap.add_argument('--workers',type=int,default=4);a=ap.parse_args()
    src=OUT/a.stem;text=src.with_suffix('.qasm').read_text();meta=json.loads(src.with_suffix('.json').read_text());head,raw,tail=S.qasm_ops(text);units=S.fold_units(raw);old=native_times(text,units);end=meta['pre_end']
    pre={i for i,t in enumerate(old)if t<=end};m=cp_model.CpModel();ts=[m.new_int_var(0,max(old),f't{i}')for i in range(len(units))];shift=m.new_int_var(-end,0,'shift')
    for i,t in enumerate(old):
        if i not in pre:m.add(ts[i]==t+shift)
    per={}
    for i,u in enumerate(units):
        for q in u.qs:per.setdefault(q,[]).append(i)
    for q,seq in per.items():
        for x,y in zip(seq,seq[1:]):m.add(ts[y]>=ts[x]+1)
    # In a fixed circuit per-wire order implies mutual exclusion for all gates.
    m.minimize(shift);s=cp_model.CpSolver();s.parameters.num_search_workers=a.workers;s.parameters.max_time_in_seconds=30
    status=s.solve(m);assert status in (cp_model.OPTIMAL,cp_model.FEASIBLE)
    sh=s.value(shift);m.add(shift==sh)
    if a.mode=='alap':obj=-sum(ts[i]for i in pre)
    elif a.mode=='asap':obj=sum(ts[i]for i in pre)
    else:
        terms=[]
        for q,seq in per.items():
            # Charge time only within live lifetimes, excluding pre-reset gaps.
            for x,y in zip(seq,seq[1:]):
                if y in pre and units[y].name not in ('RESET','RX'):
                    terms.append((4 if q in [0,20,7,4,3,15,8] else 1)*(ts[y]-ts[x]-1))
            # Prompt terminal measurements next to bottleneck data cells.
            for i in seq:
                if i in pre and units[i].last_is_measure and q in [1,6,13,2,9,14,19]:terms.append(3*ts[i])
        obj=sum(terms)
    m.minimize(obj);status=s.solve(m);assert status in (cp_model.OPTIMAL,cp_model.FEASIBLE)
    times=[s.value(t)for t in ts];out=S.emit(head,units,times,tail);name=f'{a.stem}_{a.mode}';stem=OUT/name
    h,r,t=S.qasm_ops(out);nu=S.fold_units(r);nt=native_times(out,nu);R=max(t for u,t in zip(nu,nt)if u.lines==['cx q[0],q[1];']);pe=max(t for u,t in zip(nu,nt)if u.name in ('T','TDG'))
    ordered=sorted(range(len(units)),key=lambda i:(times[i],i))
    assert [units[i].lines for i in ordered]==[u.lines for u in nu]
    stem.with_suffix('.qasm').write_text(out);stem.with_suffix('.json').write_text(json.dumps(dict(meta,R=R,pre_end=pe,source=a.stem,schedule_mode=a.mode,suffix_shift=sh,
              prefix_unit_indices=[j for j,i in enumerate(ordered)if i in pre]),indent=2)+'\n')
    ev=Eval(out,meta['data_qubits']);print(name,'shift',sh,'R',R,'pre_end',pe,'c1',float((ev.fp*ev.n_single).sum()),flush=True)

if __name__=='__main__':main()
