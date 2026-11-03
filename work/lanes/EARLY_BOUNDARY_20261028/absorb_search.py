import os,sys,json,itertools,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
sys.path[:0]=[str(R/'work/lanes/NATIVE2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
from incumbent_a_sx import f,emit
from qtools.validity import raw_check
import record_contract
record_contract.fa=f
P=next((R/'work/lanes/SOTA_20261028/native_best').glob('*.qasm'));orig,dets=f.parse_current(P.read_text());D=[6,20,19,10,2,22,16];f.DATA=D
# Keep an early data-copy into q15, remove its destructive source read. Test A network deletion subsets and the recopy gate both ways.
targets=[(41,(9,15)),(42,(21,15)),(43,(15,14)),(44,(15,9)),(45,(9,15)),(46,(16,15))]
results=[]
for mask in range(64):
 removed={(39,(16,15))}|{targets[i] for i in range(6) if mask>>i&1}
 ops=[copy.deepcopy(o) for o in orig if not (o.kind=='CX' and (o.time,o.qs) in removed) and not (o.bit==322)]
 ds=[]
 try:
  contract=record_contract.complete(f.make_model(ops,ds),ds); ds += [set(x['bits']) for x in contract['missing'] if not x['reference']]
  text=emit(ops,ds);raw=raw_check(text,D)
  row=dict(mask=mask,removed=sorted([list((t,list(q))) for t,q in removed]),raw=raw,extra_rows=len(contract['missing']))
  if raw['ok']:
   name=H/f'absorb_{mask:02d}';name.with_suffix('.qasm').write_text(text);name.with_suffix('.json').write_text(json.dumps({'data_qubits':D},indent=2)+'\n')
   row['stem']=str(name)
  print(json.dumps(row),flush=True);results.append(row)
 except Exception as e:print(json.dumps({'mask':mask,'error':repr(e)}),flush=True)
 (H/'absorb_search.json').write_text(json.dumps(results,indent=2)+'\n')
