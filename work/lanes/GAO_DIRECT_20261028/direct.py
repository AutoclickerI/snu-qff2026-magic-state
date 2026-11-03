"""Gao full noisy source-only benchmark; deliberately abstract 2q adjacency."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,copy,time
from pathlib import Path
from ortools.sat.python import cp_model
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path[:0]=[str(R/'work/lanes/GAO_QUOTIENT_20261028'),str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
import quotient as q,frame_tools as ft,record_contract
from price_abstract import abstract_raw
from qtools.evaluator import frontend as f,sparse_walsh as sw
ft.f=f;sw.fa=f;sw.parse_current=f.parse_current;record_contract.fa=f;ft.raw_check=abstract_raw;ft.OUT=H
D=[0,1,2,3,6,5,4];f.DATA=D
P=R/'work/lanes/SOTA_SOURCE_20261028/gao/gao_abstract_parallel'
def commutes(a,b):
 if not set(a.qs)&set(b.qs):return True
 if a.kind=='CX' and b.kind=='CX':return a.qs[0]!=b.qs[1] and b.qs[0]!=a.qs[1]
 if a.kind in ('T','TDG') and b.kind in ('T','TDG'):return True
 if a.kind in ('T','TDG') and b.kind=='CX':return a.qs[0]==b.qs[0]
 if b.kind in ('T','TDG') and a.kind=='CX':return b.qs[0]==a.qs[0]
 return False

def schedule(ops,seconds=15):
 N=len(ops);upper=max(o.time for o in ops);m=cp_model.CpModel();tt=[m.new_int_var(0,upper,f't{i}')for i in range(N)];iv=[m.new_fixed_size_interval_var(tt[i],1,f'i{i}')for i in range(N)]
 for wire in range(36):m.add_no_overlap([iv[i]for i,o in enumerate(ops)if wire in o.qs])
 for j,b in enumerate(ops):
  for i,a in enumerate(ops[:j]):
   if not commutes(a,b):m.add(tt[j]>=tt[i]+1)
 end=m.new_int_var(0,upper+1,'end');m.add_max_equality(end,[t+1 for t in tt])
 for i,o in enumerate(ops):
  if o.kind in ('T','TDG') and o.qs[0] in D:m.add(tt[i]==end-1)
 # prefer late reset and phases, which reduces waiting without adding ideal operations.
 m.minimize(100000*end-sum(tt[i] for i,o in enumerate(ops) if o.kind in ('R','RX','T','TDG')))
 for i,o in enumerate(ops):m.add_hint(tt[i],o.time)
 s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_search_workers=1;s.parameters.random_seed=7
 status=s.solve(m)
 if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):raise RuntimeError(s.status_name(status))
 for i,o in enumerate(ops):o.time=s.value(tt[i])
 ops.sort(key=lambda x:x.time)
 return {'status':s.status_name(status),'ticks':s.value(end),'solver_s':s.wall_time,'bound':s.best_objective_bound}

def run(kind):
 if kind=='original':
  ops,_=f.parse_current(P.with_suffix('.qasm').read_text());ops=[o for o in ops if o.time<57];frame=None
 elif kind=='frame':
  ops,frame,_=q.build('frame');ops=[o for o in ops if o.time<50]
 elif kind=='coherent':
  ops,frame,_=q.build('coherent',7,2);ops=[o for o in ops if o.time<50]
 else:raise ValueError(kind)
 # T on face commutes with every retained later face-control CX and other-wire reads.
 cutoff=max(o.time for o in ops)+1
 for o in ops:
  if o.kind in ('T','TDG') and o.qs[0] in D:o.time=cutoff
 ops.sort(key=lambda o:o.time)
 info=schedule(ops)
 f.DATA=D
 comp=record_contract.complete(f.make_model(ops,[]),[]);neg=[v for v in comp['missing'] if v['reference']]
 if neg:
  print('NEGATIVE',json.dumps(neg),flush=True);return
 ds=[set(r['bits'])for r in comp['missing']]
 stem=ft.emit(kind,ops,ds,D,frame,metadata={'abstract':True,'scope':'complete source only; no tail or resource operations','schedule':info,'contract':'all deterministic source rows'})
 raw=abstract_raw(stem.with_suffix('.qasm').read_text(),D)
 print('RAW',json.dumps({'kind':kind,'raw':raw,'schedule':info,'rows':len(ds),'cx':sum(o.kind=='CX'for o in ops),'T':sum(o.kind in ('T','TDG')for o in ops)}),flush=True)
 if raw['ok']:
  ss=ft.singles(stem);print('SINGLES',json.dumps({'kind':kind,'first_order_loss_at_p001':ss['first_order_loss'],'count':ss['harmful_count']}),flush=True)
  print('PRICE',json.dumps(ft.price(stem)),flush=True)
if __name__=='__main__':run(sys.argv[1])
