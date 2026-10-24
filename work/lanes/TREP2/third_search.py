"""Use exact third order to resolve promising single-placement changes."""
import os,sys,json,argparse,math,time,random
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import numpy as np
import schedule as S
from quadratic_search import Quadratic
from exact2 import Eval,run
from fast_third import third_order
from util import native_times
from schedules import write

def score3(q,ts,procs):
    ts=S.compress(ts)
    p=q.probabilities(ts);sc=q.score(ts);kp=q.K@p
    # c1=0 => K is the raw pair-loss coefficient. This is exact2's t3bc.
    sa=float(p.sum()-sc['A1']);bc=-sa*sc['loss2']+float((p*p)@kp)
    ev=Eval(S.emit(q.header,q.units,ts,q.suffix),q.data)
    assert abs(ev.fp@ev.n_single)<1e-12
    tri=third_order(ev,procs)[0]
    return dict(sc,third=tri+bc,total=sc['loss2']+tri+bc,T3a=tri,t3bc=bc)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--procs',type=int,default=4);ap.add_argument('--passes',type=int,default=2);ap.add_argument('--candidates',type=int,default=20);a=ap.parse_args()
    base=OUT/a.stem;text=base.with_suffix('.qasm').read_text();meta=json.loads(base.with_suffix('.json').read_text());h,r,tail=S.qasm_ops(text);units=S.fold_units(r);times=native_times(text,units)
    q=Quadratic(text,meta['data_qubits'],units,h,tail);q.data=meta['data_qubits'];pred,succ=S.build_dag(units);trace=[];seen=set();rng=random.Random(20261024)
    best=score3(q,times,a.procs)
    reference=run(Eval(text,meta['data_qubits']),a.procs,third=True,keep_thr=1)
    assert abs(reference['t3bc']-best['t3bc'])<1e-14,(reference['t3bc'],best)
    assert abs(reference['loss2']-best['loss2'])<1e-14
    print('base',best,flush=True);trace.append(dict(name=a.stem,**best))
    for stage in range(a.passes):
        proposals=[]
        for i in range(len(units)):
            lo=max((times[j]+1 for j in pred[i]),default=0);hi=min((times[j]-1 for j in succ[i]),default=max(times))
            for t in set([lo,hi,times[i]-1,times[i]+1]):
                if t==times[i]or not lo<=t<=hi:continue
                ts=times[:];ts[i]=t;ts=S.compress(ts);key=tuple(ts)
                if key in seen:continue
                v=q.score(ts)
                if v['A1']>-math.log(.506):continue
                proposals.append((v['loss2'],rng.random(),i,t,ts,v))
        proposals.sort();selected=[];used=set()
        for prop in proposals:
            if prop[2]in used:continue
            used.add(prop[2]);selected.append(prop)
            if len(selected)>=a.candidates:break
        if not selected:break
        improved=False;winner=None
        for j,(_,_,i,t,ts,v)in enumerate(selected):
            seen.add(tuple(ts));row=score3(q,ts,a.procs);name=f'{a.stem}_third_p{stage}_n{j}';write(a.stem,name,ts,units,h,tail,meta)
            row.update(name=name,unit=i,operation=units[i].lines,new_time=t,stage=stage)
            (OUT/(name+'.third_search.json')).write_text(json.dumps(row,indent=2)+'\n');trace.append(row);print(json.dumps(row),flush=True)
            (OUT/(a.stem+'.third_search_trace.json')).write_text(json.dumps(trace,indent=2)+'\n')
            if row['total']<best['total']-1e-12:best=row;winner=ts;improved=True
        if not improved:break
        times=winner
        write(a.stem,a.stem+'_third_best',times,units,h,tail,meta)
        (OUT/(a.stem+'.third_search_best.json')).write_text(json.dumps(best,indent=2)+'\n')
    print('best',best,flush=True)
