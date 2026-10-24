#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Screen one prep in v18: Stim/FT, native schedule, judge, and exact2."""
import argparse,json,os,subprocess,sys
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def run(cmd,log=None):
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,env=os.environ.copy())
    if log:Path(log).write_text(p.stdout+'\n'+p.stderr)
    return p
def main():
    ap=argparse.ArgumentParser();ap.add_argument('prep');ap.add_argument('--tag');ap.add_argument('--workers',type=int,default=8);a=ap.parse_args()
    prep=Path(a.prep);tag=a.tag or prep.stem;out=HERE/tag
    v=run([str(ROOT/'.venv/bin/python'),str(HERE/'verify_prep.py'),str(prep),'--rule','clean'],HERE/(tag+'.prep_verify.log'))
    if v.returncode:
        print(v.stdout);raise SystemExit(v.returncode)
    s=run([str(ROOT/'.venv/bin/python'),str(HERE/'screen_prep.py'),str(prep),str(out),'--workers',str(a.workers)],HERE/(tag+'.screen.log'))
    if s.returncode:print(s.stdout,s.stderr);raise SystemExit(s.returncode)
    # Generate all first-use-measure variants, then score each with the judge.
    md=HERE/(tag+'_minit');md.mkdir(exist_ok=True)
    run([str(ROOT/'.venv/bin/python'),str(ROOT/'work/lanes/BC2/minit.py'),str(out),str(md)],HERE/(tag+'.minit.log'))
    rows=[]
    for q in sorted(md.glob('*.qasm')):
        d=json.loads(q.with_suffix('.json').read_text())
        # use tprep.check through a short helper so the result is JSON-safe
        chk=run([str(ROOT/'.venv/bin/python'),str(ROOT/'work/lanes/BCSYN/judge_check.py'),str(q),str(q.with_suffix('.json'))])
        (HERE/(q.stem+'.check.log')).write_text(chk.stdout+'\n'+chk.stderr)
        if chk.returncode:continue
        rows.append(json.loads(chk.stdout.strip().splitlines()[-1]))
        if rows[-1].get('passed'):
            ex=run([str(ROOT/'.venv/bin/python'),str(ROOT/'work/lanes/EVAL/exact2.py'),str(q),'--third','--procs',str(a.workers)],HERE/(q.stem+'.exact.log'))
    (HERE/(tag+'.candidates.json')).write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2),flush=True)
if __name__=='__main__':main()
