"""PRESYN native operations, audited provenance, and full circuit pricing."""
import os,sys,re,json,copy,math,time,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT/'inputs'),str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/TREP2'),str(ROOT/'work/lanes/EVAL'),str(ROOT/'work')]
import schedule as S
from util import native_times
import exact2,fast_third
import numpy as np
from ortools.sat.python import cp_model
import xtim
xtim.cache_dir=str(OUT/'.xtim_cache')
sys.path.insert(0,str(OUT))
A=[1,14,8,9,2,16,15];B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28]
D=[0,20,7,10,3,22,21];PD=[0,20,7,4,3,15,8]
BASE=OUT/'inputs/v22h_c2c9';BAR=7.13060e-5
OriginalUnit=S.Unit
class Unit(OriginalUnit):
 def __init__(self,lines,raw_indices=()):
  if len(lines)==1 and lines[0].startswith('h '):
   self.lines=lines;self.raw_indices=list(raw_indices);self.name='H';self.qs=S.name_qs(lines[0])[1];self.last_is_measure=False
  else:super().__init__(lines,list(raw_indices))
S.Unit=Unit

def read(stem):
 stem=Path(stem);text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text())
 h,r,tail=S.qasm_ops(text);us=S.fold_units(r);ts=native_times(text,us)
 return dict(h=h,u=us,t=ts,tail=tail,meta=meta,source=str(stem))
def textof(c):return S.emit(c['h'],c['u'],c['t'],c['tail'])
def key(u):return tuple(u.lines[:2] if u.name=='MX' else u.lines)
def provenance(c):
 ref=read(OUT/'inputs/encoder19');avail={}
 for i,u in enumerate(c['u']):avail.setdefault(key(u),[]).append(i)
 tags=['suffix']*len(c['u']);origin={}
 for ri,(u,t) in enumerate(zip(ref['u'],ref['t'])):
  if t>29:continue
  assert key(u) in avail and avail[key(u)],(ri,u.lines)
  i=avail[key(u)].pop(0);origin[i]=ri
  tags[i]='T_layers' if u.name in ('T','TDG') else ('injection' if ri<=30 else 'stabilizer' if ri<=76 else 'check1' if ri<=102 else 'check2')
 assert len(origin)==129 and sum(c['u'][i].name=='CX' for i in origin)==75
 c['tags']=tags;c['origin']=origin;c['meta']['prefix_unit_indices']=sorted(origin)
 return c
def normalize(c):
 c['h']=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];','creg c[256];']
 order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));text=textof(c)
 h,r,tail=S.qasm_ops(text);us=S.fold_units(r);ts=native_times(text,us)
 assert [c['u'][i].lines for i in order]==[u.lines for u in us], 'native fold changed'
 assert [S.compress(c['t'])[i] for i in order]==ts, 'native timing mismatch'
 for u in us:
  if u.name=='CX':
   x,y=u.qs;assert abs(x//6-y//6)+abs(x%6-y%6)==1,(x,y)
 if 'tags'in c:c['tags']=[c['tags'][i]for i in order]
 if 'origin'in c:c['origin']={j:c['origin'][i]for j,i in enumerate(order)if i in c['origin']}
 c.update(h=h,u=us,t=ts,tail=tail)
 roundts=[max(t for u,t in zip(us,ts)if u.lines==[f'cx q[{a}],q[{b}];'])for a,b in list(zip(D,A))+list(zip(B,C))]
 c['meta'].update(data_qubits=D,R=min(roundts),round_range=[min(roundts),max(roundts)],native_depth=max(ts)+1,cx=sum(u.name=='CX'for u in us))
 if 'tags'in c:c['meta'].update(prefix_unit_indices=[i for i,t in enumerate(c['tags'])if t!='suffix'],component_tags=c['tags'])
 return c
def save(c,name,change):
 c=normalize(c);c['meta'].update(change=change,source=c['source']);stem=OUT/name
 stem.with_suffix('.qasm').write_text(textof(c));stem.with_suffix('.json').write_text(json.dumps(c['meta'],indent=2)+'\n')
 return stem
def placement(c,mode='alap',rigid=False,compact=False,weights=None):
 us=c['u'];old=c['t'];m=cp_model.CpModel();horizon=max(max(old)+50,100)
 ts=[m.new_int_var(0,horizon,f't{i}')for i in range(len(us))];per={}
 for i,u in enumerate(us):
  for q in u.qs:per.setdefault(q,[]).append(i)
 for seq in per.values():
  for a,b in zip(seq,seq[1:]):m.add(ts[b]>ts[a])
 end=m.new_int_var(0,horizon,'end');m.add_max_equality(end,ts)
 if rigid:
  shift=m.new_int_var(-50,50,'shift')
  for i,tag in enumerate(c['tags']):
   if tag=='suffix':m.add(ts[i]==old[i]+shift)
 m.minimize(end);s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=20
 status=s.solve(m)
 if status not in(cp_model.OPTIMAL,cp_model.FEASIBLE):raise ValueError(s.status_name(status))
 endval=s.value(end);m.add(end==endval)
 if compact:
  gaps=[]
  for q,seq in per.items():
   for a,b in zip(seq,seq[1:]):
    if c['tags'][b]!='suffix' and us[b].name not in ('RX','RESET'):
     gaps.append((weights or {}).get(q,4 if q in PD else 1)*(ts[b]-ts[a]-1))
  m.minimize(10000*sum(gaps)-sum(ts))
 elif mode=='asap':m.minimize(sum(ts))
 else:m.maximize(sum(ts))
 status=s.solve(m);assert status in(cp_model.OPTIMAL,cp_model.FEASIBLE)
 c['t']=[s.value(t)for t in ts];c['meta']['schedule_objective']=dict(mode=mode,rigid=rigid,compact=compact,makespan=endval+1,status=s.status_name(status))
 return c
def add(c,index,lines,tag='check_extra'):
 c['u'].insert(index,Unit(lines));c['t'].insert(index,c['t'][min(index,len(c['t'])-1)])
 c['tags'].insert(index,tag);c.pop('origin',None)
def score(stem,procs=1):
 stem=Path(stem);text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text())
 t=time.monotonic();ev=exact2.Eval(text,meta['data_qubits']);c1=float(ev.fp@ev.n_single)
 if os.getenv('PRESYN_MOMENTS')=='1' and abs(c1)<1e-12:
  import moments
  row=moments.evaluate(ev);row.update(CX=meta['cx'],R=meta['R'],evaluator='exact2 model, Fourier-moment exact contraction',sha256=hashlib.sha256(text.encode()).hexdigest())
  stem.with_suffix('.exact.json').write_text(json.dumps(row,indent=2)+'\n');print(stem.name,json.dumps(row),flush=True);return row
 r=exact2.run(ev,procs,third=abs(c1)<1e-12,keep_thr=1)
 row=dict(c1=c1,second=r['loss'],exp_minus_A1=math.exp(-r['A1']),CX=meta['cx'],R=meta['R'])
 if abs(c1)<1e-12:
  tri,_=fast_third.third_order(ev,procs);row.update(third=tri+r['t3bc'],total=r['loss']+tri+r['t3bc'],weight3=tri,pair_times_others=r['t3bc'])
 row['seconds']=time.monotonic()-t;row['sha256']=hashlib.sha256(text.encode()).hexdigest()
 stem.with_suffix('.exact.json').write_text(json.dumps(row,indent=2)+'\n');print(stem.name,json.dumps(row),flush=True)
 return row
