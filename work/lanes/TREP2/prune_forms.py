"""Simplify the verified |+_L> resource used by the alternative forms.

Deletion trials preserve the judge's ideal checks and full single-fault
protection. These are constrained synthesis trials, not MC rankings.
"""
import os,sys,json,random,collections
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from schedules import placement,write
from exact2 import Eval
from util import native_times

if __name__=='__main__':
    base=OUT/'f00_0_parity';text=base.with_suffix('.qasm').read_text();meta=json.loads(base.with_suffix('.json').read_text());h,r,tail=S.qasm_ops(text);units=S.fold_units(r)
    src=(OUT/'encoder19.qasm').read_text();hh,rr,tt=S.qasm_ops(src);pu=S.fold_units(rr);pt=native_times(src,pu)
    prefix=[u for u,t in zip(pu,pt)if t<=29 and u.name not in('T','TDG')]
    positions=collections.defaultdict(list)
    for i,u in enumerate(units):positions[tuple(u.lines)].append(i)
    mapping={}
    for j,u in enumerate(prefix):mapping[j]=positions[tuple(u.lines)].pop(0)
    cx=[j for j,u in enumerate(prefix)if u.name=='CX'];pairs=[]
    for a in cx:
        for b in cx:
            if b>a and prefix[a].lines==prefix[b].lines:pairs.append([a,b])
    trials=[];best=None
    for seed in range(3):
        rng=random.Random(seed);removed=set();moves=pairs+[[i]for i in cx];rng.shuffle(moves)
        while True:
            changed=False
            for move in moves:
                if any(j in removed for j in move):continue
                rr=removed|set(move);delete={mapping[j]for j in rr};nu=[u for i,u in enumerate(units)if i not in delete];ts=placement(nu,'alap');txt=S.emit(h,nu,ts,tail)
                row=dict(seed=seed,move=move)
                try:
                    ev=Eval(txt,meta['data_qubits']);c1=float(ev.fp@ev.n_single);row.update(correct=True,c1=c1)
                    if abs(c1)<1e-12:
                        removed=rr;changed=True;row['accepted']=True;print('accepted',seed,len(removed),move,flush=True)
                except ValueError as ex:row.update(correct=False,error=str(ex))
                trials.append(row)
            if not changed:break
        delete={mapping[j]for j in removed};nu=[u for i,u in enumerate(units)if i not in delete];ts=placement(nu,'alap');key=(-len(removed),max(ts))
        if best is None or key<best[0]:best=(key,removed,nu,ts)
    key,removed,nu,ts=best
    write('f00_0_parity','f00_0_pruned',ts,nu,h,tail,dict(meta,removed_prefix_indices=sorted(removed)))
    (OUT/'prefix_prune.json').write_text(json.dumps(dict(removed_prefix_indices=sorted(removed),removed_lines=[prefix[j].lines for j in sorted(removed)],trials=trials),indent=2)+'\n')
    print('best',key,sorted(removed),flush=True)
