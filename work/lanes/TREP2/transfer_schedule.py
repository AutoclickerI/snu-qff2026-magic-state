"""Transfer measured placement changes onto the q10-reuse circuits."""
import os,sys,json,collections,argparse
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from schedules import write
from exact2 import Eval
from ortools.sat.python import cp_model

def read(name):
    stem=OUT/name;text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());h,r,t=S.qasm_ops(text);us=S.fold_units(r);ts=native_times(text,us);seen=collections.Counter();keys={}
    for i,u in enumerate(us):
        lines=tuple(u.lines[:2]if u.name=='MX'else u.lines);key=(lines,seen[lines]);seen[lines]+=1;keys[key]=i
    return meta,h,us,ts,t,keys

def transfer(base,opt,target,out):
    bm,bh,bu,bt,bd,bk=read(base);om,oh,ou,ot,od,ok=read(opt);meta,h,u,ts,tail,keys=read(target)
    assert set(bk)==set(ok)
    deltas={k:ot[ok[k]]-bt[bk[k]]for k in bk if ot[ok[k]]!=bt[bk[k]]};wanted={keys[k]:ts[keys[k]]+d for k,d in deltas.items()if k in keys}
    m=cp_model.CpModel();tv=[m.new_int_var(0,max(ts),f't{i}')for i in range(len(u))];pred,succ=S.build_dag(u);dev=[];amount=[]
    for i in range(len(u)):
        for j in pred[i]:m.add(tv[i]>tv[j])
        if i not in wanted:m.add(tv[i]==ts[i])
        else:
            v=m.new_int_var(0,100,f'd{i}');m.add_abs_equality(v,tv[i]-wanted[i]);dev.append(v)
            a=m.new_int_var(0,100,f'a{i}');m.add_abs_equality(a,tv[i]-ts[i]);amount.append(a)
    m.minimize(10000*sum(dev)+sum(amount));s=cp_model.CpSolver();s.parameters.num_search_workers=1;status=s.solve(m);assert status in(cp_model.OPTIMAL,cp_model.FEASIBLE)
    nt=[s.value(v)for v in tv];changes=[dict(operation=u[i].lines,old=ts[i],requested=wanted[i],actual=nt[i])for i in wanted]
    info=dict(base=base,optimized=opt,target=target,changes=changes,unavailable=[list(k[0])for k in deltas if k not in keys],projection_distance=sum(abs(nt[i]-wanted[i])for i in wanted))
    meta['injection_cx']=25 if base.startswith('v17')else meta.get('injection_cx',19)
    stem=write(target,out,nt,u,h,tail,dict(meta,transferred_schedule=info));ev=Eval(stem.with_suffix('.qasm').read_text(),meta['data_qubits']);info['c1']=float(ev.fp@ev.n_single)
    stem.with_suffix('.transfer.json').write_text(json.dumps(info,indent=2)+'\n');print(out,info,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('optimized');p.add_argument('target');p.add_argument('out');a=p.parse_args();transfer(a.base,a.optimized,a.target,a.out)
