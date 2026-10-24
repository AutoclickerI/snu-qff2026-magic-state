import os,sys,json,subprocess
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');sys.path.insert(0,str(ROOT/'work'));import tprep,fast_check
args=sys.argv[1:];procs=int(args.pop(0))
for name in args:
 stem=ROOT/'work/lanes/EARLYBC'/name
 txt=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
 r=tprep.check(txt,data,shots=10**6,seed=0)
 result=dict(check={k:getattr(r,k) for k in ('passed','acceptance','score')},check_repr=str(r));stem.with_suffix('.check.json').write_text(json.dumps(result,indent=2));print(name,'check',r,flush=True)
 if not r.passed:continue
 with stem.with_suffix('.exact.log').open('w') as log:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'work/lanes/EVAL/exact2.py'),str(stem)+'.qasm','--third','--procs',str(procs),'--top','5'],stdout=log,stderr=subprocess.STDOUT,check=True)
 print(name,'exact',stem.with_suffix('.exact.log').read_text().split('time:')[0],flush=True)
