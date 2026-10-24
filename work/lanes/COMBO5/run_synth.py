"""Release-constrained BC2 clean-rule synthesis, with saved solver receipts."""
import argparse, json, math, os, subprocess, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def capacity(n=1):
    reported=int(subprocess.check_output(['nproc','--all'],text=True))
    cores=min(reported,len(os.sched_getaffinity(0)))
    load=float(Path('/proc/loadavg').read_text().split()[0])
    rows=[r.split() for r in subprocess.check_output(['ps','-eo','pid=,uid=,etimes=,stat=,pcpu='],text=True).splitlines()]
    rows=[r for r in rows if int(r[0])!=os.getpid() and int(r[2])>=2 and not r[3].startswith(('T','Z'))]
    usage=sum(float(r[4]) for r in rows if int(r[1])==os.getuid())/100
    total=sum(float(r[4]) for r in rows)/100
    receipt=dict(time=time.time(),cores=cores,nproc_all=reported,load=load,user_cpu=usage,total_cpu=total,requested=n)
    with (HERE/'capacity.jsonl').open('a') as f:f.write(json.dumps(receipt)+'\n')
    if load>cores or usage+n>cores*.75 or total+n>cores: raise RuntimeError(f'Capacity unavailable: {receipt}')
    return receipt

def workers(wanted):
    r=capacity(0)
    available=math.floor(min(.75*r['cores']-r['user_cpu']-1,r['cores']-r['total_cpu']-2))
    if available<1:raise RuntimeError(f'No worker capacity: {r}')
    n=min(wanted,available)
    capacity(n)
    return n

def main():
    import sat6
    ap=argparse.ArgumentParser();ap.add_argument('name');ap.add_argument('--depth',type=int,required=True)
    ap.add_argument('--late',type=int,required=True);ap.add_argument('--cap',type=int,default=100)
    ap.add_argument('--seed',type=int,default=0);ap.add_argument('--seconds',type=float,default=360)
    ap.add_argument('--free-pivots',action='store_true');ap.add_argument('--helpers',default='')
    ap.add_argument('--rule',default='clean');ap.add_argument('--split',default='')
    ap.add_argument('--initial');ap.add_argument('--free',type=int)
    a=ap.parse_args();cap=capacity()
    first={q:a.late for q in (4,6,13,19)}
    if a.split:first.update({int(q):int(t) for q,t in (x.split(':') for x in a.split.split(','))})
    base=json.loads(Path(a.initial).read_text()) if a.initial else json.loads((ROOT/'work/lanes/BC2/baseline_prep.json').read_text())
    base['ops']=(base['ops']+[[]]*a.depth)[:a.depth]
    helpers=[int(x) for x in a.helpers.split(',') if x]
    status,d,elapsed,iters,nfaults=sat6.solve(a.depth,helpers,a.seed,K=a.cap,rule=a.rule,seconds=a.seconds,
        initial=base,fix_pivots=not a.free_pivots,first_use=first,free_layers=list(range(a.free)) if a.free is not None else None)
    r=dict(vars(a),status=status,elapsed=elapsed,iters=iters,constraints=nfaults,first_use=first,capacity=cap)
    if d:
        r['cx']=sum(map(len,d['ops']))
        assert all(t>=first.get(q,0) for t,l in enumerate(d['ops']) for e in l for q in e)
        assert not sat6.ft.faults(d,rule=a.rule)
        (HERE/(a.name+'.prep.json')).write_text(json.dumps(d,indent=2))
    (HERE/(a.name+'.receipt.json')).write_text(json.dumps(r,indent=2))
    print(json.dumps(r),flush=True)

if __name__=='__main__':main()
