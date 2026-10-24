"""Independent dense 128x128 recovery-adjoint check of the terminal relaxation."""
import os,sys,json,itertools
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
import numpy as np
O=Path(__file__).resolve().parent
ix=np.arange(128,dtype=np.int64)
span={0}
for g in [85,102,120]:span|={x^g for x in list(span)}
psi=np.zeros(128,dtype=complex)
for x in span:psi[x]=.25;psi[x^127]=np.exp(1j*np.pi/4)/4
assert abs(np.vdot(psi,psi)-1)<1e-14
Q=np.zeros((128,128),dtype=complex)
reps=[0]+[1<<j for j in range(7)]
for x,z in itertools.product(reps,repeat=2):
 v=psi[ix^x]*(1-2*(np.bitwise_count((ix^x)&z)&1).astype(float));Q+=np.outer(v,v.conj())
assert np.max(np.abs(Q@Q-Q))<1e-14

def conjugate(a,x,z):
 s=1-2*(np.bitwise_count(ix&z)&1).astype(float)
 return a[np.ix_(ix^x,ix^x)]*s[:,None]*s[None,:]
def channel(a,qs,p):
 out=(1-p)*a
 for acts in itertools.product(range(4),repeat=len(qs)):
  if not any(acts):continue
  x=sum((1<<q)for q,k in zip(qs,acts)if k&1);z=sum((1<<q)for q,k in zip(qs,acts)if k&2)
  out+=p/(4**len(qs)-1)*conjugate(a,x,z)
 return out
rows={}
for pairs in [0,1]:
 a=Q.copy()
 if pairs:a=channel(a,[0,1],.001)
 for q in range(2*pairs,7):a=channel(a,[q],.0008)
 eig=np.linalg.eigvalsh(a);rows[str(pairs)]=dict(minimum_loss=float(1-max(eig)),target_loss=float(1-np.vdot(psi,a@psi).real))
f=json.loads((O/'floors.json').read_text())['terminal_relaxation']
for k,r in rows.items():
 r['difference_from_sector_enumeration']=r['minimum_loss']-f[k]['minimum'];assert abs(r['difference_from_sector_enumeration'])<2e-13
(O/'terminal_matrix.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
