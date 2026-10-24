"""Audit sparse frontend against the official Model, then contract all noise orders."""
import os,sys,json,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path[:0]=[str(H/'sparse'),str(ROOT/'work/lanes/EVAL')]
import sparse_walsh as sw,frontend as fa,exact2,xtim
xtim.cache_dir=str(H/'.xtim_cache')
def audit(stem):
 text=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits'];ev=exact2.Eval(text,data)
 assert ev.m.frame=={'X':(0,[]),'Z':(0,[])} and not ev.m.post,ev.m.frame
 fa.DATA=data;ops,dets=fa.parse_current(text);original=fa.noise_blocks
 fa.noise_blocks=lambda text,p,first_order=True:original(text,p,first_order=False)
 try:m=fa.make_model(ops,dets)
 finally:fa.noise_blocks=original
 # Exact2 inserts detectors as soon as their last measurement exists; frontend preserves
 # QASM declaration order. Recover their physical record supports and permute d masks.
 records=[];detrows=[]
 for i,ins in enumerate(ev.m.prog):
  if ins.name in ('M','MX'):
   label=ev.m.labels[i];k=int(__import__('re').search(r'instruction (\d+)',label).group(1));raw=exact2.qasm_lines(text)[k-1][1]
   records.append(int(__import__('re').search(r'c\[(\d+)\]',raw).group(1)))
  elif ins.name=='DETECTOR':detrows.append(frozenset(records[len(records)-int(t[5:-1])] for t in ins.targets))
 reorder=[detrows.index(frozenset(row)) for row in dets]
 assert len(m.rots)==len(ev.m.rots)
 for a,b in zip(m.rots,ev.m.rots):
  assert a[:3]==b[:3] and abs(a[3]-b[3])<1e-15,(a,b)
 for i,j in enumerate(reorder):assert m.proj_m[i]==ev.m.proj_m[j],(i,j,m.proj_m[i],ev.m.proj_m[j])
 assert m.Q==ev.m.Q
 assert len(m.chans)==len(ev.m.chans),(len(m.chans),len(ev.m.chans))
 assert len(m.faults)==len(ev.m.faults)
 # Noise instructions on empty detector rows generate no channels, so physical channel
 # order is identical. Signatures s/e are gauge-independent; detector d is permuted.
 for a,b in zip(m.chans,ev.m.chans):
  assert list(a['qs'])==list(b['qubits']) and abs(a['p']-b['prob'])<1e-16,(a,b)
 for i,(a,b) in enumerate(zip(m.faults,ev.m.faults)):
  want=sum(((b['d']>>j)&1)<<k for k,j in enumerate(reorder))
  assert (a['chan'],a['pauli'],a['s'],a['e'],a['d'])==(b['chan'],b['pauli'],b['s'],b['e'],want),(i,a,b)
  assert abs(a['p']-b['p'])<1e-16
 return dict(channels=len(m.chans),faults=len(m.faults),detectors=len(dets),all_fault_signatures_match=True,all_rotations_projectors_observables_match=True)
for name in sys.argv[1:]:
 p=H/name;t=time.monotonic();proof=audit(p);print('AUDIT',name,json.dumps(proof),flush=True)
 out=sw.run(p,72,True,1);out['frontend_audit']=proof;out['sha256']=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest();out['total_seconds']=time.monotonic()-t
 (H/(name+'.allorders.json')).write_text(json.dumps(out,indent=2));print('COMPLETE',name,out['loss'],out['acceptance'],flush=True)
