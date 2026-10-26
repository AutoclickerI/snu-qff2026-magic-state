"""Full INTEG2 echo/pair/guard/trade passes, choosing the best feasible exact-J edit each pass."""
import argparse,itertools,json,shutil,subprocess,sys,os
from concurrent.futures import ThreadPoolExecutor
from price import price,ROOT,TAU

ap=argparse.ArgumentParser();ap.add_argument('base');ap.add_argument('tag');ap.add_argument('--jobs',type=int,default=22);ap.add_argument('--floor',type=float,default=.5002);ap.add_argument('--fast',action='store_true');a=ap.parse_args()
current=a.base;r=price(ROOT/'builds'/current,1);chain=[]
for step in itertools.count():
    if os.environ.get('GLOBAL_AUTOBASIS')=='1':
        from autobasis import ensure
        ensure(current)
    script=ROOT/'repairtools/singles.py'
    with (ROOT/'logs'/f'{a.tag}_{step}.menu.txt').open('w') as f:subprocess.run([sys.executable,str(script),current],stdout=f,stderr=subprocess.STDOUT,check=True)
    names=(ROOT/'repairtools'/f'singles_{current}.list').read_text().split()
    print(json.dumps(dict(step=step,base=current,menu=len(names),loss=r['loss'],acceptance=r['acceptance'])),flush=True)
    jobs=int((ROOT/os.environ['GLOBAL_JOBS_FILE']).read_text()) if os.environ.get('GLOBAL_JOBS_FILE') else a.jobs
    assert 1<=jobs<=22
    with ThreadPoolExecutor(jobs) as pool:values=list(pool.map(lambda n:price(ROOT/'builds'/n,1),names))
    good=sorted([(v['J_tau'],n,v) for n,v in zip(names,values) if v and v['acceptance']>=a.floor and v['J_tau']<r['J_tau']-1e-13])
    if a.fast:
        import general_atoms
        screened=[]
        for item in good:
            name=item[1];screen=general_atoms.analyze(ROOT/'builds'/name)
            (ROOT/'logs'/(name+'.speed_screen.json')).write_text(json.dumps(screen,indent=2)+'\n')
            if screen['prediction']=='FAST':screened.append(item);break
        good=screened
    if not good:break
    _,selected,r=good[0];alias=f'{a.tag}_{step:03d}'
    for ext in ['.qasm','.json']:shutil.copy2((ROOT/'builds'/selected).with_suffix(ext),(ROOT/'builds'/alias).with_suffix(ext))
    chain.append(dict(before=current,selected=selected,alias=alias,loss=r['loss'],acceptance=r['acceptance'],J_tau=r['J_tau']))
    current=alias;print(json.dumps(chain[-1]),flush=True)
out=dict(base=a.base,best=current,loss=r['loss'],acceptance=r['acceptance'],J_tau=r['J_tau'],chain=chain)
(ROOT/'logs'/f'{a.tag}.integ_result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
