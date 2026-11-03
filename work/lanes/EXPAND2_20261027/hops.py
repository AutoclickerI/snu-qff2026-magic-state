"""Change coherent-transfer noise orientation; optionally retain source flag."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,copy,json,sys,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/lanes/PREFIX20261027'))
sys.path.insert(0,str(ROOT/'work/tools'))
import synth
from qcirc import parse,save
from qtools import price
BASE=ROOT/'work/lanes/PREFIX20261027/cand/final_phase_random_1'


def make(mask,retain=False,schedule='fixed'):
    us,ds=parse(BASE.with_suffix('.qasm').read_text())
    flag=next(u for u in us if u['b']==500);ft=flag['t'];ds=[list(d) for d in ds]
    for j,(a,d) in enumerate(zip(synth.A,synth.D)):
        if not mask>>j&1:continue
        init=next(u for u in us if u['k']=='R' and u['q']==(d,) and u['t']==ft+1)
        init['k']='RX'
        for u in us:
            if u['k']=='CX' and set(u['q'])=={a,d} and u['t'] in (ft+2,ft+3):u['q']=tuple(reversed(u['q']))
        herald=next((u for u in us if u['b']==502+j),None)
        if herald:herald['k']='MX'
    if retain:
        # q3 carries the already prepared + flag. The reversed transfer puts
        # its X eigenvalue on old source q2; read that source after the hop.
        j=synth.D.index(3);assert mask>>j&1
        old=next(u for u in us if u['b']==502+j)
        init=next(u for u in us if u['k']=='RX' and u['q']==(3,) and u['t']==ft+1)
        us.remove(flag);us.remove(init)
        ds=[sorted({old['b'] if b==500 else b for b in row}) for row in ds if row!=[old['b']]]
    if schedule!='fixed':
        last={q:-1 for q in range(36)}
        for u in sorted(us,key=lambda x:x['t']):
            t=max(last[q] for q in u['q'])+1;u['t']=t
            for q in u['q']:last[q]=t
        if schedule=='asap_jit':
            for u in us:
                if u['k'] not in ('R','RX'):continue
                uses=[v['t'] for v in us if v['t']>u['t'] and u['q'][0] in v['q']]
                if uses:u['t']=min(uses)-1
    stem=HERE/'cand'/f'hop_{mask}_keep{int(retain)}_{schedule}'
    return save(stem,us,ds,synth.D,dict(mask=mask,retain_flag=retain,schedule=schedule))


def one(job):
    mask,retain,schedule=job;stem=make(mask,retain,schedule)
    try:
        result=price(stem,processes=1)
        return dict(mask=mask,retain=retain,schedule=schedule,stem=str(stem.relative_to(ROOT)),**result)
    except Exception as e:return dict(mask=mask,retain=retain,schedule=schedule,error=str(e))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--all',action='store_true');a=p.parse_args()
    masks=list(range(128)) if a.all else sorted({0,127}|{1<<j for j in range(7)}|{127^(1<<j) for j in range(7)})
    jobs=[(m,False,'fixed') for m in masks]
    jobs += [(m,True,sch) for m in [16,127] for sch in ['fixed','asap','asap_jit']]
    jobs += [(m,False,sch) for m in [0,127] for sch in ['asap','asap_jit']]
    results=[]
    with ProcessPoolExecutor(max_workers=2) as pool:
        fs=[pool.submit(one,job) for job in jobs]
        for future in as_completed(fs):
            r=future.result();results.append(r)
            print(json.dumps({k:r[k] for k in ('mask','retain','schedule','loss','acceptance','error') if k in r}),flush=True)
            (HERE/'hop_results.json').write_text(json.dumps(results,indent=2)+'\n')
