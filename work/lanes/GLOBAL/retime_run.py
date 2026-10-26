"""Price order-preserving native operation retiming; all edits keep the existing depth."""
import argparse,itertools,json,shutil,sys,os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from price import price,ROOT,TAU
sys.path.insert(0,str(Path(__file__).resolve().parent/'repairtools'))
from lib import read,unit,copy,C,save,depth

ap=argparse.ArgumentParser();ap.add_argument('base');ap.add_argument('tag');ap.add_argument('--jobs',type=int,default=6);ap.add_argument('--fast',action='store_true');a=ap.parse_args()
current=a.base;r=price(C/current,1);chain=[]
for step in itertools.count():
    if os.environ.get('GLOBAL_AUTOBASIS')=='1':
        from autobasis import ensure
        ensure(current)
    c=read(C/current);T=depth(c);names=[]
    for i,o in enumerate(c['ops']):
        u=unit(o);qs=set(u.qs);old=o['t']
        others=[v['t'] for j,v in enumerate(c['ops']) if j!=i and qs.intersection(unit(v).qs)]
        lo=1+max([t for t in others if t<old],default=-1)
        hi=min([t for t in others if t>old],default=T)-1
        for t in range(lo,hi+1):
            if t==old:continue
            cc=copy.deepcopy(c);cc['ops'][i]['t']=t
            name=f'{a.tag}_{step:03d}_o{i}_t{t}'
            try:save(cc,name,dict(family='order-preserving retime',base=current,operation=i,gate=u.name,qubits=u.qs,old=old,new=t))
            except (ValueError,AssertionError):continue
            names.append(name)
    print(json.dumps(dict(step=step,base=current,menu=len(names),loss=r['loss'],acceptance=r['acceptance'])),flush=True)
    jobs=int((ROOT/os.environ['GLOBAL_JOBS_FILE']).read_text()) if os.environ.get('GLOBAL_JOBS_FILE') else a.jobs
    assert 1<=jobs<=22
    with ThreadPoolExecutor(jobs) as pool:values=list(pool.map(lambda n:price(C/n,1),names))
    good=sorted([(v['J_tau'],n,v) for n,v in zip(names,values) if v and v['acceptance']>=.5002 and v['J_tau']<r['J_tau']-1e-13])
    if a.fast:
        import general_atoms
        screened=[]
        for item in good:
            name=item[1];screen=general_atoms.analyze(C/name)
            (ROOT/'logs'/(name+'.speed_screen.json')).write_text(json.dumps(screen,indent=2)+'\n')
            if screen['prediction']=='FAST':screened.append(item);break
        good=screened
    if not good:break
    _,selected,r=good[0];alias=f'{a.tag}_{step:03d}'
    for ext in ['.qasm','.json']:shutil.copy2((C/selected).with_suffix(ext),(C/alias).with_suffix(ext))
    chain.append(dict(before=current,selected=selected,alias=alias,loss=r['loss'],acceptance=r['acceptance'],J_tau=r['J_tau']))
    current=alias;print(json.dumps(chain[-1]),flush=True)
out=dict(base=a.base,best=current,loss=r['loss'],acceptance=r['acceptance'],J_tau=r['J_tau'],chain=chain)
(ROOT/'logs'/f'{a.tag}.retime_result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
