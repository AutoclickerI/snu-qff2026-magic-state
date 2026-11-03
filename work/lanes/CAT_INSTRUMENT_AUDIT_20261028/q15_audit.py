import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path[:0]=[str(R/'work/lanes/END2_20261027'),str(R/'work/tools')]
from qtools.evaluator import frontend as f
from joint import emit
from tprep.qasm import to_stim
from tprep.exact import run
P=next((R/'work/lanes/NATIVE_CAT7_20261028/boundary').glob('cat7_opt_t11_m0_d21*.qasm'));ops,dets=f.parse_current(P.read_text());prefix=[o for o in ops if o.time<32];bits={o.bit for o in prefix if o.bit is not None};st,err=to_stim(emit(prefix,[r for r in dets if r<=bits]));assert not err
state,inv,records,_,w=run(st,36);recops=[o for o in prefix if o.bit is not None];rw={o.bit:records[i] for i,o in enumerate(recops)};last=next(o for o in reversed(prefix) if 15 in o.qs);assert last.kind=='MX' and last.bit==21
out={'source_last_q15':{'kind':last.kind,'clock':last.time,'record':last.bit},'expectations':{}}
for axis in 'XYZ':
 p=state.stim.PauliString(state.n);p[w[15]]=axis;out['expectations'][axis]=float(state.expectation(p,inv))
 p[rw[21]]='Z';out['expectations'][axis+'_record21']=float(state.expectation(p,inv))
(H/'q15_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
