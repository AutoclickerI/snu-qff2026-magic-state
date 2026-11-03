"""Joint sector relaxation and logical affine-frame recovery, on full noisy circuit."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import sys,json,time,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'work/lanes/FRAME20261027'),str(ROOT/'work/lanes/EXPAND2_20261027'),str(ROOT/'work/tools')]
import acceptance_search as ac
import frame_tools as ft
import frontend_axis as f
from qtools.evaluator import sparse_walsh as sw
ft.f=f;sw.fa=f;sw.parse_current=f.parse_current
ft.OUT=HERE/'frame_cand';ft.OUT.mkdir(exist_ok=True)
stem=ROOT/'work/lanes/EXPAND2_20261027/release_phase/native_incumbent_phase_late'
ops,rows,data,m,eng,groups=ac.prepare(stem)
cache={}
def table(s,d):
 k=(s,d)
 if k not in cache:cache[k]=eng.ntable(s,d)
 return cache[k]
def offset(p):
 # p bit0 X, bit1 Z; e8=Z, e9=X XOR Z
 return (((p>>1)&1)<<8)|((((p&1)^((p>>1)&1)))<<9)
scores=[]
for v, entries in groups.items():
 if not v:continue
 for p in (1,2,3):
  a=n=0.;off=offset(p)
  for s,d,e,w,ch in entries:
   aa,nn=table(s,d);a+=w*aa
   if nn is not None:n+=w*max(0.,float(nn[e^off]))
  if a>.05 and n<1e-10:scores.append(dict(direction=v,pauli=p,acceptance_coefficient=a,single_loss=n))
print('qualifying',len(scores),flush=True)
# Test all candidate sectors against physical distinct-channel pair weights.
def pair_risk(v,p):
 total=0.;off=offset(p)
 for u,aa in groups.items():
  w=u^v
  if w<u or w not in groups:continue
  bb=groups[w]
  for ia,a in enumerate(aa):
   for ib,b in enumerate(bb):
    if u==w and ib<ia:continue
    _,nn=table(a[0]^b[0],a[1]^b[1])
    if nn is None:continue
    loss=max(0.,float(nn[a[2]^b[2]^off]))
    if loss<1e-12:continue
    weight=a[3]*b[3]-sum(x*b[4].get(ch,0.) for ch,x in a[4].items())
    if u==w and ia==ib:weight*=.5
    total+=weight*loss
 return total
for i,x in enumerate(scores):
 x['pair_risk']=pair_risk(x['direction'],x['pauli'])
 print('screen',i,json.dumps(x),flush=True)
 (HERE/'frame_screen.json').write_text(json.dumps(scores,indent=2)+'\n')
scores.sort(key=lambda x:(x['pair_risk']/x['acceptance_coefficient'],-x['acceptance_coefficient']))
for i,x in enumerate(scores[:12]):
 v=x['direction'];p=x['pauli'];idx=(v&-v).bit_length()-1
 dets=[ac.xor_rows(rows,r) for r in ac.null_rows([v],len(rows))]
 selector=set(rows[idx]);frame={'X':(0,selector if p&1 else set()),'Z':(0,selector if p&2 else set())}
 s=ft.emit('framed_'+str(i),ops,dets,data,frame,{'parent':str(stem),'sector':v,'pauli':p,'selector_row':idx})
 try:
  z=ft.price(s);x['stem']=str(s);x['price']=z
  print('PRICE',i,json.dumps({k:z.get(k) for k in ('loss','acceptance','raw')}),flush=True)
 except Exception as e:
  x['error']=repr(e);print('ERROR',i,repr(e),flush=True)
 (HERE/'frame_prices.json').write_text(json.dumps(scores,indent=2)+'\n')
