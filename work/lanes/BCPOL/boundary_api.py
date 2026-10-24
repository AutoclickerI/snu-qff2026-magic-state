"""Public fixed-exterior boundary-cache API. No file writes on scoring."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
from dataclasses import dataclass
import numpy as np,math,time
import subprocess
from functools import lru_cache
H=Path(__file__).resolve().parent
ROOT=H.parents[2]

def fwht(a):
    a=np.array(a,copy=True,dtype=float);n=a.shape[-1];h=1
    if a.size==0:return a
    while h<n:
        z=a.reshape(*a.shape[:-1],-1,2*h);u=z[...,:h].copy();v=z[...,h:].copy();z[...,:h]=u+v;z[...,h:]=u-v;h*=2
    return a

@dataclass(frozen=True)
class PreparedRegion:
    fingerprint: str
    channels: tuple
    n_classes: int

def prepare_candidate(stem):
    """Full-model audit and channel extraction; outside the ~0.05 s hot path."""
    import json
    result=subprocess.run([str(ROOT/'.venv/bin/python'),str(H/'cache_export.py'),str(Path(stem).resolve())],cwd=ROOT,capture_output=True,text=True,check=True)
    d=json.loads(result.stdout)
    return PreparedRegion(d['fingerprint'],tuple(tuple((int(k),float(p)) for k,p in channel) for channel in d['channels']),int(d['n_classes']))

@lru_cache(maxsize=4)
def _parities(n):
    if n<1 or n&(n-1):raise ValueError('Boundary dimension must be a power of two')
    return np.arange(n),np.array([k.bit_count()&1 for k in range(n)],dtype=float)

def _characters(region,expected,n):
    if region.fingerprint!=expected:raise ValueError('Exterior/ideal/boundary fingerprint mismatch; compile a new cache')
    if region.n_classes!=n:raise ValueError('Boundary dimension mismatch')
    # A sparse categorical channel has character 1 - 2 sum_{k.y odd} p_k.
    # Evaluate that directly instead of transforming a mostly-zero dense row.
    indices,parity=_parities(n)
    arrays=np.ones((len(region.channels),n))
    for i,channel in enumerate(region.channels):
        total=0.
        for k,p in channel:
            if not 0<=k<n or not math.isfinite(p) or p<0:raise ValueError('Invalid categorical Pauli outcome')
            arrays[i]-=2*p*parity[indices&k];total+=p
        if total>1+1e-14:raise ValueError('Channel probability exceeds one')
    return arrays

class AllOrdersCache:
    def __init__(self,path):
        with np.load(path,allow_pickle=False) as z:
            self.N=z['N'].copy();self.A=z['A'].copy();self.fingerprint=str(z['exterior_hash'])
        self.n_classes=len(self.N)
    def score(self,region):
        t=time.monotonic();char=_characters(region,self.fingerprint,self.n_classes)
        p=fwht(np.prod(char,axis=0))/self.n_classes
        if abs(p.sum()-1)>1e-11 or p.min()<-1e-12:raise ArithmeticError('Invalid transformed boundary probability')
        numerator=float(p@self.N);acceptance=float(p@self.A)
        if acceptance<=0:raise ValueError('Zero acceptance')
        return dict(loss=numerator/acceptance,numerator=numerator,acceptance=acceptance,score_seconds=time.monotonic()-t,all_orders=True)

class CubicCache:
    def __init__(self,path):
        with np.load(path,allow_pickle=False) as z:
            self.response=z['response'].copy();self.n3=float(z['n3']);self.fingerprint=str(z['ext_hash'])
        self.n_classes=self.response.shape[-1]
    def score(self,region):
        t=time.monotonic();v=_characters(region,self.fingerprint,self.n_classes)-1
        a=v.sum(axis=0);b=(v*v).sum(axis=0);c=(v*v*v).sum(axis=0);n=self.n_classes
        P1=fwht(a)/n;P2=fwht((a*a-b)/2)/n;P3=fwht((a*a*a-3*a*b+2*c)/6)/n;N,A=self.response
        n1=N[1,0]+P1@N[0]
        if abs(n1)>=1e-12:raise ValueError('The cubic shortcut requires |c1| < 1e-12')
        n2=N[2,0]+P1@N[1]+P2@N[0];n3=self.n3+P1@N[2]+P2@N[1]+P3@N[0];a1=A[1,0]+P1@A[0]
        return dict(c1=float(n1),second=float(n2),third=float(n3-a1*n2),total=float(n2+n3-a1*n2),exp_minus_A1=math.exp(a1),score_seconds=time.monotonic()-t,all_orders=False)
