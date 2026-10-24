"""Finite recipe sweep, process-exit driven. Every result gets Stim + 1e6 check."""
import os,sys,json,itertools,subprocess,concurrent.futures,time,argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=3);ap.add_argument('--procs',type=int,default=8);ap.add_argument('--phase',default='single');a=ap.parse_args()
assert a.workers*a.procs<=24
jobs=[]
contexts=[('sep',33),('v22',45)]
if a.phase=='single':
    for pre,R in contexts:
        jobs.append((f'{pre}_ref',[],R,pre))
        for kind in ['direct','seq','cat','flag','redundant','hybrid1','hybrid2']:
            for block in 'ABC':
                for order in itertools.permutations(range(3)):
                    o=''.join(map(str,order));name=f'{pre}_{block}_{kind}_{o}'
                    jobs.append((name,['--blocks',block,'--kind',kind,'--order',o],R,pre))
elif a.phase=='combined':
    for pre,R in contexts:
        for kind in ['direct','seq','cat','flag','redundant','hybrid1','hybrid2']:
            for blocks in ['AB','AC','BC','ABC']:
                for order in itertools.permutations(range(3)):
                    o=''.join(map(str,order));name=f'{pre}_{blocks}_{kind}_{o}'
                    jobs.append((name,['--blocks',blocks,'--kind',kind,'--order',o],R,pre))
elif a.phase=='extended':
    for pre,R in contexts:
        for kind in ['cat13','cat3','cat4','catred','cat13red']:
            for blocks in ['A','B','C','BC']:
                for order in itertools.permutations(range(3)):
                    o=''.join(map(str,order));name=f'{pre}_{blocks}_{kind}_{o}'
                    jobs.append((name,['--blocks',blocks,'--kind',kind,'--order',o],R,pre))
        for blocks in ['A','B','C','BC','ABC']:
            for order in itertools.permutations(range(4)):
                if order[-1]==3:continue
                o=''.join(map(str,order));name=f'{pre}_{blocks}_redundant_{o}'
                jobs.append((name,['--blocks',blocks,'--kind','redundant','--order',o],R,pre))
        for order in itertools.permutations(range(3)):
            o=''.join(map(str,order));name=f'{pre}_ABC_flag_redundant_{o}'
            jobs.append((name,['--blocks','ABC','--kind','flag,redundant,redundant','--order',o],R,pre))
        for blocks in ['A','B','C','AB','AC','BC','ABC']:
            name=f'{pre}_{blocks}_hybrid2t_012'
            jobs.append((name,['--blocks',blocks,'--kind','hybrid2t'],R,pre))
elif a.phase=='cat_orders':
    for pre,R in contexts:
        for kind in ['catred','cat13red']:
            for blocks in ['A','B','C','BC']:
                for order in itertools.permutations(range(4)):
                    if order[-1]==3:continue
                    o=''.join(map(str,order));name=f'{pre}_{blocks}_{kind}_{o}'
                    jobs.append((name,['--blocks',blocks,'--kind',kind,'--order',o],R,pre))
        for kind in ['cat3red','cat3reusered']:
            for blocks in ['B','C','BC']:
                for order in itertools.permutations(range(4)):
                    o=''.join(map(str,order));name=f'{pre}_{blocks}_{kind}_{o}'
                    jobs.append((name,['--blocks',blocks,'--kind',kind,'--order',o],R,pre))
elif a.phase in ('spine','finish'):
    for pre,R in contexts:
        for blocks in ['B','C','BC']:
            for order in itertools.permutations(range(4)):
                o=''.join(map(str,order));name=f'{pre}_{blocks}_cat3spinered_{o}'
                jobs.append((name,['--blocks',blocks,'--kind','cat3spinered','--order',o],R,pre))
elif a.phase=='cover':
    for pre,R in [('sep',33),('v22h',45)]:
        for blocks in ['AB','AC']:
            for order in itertools.permutations(range(4)):
                if order[-1]==3:continue
                o=''.join(map(str,order));name=f'{pre}_{blocks}_redundant_{o}'
                jobs.append((name,['--blocks',blocks,'--kind','redundant','--order',o],R,pre))
if a.phase in ('pair_red','finish'):
    for pre,R in contexts:
        for kind in ['redundant','cat13red']:
            for mask in [3,5,6]:
                for order in itertools.permutations(range(4)):
                    o=''.join(map(str,order));name=f'{pre}_BC_{kind}_m{mask}_{o}'
                    jobs.append((name,['--blocks','BC','--kind',kind,'--red-mask',str(mask),'--order',o],R,pre))
def run(job):
    name,extra,R,pre=job;stem=HERE/'runs'/name
    res=stem.with_suffix('.result.json')
    if res.exists():return dict(name=name,cached=True)
    with stem.with_suffix('.log').open('w') as log:
        cmd=[sys.executable,str(HERE/'mbp.py'),'runs/'+name,'--R',str(R),'--pre',pre,'--procs',str(a.procs)]+extra
        # Resource check before every launch; pool size caps this lane's workers.
        load=os.getloadavg()[0];cores=os.cpu_count();assert load<cores,(load,cores)
        p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'))
        rc=p.wait()
    row=dict(name=name,exit=rc)
    if rc==0:
        r=json.loads(res.read_text());row.update({k:r[k] for k in ('c1','second','third','total','expA1','check','seconds')})
    print(json.dumps(row),flush=True)
    return row
(HERE/'runs').mkdir(exist_ok=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:rows=list(ex.map(run,jobs))
(HERE/f'{a.phase}.receipt.json').write_text(json.dumps(rows,indent=2)+'\n')
