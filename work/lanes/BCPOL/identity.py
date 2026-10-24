"""Exhaustive pair identity edits with singleton residuals, using boundary cache.
All variants preserve the full ideal linear map and frozen initialization times.
"""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from synth import B,C,nb,verify,trace
from build import build
from cache import setup,contract,compile_cache,evaluate
import json,numpy as np,time,lzma,copy,hashlib
base=json.loads((H/'inputs/base.prep.json').read_text());base.update(kind='policy',value=9)
text,md=build(base,dict(timing='project'));init=md['init_times'];cached=np.load(H/'boundary.cache.npz',allow_pickle=True);rows=[];seen=set();n=0
# Single edits are insert two identical gates at free consecutive layer slots,
# or remove two identical gates adjacent on both participating wires.
proposals=[];ops=base['ops'];D=len(ops)
for a in range(D):
 for b in range(a+1,D):
  for edge in ops[a]:
   if edge not in ops[b]:continue
   if any(set(edge)&set(e) for layer in ops[a+1:b] for e in layer):continue
   d=copy.deepcopy(base);d['ops'][a].remove(edge);d['ops'][b].remove(edge);proposals.append((f'delete_{a}_{b}_{edge}',d))
for u in B+C:
 for v in nb(u):
  if v not in B+C:continue
  for a in range(D-1):
   if any({u,v}&set(e) for layer in ops[a:a+2] for e in layer):continue
   d=copy.deepcopy(base);d['ops'][a].append([u,v]);d['ops'][a+1].append([u,v]);proposals.append((f'insert_{a}_{u}_{v}',d))
with lzma.open(H/'runs/identity.jsonl.xz','wt') as f:
 for name,d in proposals:
  v=verify(d);classes=set(map(int,v['residual_classes']))
  if not classes or not classes<={9,10,11,12,13,14,15} or len(classes)!=1:continue
  d['value']=next(iter(classes));v=verify(d);assert v['policy_pass']
  tr=trace(d)
  if tr in seen:continue
  seen.add(tr);row=dict(name=name,policy=d['value'],verification=v)
  try:
   text,md=build(d,dict(timing='alap',fixed_init=init));stem=H/'inputs/identity_current';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md));ev,b,ks,prep,ext,hh=setup(stem);compatible=hh==str(cached['ext_hash']);row['cache_compatible']=compatible
   if compatible:
    row.update(contract(ev,prep,cached['response'],cached['n3']));full=evaluate(ev);assert abs(row['total']-full['total'])<1e-14;row['full_delta']=row['total']-full['total']
   else:row.update(evaluate(ev))
   tag='identity_'+hashlib.sha256(name.encode()).hexdigest()[:10];row['tag']=tag
   out=H/'finalists'/tag;out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(md,indent=2));out.with_suffix('.screen.json').write_text(json.dumps(row,indent=2))
  except (ValueError,AssertionError) as e:row.update(status='INVALID',error=str(e))
  rows.append(row);f.write(json.dumps(dict(row=row,prep=d))+'\n');print(json.dumps(row),flush=True)
(H/'identity.receipt.json').write_text(json.dumps(dict(proposals=len(proposals),singleton_witnesses=len(rows),rows=rows),indent=2))
