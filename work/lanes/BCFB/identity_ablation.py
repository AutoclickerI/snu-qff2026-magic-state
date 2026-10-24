"""Attribute the first winning circuit's exact gain to its four added CXs."""
import sys,os
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,itertools,concurrent.futures
from build import H,S,native_times,B,C
from synth import verify
from scan import save_screen
f=H/'finalists/fb_d15_c105_s506_00008';text=f.with_suffix('.qasm').read_text();md=json.loads(f.with_suffix('.json').read_text());h,r,tail=S.qasm_ops(text);u=S.fold_units(r);ts=native_times(text,u)
pairs=[[(t,i) for i,(x,t) in enumerate(zip(u,ts)) if x.lines==[f'cx q[{q}],q[{v}];'] and t in times] for q,v,times in [(5,4,[34,36]),(12,6,[38,39])]]
assert all(len(p)==2 for p in pairs),pairs
for mask in range(4):
 drop={i for k,p in enumerate(pairs) if mask>>k&1 for t,i in p};us=[x for i,x in enumerate(u) if i not in drop];tt=[t for i,t in enumerate(ts) if i not in drop];txt=S.emit(h,us,tt,tail)
 init={q:max(t for x,t in zip(us,tt) if x.qs==(q,) and t<md['R'] and x.name in ('RESET','RX','MX','MEASURE')) for q in B+C};ops=[[] for _ in range(md['R'])]
 for x,t in zip(us,tt):
  if x.name=='CX' and t<md['R'] and set(x.qs)<=set(B+C) and all(t>init[q] for q in x.qs):ops[t].append(list(map(int,__import__('re').findall(r'q\[(\d+)\]',x.lines[0]))))
 prep=dict(md['prep'],ops=[l for l in ops if l]);v=verify(prep);assert v['clean_pass'] and v['stim_target_pass']
 nmd=dict(md,prep=prep,verification=v,CX=sum(x.name=='CX' for x in us));tag=f'ablate506_remove{mask}'
 save_screen(tag,'identity_ablation',txt,nmd,dict(source=f.name,removed=[dict(time=ts[i],lines=u[i].lines) for i in sorted(drop)]))
