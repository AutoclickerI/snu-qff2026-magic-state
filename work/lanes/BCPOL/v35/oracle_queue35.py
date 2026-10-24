"""Full all-orders queue with isolated processes and host-capacity admission."""
from pathlib import Path
import os,sys,json,subprocess,concurrent.futures,ctypes,select,argparse,time
V=Path(__file__).resolve().parent;H=V.parent;ROOT=H.parents[2]
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',XTIM_TWIRL_CACHE_DIR=str(H/'.xtim_cache'))
def capacity(n):
    libc=ctypes.CDLL(None)
    while True:
        rows=[r.split() for r in subprocess.check_output(['ps','-u',str(os.getuid()),'-o','pid=,pcpu=,stat='],text=True).splitlines()]
        used=sum(float(r[1]) for r in rows if 'T' not in r[2])/100
        if used+n<=.75*os.cpu_count() and os.getloadavg()[0]+n<os.cpu_count():return used
        fds=[libc.syscall(434,int(r[0]),0) for r in rows if float(r[1])>20 and int(r[0])!=os.getpid() and 'T' not in r[2]];fds=[f for f in fds if f>=0];assert fds
        select.select(fds,[],[])
        for f in fds:os.close(f)
def job(tag,procs):
    stem=V/'finalists'/tag;used=capacity(procs)
    with stem.with_suffix('.oracle.log').open('w') as log:p=subprocess.run([str(ROOT/'.venv/bin/python'),str(V/'evaluator.py'),str(stem),'--procs',str(procs)],stdout=log,stderr=subprocess.STDOUT,cwd=ROOT)
    row=dict(tag=tag,returncode=p.returncode,cpu_before=used)
    if p.returncode==0:
        d=json.loads(stem.with_suffix('.allorders.json').read_text());row.update(loss=d['loss'],acceptance=d['acceptance'])
    print(json.dumps(row),flush=True);return row
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('selection',type=Path);p.add_argument('--workers',type=int,default=4);p.add_argument('--procs',type=int,default=2);a=p.parse_args();tags=json.loads(a.selection.read_text());capacity(a.workers*a.procs)
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:out=list(ex.map(lambda t:job(t,a.procs),tags))
    a.selection.with_suffix('.oracle_receipt.json').write_text(json.dumps(out,indent=2))
