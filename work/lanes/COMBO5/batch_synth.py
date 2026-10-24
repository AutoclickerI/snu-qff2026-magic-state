import concurrent.futures,json,os,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PY=str(ROOT/'.venv/bin/python')
def one(j):
    cmd=[PY,str(HERE/'run_synth.py'),j['name'],'--depth',str(j['depth']),'--late',str(j['late']),'--seed',str(j['seed'])]
    if j.get('free'):cmd+=['--free-pivots']
    with (HERE/(j['name']+'.solver.log')).open('w') as f:
        r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=os.environ)
    print(j['name'],'EXIT',r.returncode,flush=True)
    return dict(name=j['name'],exit=r.returncode)
if __name__=='__main__':
    jobs=json.loads((HERE/'synth_jobs.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:r=list(pool.map(one,jobs))
    (HERE/'synth_batch.json').write_text(json.dumps(r,indent=2))
