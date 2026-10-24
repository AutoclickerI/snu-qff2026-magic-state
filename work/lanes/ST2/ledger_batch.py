import os,sys,subprocess,json,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
REGIONS=['prefix_ops','prefix_idles','data_wait','BC','A','round']
def job(mode,label,procs):
    stem=H/('ledger_'+label.replace(':','_')+'.'+mode+'.log')
    cmd=[str(ROOT/'.venv/bin/python'),'-B',str(H/'ledger.py'),mode,label,str(procs)]
    t=time.monotonic()
    with stem.open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
    return dict(mode=mode,label=label,returncode=r.returncode,seconds=time.monotonic()-t)
if __name__=='__main__':
    mode=sys.argv[1];workers=int(sys.argv[2]);procs=int(sys.argv[3]) if len(sys.argv)>3 else 1
    labels=['all']+[f'{m}:{r}' for m in ['no','only'] for r in REGIONS]
    rows=[]
    with ThreadPoolExecutor(workers) as pool:
        fs=[pool.submit(job,mode,l,procs) for l in labels]
        for f in as_completed(fs):r=f.result();rows.append(r);print(json.dumps(r),flush=True)
    (H/('ledger_'+mode+'_jobs.json')).write_text(json.dumps(rows,indent=2))
    assert all(r['returncode']==0 for r in rows),rows
