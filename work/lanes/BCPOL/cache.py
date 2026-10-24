"""Exact degree-three boundary response cache; no all-orders claim.
Physical channels remain categorical. Fixed exterior signatures, probabilities,
and the ideal decoder response must match before a cache can score a candidate.
"""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
os.environ.setdefault('XTIM_TWIRL_CACHE_DIR',str(H/'.xtim_cache'))
sys.path[:0]=[str(H),str(ROOT/'work/lanes/EVAL')]
import numpy as np,json,math,collections,hashlib,time,copy
from boundary import audit,pack,unpack
from model import Basis
from synth import B,C
from moments_batch import evaluate

def fwht(a):
 a=np.array(a,copy=True,dtype=float);n=a.shape[-1];h=1
 while h<n:
  z=a.reshape(*a.shape[:-1],-1,2*h);u=z[...,:h].copy();v=z[...,h:].copy();z[...,:h]=u+v;z[...,h:]=u-v;h*=2
 return a

def setup(stem):
 ev,b,rec=audit(stem);m=ev.m;nd=rec['nd'];boundary=rec['boundary'];region=rec['region_qubits'];r=len(b.vecs);assert r<=14
 keys=[unpack(v,nd) for v in b.vecs];ks=[(0,0,0)]
 for a in keys:ks += [tuple(x^y for x,y in zip(k,a)) for k in ks[:]]
 init={q:max((min(t for qq,t in m.steps[i]) for i,u in enumerate(m.prog) if q in u.qubits and u.name in ('M','MX','R','RX') and m.steps[i] and min(t for qq,t in m.steps[i])<boundary),default=-1) for q in region}
 if rec['region_init_times'] is not None:init.update({int(q):int(t) for q,t in rec['region_init_times'].items() if int(q) in region})
 members=collections.defaultdict(list)
 for i,f in enumerate(m.faults):members[f['chan']].append(i)
 prep={};external=[]
 for ch,ix in members.items():
  c=m.chans[ch];st=m.steps[c['ins']];tt=min(t for q,t in st) if st else -1
  eligible=set(c['qubits'])<=set(region) and tt<boundary and all(tt>=init[q] for q in c['qubits'])
  if c['gap'] is not None:
   q,first,n=c['gap'];eligible=eligible and first>init[q] and first+n<=boundary
  coords=[b.express(pack((m.faults[i]['s'],m.faults[i]['d'],m.faults[i]['e']),nd)) for i in ix]
  if eligible and all(k is not None for k in coords):prep[ch]=list(zip(ix,coords))
  else:external.extend(ix)
 # A cache can only be reused when exterior physical channels match exactly.
 extcanon=[]
 for ch,ix in members.items():
  if ch not in prep:extcanon.append(sorted((m.faults[i]['s'],m.faults[i]['d'],m.faults[i]['e'],m.faults[i]['p']) for i in ix))
 ideal=(ev.e.rot,ev.e.projs,ev.e.Qs,ev.e.v.tolist(),ev.e.beta.tolist(),ks)
 ext_hash=hashlib.sha256(repr((sorted(extcanon),ideal)).encode()).hexdigest()
 return ev,b,ks,prep,external,ext_hash

def masks(ev):
 out=[0]
 for T,a,b in ev.e.keys:out.append(a|(b<<3)|(1<<6)|((1<<8) if T=='X' else ((1<<7)|(1<<9))))
 return np.array(out,dtype=np.int64)

def prep_polynomials(ev,prep,n):
 # Product_c (1 + epsilon * (noise_character_c - 1)).
 sums=np.zeros((3,n));x=np.zeros(n)
 for items in prep.values():
  x[:]=0
  for i,k in items:x[k]+=ev.fp[i];x[0]-=ev.fp[i]
  v=fwht(x)
  for j in range(3):sums[j]+=v**(j+1)
 a,b,c=sums
 return np.array([np.eye(1,n)[0],fwht(a)/n,fwht((a*a-b)/2)/n,fwht((a*a*a-3*a*b+2*c)/6)/n])

def constraints(ev):
 bas=Basis();inds=[];cs=[]
 for i,(x,z,c) in enumerate(ev.e.projs):
  v=bas.express(x|(z<<ev.e.r))
  if v is None:bas.add(x|(z<<ev.e.r));inds.append(i)
  else:cs.append((1<<i)^sum(1<<j for a,j in enumerate(inds) if v>>a&1))
 return lambda d:sum(((d&h).bit_count()%2)<<j for j,h in enumerate(cs))

