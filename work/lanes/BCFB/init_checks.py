"""Repeated same-basis BC-init checks, with exact native schedule and detectors."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,re,itertools,concurrent.futures
from pathlib import Path
from ortools.sat.python import cp_model
from build import H,S,B,C,bit,native_times
from scan import save_screen

def job(job):
 stem,qs=job[:2];window=job[2] if len(job)>2 else 0;f=H/'finalists'/stem;text=f.with_suffix('.qasm').read_text();md=json.loads(f.with_suffix('.json').read_text());h,raw,tail=S.qasm_ops(text);u=S.fold_units(raw);ts=native_times(text,u);R=md['R'];init={q:max(i for i,x in enumerate(u) if x.qs==(q,) and ts[i]<R and x.name in ('RX','RESET','MX','MEASURE')) for q in B+C}
 nbit=int(re.search(r'creg c\[(\d+)\]','\n'.join(h))[1]);uu=[];tt=[];movable=[]
 for i,x in enumerate(u):
  isbc=ts[i]<R and set(x.qs)<=set(B+C) and all(i>=init[q] for q in x.qs)
  if isbc:movable.append(len(uu))
  uu.append(x);tt.append(ts[i])
  for q in qs:
   if i!=init[q]:continue
   basis=x.name in ('MX','RX');ls=[f'h q[{q}];',f'measure q[{q}] -> c[{nbit}];',f'h q[{q}];'] if basis else [f'measure q[{q}] -> c[{nbit}];']
   bits=[nbit]+([bit(x)] if x.name in ('MX','MEASURE') else []);tail.append('// DETECTOR '+' '.join(f'c[{b}]' for b in bits));nbit+=1;movable.append(len(uu));uu.append(S.Unit(ls,[]));tt.append(ts[i]+1)
 m=cp_model.CpModel();tv=[m.NewIntVar(0,60,f't{i}') for i in range(len(uu))];p,s=S.build_dag(uu);dev=[];keepdev=[]
 for i in range(len(uu)):
  if i not in movable:
   if window and tt[i]<R:
    m.Add(tv[i]>=max(0,tt[i]-window));m.Add(tv[i]<=min(R-1,tt[i]+window));z=m.NewIntVar(0,60,'keepdev');m.AddAbsEquality(z,tv[i]-tt[i]);keepdev.append(z)
   else:m.Add(tv[i]==tt[i])
  else:
   m.Add(tv[i]<R);z=m.NewIntVar(0,60,'dev');m.AddAbsEquality(z,tv[i]-tt[i]);dev.append(z)
  for j in p[i]:m.Add(tv[i]>tv[j])
 m.Minimize(1000000*sum(keepdev)+10000*sum(dev)-sum(tv[i] for i in movable));so=cp_model.CpSolver();so.parameters.num_workers=1;so.parameters.max_time_in_seconds=10;st=so.Solve(m)
 tag='ic_'+stem+'_'+'_'.join(map(str,qs))+('_rt'+str(window) if window else '');change=dict(source=stem,checked=qs,retime_window=window)
 if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
  from evaluate import record
  r=dict(status='INVALID',error='SCHEDULE_'+so.StatusName(st));record(tag,'init_checks',r,change);return r
 times=[so.Value(x) for x in tv];h=[re.sub(r'creg c\[\d+\]',f'creg c[{nbit}]',l) for l in h];new=S.emit(h,uu,times,tail);_,rr,_=S.qasm_ops(new);nu=S.fold_units(rr);nt=native_times(new,nu);order=sorted(range(len(uu)),key=lambda i:(times[i],i));assert [uu[i].lines for i in order]==[x.lines for x in nu];assert [times[i] for i in order]==nt
 nmd=dict(md,init_checks=qs,init_check_retime=window,non_BC_check_retime=[dict(lines=uu[i].lines,old=tt[i],new=times[i]) for i in range(len(uu)) if i not in movable and tt[i]!=times[i]]);threshold=json.loads(f.with_suffix('.screen.json').read_text())['total']-1e-12
 return save_screen(tag,'init_checks',new,nmd,change,threshold=threshold)
def main():
 p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--workers',type=int,default=4);p.add_argument('--wide',action='store_true');a=p.parse_args();qs=B+C
 if a.wide:
  import random
  rng=random.Random(918);masks={sum(1<<i for i in ix) for ix in itertools.combinations(range(14),3)}|{rng.randrange(1,1<<14) for _ in range(512)}
  jobs=[(a.stem,[q for i,q in enumerate(qs) if mask>>i&1]) for mask in sorted(masks)]
 else:jobs=[(a.stem,[q]) for q in qs]+[(a.stem,list(pair)) for pair in itertools.combinations(qs,2)]+[(a.stem,qs)]
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as ex:rows=list(ex.map(job,jobs))
 out=dict(status='COMPLETE',prices=len(rows),best=min((r.get('total',1) for r in rows),default=None));(H/'runs'/f'initchecks_{a.stem}{"_wide" if a.wide else ""}.receipt.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':main()
