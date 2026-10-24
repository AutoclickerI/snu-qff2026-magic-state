"""Official fast_check gate, unchanged speed probe, and unchanged MAIN/spec/mc3 CLI."""
import os,sys,json,subprocess,time,re,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2];os.chdir(ROOT)
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1';os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
sys.path.insert(0,str(ROOT/'work'))
import fast_check,xtim,speed_predict_local
xtim.cache_dir=str(H/'.xtim_cache')
for stem in sys.argv[1:]:
 p=H/stem;md=json.loads(p.with_suffix('.json').read_text());text=p.with_suffix('.qasm').read_text();t=time.monotonic()
 r=fast_check.check(text,md['data_qubits'],shots=10**6,seed=0,procs=1)
 out=dict(stem=stem,passed=r.passed,format=r.format_ok,correctness=r.correct_ok,acceptance=r.acceptance,score=float(r.score) if r.score is not None else None,sem=float(r.sem) if r.sem is not None else None,cx=r.n_2q,seconds=time.monotonic()-t,host=os.uname().nodename,sha256=hashlib.sha256(text.encode()).hexdigest())
 (H/(stem+'.judge.log')).write_text(str(r)+'\n')
 if r.passed:out['speed']=speed_predict_local.predict(str(p))
 (H/(stem+'.gates.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
 if not r.passed or out['speed']['classification']!='FAST':continue
 # Run source-identical mc3 (copy is necessary because tom's mirror lacks MAIN/spec).
 log=H/(stem+'.mc3.log')
 with log.open('w') as f:rc=subprocess.run([str(ROOT/'.venv/bin/python'),'-u',str(H/'mc3_local.py'),str(p),'--procs',os.environ.get('WAITPROT_MC_PROCS','1')],stdout=f,stderr=subprocess.STDOUT).returncode
 s=log.read_text();seeds=[]
 for seed,score,sem,acc in re.findall(r' (0|1000|2000) ([0-9.e+-]+) ± ([0-9.e+-]+) acc ([0-9.]+)',s):seeds.append(dict(seed=int(seed),score=float(score),sem=float(sem),acceptance=float(acc)))
 mc=dict(stem=stem,returncode=rc,seeds=seeds)
 if rc==0 and len(seeds)==3:mc.update(mean=sum(x['score'] for x in seeds)/3,mean_sem=sum(x['sem']**2 for x in seeds)**.5/3)
 (H/(stem+'.mc.json')).write_text(json.dumps(mc,indent=2));print(json.dumps(mc),flush=True)
