"""Independent Bellman-potential check of every fixed-seven-cell minimum-CX claim."""
import os,sys,json,struct,hashlib
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent
raw=(H/'library_distance_certificate.bin').read_bytes();ns,n=struct.unpack('<ii',raw[:8]);states=np.frombuffer(raw,dtype='<i4',count=n,offset=8);dist=np.frombuffer(raw,dtype=np.uint8,offset=8+4*n).reshape(ns,n)
L=json.loads((H/'library_input.json').read_text());E=json.loads((H/'library_encoders.json').read_text());ids={int(s):i for i,s in enumerate(states)}
# Independent vectorized row reduction, selecting pivot columns from left to right.
rows=np.stack([(states>>(7*i))&127 for i in range(3)],axis=1)
ctz=np.array([99]+[(q&-q).bit_length()-1 for q in range(1,128)])
trans={}
for u in range(7):
 for v in range(7):
  if u==v:continue
  rr=rows.copy();rr^=(((rr>>u)&1)<<v)
  for i in range(3):
   piv=np.argmin(ctz[rr[:,i:]],axis=1)+i;tmp=rr[np.arange(n),piv].copy();rr[np.arange(n),piv]=rr[:,i];rr[:,i]=tmp;bit=rr[:,i]&-rr[:,i]
   for j in range(3):
    if i!=j:rr[:,j]^=np.where(rr[:,j]&bit,rr[:,i],0)
  keys=rr[:,0]|rr[:,1]<<7|rr[:,2]<<14;trans[u,v]=np.array([ids[int(k)]for k in keys])
coord=np.all((rows&(rows-1))==0,axis=1);assert coord.sum()==35
checks=0
for sid,s in enumerate(L['shapes']):
 dd=dist[sid].astype(int);assert (dd[coord]==0).all();assert (dd[~coord]>0).all()
 for u in range(7):
  for v in range(7):
   if abs(s[u][0]-s[v][0])+abs(s[u][1]-s[v][1])==1:
    assert np.all(np.abs(dd-dd[trans[u,v]])<=1),(sid,u,v);checks+=n
 for cid,t in enumerate(L['targets']):assert dd[ids[t]]==E[sid][cid]['cx']
out=dict(status='PASS',states=n,coordinate_sources=int(coord.sum()),shape_label_minima=ns*30,edge_potential_checks=checks,certificate_sha256=hashlib.sha256(raw).hexdigest(),proof='Potential is zero on every coordinate input and changes by at most one along every allowed CX. Each target potential equals the emitted verified witness length. Therefore every reported minimum is both a lower and upper bound.',scope='fixed seven-cell CSS subspace preparation; not an end-state UNSAT certificate')
(H/'library_certificate_verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
