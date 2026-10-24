"""Independent actual-prep extraction from every retained full circuit."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,re
from build import H,S,native_times,B,C
from synth import verify
rows=[]
for f in sorted((H/'finalists').glob('*.qasm')):
 md=json.loads(f.with_suffix('.json').read_text());h,raw,tail=S.qasm_ops(f.read_text());u=S.fold_units(raw);ts=native_times(f.read_text(),u);R=md['R'];init={q:max(t for x,t in zip(u,ts) if x.qs==(q,) and t<R and x.name in ('RESET','RX','MX','MEASURE')) for q in B+C};ops=[[] for _ in range(R)]
 for x,t in zip(u,ts):
  if x.name=='CX' and t<R and set(x.qs)<=set(B+C) and all(t>init[q] for q in x.qs):ops[t].append(list(map(int,re.findall(r'q\[(\d+)\]',x.lines[0]))))
 d=dict(md['prep'],ops=[l for l in ops if l]);v=verify(d);assert v['clean_pass'] and v['stim_target_pass'],(f,v)
 mismatch=md['verification']['cx']!=v['cx'];row=dict(stem=f.stem,actual_verification=v,metadata_cx_correct=not mismatch);rows.append(row)
 if mismatch:
  assert f.stem.startswith('ablate506'),(f,md['verification'],v)
  md.update(prep=d,verification=v);f.with_suffix('.json').write_text(json.dumps(md,indent=2));row['repaired']=True
(H/'metadata_audit.json').write_text(json.dumps(rows,indent=2));print(json.dumps(dict(finalists=len(rows),mismatch_repaired=sum(r.get('repaired',False) for r in rows))))
