"""Validated extension of the audit contraction to five diagonal projectors.
Retains the complete quantum projector sectors (including empty sectors) and
categorical noise factors. Width 26 is handled by parallel decoder characters.
"""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
os.environ['QUANTUMN_REPO']=str(ROOT);os.environ.setdefault('XTIM_TWIRL_CACHE_DIR',str(H/'.xtim_cache'))
sys.path[:0]=[str(H/'audit'),str(H)]
import fresh_exact_walsh as w
from fresh_signature_width import parse_current,minfill
import full_single_audit as fa
import json,math,time,collections,itertools,random,multiprocessing as mp,argparse
import numpy as np

def prepare(stem):
 fa.DATA=json.loads(stem.with_suffix('.json').read_text())['data_qubits'];ops,dets=parse_current(stem.with_suffix('.qasm').read_text());old=fa.noise_blocks;fa.noise_blocks=lambda text,p,first_order=True:old(text,p,first_order=False)
 try:m=fa.make_model(ops,dets)
 finally:fa.noise_blocks=old
 e=fa.Engine(m);nd=len(dets);nr=len(m.rots);active=[i for i,p in enumerate(e.projs) if p[:2]!=(0,0)]
 if e.r>5 or nr>15 or len(active)>5 or any(p[0] for p in e.projs) or any(e.v):raise ValueError(dict(rank=e.r,rotations=nr,active=active,non_diagonal=any(p[0] for p in e.projs),nonzero_reference=any(e.v)))
 ks=tuple(active+list(range(nd,nd+nr)));states=np.arange(1<<nr,dtype=np.uint32);psi=np.zeros((len(states),e.N),dtype=complex);psi[:,0]=1
 for j,(mj,wj,coef,theta) in enumerate(e.rot):
  signs=1-2*((states>>j)&1).astype(np.int8);psi=np.cos(theta)*psi+(1j*math.sin(theta)*coef)*signs[:,None]*(psi*e.sgn(wj)[None,:])[:,e.idx.astype(int)^mj]
 dvals=np.zeros(e.N,dtype=np.int32)
 for j,i in enumerate(active):dvals|=np.bitwise_count(np.arange(e.N)&e.projs[i][1])%2<<j
 where=[np.flatnonzero(dvals==v) for v in range(1<<len(active))]
 assert sum(map(len,where))==e.N and len(set(np.concatenate(where)))==e.N
 groups=collections.defaultdict(list)
 for f in m.faults:groups[f['chan']].append(f)
 scopes=[]
 for fs in groups.values():
  union=0
  for f in fs:union|=f['d']|(f['s']<<nd)
  scopes.append({i for i in range(union.bit_length()) if union>>i&1})
 elim=minfill(scopes+[set(ks)])
 if elim['width']>26:raise ValueError(f'Width {elim["width"]} exceeds validated computational scope 26')
 return m,e,groups,nd,ks,psi,where,elim

G=None

def one(key):
 m,e,groups,nd,ks,psi,where,elim=G;t=time.monotonic();emask=0 if key is None else w.emask_for(key)
 factors=[w.channel_factor(m,fs,nd,emask) for fs in groups.values()];factors.append(w.kernel(e,ks,psi,where,key));v=w.contract(factors,elim['order']);return dict(key=key,value=v,seconds=time.monotonic()-t)

