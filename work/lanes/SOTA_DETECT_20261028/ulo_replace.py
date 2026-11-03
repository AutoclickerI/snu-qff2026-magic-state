"""Replace final BC check by published Steane gadget; all physical noise retained."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027')]
import smallcat as s
from joint import emit
base=H/'deep_extra_best/flag_9_0_5';out=H/'ulo';out.mkdir(exist_ok=True)
perm=(0,1,3,6,2,4,5);mp={i:perm[i]for i in range(7)};mp.update({7:28,8:29,9:30,10:31})
pairs=[(3,8),(5,9),(6,7),(10,9),(10,8),(9,7),(7,8),(0,7),(8,9),(7,9),(10,7),(1,7),(2,8),(4,9)]
def one(axis):
 orig,_=s.f.parse_current(base.with_suffix('.qasm').read_text());bit=max(o.bit or 0 for o in orig)+1
 ready={i:19 for i in range(11)};checks=[]
 for i in range(7,11):checks.append(s.f.Op('RX' if (i==10)==(axis=='Z') else 'R',(mp[i],),18))
 for a,b in pairs:
  if axis=='X':a,b=b,a
  t=max(ready[a],ready[b]);ready[a]=ready[b]=t+1;checks.append(s.f.Op('CX',(mp[a],mp[b]),t))
 m=max(ready.values());checks += [s.f.Op('MX' if (i==10)==(axis=='Z') else 'M',(mp[i],),m,bit+i-7)for i in range(7,11)];delta=m+1-18
 ops=[]
 for o in orig:
  if o.time<13:ops.append(o);continue
  # Preserve all source cat interactions/readouts and earlier source measurements.
  if set(o.qs)&set(range(28,35)) or (o.bit is not None and o.bit<28):ops.append(o);continue
  if o.time<18 and set(o.qs)&set(range(7)):
   ops.append(o);continue
  # Preserve A=PB resource preparation and D->A check/read, eliminate B/C final instrument.
  if set(o.qs)<=set(range(14,21)):
   ops.append(s.f.Op(o.kind,o.qs,o.time+delta-(1 if o.time==20 else 0),o.bit));continue
  if o.kind=='CX' and o.time==18 and o.qs[0] in range(7) and o.qs[1] in range(14,21):
   ops.append(s.f.Op('CX',o.qs,o.time+delta));continue
 ops+=checks;ops.sort(key=lambda o:o.time);used=set()
 for o in ops:
  k={(o.time,q)for q in o.qs}
  if k&used:return {'axis':axis,'error':'collision','op':repr(o)}
  used|=k
 s.f.DATA=list(range(7));contract=s.record_contract.complete(s.f.make_model(ops,[]),[])
 if any(x['reference']for x in contract['missing']):return {'axis':axis,'error':'negative reference'}
 ds=[set(x['bits'])for x in contract['missing']];text=emit(ops,ds);raw=s.ideal_contract_check(text,list(range(7)));row={'axis':axis,'raw':raw['ok'],'detail':raw,'clocks':max(o.time for o in ops)+1,'cx':sum(o.kind=='CX'for o in ops)}
 if raw['ok']:
  stem=out/f'replace_{axis}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':list(range(7)),'abstract':True,'instrument':'ULO plus A, final BC removed'}));a=s.record_contract.singles(s.f.make_model(ops,ds));v=s.exact(stem);row.update(c1=a['c1'],loss=v['loss'],acceptance=v['acceptance'],stem=str(stem))
 return row
if __name__=='__main__':
 with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:rows=list(ex.map(one,['X','Z']))
 (H/'ulo_replace_results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
