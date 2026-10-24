"""Whole-circuit placement search, preserving native per-wire operation order."""
import os,sys,json,argparse,random,math,pickle
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from ortools.sat.python import cp_model

def placement(units,mode='alap',seed=0,slack=0):
    pred,succ=S.build_dag(units);early=[]
    for i in range(len(units)):early.append(max((early[j]+1 for j in pred[i]),default=0))
    horizon=max(early)+slack
    late=[horizon]*len(units)
    for i in reversed(range(len(units))):late[i]=min((late[j]-1 for j in succ[i]),default=horizon)
    if mode=='asap':return early
    if mode=='alap':return late
    rng=random.Random(seed);m=cp_model.CpModel();ts=[m.new_int_var(early[i],late[i],f't{i}')for i in range(len(units))]
    for i in range(len(units)):
        for j in pred[i]:m.add(ts[i]>=ts[j]+1)
    if mode=='priority':w=[rng.randint(-100,100)for u in units]
    elif mode=='data':w=[100 if any(q in (0,20,7,10,3,22,21) for q in u.qs) else rng.randint(-5,5)for u in units]
    else:raise ValueError(mode)
    m.maximize(sum(x*v for x,v in zip(w,ts)));s=cp_model.CpSolver();s.parameters.num_search_workers=1;s.parameters.random_seed=seed
    status=s.solve(m);assert status in (cp_model.OPTIMAL,cp_model.FEASIBLE)
    return [s.value(t) for t in ts]

def write(src,name,times,units,head,tail,meta):
    text=S.emit(head,units,times,tail);h,r,t=S.qasm_ops(text);nu=S.fold_units(r);nt=native_times(text,nu)
    order=sorted(range(len(units)),key=lambda i:(times[i],i));assert [units[i].lines for i in order]==[x.lines for x in nu]
    # All reported times come from the native judge; equality verifies emission.
    compressed=S.compress(times);assert [compressed[i]for i in order]==nt
    stem=OUT/name;stem.with_suffix('.qasm').write_text(text)
    oldpre=set(meta.get('prefix_unit_indices',[]))
    extra=dict(source=src,schedule=name,R=max(t for u,t in zip(nu,nt)if u.lines==['cx q[0],q[1];']),native_depth=max(nt)+1)
    if oldpre:extra['prefix_unit_indices']=[j for j,i in enumerate(order)if i in oldpre]
    stem.with_suffix('.json').write_text(json.dumps(dict(meta,**extra),indent=2)+'\n')
    print(name,'R',extra['R'],'depth',extra['native_depth'],flush=True)
    return stem

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--random',type=int,default=8);p.add_argument('--slack',type=int,default=0);a=p.parse_args()
    src=OUT/a.stem;text=src.with_suffix('.qasm').read_text();meta=json.loads(src.with_suffix('.json').read_text());h,r,t=S.qasm_ops(text);u=S.fold_units(r)
    for mode,seed in [('asap',0),('alap',0),('data',0)]+[('priority',i)for i in range(a.random)]:
        ts=placement(u,mode,seed,a.slack);write(a.stem,f'{a.stem}_whole_{mode}{seed}_s{a.slack}',ts,u,h,t,meta)
