import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,collections,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path[:0]=[str(H),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/tools')]
import acceptance_search as ac
stem=R/'work/lanes/EXPAND2_20261027/release_phase/native_incumbent_phase_late'
ops,rows,data,m,e,groups=ac.prepare(stem)
v=1180596138885567741952^296881791826164449280;off=1<<9
cache={};acc=collections.defaultdict(float)
for u,aa in groups.items():
 w=u^v
 if w<u or w not in groups:continue
 for ia,a in enumerate(aa):
  for ib,b in enumerate(groups[w]):
   if u==w and ib<ia:continue
   key=(a[0]^b[0],a[1]^b[1])
   if key not in cache:cache[key]=e.ntable(*key)
   _,nn=cache[key]
   if nn is None:continue
   loss=max(0.,float(nn[a[2]^b[2]^off]))
   if loss<1e-12:continue
   for ca,pa in a[4].items():
    for cb,pb in b[4].items():
     if ca==cb:continue
     weight=pa*pb*loss*(.5 if u==w and ia==ib else 1)
     cha,chb=m.chans[ca],m.chans[cb]
     def desc(ch):
      op=ops[ch['ins']];return (op.time,op.kind,tuple(op.qs),ch['name'],ch['jl'])
     k=tuple(sorted([desc(cha),desc(chb)]));acc[k]+=weight
out=[{'channels':k,'c2':v} for k,v in sorted(acc.items(),key=lambda t:-t[1])]
(H/'frame_joint_cross_pairs.json').write_text(json.dumps(out,indent=2)+'\n')
print('sum',sum(x['c2'] for x in out),'count',len(out))
for row in out[:30]:print(row)
