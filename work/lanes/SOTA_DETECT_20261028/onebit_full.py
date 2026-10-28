"""Fully noisy seven-cat source, two one-bit terminal orientations and optional resource coupling."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027'),str(R/'work/tools')]
import frame_tools as ft,smallcat as s
import tprep.qasm as jq
D=list(range(7));A=list(range(14,21));B=list(range(7,14));C=list(range(21,28));K=list(range(28,35));F=s.f
base=H/'deep_bcheck/bcheck_029';out=H/'onebit_full';out.mkdir(exist_ok=True)
def one(job):
 axis,couple=job;ft.OUT=out;ops,dets=F.parse_current(base.with_suffix('.qasm').read_text());keep=[]
 for o in ops:
  qs=set(o.qs)
  if o.time<=9 or (qs&set(D) and o.time<=13) or (qs&set(A) and o.time<=12) or (qs&set(B) and o.time<=10) or (qs&set(C) and o.time<=11) or (qs&set(K) and o.time<=13):keep.append(o)
 ops=keep;bits={o.bit for o in ops if o.bit is not None};dets=[x for x in dets if set(x)<=bits];nextbit=max(bits)+1
 # For the correlated control, the optional B->A pre-entangler is a real transversal layer.
 s.prep(ops,A,13,axis=='Z');s.prep(ops,B,12 if couple else 14,axis=='X')
 first=18 if couple else 17
 if couple:ops += [F.Op('CX',(b,a),17) for a,b in zip(A,B)]
 for d,a,b in zip(D,A,B):
  ops.append(F.Op('CX',(a,d)if axis=='X'else(d,a),first))
  if not any(x.time==first and b in x.qs for x in ops):ops.append(F.Op('ID',(b,),first))
  ops.append(F.Op('CX',(b,d)if axis=='X'else(d,b),first+1))
 for i,a in enumerate(A):ops.append(F.Op('MX'if axis=='X'else'M',(a,),first+1,nextbit+7+i))
 for i,d in enumerate(D):ops.append(F.Op('M'if axis=='X'else'MX',(d,),first+2,nextbit+i))
 for b in B:ops.append(F.Op('ID',(b,),first+2))
 dets += [{nextbit+j for j in row}for row in F.SUPPORTS]+[{nextbit+7+j for j in row}for row in F.SUPPORTS]
 frames={'X':(0,set(range(nextbit,nextbit+7))if axis=='X'else set()),'Z':(0,set(range(nextbit,nextbit+7))if axis=='Z'else set())}
 ops.sort(key=lambda o:o.time);used=set()
 for o in ops:
  key={(o.time,q)for q in o.qs}
  if key&used:return {'axis':axis,'couple':couple,'error':'collision','op':repr(o)}
  used|=key
 stem=ft.emit(f'onebit_{axis}_{int(couple)}',ops,dets,B,frames,{'abstract':True,'axis':axis,'coupled':couple,'all_channels_noisy':True})
 old=jq.adjacent
 try:
  jq.adjacent=lambda a,b:a!=b
  val=ft.price(stem);return {'axis':axis,'couple':couple,'raw':val['raw'],'loss':val.get('loss'),'acceptance':val.get('acceptance'),'cx':sum(o.kind=='CX'for o in ops),'clocks':max(o.time for o in ops)+1,'stem':str(stem)}
 except Exception as e:
  import traceback;return {'axis':axis,'couple':couple,'error':str(e),'traceback':traceback.format_exc()}
 finally:jq.adjacent=old
if __name__=='__main__':
 with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:rows=list(ex.map(one,[(p,c)for p in ['X','Z']for c in [False,True]]))
 (H/'onebit_full_results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2),flush=True)
