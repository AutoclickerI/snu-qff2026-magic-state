"""Gao-Yuan-Yao grouped source, coherent bulk frame, complete abstract tail.

Reconstructed from arXiv:2609.12698 Eq. 14, 42 and 46-49, Table 3.
Includes explicit noisy generic CSS encoder, verifier, all grouped checks,
15 T/TDG gates, coherent Pauli-frame corrections, bulk reads, and a noisy
physical square terminal. CX adjacency is deliberately relaxed for diagnosis.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,sys,hashlib,contextlib,io
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
for d in ('work/tools','work/lanes/END2_20261027','work/lanes/REBUILD20261027','upstream/snu-qff2026-problem'):sys.path.insert(0,str(ROOT/d))
from qtools.evaluator import frontend as f
sys.path.insert(0,str(ROOT/'work/lanes/CAT3_20261027'))
from smallcat import exact
from partial_square import prep,ideal_contract_check
from joint import emit
from record_contract import complete,singles

# The paper's face stabilizers map to the judge's canonical coordinate order.
D=[0,1,2,3,6,5,4];A=list(range(7,14));B=list(range(14,21));C=list(range(21,28))
# Published checks; physical labels 1..15 become q0..q14.
h1=[1,2,6,7];h2=[2,3,4,7];h3=[4,5,6,7]
b1=[8,9,13,14];b2=[9,10,11,14];b3=[11,12,13,14];b4=list(range(8,16));
gens=[h1+b1,h2+b2,h3+b3,b4,list(range(1,8))]

def code_encoder():
 rows=[sum(1<<(q-1)for q in g)for g in gens];piv=[];k=0
 for col in range(15):
  j=next((i for i in range(k,len(rows))if rows[i]>>col&1),None)
  if j is None:continue
  rows[k],rows[j]=rows[j],rows[k]
  for z in range(len(rows)):
   if z!=k and rows[z]>>col&1:rows[z]^=rows[k]
  piv.append(col);k+=1
  if k==len(rows):break
 assert len(piv)==5
 return piv,[(p,i)for p,row in zip(piv,rows)for i in range(15)if i!=p and row>>i&1]

def build():
 ops=[];dets=[];last=[-1]*36;bit=0
 def barrier():
  t=max(last)+1
  for i in range(36):last[i]=max(last[i],t-1)
 def add(k,qs):
  nonlocal bit
  t=max(last[q]for q in qs)+1;b=bit if k in ('M','MX')else None
  if b is not None:bit+=1
  ops.append(f.Op(k,tuple(qs),t,b))
  for q in qs:last[q]=t
  return b
 def cx(a,b):add('CX',(a,b))
 piv,pairs=code_encoder()
 for q in range(15):add('RX'if q in piv else'R',(q,))
 for a,b in pairs:cx(a,b)
 barrier();add('RX',(29,))
 for d in range(7):cx(29,d)
 dets.append({add('MX',(29,))});barrier()
 # Four independently prepared rail sets allow compatible Z checks to overlap.
 def group3(c,d,e,g,ua,ub,uc,sa,sb,sc,flag):
  for q in (sa,sb,sc):add('R',(q,))
  add('RX',(flag,));cv=lambda q:q-1
  for x,y in [(cv(c),sa),(flag,sa),(sa,sc),(cv(d),sa),(sa,sb),
              (cv(e),sa),(cv(ua),sa),(cv(ub),sb),(cv(g),sb),
              (cv(e),sc),(cv(uc),sc),(cv(g),sc),(flag,sa),(flag,sb),(flag,sc)]:cx(x,y)
  ra,rb,rc=add('M',(sa,)),add('M',(sb,)),add('M',(sc,));ff=add('MX',(flag,))
  dets.extend([{ra},{ra,rb},{ra,rc},{ff}])
 def group2(a,b,u1,u2,v1,v2,sa,sb,flag):
  for q in (sa,sb):add('R',(q,))
  add('RX',(flag,));cv=lambda q:q-1
  for x,y in [(cv(a),sa),(flag,sa),(cv(b),sa),(sa,sb),
              (cv(u1),sa),(cv(u2),sa),(cv(v1),sb),(cv(v2),sb),(flag,sa),(flag,sb)]:cx(x,y)
  ra,rb=add('M',(sa,)),add('M',(sb,));ff=add('MX',(flag,))
  dets.extend([{ra},{ra,rb},{ff}])
 group3(9,8,10,14,15,13,11,15,16,17,18)
 group3(7,2,6,4,1,3,5,19,20,21,22)
 group2(4,11,5,12,7,14,23,24,25)
 group2(7,14,6,13,2,9,26,27,28)
 barrier()
 for d in range(15):add('T'if (d+1)%2 else'TDG',(d,))
 barrier()
 # F(u)=Z47^s1 Z45^s2 Z27^s3. Every CZ(X-bulk, face)
 # equals CX(face, bulk) immediately before the bulk MX.
 matrix={}
 for support,face in [([8,9,13,14],[4,7]),([9,10,11,14],[4,5]),([11,12,13,14],[2,7])]:
  for bulk in support:
   for v in face:matrix[(v-1,bulk-1)]=matrix.get((v-1,bulk-1),0)^1
 correction=[e for e,v in matrix.items()if v];assert len(correction)==16
 for a,b in correction:cx(a,b)
 bulk=[add('MX',(q,))for q in range(7,15)];dets.append(set(bulk));barrier()
 # All resources are reset and prepared by explicit noisy operations.
 t=max(last)+1
 for block,plus in ((A,True),(B,False),(C,True)):prep(ops,block,t,plus)
 terminal=t+4
 for i in range(7):
  ops += [f.Op('CX',(D[i],A[i]),terminal),f.Op('CX',(B[i],C[i]),terminal),f.Op('CX',(B[i],D[i]),terminal+1),f.Op('CX',(C[i],A[i]),terminal+1)]
 first=bit
 for block,k in ((A,'M'),(B,'MX'),(C,'MX')):
  for q in block:ops.append(f.Op(k,(q,),terminal+2,bit));bit+=1
 ops.sort(key=lambda o:o.time);f.DATA=D
 text=emit(ops,dets);model=f.make_model(*f.parse_current(text));contract=complete(model,dets)
 extra=[r for r in contract['missing']if any(x>=first for x in r['bits'])];assert all(not x['reference']for x in extra)
 dets += [set(x['bits'])for x in extra];text=emit(ops,dets);raw=ideal_contract_check(text,D)
 stem=H/'gao_abstract_parallel';stem.with_suffix('.qasm').write_text(text)
 meta=dict(data_qubits=D,raw=raw,encoder_cx=len(pairs),coherent_frame_cx=len(correction),cx=sum(o.kind=='CX'for o in ops),ticks=max(o.time for o in ops)+1,
   source_detector_count=len(dets)-len(extra),raw_source_model='25? generic exact rank-5 CSS preparation; full physical channels noisy',
   output_order=D,source='Gao et al. exact group equations, separate parallel rails and coherent bulk frame',
   grid_valid=False,diagnostic_only=True,scope='All-to-all complete circuit; every source/resource/tail channel noisy, adjacency deliberately relaxed.',sha256=hashlib.sha256(text.encode()).hexdigest())
 stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n');print('raw',json.dumps(meta),flush=True)
 if raw['ok']:
  sg=singles(f.make_model(*f.parse_current(text)));print('SINGLES',json.dumps({'c1':sg['c1'],'harmful':len(sg['harmful_faults'])}),flush=True);p=exact(stem);meta.update(singles=sg,exact=p)
  stem.with_suffix('.result.json').write_text(json.dumps(meta,indent=2)+'\n');print('RESULT',json.dumps({'loss':p['loss'],'acceptance':p['acceptance'],'c1':sg['c1'],'harmful':len(sg['harmful_faults'])}),flush=True)
if __name__=='__main__':build()
