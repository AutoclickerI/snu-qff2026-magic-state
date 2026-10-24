"""Explicit singleton-policy witnesses and nontrivial boundary-cache controls."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from synth import B,C,verify
from build import build
from cache import setup,contract,evaluate
import copy,json,numpy as np,time
base=json.loads((H/'inputs/base.prep.json').read_text());base.update(kind='policy',value=9)
text,md=build(base,dict(timing='project'));init=md['init_times'];z=np.load(H/'boundary.cache.npz',allow_pickle=True);rows=[]
for a,b in [(10,11),(11,12)]:
 d=copy.deepcopy(base);d['ops'][a].remove([4,5]);d['ops'][b].remove([4,5]);v=verify(d);assert v['stim_target_pass'] and v['policy_pass']
 text,md=build(d,dict(timing='alap',fixed_init=init));stem=H/'inputs'/f'cache_cancel_{a}_{b}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));ev,bb,ks,prep,ext,hh=setup(stem);assert hh==str(z['ext_hash']),hh
 result=contract(ev,prep,z['response'],z['n3']);full=evaluate(ev);assert abs(result['total']-full['total'])<1e-14
 rows.append(dict(control=str(stem),cache=result,full=full,delta=result['total']-full['total']));print(json.dumps(rows[-1]),flush=True)
(H/'cache.physical_validation.json').write_text(json.dumps(rows,indent=2));rows=[]
for i in range(7):
 d=copy.deepcopy(base);d['value']=9+i;d['ops'] += [[[B[i],C[i]]],[[B[i],C[i]]]];v=verify(d);assert v['stim_target_pass'] and v['policy_pass'] and not v['clean_pass'];assert set(map(int,v['residual_classes']))=={9+i}
 attempts=[]
 for shift in (0,1,2):
  try:text,md=build(d,dict(timing='alap',round_shift=shift));break
  except ValueError as e:attempts.append(dict(shift=shift,error=str(e)))
 else:raise AssertionError('two extra gates must schedule with two added steps')
 stem=H/'finalists'/f'policy_tail_{9+i}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2))
 from exact2 import Eval
 ev=Eval(text,md['data_qubits']);row=evaluate(ev);row.update(tag=stem.name,verification=v,R=md['R'],CX=md['CX'],shift=shift,attempts=attempts,delta_loss=row['total']-6.922103982278669e-5,delta_A1=-np.log(row['exp_minus_A1']/.5408595777123605))
 stem.with_suffix('.screen.json').write_text(json.dumps(row,indent=2));rows.append(row);print(json.dumps(row),flush=True)
(H/'policy_controls.json').write_text(json.dumps(rows,indent=2))
