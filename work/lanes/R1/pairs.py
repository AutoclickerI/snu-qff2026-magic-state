"""MAIN/ablate.py --pairs engine with route-aware labels for staggered rounds.
The stock time cutoff calls every post-33 event 'round', hiding block transfers.
"""
import os,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2];sys.path.insert(0,str(H.parent/'MAIN'))
import ablate,xtim
xtim.cache_dir=str(H/'.xtim_cache')
stem=Path(sys.argv[1]);procs=int(sys.argv[2]);d=json.loads(Path(str(stem)+'.json').read_text());lp=Path(d['source']['layout']);lp=lp if lp.is_absolute() else ROOT/lp;lay=json.loads(lp.read_text());P=set(lay['P']);A=set(lay['a']);roles={};physical=lay['args'].get('physical',False)
def put(t,qs,role):roles[t,tuple(sorted(qs))]=role
for key,v in lay['tokens'].items():
 for j,(u,w,t,e) in enumerate(zip(v['pos'],v['pos'][1:],v['times'],v['ends'])):
  if u==w:continue
  role=key[0].upper()+'move'
  if physical:
   if not v['fast'][j]:put(v['target_start'][j],[w],role)
   put(t,[u,w],role);put(t+1,[u,w],role)
  else:put(t,[w],role);put(t+1,[u,w],role);put(t+2,[u,w],role)
for i in range(7):
 for k in 'ab':
  v=lay['tokens'][f'{k}{i}'];q=v['pos'][-1];dq=lay['data_at_A'][i] if k=='a' else lay['tokens'][f'd{i}']['pos'][-1]
  put(v['coupling'],[q,dq],'round');put(v['coupling']+1,[q],'round')
def role_at(q,t):
 for key,v in lay['tokens'].items():
  if key[0]!='d' and t>v['coupling']+1:continue
  qq=v['pos'][0]
  for dst,e in zip(v['pos'][1:],v['ends']):
   if e<=t:qq=dst
  if q==qq:return key
 return None
def op(qs,t):
 if (t,tuple(sorted(qs))) in roles:return roles[t,tuple(sorted(qs))]
 if t<=32 and set(qs)<=P:return 'pre'
 if set(qs)<=A:return 'Aprep'
 return 'BCprep'
def idle(q,t,owner):
 if t<=32 and q in P:return 'pre'
 key=role_at(q,t)
 if key:
  if key[0]=='d':return 'tail' if t>lay['tokens']['b'+key[1:]]['coupling'] else 'wait'
  return key[0].upper()+'idle'
 return owner
ablate.pairs(Path(str(stem)+'.qasm').read_text(),d['data_qubits'],op,idle,procs)
