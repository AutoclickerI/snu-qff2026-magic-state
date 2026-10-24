"""Repeat the R45 sweep with the exact v22h prefix times and all 18 detectors."""
import os,sys,json,argparse,subprocess,concurrent.futures
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=21);p.add_argument('--host',choices=['sunfish','zebra','all'],required=True);a=p.parse_args()
jobs=[]
for f in sorted((HERE/'runs').glob('v22_*.result.json')):
    r=json.loads(f.read_text())
    if r['pre']!='v22':continue
    jobs.append((f.stem.removesuffix('.result').replace('v22_','v22h_',1),r))
assert len(jobs)>900,len(jobs)
def run(job):
    i,(name,r)=job
    # Twenty-one remote workers, six local workers; assignment is deterministic.
    local=i%27>=21
    if a.host!='all' and local!=(a.host=='zebra'):return None
    stem=HERE/'runs'/name
    if stem.with_suffix('.result.json').exists():return dict(name=name,cached=True)
    cmd=[sys.executable,str(HERE/'mbp.py'),'runs/'+name,'--pre','v22h','--R','45','--blocks',r['blocks'],'--kind',r['kind'],'--order',''.join(map(str,r['order'])),'--perm',''.join(map(str,r['perm'])),'--red-mask',str(r.get('red_mask',7)),'--procs','1']
    assert os.getloadavg()[0]<os.cpu_count()
    with stem.with_suffix('.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);rc=proc.wait()
    out=dict(name=name,exit=rc)
    if rc==0:
        row=json.loads(stem.with_suffix('.result.json').read_text());out.update({k:row[k] for k in ['c1','second','third','total','expA1','check']})
    print(json.dumps(out),flush=True);return out
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:rows=[r for r in ex.map(run,enumerate(jobs)) if r is not None]
(HERE/f'matched_{a.host}.receipt.json').write_text(json.dumps(rows,indent=2)+'\n')
