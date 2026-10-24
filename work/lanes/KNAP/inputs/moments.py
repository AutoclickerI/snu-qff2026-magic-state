"""Exact second/third-order contraction in decoder Fourier moments.
Shares exact2's model/Engine. Distinct-channel inclusion-exclusion is exact.
"""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import collections,itertools,json,math,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
import numpy as np
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
import exact2
from model import Basis

def evaluate(ev):
 t=time.monotonic();ng=len(ev.gkeys);nch=len(ev.m.chans);masks=[0];coefs=[1.]
 for key,coef in zip(ev.e.keys,ev.e.W*ev.e.beta):
  T,a,b=key;mask=a|(b<<3)|(1<<6)
  mask|=(1<<8) if T=='X' else ((1<<7)|(1<<9))
  masks.append(mask);coefs.append(-coef)
 K=len(masks);chars=1-2*(np.bitwise_count(ev.fe[:,None]&np.array(masks)[None,:])%2).astype(float)
 fmoment=ev.fp[:,None]*chars
 M=np.zeros((ng,K));MC=np.zeros((ng,nch,K));Pch=np.bincount(ev.fch,weights=ev.fp,minlength=nch)
 MW=np.zeros((ng,K));chsets=[]
 for g,ix in enumerate(ev.gmem):
  M[g]=fmoment[ix].sum(axis=0);np.add.at(MC[g],ev.fch[ix],fmoment[ix]);MW[g]=(fmoment[ix]*Pch[ev.fch[ix],None]).sum(axis=0);chsets.append(set(ev.fch[ix]))
 # Dependent projector products must retain their noiseless signs.
 bas=Basis();indices=[];constraints=[]
 for i,(x,z,c) in enumerate(ev.e.projs):
  combo=bas.express(x|(z<<ev.e.r))
  if combo is None:bas.add(x|(z<<ev.e.r));indices.append(i)
  else:
   rel=1<<i
   for j,bi in enumerate(indices):
    if combo>>j&1:rel^=1<<bi
   constraints.append(rel)
 def syndrome(d):return sum(((d&h).bit_count()%2)<<j for j,h in enumerate(constraints))
 sy=[syndrome(d) for s,d in ev.gkeys];groups=collections.defaultdict(list)
 for i,y in enumerate(sy):groups[y].append(i)
 overlap={};overlapw={};overlapch={};zero=np.zeros(K)
 # Only pairs that share a physical channel need a correction.
 cgroups=collections.defaultdict(set)
 for g,cs in enumerate(chsets):
  for c in cs:cgroups[c].add(g)
 opairs={tuple(sorted((a,b))) for gs in cgroups.values() for a in gs for b in gs}
 for a,b in opairs:
  ch=np.array(sorted(chsets[a]&chsets[b]),dtype=int);prod=MC[a,ch]*MC[b,ch]
  overlap[a,b]=prod.sum(axis=0);overlapw[a,b]=(prod*Pch[ch,None]).sum(axis=0);overlapch[a,b]=ch
 def cross(a,b):return overlap.get((min(a,b),max(a,b)),zero)
 cache={}
 def coeff(s,d):
  key=(s,d)
  if key not in cache:
   v=ev.e.table(s,d)
   cache[key]=None if v is None else .5*np.array([v[0],*v[1]])*np.array(coefs)
  return cache[key]
 SA=float(ev.fp@ev.a_single);A1=float(ev.fp@(1-ev.a_single));c1=float(ev.fp@ev.n_single)
 assert abs(c1)<1e-12,c1
 pair=0.;t3bc=0.;npairs=0
 for a in range(ng):
  sa,da=ev.gkeys[a]
  for b in groups[sy[a]]:
   if b<a:continue
   sb,db=ev.gkeys[b];coef=coeff(sa^sb,da^db)
   if coef is None:continue
   W=M[a]*M[b]-cross(a,b);den=2 if a==b else 1
   pair+=float(coef@W)/den
   weighted=MW[a]*M[b]+M[a]*MW[b]-2*overlapw.get((a,b),zero)
   t3bc+=float(coef@(-SA*W+weighted))/den;npairs+=1
 tpair=time.monotonic()-t;t3=0.;ntriples=0
 for a in range(ng):
  sa,da=ev.gkeys[a]
  for b in range(a,ng):
   sb,db=ev.gkeys[b];Cab=cross(a,b)
   for c in groups.get(sy[a]^sy[b],()):
    if c<b:continue
    sc,dc=ev.gkeys[c];coef=coeff(sa^sb^sc,da^db^dc)
    if coef is None:continue
    W=M[a]*M[b]*M[c]-Cab*M[c]-cross(a,c)*M[b]-cross(b,c)*M[a]
    common=chsets[a]&chsets[b]&chsets[c]
    if common:
     ix=np.array(sorted(common),dtype=int);W+=2*(MC[a,ix]*MC[b,ix]*MC[c,ix]).sum(axis=0)
    den=6 if a==c else (2 if a==b or b==c else 1)
    t3+=float(coef@W)/den;ntriples+=1
 return dict(c1=c1,second=pair,third=t3+t3bc,total=pair+t3+t3bc,exp_minus_A1=math.exp(-A1),T3a=t3,t3bc=t3bc,pair_seconds=tpair,seconds=time.monotonic()-t,pairs=npairs,triples=ntriples,table_keys=len(cache))

if __name__=='__main__':
 stem=Path(sys.argv[1]);text=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits'];ev=exact2.Eval(text,data);row=evaluate(ev);stem.with_suffix('.moments.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
