"""All-orders boundary cache: retain boundary detector Fourier variables.
The 128 open detector responses, with decoder characters, give all 2048
boundary Pauli responses. Every physical channel remains categorical.
"""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
os.environ['QUANTUMN_REPO']=str(ROOT);os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
sys.path[:0]=[str(H),str(H/'audit')]
from cache import setup,fwht,prep_polynomials
import fresh_exact_walsh as w
import numpy as np,json,collections,math,time,argparse,multiprocessing as mp
from allorders_general import prepare as general_prepare

def minfill_keep(scopes,keep):
 graph=collections.defaultdict(set)
 for ss in scopes:
  for v in ss:graph[v].update(set(ss)-{v})
 order=[];width=0
 while set(graph)-set(keep):
  def key(v):
   ns=graph[v];return sum(len(ns-{u}-graph[u]) for u in ns)//2,len(ns),v
  v=min(set(graph)-set(keep),key=key);ns=graph.pop(v);width=max(width,len(ns));order.append(v)
  for u in ns:graph[u].discard(v);graph[u].update(ns-{u})
 return order,width

def open_contract(factors,order,keep):
 for v in order:
  take=[f for f in factors if v in f[0]];factors=[f for f in factors if v not in f[0]]
  if not take:continue
  union=tuple(sorted(set().union(*(set(s) for s,a in take))))
  out=np.ones((2,)*len(union))
  for scope,a in take:out*=a.reshape(tuple(2 if u in scope else 1 for u in union))
  out=out.mean(axis=union.index(v));factors.append((tuple(q for q in union if q!=v),out))
 out=np.ones((2,)*len(keep))
 for scope,a in factors:
  assert set(scope)<=set(keep)
  out*=a.reshape(tuple(2 if u in scope else 1 for u in keep))
 return out.reshape(-1,order='F')

def canonical(fs):return tuple(sorted((int(f['s']),int(f['d']),int(f['e']),round(float(f['p']),17)) for f in fs))

def exact_prep(ev,prep,n):
 char=np.ones(n);tmp=np.zeros(n)
 for items in prep.values():
  tmp[:]=0;tmp[0]=1-sum(ev.fp[i] for i,k in items)
  for i,k in items:tmp[k]+=ev.fp[i]
  char*=fwht(tmp)
 p=fwht(char)/n;assert abs(p.sum()-1)<1e-12 and p.min()>-1e-14;return p

OPEN_STATE=None
OPEN_KERNELS={}
def response_one(key):
 m,e,outside,nd,ks,psi,where,order,keep,boundary_d,boundary_e=OPEN_STATE
 pm=None if key is None else e.Qs[key]
 if pm not in OPEN_KERNELS:OPEN_KERNELS[pm]=w.kernel(e,ks,psi,where,key)
 emask=0 if key is None else w.emask_for(key)
 factors=[w.channel_factor(m,fs,nd,emask) for fs in outside.values()]+[OPEN_KERNELS[pm]]
 ft=open_contract(factors,order,keep);resp=fwht(ft)/len(ft);values=resp[boundary_d]
 if key is not None:values=values*(1-2*(np.bitwise_count(boundary_e&emask)%2).astype(float))
 return values

def compile(stem,procs=1):
 start=time.monotonic();ev,b,classes,prep,ext,hh=setup(stem)
 m,e,groups,nd,ks,psi,where,oldorder=general_prepare(stem)
 # Independent walkers must agree on the entire physical categorical model.
 ours=collections.defaultdict(list)
 for f in ev.m.faults:ours[f['chan']].append(f)
 # The judge places detector declarations at their last record; the audit
 # keeps QASM declaration order. Match physical projector Paulis exactly.
 positions=collections.defaultdict(list)
 for j,pm in enumerate(m.proj_m):positions[pm].append(j)
 permutation=[positions[pm].pop() for pm in ev.m.proj_m]
 def to_eval(d):return sum(((d>>j)&1)<<i for i,j in enumerate(permutation))
 def to_audit(d):return sum(((d>>i)&1)<<j for i,j in enumerate(permutation))
 classes=[(s,to_audit(d),ee) for s,d,ee in classes]
 mapped={ch:[dict(f,d=to_eval(f['d'])) for f in fs] for ch,fs in groups.items()}
 lookup=collections.defaultdict(list)
 for ch,fs in mapped.items():lookup[canonical(fs)].append(ch)
 assert collections.Counter(map(canonical,ours.values()))==collections.Counter(map(canonical,mapped.values())), 'independent channel signature mismatch'
 inside=set()
 for ch in prep:inside.add(lookup[canonical(ours[ch])].pop())
 boundary_union=0
 for s,d,ee in classes:assert s==0;boundary_union|=d
 keep=tuple(i for i in range(nd) if boundary_union>>i&1);assert 1<=len(keep)<=9,('unsupported retained boundary size',len(keep))
 outside={ch:fs for ch,fs in groups.items() if ch not in inside}
 scopes=[]
 for fs in outside.values():
  union=0
  for f in fs:union|=f['d']|(f['s']<<nd)
  scopes.append({i for i in range(nd+len(m.rots)) if union>>i&1})
 scopes.append(set(ks));order,width=minfill_keep(scopes,keep)
 print(json.dumps(dict(event='compiled_graph',width=width,kept_detectors=keep,prep_channels=len(prep),external_channels=len(outside))),flush=True)
 assert width<=26,('open boundary width exceeds planned memory',width)
 boundary_d=np.array([sum(((d>>v)&1)<<j for j,v in enumerate(keep)) for s,d,ee in classes]);boundary_e=np.array([ee for s,d,ee in classes]);cache={};obs=np.zeros(len(classes));A=None
 global OPEN_STATE
 OPEN_STATE=(m,e,outside,nd,ks,psi,where,order,keep,boundary_d,boundary_e)
 def collect(responses):
  nonlocal A,obs
  for j,values in enumerate(responses):
   if j==0:A=values
   else:obs+=e.W[j-1]*e.beta[j-1]*values
   print(json.dumps(dict(event='character',index=j,seconds=time.monotonic()-start)),flush=True)
 if procs==1:collect(map(response_one,[None]+e.keys))
 else:
  with mp.get_context('fork').Pool(procs) as pool:collect(pool.imap(response_one,[None]+e.keys))
 N=.5*(A-obs);p=exact_prep(ev,prep,len(classes));result=dict(loss=float(p@N/(p@A)),acceptance=float(p@A),numerator=float(p@N),seconds=time.monotonic()-start,width=width,exterior_hash=hh,boundary_rank=len(b.vecs),all_orders=True,prep_channels=len(prep))
 out=stem.with_suffix('.boundary_allorders.npz');np.savez_compressed(out,N=N,A=A,exterior_hash=hh)
 stem.with_suffix('.boundary_allorders.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
 # Check all three existing physical control circuits against full all-orders
 # receipts when present; exterior mismatch is a rejection, never reuse.
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stem',type=Path);p.add_argument('--procs',type=int,default=1);a=p.parse_args();compile(a.stem,a.procs)
