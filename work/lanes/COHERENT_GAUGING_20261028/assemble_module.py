import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(H),str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
import frontend_axis as f,frame_tools as ft,record_contract,stab
from qtools.evaluator import sparse_walsh as sw
ft.f=f;record_contract.fa=f;sw.fa=f;sw.parse_current=f.parse_current;ft.OUT=H
D=[0,11,9,26,12,21,14];f.DATA=D
mod=json.loads((R/'work/lanes/GAUGE_SCHEDULE_20261028/best.json').read_text());ops,dets=f.parse_current((H/'seed_t.qasm').read_text());mapping={};bit=4
for o in mod['operations']:
 b=None
 if 'record' in o:mapping[o['record']]=bit;b=bit;bit+=1
 ops.append(f.Op(o['kind'],tuple(o['qs']),o['time']+18,b))
t=18+mod['clocks'];ops,dets,t,bit=stab.append_stab(ops,dets,t,bit)
ops.sort(key=lambda o:o.time);used=set()
for o in ops:
 for q in o.qs:
  if (o.time,q)in used:raise ValueError((o.time,o.kind,o.qs))
  used.add((o.time,q))
 if o.kind=='CX':
  a,b=o.qs;assert abs(a//6-b//6)+abs(a%6-b%6)==1
comp=record_contract.complete(f.make_model(ops,[]),[]);neg=[r for r in comp['missing'] if r['reference']]
if neg:print('NEGATIVE',json.dumps(neg),flush=True);sys.exit(1)
ds=[set(x['bits'])for x in comp['missing']];stem=ft.emit('module_best_post',ops,ds,D,metadata={'module_root':mod['root'],'module_clocks':mod['clocks'],'module':'GAUGE_SCHEDULE_20261028/best.json','record_map':mapping})
raw=ft.raw_check(stem.with_suffix('.qasm').read_text(),D);print('RAW',json.dumps({'raw':raw,'root':mod['root'],'ticks':t,'rows':len(ds)}),flush=True)
if raw['ok']:
 s=ft.singles(stem);print('SINGLES',json.dumps({'loss':s['first_order_loss'],'n':s['harmful_count']}),flush=True);print('PRICE',json.dumps(ft.price(stem)),flush=True)
