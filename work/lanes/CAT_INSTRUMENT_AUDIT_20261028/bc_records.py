import os,sys,json,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path[:0]=[str(R/'work/lanes/END2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
from qtools.evaluator import frontend as f
from joint import emit
import record_contract
P=next((R/'work/lanes/NATIVE_CAT7_20261028/boundary').glob('cat7_opt_t11_m0_d21*.qasm'));base,dets=f.parse_current(P.read_text());prefix=[o for o in base if o.time<38];available={o.bit for o in prefix if o.bit is not None};initial=[r for r in dets if r<=available];D=[6,20,19,10,2,22,16];B=[12,26,25,11,3,28,17];C=[18,27,24,5,4,29,23];S=[{0,2,4,6},{1,2,5,6},{3,4,5,6}];f.DATA=D;ans=[]
for k,g in enumerate(S):
 ops=copy.deepcopy(prefix);bit=max(available)+1;t=38;ops.append(f.Op('RX',(35,),t));t+=1
 supp=[B[i] for i in sorted(g)]+[C[i] for i in sorted(g) if i!=4]
 for q in supp:ops.append(f.Op('CX',(35,q),t));t+=1
 ops.append(f.Op('MX',(35,),t,bit));contract=record_contract.complete(f.make_model(ops,initial),initial);rows=[r for r in contract['missing'] if bit in r['bits']]
 ans.append({'index':k,'support':supp,'probe_bit':bit,'record_relations':rows})
print(json.dumps(ans,indent=2));(H/'bc_records.json').write_text(json.dumps(ans,indent=2)+'\n')
