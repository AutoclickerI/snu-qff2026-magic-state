"""Published 14-CX Steane instrument inserted before final square. Abstract geometry."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027')]
import smallcat as s
from joint import emit
base=H/'deep_extra_best/flag_9_0_5';out=H/'ulo';out.mkdir(exist_ok=True)
# Published paper coordinates mapped into the existing Steane generator space.
perm=(0,1,3,6,2,4,5);mapq={i:perm[i]for i in range(7)};mapq.update({7:28,8:29,9:30,10:31})
pairs=[(3,8),(5,9),(6,7),(10,9),(10,8),(9,7),(7,8),(0,7),(8,9),(7,9),(10,7),(1,7),(2,8),(4,9)]
def one(baseaxis):
 ops,dets=s.f.parse_current(base.with_suffix('.qasm').read_text());bit=max(o.bit or 0 for o in ops)+1
 ready={i:19 for i in range(11)};checks=[]
 for i in range(7,11):checks.append(s.f.Op('RX' if (i==10)==(baseaxis=='Z') else 'R',(mapq[i],),18))
 for a,b in pairs:
  if baseaxis=='X':a,b=b,a
  t=max(ready[a],ready[b]);ready[a]=ready[b]=t+1;checks.append(s.f.Op('CX',(mapq[a],mapq[b]),t))
 m=max(ready.values());checks += [s.f.Op('MX' if (i==10)==(baseaxis=='Z') else 'M',(mapq[i],),m,bit+i-7) for i in range(7,11)]
 delta=m+1-18
 moved=[];resource=set(range(7,28))|{35}
 for o in ops:
  move=o.time>=18
  if o.time>=13 and set(o.qs)&resource and not(set(o.qs)&set(range(7))):
   # The original C cat readouts finish at 13/14; keep these before resource reset.
   if not(o.kind=='MX' and o.qs[0] in range(21,28) and o.time<=14):move=True
  moved.append(s.f.Op(o.kind,o.qs,o.time+delta if move else o.time,o.bit))
 ops=moved+checks;ds=dets+[{bit+i}for i in range(4)];ops.sort(key=lambda o:o.time)
 used=set()
 for o in ops:
  k={(o.time,q)for q in o.qs}
  if k&used:return {'axis':baseaxis,'error':'collision','op':repr(o)}
  used|=k
 text=emit(ops,ds);raw=s.ideal_contract_check(text,list(range(7)));row={'axis':baseaxis,'extra_clock':delta,'raw':raw['ok'],'raw_detail':raw,'cx':sum(o.kind=='CX' for o in ops),'clocks':max(o.time for o in ops)+1}
 if raw['ok']:
  stem=out/f'insert_{baseaxis}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':list(range(7)),'abstract':True,'instrument':'published 14 CX nonadaptive zero syndrome','axis':baseaxis}))
  s.f.DATA=list(range(7));a=s.record_contract.singles(s.f.make_model(*s.f.parse_current(text)));row['c1']=a['c1'];v=s.exact(stem);row.update(loss=v['loss'],acceptance=v['acceptance'],stem=str(stem))
 return row
if __name__=='__main__':
 with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:rows=list(ex.map(one,['Z','X']))
 (H/'ulo_results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2),flush=True)
