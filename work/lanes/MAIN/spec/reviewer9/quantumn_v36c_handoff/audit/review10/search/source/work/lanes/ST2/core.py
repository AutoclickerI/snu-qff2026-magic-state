"""Lane-local native circuit edits and algebraically pruned exact screening."""
import os,sys,re,json,math,time,hashlib,copy,traceback
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(OUT/'.xtim_cache')
sys.path[:0]=[str(ROOT/'work/lanes/TREP2'),str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
import exact2,fast_third
from model import Basis
import numpy as np
from ortools.sat.python import cp_model
import xtim
xtim.cache_dir=str(OUT/'.xtim_cache')
OrigUnit=S.Unit
class Unit(OrigUnit):
 def __init__(self,lines,raw_indices=()):
  if len(lines)==1 and lines[0].startswith('h '):
   self.lines=lines;self.raw_indices=list(raw_indices);self.name='H';self.qs=S.name_qs(lines[0])[1];self.last_is_measure=False
  else:super().__init__(lines,list(raw_indices))
S.Unit=Unit
A=[1,14,8,9,2,16,15];B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28];D=[0,20,7,10,3,22,21]
BASE=ROOT/'work/lanes/MAIN/v22h_c2c9'
BAR=7.130595678543103e-5

def read(stem):
 stem=Path(stem);text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());h,r,tail=S.qasm_ops(text);us=S.fold_units(r);ts=native_times(text,us)
 return dict(h=h,u=us,t=ts,tail=tail,meta=meta,source=str(stem))

def textof(c):return S.emit(c['h'],c['u'],c['t'],c['tail'])
def clone(c):return copy.deepcopy(c)
def bit(c):return max(map(int,re.findall(r'c\[(\d+)\]','\n'.join(s for u in c['u'] for s in u.lines)+'\n'+'\n'.join(c['tail']))))+1

