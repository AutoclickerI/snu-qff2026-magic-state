"""Literal native terminal role reversal and affine frame; two source policies."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
import frame_tools as ft,frontend_axis as f,record_contract
from qtools.evaluator import sparse_walsh as sw
ft.f=f;sw.fa=f;sw.parse_current=f.parse_current;record_contract.fa=f;ft.OUT=H/'native_teleport';ft.OUT.mkdir(exist_ok=True)
base=R/'work/lanes/SOTA_20261028/native_best/schedule_heralds_c167977fdd48de1f_d6_20_19_10_2_22_16'
D=[6,20,19,10,2,22,16];B=[12,26,25,11,3,28,17]
rows=[]
for fresh in (False,True):
 ops,dets=f.parse_current(base.with_suffix('.qasm').read_text());removed=set()
 for o in ops:
  if o.time==47 and o.kind=='CX' and o.qs in list(zip(B,D)):o.qs=o.qs[::-1]
  if o.time==48 and o.kind=='MX' and o.qs[0] in B:removed.add(o.bit)
 ops=[o for o in ops if o.bit not in removed]
 # Optional independent control, not the user-requested fixed source.
 sourcebits={352,353,361}
 if fresh:
  for o in ops:
   if o.bit in sourcebits:o.kind='RX';o.bit=None
  removed |=sourcebits
 dets=[row-set(sourcebits) if fresh else row for row in dets if not(row&removed-set(sourcebits))]
 dets=[x for x in dets if x]
 b=max(o.bit or 0 for o in ops)+1
 ops += [f.Op('MX',(q,),48,b+i) for i,q in enumerate(D)]
 dets += [{b+j for j in support}for support in f.SUPPORTS]
 frame={'X':(0,set()),'Z':(0,set(range(b,b+7)))}
 stem=ft.emit('fresh'if fresh else'fixed_source',ops,dets,B,frame,{'parent':str(base),'fresh_sources':fresh})
 text=stem.with_suffix('.qasm').read_text();raw=ft.raw_check(text,B);row={'fresh_sources':fresh,'stem':str(stem),'raw':raw,'cx':sum(o.kind=='CX' for o in ops)};print('RAW',json.dumps(row),flush=True)
 if raw['ok']:
  val=ft.price(stem);row.update(loss=val['loss'],acceptance=val['acceptance']);print('PRICE',json.dumps(row),flush=True)
 rows.append(row);(H/'native_teleport_results.json').write_text(json.dumps(rows,indent=2)+'\n')
