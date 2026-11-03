import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,collections
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/tools')]
import frame_tools as ft,frontend_axis as f
ft.f=f
stem=H/'full_post';ops,ds,md=ft.load(stem);m=ft.frame_model(ops,ds,md['data_qubits'],ft.parse_frames(stem.with_suffix('.qasm').read_text()),False);e=f.Engine(m)
active=sum(1<<i for i,p in enumerate(e.projs)if p[:2]!=(0,0));group=collections.defaultdict(list)
for x in m.faults:group[x['d']&~active].append(x)
def mod(x):
 t=ops[x['ins']].time
 if t<18:return 'seed'
 if t<23:return 'gauge_prepare'
 if t<26:return 'gauge_measure'
 if t<42:return 'gauge_recovery'
 return 'final_stab'
cache={};acc=collections.defaultdict(float)
def loss(s,d,err):
 k=(s,d)
 if k not in cache:cache[k]=e.ntable(s,d)
 _,n=cache[k]
 return 0 if n is None else max(0.,float(n[err]))
for ff in group.values():
 agg=collections.defaultdict(list)
 for x in ff:agg[(x['s'],x['d'],x['e'],mod(x))].append(x)
 entries=[]
 for (s,d,err,modu),fs in agg.items():
  by=collections.defaultdict(float)
  for x in fs:by[x['chan']]+=x['p']/.001
  entries.append((s,d,err,modu,sum(by.values()),by))
 for i,a in enumerate(entries):
  for j in range(i,len(entries)):
   b=entries[j];n=loss(a[0]^b[0],a[1]^b[1],a[2]^b[2])
   if n<1e-14:continue
   w=a[4]*b[4]-sum(p*b[5].get(ch,0)for ch,p in a[5].items())
   if i==j:w*=.5
   acc[' + '.join(sorted((a[3],b[3])))]+=w*n
out={'second_order_coefficient':sum(acc.values()),'breakdown':sorted(acc.items(),key=lambda v:-v[1]),'kernel_tables':len(cache),'scope':'truncated two-fault expansion, no finite-p ranking claim'}
(H/'pair_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
