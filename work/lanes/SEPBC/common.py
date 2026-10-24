"""ST1 native circuits, CP-SAT scheduling, and full-circuit exact objective."""
import os,sys,re,json,math,time,copy,hashlib,importlib.util
from pathlib import Path
H=Path(__file__).resolve().parent; ROOT=H.parents[2]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.dont_write_bytecode=True
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
sys.path[:0]=[str(ROOT/'work/lanes/BCSYN2'),str(ROOT/'work/lanes/EVAL'),str(ROOT/'work')]
import schedule as S
from util import native_times
import exact2
from ortools.sat.python import cp_model
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
OriginalUnit=S.Unit
class Unit(OriginalUnit):
 def __init__(self,lines,raw_indices=()):
  if len(lines)==1 and lines[0].startswith('h '):
   self.lines=lines;self.raw_indices=list(raw_indices);self.name='H';self.qs=S.name_qs(lines[0])[1];self.last_is_measure=False
  else:super().__init__(lines,list(raw_indices))
S.Unit=Unit
spec=importlib.util.spec_from_file_location('st1_moments',H/'moments.py');mom=importlib.util.module_from_spec(spec);spec.loader.exec_module(mom)
A=[1,14,8,9,2,16,15];B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28];D=[0,20,7,10,3,22,21]
def read(stem):
 stem=Path(stem);txt=stem.with_suffix('.qasm').read_text();h,r,tail=S.qasm_ops(txt);u=S.fold_units(r);ts=native_times(txt,u)
 return dict(h=h,ops=[dict(lines=x.lines,t=t,id=i)for i,(x,t)in enumerate(zip(u,ts))],tail=tail,meta=json.loads(stem.with_suffix('.json').read_text()),source=str(stem))
def unit(o):return Unit(o['lines'])
def rename(lines,mp):return [re.sub(r'q\[(\d+)\]',lambda m:f'q[{mp.get(int(m[1]),int(m[1]))}]',s)for s in lines]
def normalized(c):
 c=copy.deepcopy(c);c['ops'].sort(key=lambda o:o['t']);nxt={}
 for o in reversed(c['ops']):
  u=unit(o)
  if u.name=='MX' and len(u.lines)==2 and u.qs[0]in nxt and nxt[u.qs[0]]not in('RESET','RX','H'):
   o['lines'].append(f'h q[{u.qs[0]}];')
  for q in u.qs:nxt[q]=u.name
 us=[unit(o)for o in c['ops']];ts=[o['t']for o in c['ops']]
 txt=S.emit(c['h'],us,ts,c['tail']);h,r,tail=S.qasm_ops(txt);nu=S.fold_units(r);nt=native_times(txt,nu)
 assert [(t,u.lines)for t,u in zip(S.compress(ts),us)]==[(t,u.lines)for t,u in zip(nt,nu)],('native schedule mismatch',[(a,b)for a,b in zip([(t,u.lines)for t,u in zip(S.compress(ts),us)],[(t,u.lines)for t,u in zip(nt,nu)])if a!=b][:8],len(us),len(nu))
 for i,(o,u,t)in enumerate(zip(c['ops'],nu,nt)):
  o['t']=t
  if u.name=='CX':
   a,b=u.qs;assert abs(a//6-b//6)+abs(a%6-b%6)==1,o
 c['meta'].update(cx=sum(u.name=='CX'for u in nu),native_depth=max(nt)+1)
 return c,txt

def save(c,name):
 c,txt=normalized(c);stem=H/name
 stem.with_suffix('.qasm').write_text(txt);stem.with_suffix('.json').write_text(json.dumps(c['meta'],indent=2));stem.with_suffix('.plan.json').write_text(json.dumps(c,indent=1))
 return stem

def score(stem):
 stem=Path(stem);st=time.monotonic();txt=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits'];ev=exact2.Eval(txt,data)
 c1=float(ev.fp@ev.n_single);a1=float(ev.fp@(1-ev.a_single))
 if abs(c1)>=1e-12:r=dict(c1=c1,exp_minus_A1=math.exp(-a1),invalid_cubic=True)
 else:r=mom.evaluate(ev)
 r.update(seconds_total=time.monotonic()-st,sha256=hashlib.sha256(txt.encode()).hexdigest());stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));return r

def schedule(c,mode='alap',weights=None,fixed_round=False,delta=0,seconds=15):
 """Time-expanded native cell occupancy; exact-objective feedback sets weights."""
 c=copy.deepcopy(c)
 if not c.get('ordered'):c['ops'].sort(key=lambda o:o['t'])
 ops=c['ops'];us=[unit(o)for o in ops];old=[o['t']for o in ops];Hmax=max(old)+max(4,delta)
 m=cp_model.CpModel();ts=[m.NewIntVar(0,Hmax,f't{i}')for i in range(len(us))];last={}
 Rold=c['meta'].get('R',45);R=m.NewIntVar(0,Hmax,'R');roundids=[]
 for i,u in enumerate(us):
  for q in u.qs:
   if q in last:m.Add(ts[i]>ts[last[q]])
   last[q]=i
  if old[i]>=Rold:
   m.Add(ts[i]==R+old[i]-Rold);roundids.append(i)
  else:m.Add(ts[i]<R)
  m.AddHint(ts[i],old[i])
 if fixed_round:m.Add(R==Rold+delta)
 terminal=set()
 for q in range(36):
  seq=[i for i,u in enumerate(us)if q in u.qs]
  for j,i in enumerate(seq):
   if us[i].name in('MX','MEASURE')and(j+1==len(seq)or us[seq[j+1]].name in('RX','RESET')):terminal.add(i)
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.cp_model_presolve=False;s.parameters.max_time_in_seconds=seconds
 if not fixed_round:
  m.Minimize(R);st=s.Solve(m)
  if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):return None,dict(status=s.StatusName(st))
  m.Add(R==s.Value(R))
 if mode=='alap':m.Minimize(sum((1 if i in terminal else -1)*t for i,t in enumerate(ts)))
 elif mode=='near':
  ds=[]
  for i,t in enumerate(ts):
   d=m.NewIntVar(0,Hmax,f'd{i}');m.AddAbsEquality(d,t-old[i]);ds.append(d)
  m.Minimize(sum(ds))
 elif mode=='weighted':
  m.Minimize(sum(int(weights.get(str(o['id']),0))*ts[i]for i,o in enumerate(ops)))
 st=s.Solve(m)
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):return None,dict(status=s.StatusName(st))
 for i,o in enumerate(ops):o['t']=s.Value(ts[i])
 c['meta']['R']=s.Value(R);receipt=dict(status=s.StatusName(st),objective=s.ObjectiveValue(),bound=s.BestObjectiveBound(),seconds=s.WallTime(),mode=mode,R=s.Value(R))
 c['meta']['schedule']=receipt
 return c,receipt

def append_result(name,r,mechanism):
 with(H/'REPORT.md').open('a')as f:
  f.write(f'\n- `{name}`: '+json.dumps(r,sort_keys=True)+f' Mechanism/scope: {mechanism}\n')
