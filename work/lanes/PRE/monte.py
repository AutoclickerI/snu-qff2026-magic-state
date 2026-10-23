from common import *
import fast_check, argparse, statistics, time
p=argparse.ArgumentParser();p.add_argument('names',nargs='+');p.add_argument('--procs',type=int,default=8);a=p.parse_args()
for name in a.names:
    meta=json.loads((HERE/f'{name}.json').read_text());text=(HERE/f'{name}.qasm').read_text();rows=[]
    for seed in (0,1000,2000):
        start=time.monotonic()
        rep=fast_check.check(text,meta['data_qubits'],shots=100000000,seed=seed,procs=a.procs)
        row=dict(seed=seed,shots=100000000,passed=rep.passed,score=rep.score,sem=rep.sem,acceptance=rep.acceptance,
                 format=rep.format_ok,class_ok=rep.class_ok,correctness=rep.correct_ok,acceptance_ok=rep.acceptance_ok,
                 seconds=time.monotonic()-start,report=str(rep))
        rows.append(row);out=dict(name=name,rows=rows,mean=statistics.mean(r['score'] for r in rows),
                                 mean_sem=math.sqrt(sum(r['sem']**2 for r in rows))/len(rows))
        (HERE/f'{name}.mc.json').write_text(json.dumps(out,indent=2)+'\n')
        print(json.dumps({k:v for k,v in row.items() if k!='report'}),flush=True)
        assert rep.passed,str(rep)