def normalize(c):
 c['h']=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];','creg c[256];']
 # A native MX followed by a new reuse needs its closing H explicitly.
 # Otherwise the QASM converter unfolds the old MX into noisy H+M.
 order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));following={}
 for i in reversed(order):
  u=c['u'][i]
  if u.name=='MX' and len(u.lines)==2:
   j=following.get(u.qs[0])
   if j is not None and c['u'][j].name not in ('RESET','RX','H'):
    c['u'][i]=Unit(u.lines+[f'h q[{u.qs[0]}];'])
  for q in u.qs:following[q]=i
 text=textof(c);h,r,tail=S.qasm_ops(text);us=S.fold_units(r);ts=native_times(text,us)
 intended=sorted(zip(S.compress(c['t']),c['u']),key=lambda x:x[0])
 assert [(t,u.lines)for t,u in zip(ts,us)]==[(t,u.lines)for t,u in intended], 'native timing mismatch'
 for u in us:
  if u.name=='CX':
   x,y=u.qs;assert abs(x//6-y//6)+abs(x%6-y%6)==1
 c.update(h=h,u=us,t=ts,tail=tail)
 first=[]
 for a,b in list(zip(D,A))+list(zip(B,C)):
  first.append(max(t for u,t in zip(us,ts)if u.lines==[f'cx q[{a}],q[{b}];']))
 c['meta'].update(data_qubits=D,R=min(first),round_range=[min(first),max(first)],native_depth=max(ts)+1,cx=sum(u.name=='CX'for u in us))
 return c

def retime(c,targets=None,round_fixed=False,horizon=None):
 # Fixed per-wire order is an integral difference-constraint polytope.
 # L1 deviations are linearized; rounding a fractional optimum down retains
 # the precedence constraints and the integer optimum (checked below).
 from ortools.linear_solver import pywraplp
 old=c['t'];us=c['u'];horizon=horizon or max(old)+2
 m=pywraplp.Solver.CreateSolver('GLOP');tv=[m.NumVar(0,horizon,f't{i}')for i in range(len(us))]
 pred,_=S.build_dag(us)
 for j,ps in enumerate(pred):
  for i in ps:m.Add(tv[j]>=tv[i]+1)
 if round_fixed:
  for i,t in enumerate(old):
   if t>=c['meta']['R']:m.Add(tv[i]==t)
 for i,t in (targets or {}).items():m.Add(tv[i]==t)
 dev=[]
 for i,t in enumerate(old):
  d=m.NumVar(0,m.infinity(),f'd{i}');m.Add(d>=tv[i]-t);m.Add(d>=t-tv[i]);dev.append(d)
 m.Minimize(sum(dev));status=m.Solve()
 if status!=pywraplp.Solver.OPTIMAL:return None
 nt=[math.floor(v.solution_value()+1e-6)for v in tv]
 assert all(nt[j]>=nt[i]+1 for j,ps in enumerate(pred)for i in ps)
 assert all(0<=v<=horizon for v in nt)
 assert all(nt[i]==t for i,t in (targets or {}).items())
 assert abs(sum(abs(a-b)for a,b in zip(nt,old))-m.Objective().Value())<1e-5
 c['t']=nt;return c

def commute(a,b):
 if not set(a.qs)&set(b.qs):return True
 if a.name==b.name=='CX':
  x,y=map(int,S.QRE.findall(a.lines[0]));z,w=map(int,S.QRE.findall(b.lines[0]));return x!=w and z!=y
 return False

def setup_syndromes(ev):
 basis=Basis();indices=[];cons=[]
 for i,(x,z,c)in enumerate(ev.e.projs):
  vec=x|(z<<ev.e.r);combo=basis.express(vec)
  if combo is None:basis.add(vec);indices.append(i)
  else:
   rel=1<<i
   for j,k in enumerate(indices):
    if combo>>j&1:rel^=1<<k
   cons.append(rel)
 return [sum(((d&h).bit_count()%2)<<j for j,h in enumerate(cons))for s,d in ev.gkeys]

def score(text,data=D,details=False):
 start=time.monotonic();ev=exact2.Eval(text,data);c1=float(ev.fp@ev.n_single);a1=float(ev.fp@(1-ev.a_single))
 assert abs(c1)<1e-12, f'c1={c1}'
 sy=setup_syndromes(ev)
 # For c1=0, pairs with a nonzero state-independent detector relation
 # have exactly zero loss. Same surviving arithmetic as exact2._pair_chunk.
 pairs=[(a,b)for a in range(len(sy))for b in range(a,len(sy))if sy[a]==sy[b]]
 exact2.G.update(ev=ev,third=True,SA=float(ev.fp@ev.a_single),Pch=np.bincount(ev.fch,weights=ev.fp),pairs=pairs)
 p2,aa,sens,big,bc=exact2._pair_chunk((0,len(pairs),1e-15 if details else 1))
 tri,big3=fast_third.third_order(ev,1)
 row=dict(c1=c1,second=p2,third=tri+bc,total=p2+tri+bc,A1=a1,exp_minus_A1=math.exp(-a1),weight3=tri,pair_times_others=bc,seconds=time.monotonic()-start)
 if details:
  row['pairs']=[dict(value=x[0],faults=[ev.fault_label(j)for j in x[1:3]])for x in sorted(big,reverse=True)[:80]]
  row['triples']=[dict(value=x[0],faults=[ev.fault_label(j)for j in x[1:]])for x in sorted(big3,reverse=True)[:100]]
 return row

def worker(payload):
 text,meta,desc=payload
 try:
  import importlib.util
  spec=importlib.util.spec_from_file_location('bc_moments',OUT/'inputs/moments.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  ev=exact2.Eval(text,meta['data_qubits']);r=mod.evaluate(ev)
  r.update(A1=-math.log(r['exp_minus_A1']),weight3=r.pop('T3a'),pair_times_others=r.pop('t3bc'),evaluator='BCSYN2 exact Fourier contraction')
  threshold=min(BAR,desc.get('parent_total',BAR))
  for f in ([] if desc.get('local_track') else OUT.glob('*.exact.json')):
   try:
    prev=json.loads(f.read_text())
    if prev.get('exp_minus_A1',0)>=.505:threshold=min(threshold,prev['total'])
   except (ValueError,KeyError):pass
  if r['total']<threshold-1e-12 and r['exp_minus_A1']>=.505:
   ref=score(text,meta['data_qubits']);r['pruned_exact2_check']=ref
   assert max(abs(r[k]-ref[k])for k in ['second','third','total'])<1e-14,(r,ref)
  return dict(desc=desc,sha256=hashlib.sha256(text.encode()).hexdigest(),**r)
 except Exception as e:return dict(desc=desc,error=str(e),traceback=traceback.format_exc())

def save(stem,text,meta,row):
 stem=OUT/stem;stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(dict(meta,lns_result=row),indent=2)+'\n');stem.with_suffix('.exact.json').write_text(json.dumps(row,indent=2)+'\n')

def report():
 rows=[]
 for f in sorted(OUT.glob('*.jsonl')):
  for line in f.read_text().splitlines():
   try:
    r=json.loads(line)
    if 'desc'in r:rows.append(r)
   except json.JSONDecodeError:pass
 kept=[]
 for f in OUT.glob('*.exact.json'):
  try:
   r=json.loads(f.read_text())
   if r.get('exp_minus_A1',0)>=.505:kept.append((r['total'],f.name.replace('.exact.json',''),r))
  except (ValueError,KeyError):pass
 best=min(kept,key=lambda x:x[0])if kept else None
 mc={}
 for f in OUT.glob('*.mc.log'):
  for l in f.read_text().splitlines():
   m=re.match(r'(\S+) check (True|False)',l)
   if m:mc.setdefault(Path(m[1]).name,dict(seeds={},logs=set()))['check']=m[2]=='True'
   m=re.match(r'(\S+) (0|1000|2000) (\S+).* acc (\S+)',l)
   if m:
    z=mc.setdefault(Path(m[1]).name,dict(seeds={},logs=set()));z['seeds'][int(m[2])]=(float(m[3]),float(m[4]));z['logs'].add(f.name)
   m=re.match(r'(\S+) mean (\S+)',l)
   if m:mc.setdefault(Path(m[1]).name,dict(seeds={},logs=set()))['mean']=float(m[2])
 ranked=sorted([(v['mean'],k,v)for k,v in mc.items()if 'mean'in v and len(v['seeds'])==3 and v.get('check')and v['seeds'][0][1]>=.5])
 alias='pending'
 if (OUT/'best.json').exists():alias=json.loads((OUT/'best.json').read_text()).get('lns_result',{}).get('stem','see best.json')
 lines=['# LNS','', '**Status: running. A fully MC-ranked delivery exists; the complete move-set certificate is still open.**','',f'Delivery alias: `best.qasm/.json` = **{alias}**. Ranking uses completed 1e8-shot means at seeds 0/1000/2000; acceptance is a gate.','']
 if ranked:lines+=['Best completed MC mean: **%.9g**, `%s`; seed-0 acceptance **%.5f**.'%(ranked[0][0],ranked[0][1],ranked[0][2]['seeds'][0][1]),'']
 if best:
  val,stem,r=best;md=json.loads((OUT/(stem+'.json')).read_text());lines+=['Best exact screen: **%s**, **%.12g**, delta from v22h_c2c9 **%+.9g (%+.3f%%)**.'%(stem,val,val-BAR,100*(val/BAR-1)), 'Second %.12g; cubic %.12g; exp(-A1) %.8f; c1 p %.3g; R %s, %s CX.'%(r['second'],r['third'],r['exp_minus_A1'],r['c1'],md.get('round_range',md.get('R')),md.get('cx',md.get('CX'))),'This exact screen is not promoted by predicted acceptance or score alone. Its MC status is shown below.','']
 lines+=['| Finalist | Seed 0 | Seed 1000 | Seed 2000 | Mean | Seed-0 acc | Check |','|---|---:|---:|---:|---:|---:|---|']
 for k,v in sorted(mc.items(),key=lambda kv:kv[1].get('mean',1)):
  ss=[v['seeds'].get(i)for i in [0,1000,2000]];lines.append('| %s | %s | %s | %s | %s | %s | %s |'%(k,*[f'{z[0]:.8g}'if z else 'pending'for z in ss],f"{v['mean']:.8g}"if 'mean'in v else 'pending',f'{ss[0][1]:.5f}'if ss[0]else 'pending','PASS'if v.get('check')else 'pending'))
 lines+=['','| Move family | Evaluations | Invalid screens | Better than parent | Best exact delta vs starting bar |','|---|---:|---:|---:|---:|']
 for family in ['timing','commute','init','phase','readout','hop','triple']:
  rr=[r for r in rows if r['desc']['family']==family];vv=[r for r in rr if 'total'in r and r['exp_minus_A1']>=.505]
  lines.append('| %s | %d | %d | %d | %s |'%(family,len(rr),sum('error'in r for r in rr),sum(r['total']<r['desc'].get('parent_total',BAR)-1e-12 for r in vv),f"{min(r['total']for r in vv)-BAR:+.9g}"if vv else 'pending'))
 lines+=['','Counts are completed evaluations, including earlier controls/repeated recipes; build failures and interrupted work are not certificates. Full descriptions, hashes, objective parts and errors are in the lane JSONL logs. Physical-equivalence qualifications are below.','']
 if (OUT/'NOTES.md').exists():lines.append((OUT/'NOTES.md').read_text())
 (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')

def batch(candidates,label,workers=16):
 import concurrent.futures
 existing=set()
 for f in OUT.glob('*.jsonl'):
  for line in f.read_text().splitlines():
   try:existing.add(json.loads(line).get('sha256'))
   except:pass
 payloads=[]
 for c,desc in candidates:
  if c is None:continue
  try:c=normalize(c)
  except Exception as e:
   print('BUILD FAIL',desc,str(e),flush=True);continue
  txt=textof(c);sha=hashlib.sha256(txt.encode()).hexdigest()
  if sha in existing:continue
  existing.add(sha);payloads.append((txt,c['meta'],dict(desc,source=c['source'])))
 print(label,'candidates',len(payloads),'workers',workers,flush=True)
 best=BAR
 for f in OUT.glob('*.jsonl'):
  for line in f.read_text().splitlines():
   try:
    r=json.loads(line)
    if r.get('exp_minus_A1',0)>=.505:best=min(best,r.get('total',1))
   except:pass
 local_best=min([p[2].get('parent_total',BAR) for p in payloads if p[2].get('local_track')]+[float('inf')])
 with concurrent.futures.ProcessPoolExecutor(workers)as pool,(OUT/(label+'.jsonl')).open('a')as log:
  futures={pool.submit(worker,p):p for p in payloads}
  for fut in concurrent.futures.as_completed(futures):
   r=fut.result();payload=futures[fut];promoted=False
   if r.get('exp_minus_A1',0)>=.505 and (r.get('total',1)<best-1e-12 or (r['desc'].get('local_track')and r.get('total',1)<local_best-1e-12)):
    best=min(best,r['total']);local_best=min(local_best,r['total']);r['stem']=label+'_'+r['sha256'][:10];save(r['stem'],payload[0],payload[1],r);promoted=True
   log.write(json.dumps(r)+'\n');log.flush()
   if promoted:report()
   print(json.dumps(r),flush=True)
 report()
 return sorted([json.loads(l)for l in (OUT/(label+'.jsonl')).read_text().splitlines()if 'total'in json.loads(l)],key=lambda r:r['total'])
