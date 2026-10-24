"""Complete all-orders and reference-check queue; no screen is promoted silently."""
from evaluator import *
from moments_batch import evaluate
import subprocess,concurrent.futures,ctypes,select,hashlib

def capacity(n):
    libc=ctypes.CDLL(None,use_errno=True)
    while True:
        rows=[r.split() for r in subprocess.check_output(['ps','-u',str(os.getuid()),'-o','pid=,pcpu=,stat='],text=True).splitlines()]
        used=sum(float(r[1]) for r in rows if 'T' not in r[2])/100
        if used+n<=.75*os.cpu_count() and os.getloadavg()[0]+n<os.cpu_count():return used
        fds=[libc.syscall(434,int(r[0]),0) for r in rows if float(r[1])>15 and 'T' not in r[2] and int(r[0])!=os.getpid()];fds=[f for f in fds if f>=0];assert fds
        select.select(fds,[],[])
        for fd in fds:os.close(fd)

def command(args,path,n=1):
    used=capacity(n);t=time.monotonic()
    with path.open('w') as f:r=subprocess.run([str(ROOT/'.venv/bin/python'),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
    return dict(returncode=r.returncode,seconds=time.monotonic()-t,command=list(map(str,args)),cpu_before=used)

def one(tag,exact_procs):
    stem=V/'finalists'/tag;md=json.loads(stem.with_suffix('.json').read_text());text=stem.with_suffix('.qasm').read_text();rec=dict(tag=tag,sha256=hashlib.sha256(text.encode()).hexdigest())
    ev=exact2.Eval(text,md['data_qubits']);c1=float(ev.fp@ev.n_single)
    price=evaluate(ev) if abs(c1)<1e-12 else dict(c1=c1,exp_minus_A1=math.exp(-float(ev.fp@(1-ev.a_single))),invalid_cubic=True)
    stem.with_suffix('.screen.json').write_text(json.dumps(price,indent=2))
    oracle=[H/'allorders_general.py',stem,'--procs','1'] if '// FRAME' in text else [V/'evaluator.py',stem]
    cached=stem.with_suffix('.allorders.json')
    if cached.exists() and json.loads(cached.read_text()).get('qasm_sha256')==rec['sha256']:
        rec['oracle']=dict(returncode=0,reused=True,qasm_sha256=rec['sha256'])
    else:
        rec['oracle']=command(oracle,stem.with_suffix('.oracle.log'));assert rec['oracle']['returncode']==0,rec
    rec['gate']=command([V/'gate30.py',stem],stem.with_suffix('.gate.log'));assert rec['gate']['returncode']==0,rec
    cmd=[ROOT/'work/lanes/EVAL/exact2.py',str(stem)+'.qasm','--procs',str(exact_procs),'--top','8']
    if abs(c1)<1e-12:cmd.append('--third')
    rec['reference']=command(cmd,stem.with_suffix('.exact.log'),exact_procs);assert rec['reference']['returncode']==0,rec
    rec['price']=price;rec['allorders']=json.loads(stem.with_suffix('.allorders.json').read_text());rec['gates']=json.loads(stem.with_suffix('.gate.json').read_text());stem.with_suffix('.verified30.json').write_text(json.dumps(rec,indent=2));print(json.dumps(dict(tag=tag,loss=rec['allorders']['loss'],gate=rec['gates']['judge_pass'],fast=rec['gates']['fast'])),flush=True)
    return rec

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('selection',type=Path,nargs='?');p.add_argument('--one');p.add_argument('--workers',type=int,default=3);p.add_argument('--exact-procs',type=int,default=4);a=p.parse_args()
    if a.one:one(a.one,a.exact_procs)
    else:
        tags=json.loads(a.selection.read_text())
        def isolated(tag):
            cmd=[str(ROOT/'.venv/bin/python'),str(V/'price30.py'),'--one',tag,'--exact-procs',str(a.exact_procs)]
            with (V/'finalists'/(tag+'.price.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
            print(json.dumps(dict(tag=tag,returncode=r.returncode)),flush=True);return dict(tag=tag,returncode=r.returncode)
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:out=list(ex.map(isolated,tags))
        a.selection.with_suffix('.verified.json').write_text(json.dumps(out,indent=2))
