"""Reprice the complete acceptance-trade menu after each chosen trade, including interactions."""
import argparse,itertools,json,sys
from concurrent.futures import ThreadPoolExecutor
from price import price,ROOT,TAU
sys.path.insert(0,str(ROOT/'repairtools'))
from lib import read,save,remove_check,prep_options,delay_preps,BITRE

def main(base,tag,jobs,floor):
    current=base;r=price(ROOT/'builds'/current,1);accepted=[]
    for step in itertools.count():
        if r['acceptance']>=floor:break
        c=read(ROOT/'builds'/current);names=[];specs=[]
        bits=sorted({int(BITRE.findall(l)[0]) for l in c['tail'] if l.startswith('// DETECTOR') and len(BITRE.findall(l))==1})
        for b in bits:
            for mode in ['reset','omit','detector']:
                name=f'{tag}s{step}_{mode}{b}'
                try:
                    cc=remove_check(c,b,mode);save(cc,name,dict(family='acceptance buyer',base=current,bit=b,mode=mode))
                except (ValueError,AssertionError,KeyError):continue
                names.append(name);specs.append(dict(bit=b,mode=mode))
        for j,edit in enumerate(prep_options(c)):
            name=f'{tag}s{step}_delay{j}'
            try:save(delay_preps(c,[edit]),name,dict(family='acceptance buyer',base=current,prep_delay=edit))
            except (ValueError,AssertionError,KeyError):continue
            names.append(name);specs.append(dict(prep_delay=edit))
        print(json.dumps(dict(step=step,base=current,loss=r['loss'],acceptance=r['acceptance'],menu=len(names))),flush=True)
        with ThreadPoolExecutor(jobs) as pool:results=list(pool.map(lambda n:price(ROOT/'builds'/n,1),names))
        choices=[];need=floor-r['acceptance']
        for n,sp,x in zip(names,specs,results):
            if not x or x['acceptance']<=r['acceptance']+1e-8:continue
            delta=x['J_tau']-r['J_tau'];da=x['acceptance']-r['acceptance']
            projected=r['J_tau']+delta*max(1,need/da)
            choices.append((projected,x['J_tau'],n,sp,x))
        if not choices:raise RuntimeError('No acceptance-increasing trade')
        _,_,current,sp,r=min(choices);accepted.append(dict(path=current,trade=sp,loss=r['loss'],acceptance=r['acceptance']))
        print(json.dumps(dict(chosen=current,trade=sp,loss=r['loss'],acceptance=r['acceptance'],J_tau=r['J_tau'])),flush=True)
    out=dict(base=base,best=current,loss=r['loss'],acceptance=r['acceptance'],J_tau=r['J_tau'],trades=accepted,scope='full singleton-check/prep-delay menu repriced at every joint step')
    (ROOT/'logs'/f'{tag}.buy_result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('base');ap.add_argument('tag');ap.add_argument('--jobs',type=int,default=22);ap.add_argument('--floor',type=float,default=0.5002);a=ap.parse_args();main(a.base,a.tag,a.jobs,a.floor)
