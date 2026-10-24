"""Port completed lower-rank winners to v23 and price explicit round placements."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from build import build
from moments_batch import exact2,evaluate
import json,math
sources=['rank4_2','rank4_3','rank4_4','rank4_7','rank3_0'];rows=[];selected=[]
for family in sources:
 b=json.loads((H/'runs'/f'{family}.best.json').read_text());name=b['tag'];d=b['prep'];good=[]
 for shift in (0,1,2):
  tag=f'v23_{name}_r{shift}';opt=dict(base='v23h_c2c9',timing='alap',round_shift=shift,endpoint_parity=True,mx=[q for q in d['pivots'] if q!=19]);row=dict(tag=tag,parent=name)
  try:
   text,md=build(d,opt);ev=exact2.Eval(text,md['data_qubits']);c1=float(ev.fp@ev.n_single);row['c1']=c1
   if abs(c1)>=1e-12:row['status']='INVALID_C1'
   else:
    row.update(evaluate(ev));row.update(delta_loss=row['total']-6.922103982278669e-5,delta_A1=-math.log(row['exp_minus_A1']/.5408595777123605),R=md['R'])
    out=H/'finalists'/tag;out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(md,indent=2));out.with_suffix('.screen.json').write_text(json.dumps(row,indent=2))
    if row['exp_minus_A1']>=.5002:good.append(row)
  except (ValueError,AssertionError) as e:row.update(status='INVALID',error=str(e))
  rows.append(row);print(json.dumps(row),flush=True)
 if good:selected.append(min(good,key=lambda r:r['total'])['tag'])
(H/'lower_v23_ports.json').write_text(json.dumps(rows,indent=2));(H/'lower_v23_selected.json').write_text(json.dumps(selected,indent=2))
