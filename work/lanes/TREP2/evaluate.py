"""Exact CLI receipt, native schedule metadata, optional judge and MC receipt."""
import os, sys, json, re, argparse, subprocess, hashlib
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times

def evaluate(stem, procs=1, mc=False, check=False, reference=False):
    stem=Path(stem); stem=stem if stem.is_absolute() else OUT/stem
    text=stem.with_suffix('.qasm').read_text(); meta=json.loads(stem.with_suffix('.json').read_text())
    h,r,t=S.qasm_ops(text);u=S.fold_units(r);ts=native_times(text,u)
    data=meta['data_qubits'];aa=[1,14,8,9,2,16,15];bb=[6,26,13,11,4,23,27];cc=[12,25,19,17,5,29,28]
    def lastgate(c,v):return max(t for x,t in zip(u,ts)if x.lines==[f'cx q[{c}],q[{v}];'])
    first=[lastgate(c,v)for c,v in list(zip(data,aa))+list(zip(bb,cc))];second=[lastgate(c,v)for c,v in zip(bb,data)]
    row=dict(name=stem.name,R=min(first),round_first_range=[min(first),max(first)],B_data_range=[min(second),max(second)],CX=sum(x.name=='CX' for x in u),depth=max(ts)+1,sha256=hashlib.sha256(text.encode()).hexdigest())
    evaluator=ROOT/'work/lanes/EVAL/exact2.py' if reference else OUT/'fast_third.py'
    row['evaluator']=str(evaluator.relative_to(ROOT))
    cmd=[sys.executable,str(evaluator),str(stem.with_suffix('.qasm')),'--third','--procs',str(procs),'--top','0']
    with stem.with_suffix('.exact.log').open('w') as log: subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,cwd=OUT)
    log=stem.with_suffix('.exact.log').read_text()
    for key,pat in [('c1',r'c1 p = (\S+)'),('second',r'second order: (\S+)'),('third',r'third order: (\S+)'),('total',r'1-F \(to 3rd order\) = (\S+)'),('exp_minus_A1',r'exp\(-A1\) = (\S+)')]:
        m=re.search(pat,log)
        if m:row[key]=float(m[1])
    if check or mc:
        import tprep
        res=tprep.check(text,meta['data_qubits'],shots=10**6,seed=0)
        row['check']={'passed':res.passed,'acceptance':res.acceptance,'repr':str(res)}
    stem.with_suffix('.result.json').write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps(row),flush=True)
    if mc:
        with stem.with_suffix('.mc.log').open('w') as log:subprocess.run([sys.executable,str(OUT/'inputs/mc3.py'),str(stem),'--procs',str(procs)],stdout=log,stderr=subprocess.STDOUT,check=True,cwd=OUT)
    return row

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--procs',type=int,default=1);p.add_argument('--mc',action='store_true');p.add_argument('--check',action='store_true');p.add_argument('--reference',action='store_true');a=p.parse_args()
    for stem in a.stems:evaluate(stem,a.procs,a.mc,a.check,a.reference)
