import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from ortools.sat.python import cp_model
H=Path(__file__).resolve().parent
# Published SpiderCSS Steane-zero resource, same order as SOTA_DETECT/spider_abstract.py.
items=[]
for i in range(10):items.append(('RX' if i in (0,4,6) else 'R',(i,),None))
raw=[('CX',0,7),('CX',7,3),('CX',0,2),('CX',4,8),('CX',6,9),('CX',7,1),('CX',8,2),('CX',4,5),('CX',9,3),('CX',8,1),('CX',9,2),('CX',6,5),('CX',0,7),('M',7),('CX',4,8),('M',8),('CX',6,9),('M',9)]
for a,*qs in raw:items.append((a,tuple(qs),None))
m=cp_model.CpModel();ts=[m.NewIntVar(0,30,'t'+str(i)) for i in range(len(items))];ivs=[m.NewFixedSizeIntervalVar(t,1,'i'+str(i)) for i,t in enumerate(ts)]
for q in range(10):
 ids=[i for i,(k,qs,_) in enumerate(items) if q in qs]
 for a,b in zip(ids,ids[1:]):m.Add(ts[b]>=ts[a]+1)
for a,b in ((7,8),(8,9)):
 ma=next(i for i,(k,qs,_) in enumerate(items) if k=='M' and qs==(a,));rb=next(i for i,(k,qs,_) in enumerate(items) if k=='R' and qs==(b,));m.Add(ts[rb]>=ts[ma]+1)
for q in range(7):m.AddNoOverlap([ivs[i] for i,(k,qs,_) in enumerate(items) if q in qs])
m.AddNoOverlap([ivs[i] for i,(k,qs,_) in enumerate(items) if any(q>=7 for q in qs)])
end=m.NewIntVar(1,31,'end');m.AddMaxEquality(end,[t+1 for t in ts]);m.Minimize(end)
s=cp_model.CpSolver();s.parameters.num_search_workers=1;s.parameters.max_time_in_seconds=10;status=s.Solve(m);assert status in (cp_model.OPTIMAL,cp_model.FEASIBLE)
res={'status':s.StatusName(status),'clocks':s.Value(end),'bound':s.BestObjectiveBound(),'operations':[{'kind':k,'qs':qs,'time':s.Value(ts[i])} for i,(k,qs,_) in enumerate(items)]}
(H/'spider_serial.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res),flush=True)
