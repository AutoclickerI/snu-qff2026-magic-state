"""Bounded process queue; launches inspect host capacity, waits on exits."""
import os,sys,json,argparse,subprocess,datetime,concurrent.futures
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
OUT=Path(__file__).resolve().parent

def task(stem,procs,check,mc):
    cmd=[sys.executable,str(OUT/'evaluate.py'),stem,'--procs',str(procs)]
    if check:cmd+=['--check']
    if mc:cmd+=['--mc']
    with (OUT/(stem+'.queue.log')).open('w')as log:
        p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=OUT)
        print(json.dumps(dict(event='start',stem=stem,pid=p.pid,procs=procs)),flush=True)
        code=p.wait()
    print(json.dumps(dict(event='exit',stem=stem,code=code)),flush=True)
    return code

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('list');p.add_argument('--cores',type=int,default=20);p.add_argument('--procs',type=int,default=4);p.add_argument('--host-cores',type=int,default=64);p.add_argument('--check',action='store_true');p.add_argument('--mc',action='store_true');a=p.parse_args()
    todo=[s.strip()for s in (OUT/a.list).read_text().splitlines()if s.strip()];pending={};bad=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.cores//a.procs)as pool:
        while todo or pending:
            now=datetime.datetime.now(datetime.timezone.utc);cap=4 if now<datetime.datetime(2026,10,24,5,20,tzinfo=datetime.timezone.utc)else a.cores
            load=float(Path('/proc/loadavg').read_text().split()[0])
            # Account for launches whose work may not yet enter the 1-minute load.
            base_load=max(0,load-len(pending)*a.procs)
            while todo and (len(pending)+1)*a.procs<=cap and base_load+(len(pending)+1)*a.procs<=a.host_cores:
                nproc=subprocess.check_output(['nproc','--all'],text=True).strip();current=Path('/proc/loadavg').read_text().strip()
                print(json.dumps(dict(event='capacity',nproc=nproc,loadavg=current,lane_cap=cap)),flush=True)
                stem=todo.pop(0);f=pool.submit(task,stem,a.procs,a.check,a.mc);pending[f]=stem
            if not pending:
                (OUT/(a.list+'.remaining')).write_text('\n'.join(todo)+'\n')
                raise RuntimeError('Host capacity is occupied; remaining work saved for rerouting')
            done,_=concurrent.futures.wait(pending,return_when=concurrent.futures.FIRST_COMPLETED)
            for f in done:
                stem=pending.pop(f)
                if f.result():bad.append(stem)
    (OUT/(a.list+'.completion.json')).write_text(json.dumps(dict(finished=True,failed=bad),indent=2)+'\n')
    if bad:raise RuntimeError(('failed tasks',bad))