def compile_cache(stem,out):
 t=time.monotonic();ev,b,ks,prep,external,ext_hash=setup(stem);n=len(ks);K=len(ev.e.keys)+1;ms=masks(ev)
 chars=1-2*(np.bitwise_count(np.array([k[2] for k in ks])[:,None]&ms)%2).astype(float)
 coefs=np.r_[1,-ev.e.W*ev.e.beta];zero=np.zeros(K)
 # Signed moment polynomial of exterior channels, through degree two.
 channels=collections.defaultdict(lambda:collections.defaultdict(lambda:np.zeros(K)))
 for i in external:
  f=ev.m.faults[i];channels[f['chan']][f['s'],f['d']]+=f['p']*(1-2*(np.bitwise_count(f['e']&ms)%2).astype(float));channels[f['chan']][0,0]-=f['p']
 one=collections.defaultdict(lambda:np.zeros(K));two=collections.defaultdict(lambda:np.zeros(K))
 for ch in channels.values():
  for k,v in ch.items():one[k]+=v
 items=list(one.items())
 for ia,(a,u) in enumerate(items):
  for ib in range(ia,len(items)):
   c,v=items[ib];two[a[0]^c[0],a[1]^c[1]]+=(.5 if ia==ib else 1)*u*v
 for ch in channels.values():
  ci=list(ch.items())
  for ia,(a,u) in enumerate(ci):
   for ib in range(ia,len(ci)):
    c,v=ci[ib];two[a[0]^c[0],a[1]^c[1]]-=(.5 if ia==ib else 1)*u*v
 syn=constraints(ev);index=collections.defaultdict(list)
 for i,k in enumerate(ks):index[syn(k[1])].append(i)
 response=np.zeros((2,3,n));calls=0
 for degree,dist in enumerate([{(0,0):np.ones(K)},one,two]):
  ss=[];ds=[];idx=[];mom=[]
  def flush():
   nonlocal calls
   if not ss:return
   A,E=ev.e.batch_tables(ss,ds);ii=np.array(idx);mm=np.array(mom);val=np.c_[A,E]
   np.add.at(response[0,degree],ii,.5*np.einsum('ij,ij,j->i',val,mm*chars[ii],coefs))
   np.add.at(response[1,degree],ii,A*mm[:,0]);calls+=len(ss)
   ss.clear();ds.clear();idx.clear();mom.clear()
  for (s,d),w in dist.items():
   if np.max(np.abs(w))<1e-25:continue
   for i in index.get(syn(d),[]):
    sk,dk,ek=ks[i];ss.append(s^sk);ds.append(d^dk);idx.append(i);mom.append(w)
    if len(ss)>=2048:flush()
  flush()
  print(json.dumps(dict(event='cache_degree',degree=degree,groups=len(dist),calls=calls,seconds=time.monotonic()-t)),flush=True)
 # Exterior pure-third numerator needs k=0 only; full c1 is zero here.
 original=ev.fp.copy();ev.fp[:]=0;ev.fp[external]=original[external]
 ext=evaluate(ev);a1=-math.log(ext['exp_minus_A1']);n3=ext['third']-a1*ext['second'];ev.fp[:]=original
 assert abs(response[0,2,0]-ext['second'])<1e-15
 np.savez_compressed(out,response=response,n3=n3,basis=np.array(b.vecs,dtype=object),ext_hash=ext_hash)
 result=contract(ev,prep,response,n3);full=evaluate(ev)
 assert abs(result['total']-full['total'])<1e-14,(result,full)
 rec=dict(stem=str(stem),exterior_hash=ext_hash,boundary_rank=len(b.vecs),prep_channels=len(prep),external_faults=len(external),table_calls=calls,cache_seconds=time.monotonic()-t,cache=result,full=full,delta=result['total']-full['total'],order=3,all_orders=False)
 out.with_suffix('.json').write_text(json.dumps(rec,indent=2));return rec

def contract(ev,prep,response,n3):
 t=time.monotonic();P=prep_polynomials(ev,prep,response.shape[-1]);N,A=response
 n1=N[1,0]+P[1]@N[0]
 n2=N[2,0]+P[1]@N[1]+P[2]@N[0]
 nthird=float(n3)+P[1]@N[2]+P[2]@N[1]+P[3]@N[0]
 aa1=A[1,0]+P[1]@A[0]
 assert abs(n1)<1e-12,n1
 return dict(c1=float(n1),second=float(n2),third=float(nthird-aa1*n2),total=float(n2+nthird-aa1*n2),exp_minus_A1=math.exp(aa1),score_seconds=time.monotonic()-t)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('stem',type=Path);p.add_argument('--out',type=Path,default=H/'boundary.cache.npz');a=p.parse_args();print(json.dumps(compile_cache(a.stem,a.out)),flush=True)
