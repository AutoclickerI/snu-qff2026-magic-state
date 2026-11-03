"""Exact commutation-DAG whole-circuit retiming of Gao abstract circuit.

CX/CX only reorder when they commute; T/TDG cross only CX on their control.
Resets and measurements retain order on each wire. No adjacency is asserted.
All source, frame, and terminal channels are retained and fully noisy.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
for d in ('work/tools','work/lanes/END2_20261027','work/lanes/REBUILD20261027','work/lanes/CAT3_20261027','upstream/snu-qff2026-problem'):sys.path.insert(0,str(ROOT/d))
from ortools.sat.python import cp_model
from qtools.evaluator import frontend as f
from partial_square import ideal_contract_check
from joint import emit
from record_contract import singles
from smallcat import exact
P=H/'gao_abstract_parallel';D=json.loads(P.with_suffix('.json').read_text())['data_qubits'];ops,dets=f.parse_current(P.with_suffix('.qasm').read_text());

def commutes(a,b):
 if not(set(a.qs)&set(b.qs)):return True
 if a.kind=='CX' and b.kind=='CX':return a.qs[0]!=b.qs[1] and b.qs[0]!=a.qs[1]
 if a.kind in ('T','TDG') and b.kind in ('T','TDG'):return True
 if a.kind in ('T','TDG') and b.kind=='CX':return a.qs[0]==b.qs[0]
 if b.kind in ('T','TDG') and a.kind=='CX':return b.qs[0]==a.qs[0]
 return False

def solve(seconds=60):
 m=cp_model.CpModel();N=len(ops);oldmax=max(o.time for o in ops);t=[m.new_int_var(0,oldmax,f't{i}')for i in range(N)]
 iv=[m.new_fixed_size_interval_var(t[i],1,f'i{i}')for i in range(N)]
 for q in range(36):m.add_no_overlap([iv[i]for i,o in enumerate(ops)if q in o.qs])
 deps=0
 for j,b in enumerate(ops):
  for i in range(j):
   a=ops[i]
   if not commutes(a,b):m.add(t[j]>=t[i]+1);deps+=1
 if os.getenv('TIGHT'):
  terminal=m.new_int_var(0,oldmax,'terminal')
  for i,o in enumerate(ops):
   if o.time>=oldmax-2:m.add(t[i]==terminal+(o.time-(oldmax-2)))
 end=m.new_int_var(0,oldmax+1,'end');m.add_max_equality(end,[v+1 for v in t])
 if os.getenv('LATE'):
  chosen=[t[i]for i,o in enumerate(ops) if o.kind in ('R','RX','T','TDG')]
  m.minimize(100000*end-sum(chosen))
 else:m.minimize(end)
 for i,o in enumerate(ops):m.add_hint(t[i],o.time)
 s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_search_workers=1;s.parameters.random_seed=7
 status=s.solve(m);meta=dict(status=s.status_name(status),elapsed=s.wall_time,dependencies=deps,original_ticks=oldmax+1,objective_bound=s.best_objective_bound,objective_mode='100000*ticks - sum(reset/phase clocks)' if os.getenv('LATE') else 'ticks')
 if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):print(json.dumps(meta));return
 for i,o in enumerate(ops):o.time=s.value(t[i])
 ops.sort(key=lambda o:o.time);text=emit(ops,dets);f.DATA=D;raw=ideal_contract_check(text,D)
 stem=H/('gao_abstract_retimed_late' if os.getenv('LATE') else 'gao_abstract_retimed_tight' if os.getenv('TIGHT') else 'gao_abstract_retimed');stem.with_suffix('.qasm').write_text(text);meta.update(data_qubits=D,raw=raw,ticks=max(o.time for o in ops)+1,cx=sum(o.kind=='CX'for o in ops),diagnostic_only=True,grid_valid=False,qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),scope='Commutation-DAG retiming of full noisy all-to-all physical circuit, not adjacency-valid.')
 stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n');print('RAW',json.dumps(meta),flush=True)
 if raw['ok']:
  ss=singles(f.make_model(*f.parse_current(text)));print('SINGLES',json.dumps({'c1':ss['c1'],'harmful':len(ss['harmful_faults'])}),flush=True)
  p=exact(stem);meta.update(singles=ss,exact=p);stem.with_suffix('.result.json').write_text(json.dumps(meta,indent=2)+'\n');print('RESULT',json.dumps({'loss':p['loss'],'acceptance':p['acceptance'],'c1':ss['c1'],'harmful':len(ss['harmful_faults'])}),flush=True)
if __name__=='__main__':solve()
