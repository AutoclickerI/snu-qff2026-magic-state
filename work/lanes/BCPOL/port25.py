"""Price retained relaxed-contract preps in v25k, preserving its q19 speed repair."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from build import build,source
from moments_batch import evaluate,exact2
from synth import verify
import json,math,time
base=H/'inputs/v25k';data=json.loads(base.with_suffix('.json').read_text())['data_qubits'];ev=exact2.Eval(base.with_suffix('.qasm').read_text(),data);reference=evaluate(ev);(H/'v25k.reference.json').write_text(json.dumps(reference,indent=2));print(json.dumps(dict(event='reference',**reference)),flush=True)
names=['endpoint_5_s712_00601','endpoint_5_s712_00138']
for seed in (901,902):names.append(json.loads((H/f'runs/cache_endpoint_5_{seed}.best.json').read_text())['tag'])
rows=[]
# Original 82-CX prep is the mandatory in-situ builder recovery control.
baseprep=json.loads((H/'inputs/base.prep.json').read_text());baseprep.update(kind='policy',value=9)
md,head,units,times,tail,init,rem=source(base='v25k')
oldmx=[q for q,i in init.items() if units[i].name=='MX'];print(json.dumps(dict(event='v25_init',mx=oldmx)),flush=True)
text,meta=build(baseprep,dict(base='v25k',timing='project',mx=oldmx));out=H/'inputs/replay_v25k';out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(meta,indent=2));replay=evaluate(exact2.Eval(text,data));assert abs(replay['total']-reference['total'])<1e-14,(replay,reference)
(H/'v25k.replay.json').write_text(json.dumps(replay,indent=2))
for name in names:
 d=json.loads((H/'finalists'/f'{name}.json').read_text())['prep']
 for label,reset in [('r19',{19}),('r19417',{19,4,17}),('allrx',set(d['pivots']))]:
  tag=f'v25_{name}_{label}';opt=dict(base='v25k',timing='alap',mx=[q for q in d['pivots'] if q not in reset]);row=dict(tag=tag,source_prep=name,options=opt)
  try:
   text,meta=build(d,opt);ev=exact2.Eval(text,data);c1=float(ev.fp@ev.n_single);row['c1']=c1
   if abs(c1)<1e-12:row.update(evaluate(ev));row.update(delta_loss=row['total']-reference['total'],delta_A1=-math.log(row['exp_minus_A1']/reference['exp_minus_A1']))
   else:row['status']='INVALID_C1'
   out=H/'finalists'/tag;out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(meta,indent=2));out.with_suffix('.screen.json').write_text(json.dumps(row,indent=2))
  except (ValueError,AssertionError) as e:row.update(status='INVALID',error=str(e))
  rows.append(row);print(json.dumps(row),flush=True)
(H/'v25_ports.json').write_text(json.dumps(rows,indent=2))
