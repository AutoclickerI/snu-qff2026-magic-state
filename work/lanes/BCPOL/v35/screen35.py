"""Cubic screening of structural branches; stores errors without hiding them."""
from core35 import *
from moments_batch import evaluate
import concurrent.futures,subprocess,argparse,math

def one(tag):
    stem=V/'finalists'/tag;md=json.loads(stem.with_suffix('.json').read_text());t=time.monotonic()
    ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),md['data_qubits']);a,n=ev.e.ntable(0,0);assert abs(a-1)<1e-10 and abs(n[0])<1e-10
    c1=float(ev.fp@ev.n_single)
    p=evaluate(ev) if abs(c1)<1e-12 else dict(c1=c1,exp_minus_A1=math.exp(-float(ev.fp@(1-ev.a_single))),invalid_cubic=True)
    stem.with_suffix('.screen.json').write_text(json.dumps(p,indent=2));print(json.dumps(dict(tag=tag,wall_seconds=time.monotonic()-t,**p)),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('selection',nargs='?');p.add_argument('--one');p.add_argument('--workers',type=int,default=3);a=p.parse_args()
    if a.one:one(a.one)
    else:
        tags=json.loads(Path(a.selection).read_text())
        def job(tag):
            with (V/'finalists'/f'{tag}.screen.log').open('w') as f:r=subprocess.run([str(ROOT/'.venv/bin/python'),str(V/'screen35.py'),'--one',tag],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
            print(tag,r.returncode,flush=True);return dict(tag=tag,returncode=r.returncode)
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:rs=list(ex.map(job,tags))
        (V/'structural.screen.receipt.json').write_text(json.dumps(rs,indent=2))
