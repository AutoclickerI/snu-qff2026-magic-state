"""Full ACCBUY slot-menu pass, followed by exact-price joint integration; content-addressed caching."""
import argparse,json,os,subprocess,sys,itertools,shutil
from concurrent.futures import ThreadPoolExecutor
from price import price,ROOT,TAU

def main(base,tag,rounds,jobs,floor,single_best=False):
    r=price(ROOT/'builds'/base,1);current=base
    for rnd in (range(rounds) if rounds else itertools.count()):
        names=[]
        for script,suffix in [('prerole2.py','p'),('kstate.py','k')]:
            pre=f'{tag}r{rnd}{suffix}'
            cmd=[sys.executable,str(ROOT/'repairtools'/script),str(ROOT/'builds'/current),pre]
            with (ROOT/'logs'/f'{pre}.menu.txt').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
            names+=(ROOT/'builds'/f'{pre}.list').read_text().split()
        print(json.dumps(dict(round=rnd,base=current,menu=len(names))),flush=True)
        with ThreadPoolExecutor(jobs) as pool:res=list(pool.map(lambda n:price(ROOT/'builds'/n,1),names))
        good=sorted([(x['J_tau'],n,x) for n,x in zip(names,res) if x and x['acceptance']>=floor and x['J_tau']<r['J_tau']-5e-11])
        if single_best:
            if not good:break
            _,selected,r=good[0];alias=f'{tag}r{rnd}best'
            for ext in ['.qasm','.json']:shutil.copy2((ROOT/'builds'/selected).with_suffix(ext),(ROOT/'builds'/alias).with_suffix(ext))
            current=alias;print(json.dumps(dict(added=selected,current=current,loss=r['loss'],acceptance=r['acceptance'],J_tau=r['J_tau'])),flush=True)
            if r['loss']<TAU-5e-7:break
            continue
        accepted=[];start=current;startL=r['loss']
        for j,(loss,n,single) in enumerate(good):
            out=f'{tag}r{rnd}j{j}'
            proc=subprocess.run([sys.executable,str(ROOT/'repairtools/jslot.py'),str(ROOT/'builds'/start),out]+accepted+[n],capture_output=True,text=True)
            (ROOT/'logs'/f'{out}.build.txt').write_text(proc.stdout+proc.stderr)
            if proc.returncode:continue
            value=price(ROOT/'builds'/out,1)
            if value and value['acceptance']>=floor and value['J_tau']<r['J_tau']-5e-11:
                accepted.append(n);current=out;r=value
                print(json.dumps(dict(added=n,current=current,loss=r['loss'],acceptance=r['acceptance'])),flush=True)
        if not accepted:break
    result=dict(base=base,best=current,loss=r['loss'],acceptance=r['acceptance'],J_tau=r['J_tau'],scope='all generated pre/post-role and known-state slots; exact singles then exact joint additions')
    (ROOT/'logs'/f'{tag}.greedy_result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('base');ap.add_argument('tag');ap.add_argument('--rounds',type=int,default=0);ap.add_argument('--jobs',type=int,default=22);ap.add_argument('--floor',type=float,default=0.5002);ap.add_argument('--single-best',action='store_true');a=ap.parse_args();main(a.base,a.tag,a.rounds,a.jobs,a.floor,a.single_best)
