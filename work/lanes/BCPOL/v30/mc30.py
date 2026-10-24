"""Run the two MC cross-checks and the final clean-resource search after pricing exits."""
from pathlib import Path
import os,sys,json,subprocess,ctypes,select,concurrent.futures,time
V=Path(__file__).resolve().parent;H=V.parent;ROOT=H.parents[2]
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',XTIM_TWIRL_CACHE_DIR=str(H/'.xtim_cache'))
libc=ctypes.CDLL(None,use_errno=True)

def cpu():
    rows=[r.split() for r in subprocess.check_output(['ps','-u',str(os.getuid()),'-o','pid=,pcpu=,stat='],text=True).splitlines()]
    return sum(float(r[1]) for r in rows if 'T' not in r[2])/100,rows

while True:
    used,rows=cpu()
    if used+4<=.75*os.cpu_count() and os.getloadavg()[0]+8<os.cpu_count():break
    fds=[libc.syscall(434,int(r[0]),0) for r in rows if float(r[1])>15 and 'T' not in r[2] and int(r[0])!=os.getpid()];fds=[f for f in fds if f>=0];assert fds
    # Recheck after subscribing so exits during registration cannot be missed.
    used,_=cpu()
    if used+4>.75*os.cpu_count():select.select(fds,[],[])
    for fd in fds:os.close(fd)
print(json.dumps(dict(capacity=used,load=os.getloadavg())),flush=True)

def execute(args,log):
    with log.open('w') as f:r=subprocess.run([str(ROOT/'.venv/bin/python'),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
    assert r.returncode==0,(args,r.returncode);return r.returncode

def mc(item):
    tag,n=item;s=V/'finalists'/tag
    execute([V/'gate30.py',s],s.with_suffix('.mc_gate.log'));g=json.loads(s.with_suffix('.gate.json').read_text());assert g['judge_pass'] and g['fast']
    execute([V/'inputs/mc3.py',s,'--procs',n],s.with_suffix('.mc.log'));return dict(tag=tag,mc=True,procs=n)

def clean():
    execute([V/'search30.py','helper','0','--seed','1510','--depth','10','--cap','70','--seconds','600'],V/'clean_d10.log')
    p=V/'runs/helper_0_s1510.best.json'
    return dict(tag=json.loads(p.read_text())['tag'],priced=False) if p.exists() else dict(tag='clean_d10',no_witness=True)

def sequence():
    return [mc(('feedback_1401_02324',3)),mc(('bell4_0_s1201_00010',3))]

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
    fs=[ex.submit(sequence),ex.submit(clean)];out=[f.result() for f in fs]
if out[1].get('priced') is False:
    tag=out[1]['tag'];execute([V/'price30.py','--one',tag,'--exact-procs','4'],V/'clean_d10.price.log')
    s=V/'finalists'/tag;r=json.loads(s.with_suffix('.verified30.json').read_text());out[1]['priced']=True
    reference=json.loads((V/'finalists/feedback_1401_02324.allorders.json').read_text())['loss']
    if r['allorders']['loss']<reference-1e-13 and r['gates']['judge_pass'] and r['gates']['fast']:out.append(mc((tag,4)))
(V/'mc_clean.final.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
