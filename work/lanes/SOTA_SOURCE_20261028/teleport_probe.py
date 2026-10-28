"""Full-noise abstract output relocation via one-bit encoded teleportation.

An explicit |+L> encoder and transversal output->source CX are present, and
source Z reads drive an affine logical X frame. This is a diagnostic because
resource encoder and source/output interactions are nonlocal. No ideal state
or deleted wait is used.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
for d in ('work/tools','work/lanes/END2_20261027','work/lanes/REBUILD20261027','work/lanes/CAT3_20261027','work/lanes/FRAME20261027','work/lanes/STRATEGY_CROSS_20261027','upstream/snu-qff2026-problem'):sys.path.insert(0,str(R/d))
from qtools.evaluator import frontend as f
from partial_square import prep
from record_contract import complete
from reuse_final import raw_abstract
import frame_tools as ft
ft.OUT=H/'teleport';ft.OUT.mkdir(exist_ok=True);ft.raw_check=raw_abstract
source=R/'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16';ops,dets=f.parse_current(source.with_suffix('.qasm').read_text())
old=[6,20,19,10,2,22,16];out=[7,14,13,9,8,21,15];t=max(o.time for o in ops)+1
prep(ops,out,t,True);touch=t+4;first=max(o.bit for o in ops if o.bit is not None)+1
for a,b in zip(out,old):ops.append(f.Op('CX',(a,b),touch))
for i,q in enumerate(old):ops.append(f.Op('M',(q,),touch+1,first+i))
ops.sort(key=lambda x:x.time);f.DATA=out;m=f.make_model(ops,dets);contract=complete(m,dets);extra=[r for r in contract['missing'] if any(b>=first for b in r['bits'])]
assert all(not z['reference']for z in extra);dets += [set(z['bits']) for z in extra]
frame={'X':(0,set(range(first,first+7))),'Z':(0,set())};name='source_to_fresh_plus'
st=ft.emit(name,ops,dets,out,frame,dict(scope='All physical channels noisy; abstract nonlocal preparation and coupling; diagnostic only.',source=str(source),old_data=old,output=out,terminal=touch))
raw=raw_abstract(st.with_suffix('.qasm').read_text(),out);print('RAW',json.dumps(raw),flush=True)
if raw['ok']:
 sg=ft.singles(st);print('SINGLES',json.dumps({'c1':sg['first_order_loss'],'harmful':len(sg['harmful'])}),flush=True)
 result=ft.price(st);result['singles']=sg;st.with_suffix('.result.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT',json.dumps({k:result[k]for k in ('loss','acceptance','raw')}),flush=True)
