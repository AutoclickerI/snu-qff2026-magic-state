"""Official multi-seed screen, with errors and uncertainty retained."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'work'))
from fast_check import check

def main():
    p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--shots',type=int,default=1000000);p.add_argument('--seeds',default='0,1000,2000');args=p.parse_args()
    stem=Path(args.stem);text=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits'];rows=[]
    out=stem.with_suffix('.mc.json')
    for seed in map(int,args.seeds.split(',')):
        start=time.perf_counter();r=check(text,data,shots=args.shots,seed=seed,procs=1)
        row=dict(seed=seed,shots=args.shots,seconds=time.perf_counter()-start,score=r.score,sem=r.sem,acceptance=r.acceptance,n_2q=r.n_2q,passed=r.passed,gates_ok=r.correct_ok,format_errors=r.format_errors,class_error=r.class_error,correctness_errors=r.correctness_errors)
        rows.append(row);out.write_text(json.dumps(dict(stem=str(stem),rows=rows,mean_loss=sum(x['score'] for x in rows)/len(rows) if all(x['score'] is not None for x in rows) else None),indent=2)+'\n');print(json.dumps(row),flush=True)
        if not r.correct_ok:break

if __name__=='__main__':main()
