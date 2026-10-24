"""Judge gate, exact third-order screen, and prescribed MC, all lane-local."""
import argparse, dataclasses, json, math, os, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'work/lanes/EVAL'),str(ROOT/'work')]
import exact2, fast_check, tprep
from run_synth import capacity,workers

def record(rep):
    return dict(dataclasses.asdict(rep),passed=rep.passed)

def score(stem,procs=2,mc=False):
    stem=Path(stem);out=stem.with_suffix('.score.json')
    r=json.loads(out.read_text()) if out.exists() else {}
    text=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    def save():out.write_text(json.dumps(r,indent=2))
    if 'check_1e6' not in r:
        capacity();r['check_1e6']=record(tprep.check(text,data,shots=10**6,seed=0));save()
    if not r['check_1e6']['passed']:print(stem,'JUDGE FAIL',r,flush=True);return r
    if 'exact' not in r:
        n=workers(procs);ev=exact2.Eval(text,data);x=exact2.run(ev,n,third=True)
        x3=exact2.third_order(ev,n)[0]+x['t3bc'] if abs(x['loss1'])<1e-12 else None
        r['exact']=dict(c1=x['loss1'],second=x['loss2'],third=x3,total=x['loss']+x3 if x3 is not None else None,exp_minus_A1=math.exp(-x['A1']))
        save();print(stem.name,'EXACT',r['exact'],flush=True)
    x=r['exact'];eligible=x['total'] is not None and x['total']<=1.03*8.41984e-5
    if mc and (eligible or abs(x['c1'])>=1e-12):
        r.setdefault('MC',{})
        for seed in (0,1000,2000):
            if str(seed) not in r['MC']:
                n=workers(procs);t=time.time();rep=fast_check.check(text,data,shots=10**8,seed=seed,procs=n)
                r['MC'][str(seed)]=dict(record(rep),seconds=time.time()-t);save()
                print(stem.name,'MC',seed,rep.score,rep.acceptance,flush=True)
        r['mean']=sum(x['score'] for x in r['MC'].values())/3;save()
    return r

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stems',nargs='+');ap.add_argument('--procs',type=int,default=2);ap.add_argument('--mc',action='store_true');a=ap.parse_args()
    for stem in a.stems:score(stem,a.procs,a.mc)
