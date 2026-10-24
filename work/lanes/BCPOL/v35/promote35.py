"""Local finalist gate: independent all-orders, judge, FAST, exact CLI, MC3."""
from core35 import *
from oracle_queue35 import capacity
from moments_batch import evaluate
import argparse,subprocess,concurrent.futures

def command(args,log,n):
    used=capacity(n);start=time.monotonic()
    with log.open('w') as f:r=subprocess.run([str(ROOT/'.venv/bin/python'),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
    return dict(returncode=r.returncode,seconds=time.monotonic()-start,cpu_before=used,command=list(map(str,args)))

def run(tag,mcprocs=4,exactprocs=2):
    s=V/'finalists'/tag;sha=hashlib.sha256(s.with_suffix('.qasm').read_bytes()).hexdigest();a=json.loads(s.with_suffix('.allorders.json').read_text());base=json.loads((V/'inputs/v35a.allorders.json').read_text());assert a['qasm_sha256']==sha
    out=dict(tag=tag,sha256=sha,allorders=a,below_base=a['loss']<base['loss']-1e-13,acceptance_budget_pass=a['acceptance']>=.5005)
    assert out['below_base'] and out['acceptance_budget_pass'],out
    out['gate_process']=command([V/'gate35.py',s],s.with_suffix('.gate.log'),1);assert out['gate_process']['returncode']==0
    g=json.loads(s.with_suffix('.gate.json').read_text());out['gate']=g
    if not(g['judge_pass'] and g['fast'] and g['seed0_acceptance_1e6']>=.5):
        out['status']='GATE_REJECTED';s.with_suffix('.promotion.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(tag=tag,status=out['status'],gate=g)),flush=True);return
    md=json.loads(s.with_suffix('.json').read_text());ev=exact2.Eval(s.with_suffix('.qasm').read_text(),md['data_qubits']);c1=float(ev.fp@ev.n_single)
    out['c1']=c1;args=[V/'exact_cli35.py',s.with_suffix('.qasm'),'--procs',exactprocs,'--top','6']
    if abs(c1)<1e-12:
        args.append('--third');out['moments']=evaluate(ev);s.with_suffix('.screen.json').write_text(json.dumps(out['moments'],indent=2))
    capacity(mcprocs+exactprocs)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fm=ex.submit(command,[V/'inputs/mc3.py',s,'--procs',mcprocs],s.with_suffix('.mc.log'),mcprocs)
        fe=ex.submit(command,args,s.with_suffix('.exact.log'),exactprocs)
        out['mc_process']=fm.result();out['exact_process']=fe.result()
    assert out['mc_process']['returncode']==out['exact_process']['returncode']==0
    log=s.with_suffix('.mc.log').read_text();out['mc_mean']=float(re.search(r' mean ([0-9.e+-]+)',log)[1]);out['mc_seeds']=[dict(seed=int(seed),loss=float(loss),acceptance=float(acc)) for seed,loss,acc in re.findall(r' (0|1000|2000) ([0-9.e+-]+) .*? acc ([0-9.]+)',log)]
    assert len(out['mc_seeds'])==3 and all(r['acceptance']>=.5 for r in out['mc_seeds']) and 'check True' in log
    if abs(c1)<1e-12:
        cli=float(re.search(r'1-F \(to 3rd order\) = ([0-9.e+-]+)',s.with_suffix('.exact.log').read_text())[1]);assert abs(cli-out['moments']['total'])<5.1e-11
    out['status']='VERIFIED_FINALIST';out['delta_loss']=a['loss']-base['loss'];s.with_suffix('.promotion.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(tag=tag,status=out['status'],loss=a['loss'],acceptance=a['acceptance'],mc_mean=out['mc_mean'])),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('tag');p.add_argument('--mc-procs',type=int,default=4);p.add_argument('--exact-procs',type=int,default=2);a=p.parse_args();run(a.tag,a.mc_procs,a.exact_procs)
