#!/home/jihoon/competitions/quantumn/.venv/bin/python
import json, math, statistics, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'work'))
from fast_check import check

def run(path, procs=16):
    p=Path(path); text=p.read_text(); meta=json.loads(p.with_suffix('.json').read_text()); rows=[]
    for seed in (0,1000,2000):
        r=check(text,meta['data_qubits'],shots=10**8,seed=seed,procs=procs)
        assert r.passed, r
        rows.append(dict(seed=seed,score=r.score,sem=r.sem,acceptance=r.acceptance,passed=r.passed,report=str(r)))
    out=dict(path=str(p),rows=rows,mean=statistics.mean(x['score'] for x in rows),mean_sem=statistics.stdev([x['score'] for x in rows])/math.sqrt(3),seed0_score=rows[0]['score'])
    p.with_suffix('.mc.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out),flush=True)
    return out

if __name__=='__main__':
    args=sys.argv[1:]; procs=16
    if '--procs' in args:
        k=args.index('--procs'); procs=int(args[k+1]); args=args[:k]+args[k+2:]
    for x in args: run(x,procs)