def validate(stem,prepared):
 from moments_batch import exact2
 m,e,groups,nd,ks,psi,where,elim=prepared;ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'])
 # Independent integer-Pauli walker vs the actual Stim-based judge model.
 assert [(x,z,c,t) for x,z,c,t,i in m.rots]==[(x,z,c,t) for x,z,c,t,i in ev.m.rots], 'Rotation axes/signs mismatch'
 assert m.Q==ev.m.Q and m.cz==ev.m.cz and m.cxz==ev.m.cxz, 'Decoder observables/frame mismatch'
 pos=collections.defaultdict(list)
 for j,pm in enumerate(m.proj_m):pos[pm].append(j)
 perm=[pos[pm].pop() for pm in ev.m.proj_m]
 def to_eval(d):return sum(((d>>j)&1)<<i for i,j in enumerate(perm))
 def canonical(fs,convert=False):return tuple(sorted((int(f['s']),to_eval(int(f['d'])) if convert else int(f['d']),int(f['e']),round(float(f['p']),17)) for f in fs))
 ours=collections.defaultdict(list)
 for f in ev.m.faults:ours[f['chan']].append(f)
 assert collections.Counter(canonical(fs) for fs in ours.values())==collections.Counter(canonical(fs,True) for fs in groups.values())
 # Direct projector application cross-checks every active sector at selected
 # rotation-sign patterns; it checks the new sector construction explicitly.
 rng=random.Random(2401);patterns=[0,(1<<len(m.rots))-1]+rng.sample(range(1<<len(m.rots)),30);maxdiff=0.
 active=[i for i,p in enumerate(e.projs) if p[:2]!=(0,0)]
 for s in patterns:
  for dsub,indices in enumerate(where):
   d=sum(((dsub>>j)&1)<<i for j,i in enumerate(active));direct=e.table(s,d);A=0 if direct is None else direct[0]
   aa=float((np.abs(psi[s,indices])**2).sum());maxdiff=max(maxdiff,abs(A-aa));assert abs(A-aa)<1e-12
   for j,key in enumerate(e.keys):
    mj,wj,co=e.Qs[key];raw=(psi[s,e.idx.astype(int)^mj].conj()*co*e.sgn(wj)*psi[s]).real
    ee=float(raw[indices].sum());dd=0. if direct is None else direct[1][j];maxdiff=max(maxdiff,abs(ee-dd));assert abs(ee-dd)<1e-12
 # Three categorical channels, including correlated CX and rotation-sign faults.
 pair=exact2.run(ev,procs=1,third=False,keep_thr=1e-9)
 candidates=sorted(pair['big'],reverse=True)
 malignant=next(r for r in candidates if ev.m.chans[int(ev.fch[r[1]])]['name']=='DEPOLARIZE2' and ev.m.chans[int(ev.fch[r[2]])]['name']=='DEPOLARIZE2')
 lookup=collections.defaultdict(list)
 for c,fs in groups.items():lookup[canonical(fs,True)].append(c)
 chosen=[lookup[canonical(ours[int(ev.fch[malignant[k]])])].pop() for k in (1,2)]
 chosen.append(next(f['chan'] for f in m.faults if f['s']!=0 and len(f['qs'])==2 and f['chan'] not in chosen))
 events=[[dict(s=0,d=0,e=0,p=1-m.chans[c]['p'])]+groups[c] for c in chosen];cache={};ea=en=0.
 for trip in itertools.product(*events):
  p=math.prod(f['p'] for f in trip);s=d=ee=0
  for f in trip:s^=f['s'];d^=f['d'];ee^=f['e']
  if (s,d) not in cache:cache[s,d]=e.ntable(s,d)
  a,n=cache[s,d];ea+=p*a;en+=p*(0 if n is None else n[ee])
 vals=[];kernels={}
 for key in [None]+e.keys:
  pm=None if key is None else e.Qs[key]
  if pm not in kernels:kernels[pm]=w.kernel(e,ks,psi,where,key)
  emask=0 if key is None else w.emask_for(key);factors=[w.channel_factor(m,groups[c],nd,emask) for c in chosen]+[kernels[pm]];vals.append(w.contract(factors,elim['order']))
 A=vals[0];N=.5*(A-sum(wt*bt*v for wt,bt,v in zip(e.W,e.beta,vals[1:])));assert en>1e-10 and abs(A-ea)<1e-12 and abs(N-en)<1e-12
 return dict(channel_multiset_match=True,rotation_and_decoder_match=True,sector_checks=len(patterns)*len(where),max_sector_error=maxdiff,chosen_channels=chosen,event_count=math.prod(map(len,events)),walsh_A=A,enumerated_A=ea,walsh_N=N,enumerated_N=en,delta_A=A-ea,delta_N=N-en,width=elim['width'],active_projectors=len(active))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stem',type=Path);p.add_argument('--procs',type=int,default=3);p.add_argument('--validate-only',action='store_true');a=p.parse_args()
 if '// FRAME' in a.stem.with_suffix('.qasm').read_text():
  sys.path.insert(0,str(H/'v30'))
  from evaluator import run as judge_allorders
  if a.validate_only:raise ValueError('FRAME validation requires the full judge-model contraction')
  judge_allorders(a.stem,True);sys.exit(0)
 t=time.monotonic();G=prepare(a.stem);m,e,groups,nd,ks,psi,where,elim=G
 vr=validate(a.stem,G);a.stem.with_suffix('.allorders_general.validation.json').write_text(json.dumps(vr,indent=2));print(json.dumps(dict(event='validated',**vr)),flush=True)
 if a.validate_only:sys.exit(0)
 with mp.get_context('fork').Pool(a.procs) as pool:
  rows=[]
  for row in pool.imap(one,[None]+e.keys):rows.append(row);print(json.dumps(row),flush=True)
 A=rows[0]['value'];N=.5*(A-sum(wt*bt*r['value'] for wt,bt,r in zip(e.W,e.beta,rows[1:])));result=dict(loss=N/A,acceptance=A,numerator=N,width=elim['width'],active_projectors=vr['active_projectors'],seconds=time.monotonic()-t,procs=a.procs,validated=True,source='BCPOL five-projector extension of reviewer Walsh contraction')
 a.stem.with_suffix('.allorders.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
