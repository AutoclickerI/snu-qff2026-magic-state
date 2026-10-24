"""Actual judge gate plus the XTIM predictor, including the declared FRAME."""
from evaluator import *
import importlib.util,subprocess,re

def run(stem):
    result={};py=str(ROOT/'.venv/bin/python');cmd=[py,str(ROOT/'work/fast_check.py'),str(stem)+'.qasm',str(stem)+'.json','1000000','1']
    t=time.monotonic()
    with stem.with_suffix('.judge.log').open('w') as f:p=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    log=stem.with_suffix('.judge.log').read_text();result.update(returncode=p.returncode,seconds=time.monotonic()-t,judge_pass='passed=True' in log)
    if p.returncode==0:
        result['s_per_1e6']=float(re.search(r'\(([0-9.]+)s, 1 procs',log)[1]);result['seed0_acceptance_1e6']=float(re.search(r'acc=([0-9.e+-]+)',log)[1])
    spec=importlib.util.spec_from_file_location('lane_speed',V/'inputs/speed_predict.py');speed=importlib.util.module_from_spec(spec);spec.loader.exec_module(speed);speed.xtim.cache_dir=str(H/'.xtim_cache')
    text=stem.with_suffix('.qasm').read_text();original=speed._check.Plan
    if '// FRAME' in text:
        md=json.loads(stem.with_suffix('.json').read_text());model=exact2.Eval(text,md['data_qubits']).m
        speed._check.Plan=lambda data,frame,post,n_pre:original(data,model.frame,model.post,n_pre)
    try:result['prediction']=speed.predict(str(stem))
    finally:speed._check.Plan=original
    result['fast']=result['prediction']['classification']=='FAST';result['host']=os.uname().nodename
    stem.with_suffix('.gate.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True);return result

if __name__=='__main__':run(Path(sys.argv[1]))
