"""Boundary signature audit and exact noisy Clifford suffix response cache.
The cache includes every suffix noise order. Prefix/initialization correlations
must pass an independent compatibility test before a full circuit is priced.
"""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
os.environ.setdefault('XTIM_TWIRL_CACHE_DIR',str(H/'.xtim_cache'))
sys.path[:0]=[str(H),str(ROOT/'work/lanes/EVAL')]
import json,hashlib,math,collections,time
import numpy as np,stim
from exact2 import Eval
from model import Basis,masks,comm,CLIFFORD,ROTATIONS
from synth import B,C

def frame_at(m,boundary):
 # The deferred-wire walker uses program order. A physical-time cut must
 # therefore be a program prefix; otherwise record-wire/rotation indices
 # would not describe the requested boundary.
 after=False
 for st in m.steps:
  if not st:continue
  times=[t for q,t in st]
  if min(times)<boundary<=max(times):raise ValueError('Native instruction straddles the boundary cut')
  if min(times)>=boundary:after=True
  elif after:raise ValueError('Boundary cut is not a chronological native-step program prefix')
 sim=stim.TableauSimulator();sim.set_num_qubits(m.n);wire=list(range(36));nxt=36;nr=0
 for ii,ins in enumerate(m.prog):
  st=m.steps[ii]
  if st and min(t for q,t in st)>=boundary:break
  name,qs=ins.name,ins.qubits
  if name in ('M','MX'):
   for q in qs:
    if name=='MX':sim.h(wire[q])
    sim.cx(wire[q],nxt);nxt+=1
    if name=='MX':sim.h(wire[q])
  elif name in ('R','RX'):
   for q in qs:
    wire[q]=nxt;nxt+=1
    if name=='RX':sim.h(wire[q])
  elif name in CLIFFORD and name!='I':sim.do(stim.CircuitInstruction(name,[wire[q] for q in qs]))
  elif name in ROTATIONS:nr+=len(qs)
 return sim.current_inverse_tableau(),wire,nr

def signature(m,x,z,nr):
 s=sum(comm(x,z,r[0],r[1])<<j for j,r in enumerate(m.rots) if j>=nr)
 d=sum(comm(x,z,r[0],r[1])<<j for j,r in enumerate(m.proj_m))
 e=sum(comm(x,z,r[0],r[1])<<j for j,r in enumerate(m.sig_e))
 return s,d,e

def pack(k,nd):
 s,d,e=k;return e|(d<<10)|(s<<(10+nd))
def unpack(v,nd):return v>>(10+nd),(v>>10)&((1<<nd)-1),v&1023

def audit(stem):
 text=stem.with_suffix('.qasm').read_text();md=json.loads(stem.with_suffix('.json').read_text());ev=Eval(text,md['data_qubits']);m=ev.m;nd=len(m.proj_m);boundary=md.get('boundary_step',md.get('R',45));region=md.get('region_qubits',B+C);assert len(region)==len(set(region)) and all(0<=q<36 for q in region);tab,wire,nr=frame_at(m,boundary)
 gens=[];basis=Basis();sectors={}
 for pauli in ('X','Z'):
  bb=Basis()
  for q in region:
   ps=getattr(tab,pauli.lower()+'_output')(wire[q]);x,z,_=masks(ps);sig=signature(m,x,z,nr);v=pack(sig,nd);gens.append(dict(q=q,pauli=pauli,sde=sig,packed=v));basis.add(v);bb.add(v)
  sectors[pauli]=len(bb.vecs)
 inside=[];outside=[];suffix=[]
 for f in m.faults:
  ch=m.chans[f['chan']];st=m.steps[ch['ins']];tt=min(t for q,t in st) if st else -1
  v=pack((f['s'],f['d'],f['e']),nd)
  if set(ch['qubits'])<=set(region) and tt<boundary and ch['kind'] in ('gate2','idle') and tt>=31:
   inside.append((f,basis.express(v)))
  if tt>=boundary:suffix.append((f,basis.express(v)))
 rec=dict(stem=str(stem),boundary=boundary,region_qubits=region,region_init_times=md.get('init_times'),rank=len(basis.vecs),sector_ranks=sectors,generators=gens,basis=basis.vecs,nd=nd,prep_trial_faults=len(inside),prep_trial_unrepresentable=sum(k is None for f,k in inside),suffix_faults=len(suffix),suffix_unrepresentable=sum(k is None for f,k in suffix))
 return ev,basis,rec

if __name__=='__main__':
 ev,b,rec=audit(Path(sys.argv[1]) if len(sys.argv)>1 else H/'inputs/replay_policy');(H/'boundary.audit.json').write_text(json.dumps(rec,indent=2));print(json.dumps({k:v for k,v in rec.items() if k not in ('generators','basis')}))
