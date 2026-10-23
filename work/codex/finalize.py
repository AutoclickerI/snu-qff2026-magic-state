import sys,json,os
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/codex')
import build_flag as b
import tprep
from pathlib import Path
out=Path('/home/jihoon/competitions/quantumn/work/codex')
text=b.text; data=b.dp
# official candidate text is all five detectors in build_flag
print('checking 10m',flush=True)
r=tprep.check(text,data,p=1e-3,shots=10_000_000,seed=0)
print(r,flush=True)
print('fault scan',flush=True)
scan=tprep.fault_scan(text,data,processes=1)
print(scan,flush=True)
meta={'data_qubits':data,'score_1e7':r.score,'sem':r.sem,'acceptance':r.acceptance,'n_2q':r.n_2q,'c1':scan.c1}
(out/'measurement_flag.json').write_text(json.dumps(meta,indent=2)+'\n')
(out/'measurement_flag.qasm').write_text(text)
(out/'measurement_flag_scan.txt').write_text(str(scan)+'\n')
