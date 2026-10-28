"""Physical source-transfer heralds into the native first seven-cat initialization."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,copy
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
import frame_tools as ft,frontend_axis as f,record_contract
from qtools.evaluator import sparse_walsh as sw
ft.f=f;record_contract.fa=f;sw.fa=f;sw.parse_current=f.parse_current;ft.OUT=H
P=R/'work/lanes/CAT_INSTRUMENT_AUDIT_20261028/cat7_r15_complete_45495c4fe525cb7d_d6_20_19_10_2_22_16'
D=[6,20,19,10,2,22,16];f.DATA=D;cat=[7,14,13,9,8,21,15];root=8

def complete(ops):
 m=f.make_model(ops,[]);c=record_contract.complete(m,[]);neg=[r for r in c['missing']if r['reference']]
 if neg:raise ValueError(('negative_reference',neg))
 return [set(r['bits'])for r in c['missing']]

def run(name):
 ops,old=f.parse_current(P.with_suffix('.qasm').read_text());original_cx=sum(o.kind=='CX'for o in ops);bit=max(o.bit for o in ops if o.bit is not None)+1;reads=[]
 for o in ops:
  if o.time!=14 or o.qs[0] not in cat:continue
  if o.kind=='R' and name in ('meas','both'):
   o.kind='M';o.bit=bit;reads.append((o.qs[0],bit));bit+=1
  elif o.kind=='RX' and o.qs==(root,) and name in ('root','both'):
   o.kind='H'
 assert len(reads)==(6 if name in ('meas','both') else 0)
 assert sum(o.kind=='CX'for o in ops)==original_cx
 ops.sort(key=lambda o:o.time)
 for label,subset in [('boundary',[o for o in ops if o.time<=14]),('full',ops)]:
  dets=complete(subset);stem=ft.emit(f'{name}_{label}',subset,dets,D,metadata={'parent':str(P),'mode':name,'root':root,'source_reads':reads,'contract':'all noiseless deterministic rows','scope':'native, all actual channels noisy'})
  raw=ft.raw_check(stem.with_suffix('.qasm').read_text(),D)
  print('RAW',name,label,json.dumps({'raw':raw,'rows':len(dets),'reads':reads}),flush=True)
  if not raw['ok']:return
  if label=='full':
   singles=ft.singles(stem);out={'loss':singles['first_order_loss'],'count':singles['harmful_count']};print('SINGLES',name,json.dumps(out),flush=True)
   print('PRICE',name,json.dumps(ft.price(stem)),flush=True)
if __name__=='__main__':run(sys.argv[1])
