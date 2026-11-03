"""Direct phase-repetition C2 outer Steane source, all physical operations noisy.
Abstract connectivity; no ideal source or terminal. 36 physical wires.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/tools')]
import frontend_axis as f,frame_tools as ft,record_contract
from qtools.evaluator import sparse_walsh as sw
import tprep.qasm as jq
ft.f=f;record_contract.fa=f;sw.fa=f;sw.parse_current=f.parse_current;ft.OUT=H
D=list(range(7));K=list(range(7,14));A=list(range(14,21));B=list(range(21,28));FA=list(range(28,31));FB=list(range(31,34));f.DATA=D
PIV={0,1,3};ENC=[[(0,2),(1,5),(3,6)],[(0,4),(1,6),(3,5)],[(0,6),(1,2),(3,4)]]
ops=[]
for i,d in enumerate(D):ops += [f.Op('RX'if i in PIV|{2}else'R',(d,),0),f.Op('RX',(K[i],),0)]
ops += [f.Op('CX',(k,d),1)for d,k in zip(D,K)]
ops += [f.Op('CX',(K[2],D[2]),2),f.Op('T',(D[2],),3),f.Op('CX',(K[2],D[2]),4)]
for t,a,b in [(5,2,4),(6,2,5)]:ops += [f.Op('CX',(D[a],D[b]),t),f.Op('CX',(K[a],K[b]),t)]
for t,layer in enumerate(ENC,7):
 for a,b in layer:ops += [f.Op('CX',(D[a],D[b]),t),f.Op('CX',(K[a],K[b]),t)]
def prep(block,t,plus):
 for i,q in enumerate(block):ops.append(f.Op('RX'if ((i not in PIV)if plus else(i in PIV))else'R',(q,),t))
 for j,layer in enumerate(ENC,1):
  for a,b in layer:ops.append(f.Op('CX',(block[b],block[a])if plus else(block[a],block[b]),t+j))
prep(A,10,True);prep(B,10,False)
ops += [f.Op('CX',(d,a),14)for d,a in zip(D,A)]
ops += [f.Op('CX',(k,a),15)for k,a in zip(K,A)]
ops += [f.Op('CX',(b,d),15)for b,d in zip(B,D)]
bit=0
for block,kind in ((A,'M'),(B,'MX')):
 for q in block:ops.append(f.Op(kind,(q,),16,bit));bit+=1
# Reuse both measured precheck blocks as independently flagged seven-cats.
for block in (A,B):
 for i,q in enumerate(block):ops.append(f.Op('RX'if i==0 else'R',(q,),17))
for block in (A,B):
 for t,layer in [(18,[(0,1)]),(19,[(0,2),(1,3)]),(20,[(0,4),(1,5),(2,6)])]:
  ops += [f.Op('CX',(block[a],block[b]),t)for a,b in layer]
for fqs in (FA,FB):ops += [f.Op('R',(q,),20)for q in fqs]
for block,fqs in ((A,FA),(B,FB)):
 for j,(u,v) in enumerate(((0,1),(2,5),(4,6))):
  ops += [f.Op('CX',(block[u],fqs[j]),21),f.Op('CX',(block[v],fqs[j]),22),f.Op('M',(fqs[j],),23,bit)];bit+=1
# Logical T = CX(K,D) T(D) CX(K,D); use seven live phase-C2 blocks.
ops += [f.Op('CX',(k,d),17)for d,k in zip(D,K)]
ops += [f.Op('T',(d,),18)for d in D]
ops += [f.Op('CX',(k,d),19)for d,k in zip(D,K)]
ops += [f.Op('CX',(a,d),23)for d,a in zip(D,A)]
ops += [f.Op('CX',(b,d),24)for d,b in zip(D,B)]
for q in A:ops.append(f.Op('MX',(q,),24,bit));bit+=1
for q in B:ops.append(f.Op('MX',(q,),25,bit));bit+=1
ops += [f.Op('CX',(k,d),25)for d,k in zip(D,K)]
ops += [f.Op('TDG',(d,),26)for d in D]
# Final encoding conjugation cancels the decoder's first CX; K is measured X.
for d,k in zip(D,K):ops.append(f.Op('MX',(k,),27,bit));ops.append(f.Op('ID',(d,),27));bit+=1
ops.sort(key=lambda o:o.time);busy=set()
for o in ops:
 for q in o.qs:
  assert (o.time,q) not in busy,(o.time,o.qs,o.kind)
  busy.add((o.time,q))
comp=record_contract.complete(f.make_model(ops,[]),[]);neg=[r for r in comp['missing'] if r['reference']]
if neg:print('NEGATIVE',json.dumps(neg));sys.exit(1)
ds=[set(r['bits'])for r in comp['missing']]
stem=ft.emit('direct_phase',ops,ds,D,metadata={'scope':'complete abstract phase-C2 direct source, both prechecks and two independently flagged seven-cats, all channels noisy; no grid claim','physical_data':D,'inner_partners':K,'clock_count':28,'source_T':15,'derived_detectors':len(ds)})
old=jq.adjacent
try:
 jq.adjacent=lambda a,b:a!=b
 raw=ft.raw_check(stem.with_suffix('.qasm').read_text(),D);print('RAW',json.dumps(raw),flush=True)
 if raw['ok']:
  sg=ft.singles(stem);print('SINGLES',json.dumps({'loss_at_p001':sg['first_order_loss'],'count':sg['harmful_count']}),flush=True)
  print('PRICE',json.dumps(ft.price(stem)),flush=True)
finally:jq.adjacent=old
