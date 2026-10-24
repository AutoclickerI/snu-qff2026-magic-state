import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,collections
from pathlib import Path
from synth import verify
H=Path(__file__).resolve().parent;ROOT=H.parents[2];groups=json.loads((H/'lns_unique.json').read_text());stats=collections.Counter();best=[]
for i,fs in enumerate(groups):
 d=json.loads((ROOT/fs[0]).read_text());last={q:-1 for q in d['cells']};ops=[]
 for layer in d['ops']:
  for u,v in layer:
   t=max(last[u],last[v])+1
   while len(ops)<=t:ops.append([])
   ops[t].append([u,v]);last[u]=last[v]=t
 stats[(sum(map(len,ops)),len(ops))]+=1
 if len(ops)<14:
  dd=dict(d,ops=ops);v=verify(dd);assert v['clean_pass'] and v['stim_target_pass'];f=H/'runs'/f'compressed_{i:04d}.prep.json';dd['verification']=v;f.write_text(json.dumps(dd,indent=2));best.append(dict(source=i,cx=v['cx'],depth=v['depth'],file=str(f)))
(H/'depth_audit.json').write_text(json.dumps(dict(counts=[dict(cx=c,depth=d,count=n) for (c,d),n in sorted(stats.items())],compressed=best),indent=2));print('counts',stats,'compressed',len(best));print(best[:8])
