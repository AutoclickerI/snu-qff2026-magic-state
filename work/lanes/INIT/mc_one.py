import json,sys
from pathlib import Path
sys.path.insert(0,'work')
from fast_check import check
n=sys.argv[1]; p=Path('work/lanes/INIT')/(n+'.qasm'); m=json.loads(p.with_suffix('.json').read_text());
for s in (0,1000,2000):
 r=check(p.read_text(),m['data_qubits'],shots=10**8,seed=s,procs=6)
 print(json.dumps({'name':n,'seed':s,'score':r.score,'sem':r.sem,'acceptance':r.acceptance,'passed':r.passed,'n_2q':r.n_2q}),flush=True)
