import importlib,json,sys,time
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');OUT=ROOT/'work/lanes/PRE3';sys.path[:0]=[str(ROOT/'upstream/snu-qff2026-problem'),str(ROOT/'work')]
for mod in ('tprep.grid','tprep.parse','tprep.qasm'):
 m=importlib.import_module(mod);m.adjacent=lambda a,b:True
import fast_check
for stem in ('base','q13_19','q19_13_prompt'):
 text=(OUT/(stem+'.qasm')).read_text();data=json.loads((OUT/(stem+'.json')).read_text())['data_qubits'];vals=[]
 for seed in (0,1000,2000):
  t=time.time();r=fast_check.check(text,data,shots=10**8,seed=seed,procs=8); vals.append({'seed':seed,'score':float(r.score),'sem':float(r.sem),'acceptance':float(r.acceptance)}); print(stem,seed,vals[-1],flush=True)
 out={'variant':stem,'shots':10**8,'seeds':vals,'mean':sum(v['score'] for v in vals)/3,'cx':int(r.n_2q)};(OUT/(stem+'.mc.json')).write_text(json.dumps(out,indent=2)+'\n');print('mean',stem,out['mean'],flush=True)
