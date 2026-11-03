"""Full noisy 7-cat source plus encoded K verification of a terminal resource."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027')]
import smallcat as s
from joint import emit
base=H/'deep_extra_best/flag_9_0_5';out=H/'deep_kverify';out.mkdir(exist_ok=True)
K=list(range(28,35));blocks={'A':list(range(14,21)),'B':list(range(7,14)),'C':list(range(21,28))}
ENC=[[(0,2),(1,5),(3,6)],[(0,4),(1,6),(3,5)],[(0,6),(1,2),(3,4)]];PIV={0,1,3}
def one(which):
 try:
  ops,dets=s.f.parse_current(base.with_suffix('.qasm').read_text());target=blocks[which];plus=(which=='B')
  # Each measured cat wire is reset immediately after its own last source use.
  ready={i:max(o.time for o in ops if K[i] in o.qs and o.time<18)+1 for i in range(7)}
  new=[]
  for i,q in enumerate(K):
   t=ready[i];new.append(s.f.Op('RX' if (i not in PIV if plus else i in PIV) else 'R',(q,),t));ready[i]=t+1
  for layer in ENC:
   for a,b in layer:
    a,b=(b,a) if plus else (a,b);t=max(ready[a],ready[b]);new.append(s.f.Op('CX',(K[a],K[b]),t));ready[a]=ready[b]=t+1
  targetready=max(o.time for o in ops if set(o.qs)&set(target) and o.time<18)+1
  tap=max(max(ready.values()),targetready);bit=max(o.bit or 0 for o in ops)+1
  for i,q in enumerate(K):
   new.append(s.f.Op('CX',(target[i],q)if plus else(q,target[i]),tap))
   new.append(s.f.Op('M' if plus else 'MX',(q,),tap+1,bit+i))
  # Shift only the terminal layer and reads; prep and all K-source uses remain.
  delta=max(0,tap+1-18)
  ops=[s.f.Op(o.kind,o.qs,o.time+delta if o.time>=18 else o.time,o.bit)for o in ops]+new;ops.sort(key=lambda o:o.time)
  used=set()
  for o in ops:
   k={(o.time,q)for q in o.qs}
   if k&used:return {'block':which,'error':'collision','op':repr(o)}
   used|=k
  s.f.DATA=list(range(7));model=s.f.make_model(ops,dets);complete=s.record_contract.complete(model,dets)
  if any(x['reference']for x in complete['missing']):return {'block':which,'error':'negative_reference'}
  ds=dets+[set(x['bits'])for x in complete['missing']];text=emit(ops,ds);raw=s.ideal_contract_check(text,list(range(7)))
  row={'block':which,'tap':tap,'delta':delta,'added_detectors':len(complete['missing']),'clocks':max(o.time for o in ops)+1,'cx':sum(o.kind=='CX'for o in ops),'raw':raw['ok']}
  if not raw['ok']:row['detail']=raw;return row
  stem=out/f'verify_{which}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':list(range(7)),'abstract':True,'encoded_verifier':which}))
  a=s.record_contract.singles(s.f.make_model(ops,ds));v=s.exact(stem);row.update(c1=a['c1'],loss=v['loss'],acceptance=v['acceptance'],stem=str(stem))
  return row
 except Exception as e:
  import traceback
  return {'block':which,'error':str(e),'traceback':traceback.format_exc()}
if __name__=='__main__':
 with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:rows=list(ex.map(one,['A','B','C']))
 (H/'deep_kverify_results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2),flush=True)
