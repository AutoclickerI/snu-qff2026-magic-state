"""Price all single detector removals by exact sparse contraction marginals.

Removing row i projects its dual Fourier variable to zero. Thus each accepted
moment is baseline + the (-1)^lambda_i weighted moment. Reverse contraction
computes all one-variable marginals without changing the noise model.
"""
import os,sys,time,json,math
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent/'sparse35'));import sparse_walsh as sw
import numpy as np
CTX={}

def align(x,scope,union):return x.reshape((x.shape[0],)+tuple(2 if u in scope else 1 for u in union))
def contract_marginals(factors,order,N):
 nbase=len(factors);fs=[(s,a,i)for i,(s,a)in enumerate(factors)];trace=[]
 for v in order:
  bucket=[f for f in fs if v in f[0]];fs=[f for f in fs if v not in f[0]]
  if not bucket:continue
  union=tuple(sorted(set().union(*(set(s)for s,_,_ in bucket))));n=max(x.shape[0]for _,x,_ in bucket);P=np.ones((n,)+(2,)*len(union))
  for s,x,i in bucket:P*=align(x,s,union)
  j=union.index(v);val=P.mean(axis=1+j);scope=tuple(u for u in union if u!=v);idx=nbase+len(trace)
  trace.append((v,union,scope,P,bucket,idx));fs.append((scope,val,idx))
 Z=np.ones(N)
 for s,x,i in fs:assert not s;Z*=x.reshape(-1)
 adj={i:(Z/x.reshape(-1))for s,x,i in fs if i>=nbase};marg={}
 for v,union,scope,P,bucket,idx in reversed(trace):
  C=adj.pop(idx);W=P*align(C,scope,union)*.5;j=union.index(v)
  marg[v]=(np.take(W,0,axis=1+j)-np.take(W,1,axis=1+j)).sum(axis=tuple(range(1,W.ndim-1)))
  for s,x,i in bucket:
   if i<nbase:continue
   assert np.all(x>0),'characteristic factors must be nonzero'
   G=W/align(x,s,union);axes=tuple(k+1 for k,u in enumerate(union)if u not in s)
   adj[i]=G.sum(axis=axes)if axes else G
 assert not adj
 return Z,marg

def row(key):
 eng,ks,psi,where,compiled,elim,cols=[CTX[x]for x in ('eng','ks','psi','where','compiled','elim','cols')];start=time.monotonic()
 states,weights,eb=sw.sparse_kernel(eng,ks,psi,where,key);emask=0 if key is None else sw.emask_for(key)
 factors=sw.factors_for(compiled,states,emask);Z,mg=contract_marginals(factors,elim['order'],len(states));val=float(weights@Z/(1<<len(ks)));kmap={v:i for i,v in enumerate(ks)};bias=[]
 for variables in cols:
  if len(variables)==1:
   v=variables[0]
   vec=Z*(1-2*((states>>kmap[v])&1).astype(np.int8))if v in kmap else mg.get(v,np.zeros_like(Z))
  else:
   outer=np.ones(len(states));ss=tuple(v for v in variables if v not in kmap)
   for v in variables:
    if v in kmap:outer*=1-2*((states>>kmap[v])&1).astype(np.int8)
   parity=1-2*(np.bitwise_count(np.arange(1<<len(ss),dtype=np.uint32))&1).astype(np.int8)
   extra=outer[:,None]*parity[None,:];extra=extra.reshape((len(states),)+(2,)*len(ss),order='F')
   vec,_=sw.contract_selector(factors+[(ss,extra)],elim['order'],len(states))
  bias.append(float(weights@vec/(1<<len(ks))))
 return dict(key=key,value=val,bias=bias,omission_bound=eb,seconds=time.monotonic()-start)

def run(stem,procs):
 import multiprocessing as mp
 p=Path(stem);start=time.monotonic();m,e,g,nd,ks,psi,where,dense=sw.prepare(p,True);compiled=sw.compile_channels(m,g,nd,ks);elim=sw.minfill([set(s)for s,_,_ in compiled]);T=[m.detector_row_changes.get(i,1<<i)for i in range(nd)];cols=[[j for j,t in enumerate(T)if t>>i&1]for i in range(nd)]
 CTX.update(eng=e,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim,cols=cols)
 keys=[None]+e.keys
 if procs>1:
  with mp.get_context('fork').Pool(procs)as pool:rr=list(pool.imap(row,keys))
 else:rr=list(map(row,keys))
 A=rr[0]['value'];O=sum(w*b*r['value']for w,b,r in zip(e.W,e.beta,rr[1:]));loss=(A-O)/(2*A);dets=[s for s in p.with_suffix('.qasm').read_text().splitlines()if s.startswith('// DETECTOR')];out=[]
 for i,s in enumerate(dets):
  Ai=A+rr[0]['bias'][i];Oi=O+sum(w*b*r['bias'][i]for w,b,r in zip(e.W,e.beta,rr[1:]));Li=(Ai-Oi)/(2*Ai)
  out.append(dict(row=i,detector=s,loss=Li,acceptance=Ai,delta_loss=Li-loss,acceptance_recovered=Ai-A))
 r=dict(method='exact sparse reverse-contraction Fourier marginals',source=str(p),base_loss=loss,base_acceptance=A,detector_rows=out,rows=rr,seconds=time.monotonic()-start,canonical_rows=m.detector_row_changes)
 p.with_suffix('.detector_prices.json').write_text(json.dumps(r,indent=2));print('BASE',loss,A,'seconds',r['seconds'],flush=True)
 for x in out:print(json.dumps(x),flush=True)
 return r
if __name__=='__main__':run(sys.argv[1],int(sys.argv[2])if len(sys.argv)>2 else 1)
