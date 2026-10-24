"""Noiseless judge check, exact2 and optional exact third-order region ablations."""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
import sys
import json
import re
import time
import math
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
import xtim
xtim.cache_dir=HERE/'.xtim_cache'
sys.path[:0]=[str(ROOT/'work/lanes/EVAL')]
import model
import exact2
import fast_exact
import tprep
import tprep.qasm as tq
import importlib
tp=importlib.import_module('tprep.parse')
from tprep.noise import schedule, _repeated
if '--real' not in sys.argv:
    tq.adjacent=lambda a,b: True
    tp.adjacent=lambda a,b: True
orig=model.noise_blocks
_model=exact2.Model
def sparse_model(*args,**kw):
    m=_model(*args,**kw)
    m.faults=[f for f in m.faults if f['p']!=0]
    return m
exact2.Model=sparse_model

def ablation(meta,mode):
    ops=set(meta['round_ops'])
    # Native operation keys, and data/ancilla start of the check network.
    start={}
    for key in ops:
        t,qs=key.split(':')
        for q in map(int,qs.split(',')):
            start[q]=min(start.get(q,999),int(t))
    def nb(text,p,noise,first_order=False):
        prog,blocks=orig(text,p,noise,first_order)
        _,steps,gaps=schedule(text)
        by={}
        for i,q,t,n in gaps: by.setdefault(i,[]).append((q,t,n))
        for i,(ins,blk) in enumerate(zip(prog,blocks)):
            t=min((t for _,t in steps[i]),default=-1)
            key=f'{t}:'+','.join(map(str,sorted(ins.qubits)))
            on=key in ops
            keep=on if mode in ('round','data') else not on
            if mode=='data': keep=keep and bool(set(ins.qubits)&set(meta['data_qubits']))
            tail=len(blk)-len(by.get(i,[]))
            if not keep:
                for j in range(tail):
                    if blk[j]!=ins.text: blk[j]=re.sub(r'\([^)]*\)','(0)',blk[j],count=1)
            for j,(q,t,n) in enumerate(by.get(i,[]),tail):
                nround=sum(s>=start.get(q,999) for s in range(t,t+n))
                nk=nround if mode in ('round','data') else n-nround
                if mode=='data' and q not in meta['data_qubits']: nk=0
                blk[j]=f'DEPOLARIZE1({_repeated(p*noise.idle,nk,first_order)}) {q}'
        return prog,blocks
    return nb

def evaluate(stem,third=False,modes=('all','round','no_round'),procs=1):
    path=HERE/(stem+'.qasm'); text=path.read_text(); meta=json.loads(path.with_suffix('.json').read_text())
    out=dict(name=stem,third=third)
    check=tprep.check(text,meta['data_qubits'],p=0,shots=64)
    out['noiseless']=dict(format=check.format_ok,simulable=check.class_ok,correct=check.correct_ok,
                          errors=check.format_errors+check.correctness_errors, class_error=check.class_error,
                          acceptance=check.ideal_acceptance,frame=check.frame)
    if not check.correct_ok: return out
    for mode in modes:
        model.noise_blocks=orig if mode=='all' else ablation(meta,mode)
        try:
            st=time.monotonic(); ev=exact2.Eval(text,meta['data_qubits']); allowed=fast_exact.prepare(ev)
            r=exact2.run(ev,procs=procs,third=third)
            l3=fast_exact.third(ev,allowed)[0]+r['t3bc'] if third and abs(r['loss1'])<1e-12 else None
            out[mode]=dict(c1=r['loss1'],l2=r['loss2'],l3=l3,
                total=r['loss']+(l3 or 0), expA=math.exp(-r['A1']),A0=ev.e.A0,
                channels=len(ev.m.chans),groups=len(ev.gkeys),seconds=time.monotonic()-st)
        finally: model.noise_blocks=orig
    if 'all' in out and 'no_round' in out: out['marginal_round']=out['all']['total']-out['no_round']['total']
    return out

if __name__=='__main__':
    stem=sys.argv[1]; third='--third' in sys.argv
    modes=('all','round','no_round') if '--all-modes' in sys.argv else ('all','round')
    try: out=evaluate(stem,third,modes)
    except Exception as e:
        import traceback
        traceback.print_exc(); out=dict(name=stem,error=str(e))
    suffix='.third.json' if third else '.screen.json'
    (HERE/(stem+suffix)).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)
