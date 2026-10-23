"""Fixed-v12-suffix scheduling search, artifacts confined to the PRE lane."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(HERE/'alap_cache')
os.chdir(HERE)
sys.path[:0]=[str(ROOT/'work'),str(ROOT/'work/lanes/EVAL'),str(ROOT/'upstream/snu-qff2026-problem')]
import argparse, copy, hashlib, json, math, multiprocessing as mp, random, re, time
import numpy as np
from qcirc import Circ
from exact2 import Eval, run
import tprep

BASE=json.loads((ROOT/'work/lanes/L5_precycle/combined_lns_0012.json').read_text())
OPS=[(k,tuple(qs),b) for k,qs,b in BASE['schedule']['ops']]
TIMES=BASE['schedule']['times']
NPRE=137
DATA=BASE['data_qubits']
BTEXT=(ROOT/'work/submissions/v12_L5lns12.qasm').read_text()
COMMENTS=[s for s in BTEXT.splitlines() if s.startswith('//')]

def emit(times):
    shift=min(times)
    c=Circ(36)
    c.nbits=22
    used=sorted({q for op in OPS for q in op[1]})
    for t in range(min(times),max(times)+1):
        for i,(k,qs,b) in enumerate(OPS):
            if times[i]!=t:continue
            if k=='cx':c.cx(*qs)
            elif k=='RX':c.rx(*qs)
            elif k=='R':c.reset(*qs)
            elif k in ('M','MX','MX_KEEP'):
                if k!='M':c.ops.append(f'h q[{qs[0]}];')
                c.ops.append(f'measure q[{qs[0]}] -> c[{b}];')
                c.sops.append(('MX' if k=='MX_KEEP' else k,qs,b))
            else:c.g(k[2:],*qs)
        if t<max(times):c.barrier(*used)
    text=c.rescheduled(lazy_init=True).text()
    for k,qs,b in OPS:
        if k=='MX_KEEP':
            old=f'measure q[{qs[0]}] -> c[{b}];'
            text=text.replace(old,old+f'\nh q[{qs[0]}];')
    return text+'\n'.join(COMMENTS)+'\n'

def commute(a,b):
    ka,qa,_=a;kb,qb,_=b
    if not set(qa)&set(qb):return True
    if ka==kb=='cx':return qa[0]!=qb[1] and qb[0]!=qa[1]
    if ka=='cx' and kb in ('g:t','g:tdg','g:s','g:sdg','g:z'):return qb[0]==qa[0]
    if kb=='cx' and ka in ('g:t','g:tdg','g:s','g:sdg','g:z'):return qa[0]==qb[0]
    return False

def dag(can_commute=True):
    pred=[set() for op in OPS];succ=[set() for op in OPS]
    for j,b in enumerate(OPS):
        for i,a in enumerate(OPS[:j]):
            if set(a[1])&set(b[1]) and not(can_commute and commute(a,b)):
                pred[j].add(i);succ[i].add(j)
    return pred,succ

def pack(seed=0,can_commute=True,jitter=3,reverse=True):
    pred,succ=dag(can_commute)
    if not reverse:
        # Generate a forward priority schedule, then right-align before fixed suffix.
        rng=random.Random(seed);priority=[len(succ[i])+rng.random()*jitter for i in range(NPRE)]
        out=list(TIMES);done=set();remaining=set(range(NPRE));t=-12
        while remaining:
            taken=set();selected=[]
            for i in sorted((i for i in remaining if pred[i]<=done),key=lambda i:-priority[i]):
                if not taken&set(OPS[i][1]):
                    selected.append(i);taken.update(OPS[i][1]);out[i]=t
            done.update(selected);remaining.difference_update(selected);t+=1
        delta=min(TIMES[j]-out[i]-1 for i in range(NPRE) for j in succ[i] if j>=NPRE)
        return [s+delta for s in out[:NPRE]]+TIMES[NPRE:]
    rng=random.Random(seed)
    out=list(TIMES);remaining=set(range(NPRE));done=set(range(NPRE,len(OPS)))
    occupied={(q,t) for op,t in zip(OPS[NPRE:],TIMES[NPRE:]) for q in op[1]}
    distance=[0]*NPRE
    for i in range(NPRE):distance[i]=1+max((distance[j] for j in pred[i]),default=0)
    priorities=[distance[i]+rng.random()*jitter for i in range(NPRE)]
    t=max(TIMES[:NPRE])
    while remaining:
        ready=sorted((i for i in remaining if succ[i]<=done and all(out[j]>t for j in succ[i])),key=lambda i:-priorities[i])
        selected=[]
        for i in ready:
            if any((q,t) in occupied for q in OPS[i][1]):continue
            out[i]=t;selected.append(i);occupied.update((q,t) for q in OPS[i][1])
        remaining.difference_update(selected);done.update(selected);t-=1
        assert t>-1000
    return out

def mutate(times,rng,pred,succ,lns=False):
    if lns:
        pivot=rng.randrange(NPRE);width=rng.randrange(1,8)
        chosen={i for i in range(NPRE) if abs(times[i]-times[pivot])<=width and rng.random()<.8}
        for i in list(chosen):
            chosen.update(j for j in pred[i] if OPS[j][0] in ('R','RX'))
        if not chosen:return None
    else:
        chosen={rng.randrange(NPRE)}
    low={i:max([times[j]+1 for j in pred[i]-chosen]+[min(times)-2]) for i in chosen}
    high={i:min([times[j]-1 for j in succ[i]-chosen]+[max(times[:NPRE])+1]) for i in chosen}
    occupied={(q,t) for j,(op,t) in enumerate(zip(OPS,times)) if j not in chosen for q in op[1]}
    out=list(times)
    if not lns:
        i=next(iter(chosen))
        choices=[t for t in range(max(low[i],times[i]-5),min(high[i],times[i]+5)+1) if t!=times[i] and not any((q,t) in occupied for q in OPS[i][1])]
        if not choices:return None
        out[i]=rng.choice(choices);return out
    remaining=set(chosen);done=set(range(len(OPS)))-chosen
    priorities={i:len(pred[i])*.05+rng.random()*8 for i in chosen}
    for t in range(max(high.values()),min(low.values())-1,-1):
        selected=[]
        for i in sorted((i for i in remaining if succ[i]<=done and low[i]<=t<=high[i] and all(out[j]>t for j in succ[i])),key=lambda i:-priorities[i]):
            if any((q,t) in occupied for q in OPS[i][1]):continue
            selected.append(i);out[i]=t;occupied.update((q,t) for q in OPS[i][1])
        remaining.difference_update(selected);done.update(selected)
        if any(low[i]>t-1 for i in remaining):return None
    return out if not remaining else None

def score(job):
    label,times,source=job
    start=time.monotonic();text=emit(times)
    dest=HERE/'alap_search';dest.mkdir(exist_ok=True)
    qp=dest/(label+'.qasm');jp=qp.with_suffix('.json')
    if jp.exists() and qp.read_text()==text:
        return label,times,json.loads(jp.read_text())
    qp.write_text(text)
    meta=dict(data_qubits=DATA,source=source,n_2q=115,schedule=dict(ops=OPS,times=times,npre=NPRE),pre_end_schedule=max(times[:NPRE])-min(times),suffix_relative=[t-min(times[NPRE:]) for t in times[NPRE:]])
    try:
        ev=Eval(text,DATA)
        # Precompute exactly the same Engine tables in vectorized batches. The
        # stock evaluator repeatedly computes identical XOR classes; run() and
        # all probability/pair accounting remain unchanged.
        keys=list({(sa^sb,da^db) for ga,(sa,da) in enumerate(ev.gkeys) for sb,db in ev.gkeys[ga:]})
        cache={}
        for lo in range(0,len(keys),128):
            part=keys[lo:lo+128]
            aa,nn=ev.e.batch_n([k[0] for k in part],[k[1] for k in part])
            for key,a,n in zip(part,aa,nn):cache[key]=(float(a),n if a>1e-18 else None)
        ev.e.ntable=lambda s,d:cache[s,d]
        r=run(ev,procs=1,keep_thr=math.inf,log=lambda *a:None)
        meta.update({k:float(r[k]) for k in ('loss','loss1','loss2','A1')})
        meta['exp_A1']=math.exp(-r['A1'])
    except Exception as e:meta.update(error=repr(e),loss=math.inf)
    meta['seconds']=time.monotonic()-start
    jp.write_text(json.dumps(meta,indent=2)+'\n')
    return label,times,meta

def main():
    p=argparse.ArgumentParser();p.add_argument('--greedy',type=int,default=64);p.add_argument('--steps',type=int,default=400);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    assert emit(TIMES)==BTEXT,'baseline QASM emission mismatch'
    seen={hashlib.sha256(BTEXT.encode()).hexdigest()};jobs=[]
    for rev in (True,False):
        for cm in (False,True):
            for seed in range(a.greedy):
                ts=pack(seed,cm,(0,3,10,30)[seed%4],rev)
                h=hashlib.sha256(emit(ts).encode()).hexdigest()
                if h in seen:continue
                seen.add(h);lab=f'alap_{"r" if rev else "f"}_c{int(cm)}_{seed:03d}'
                jobs.append((lab,ts,dict(method='greedy',reverse=rev,commuting=cm,seed=seed)))
    best=1.12195e-4;archive=[(best,TIMES,'v12')];rng=random.Random(62719);pred,succ=dag(True)
    summary=[]
    with mp.get_context('fork').Pool(a.workers) as pool:
        for label,ts,row in pool.imap_unordered(score,jobs):
            summary.append(dict(label=label,**{k:v for k,v in row.items() if k!='schedule'}))
            if row['loss']<math.inf:
                archive.append((row['loss'],ts,label));archive.sort(key=lambda x:x[0]);archive=archive[:12]
            if row['loss']<best:
                best=row['loss'];print(json.dumps(dict(BEST=label,loss=best,A1=row['A1'],stage='greedy')),flush=True)
        print(json.dumps(dict(greedy_done=len(jobs),best=archive[0][0],label=archive[0][2])),flush=True)
        count=0
        while count<a.steps:
            batch=[]
            while len(batch)<min(a.workers,a.steps-count):
                val,ts,parent=rng.choice(archive[:5])
                proposal=mutate(ts,rng,pred,succ,lns=rng.random()<.4)
                if proposal is None:continue
                h=hashlib.sha256(emit(proposal).encode()).hexdigest()
                if h in seen:continue
                seen.add(h);label=f'alap_lns_{count+len(batch):04d}'
                batch.append((label,proposal,dict(method='local/LNS',parent=parent)))
            for label,ts,row in pool.map(score,batch):
                summary.append(dict(label=label,**{k:v for k,v in row.items() if k!='schedule'}))
                if row['loss']<math.inf:
                    archive.append((row['loss'],ts,label));archive.sort(key=lambda x:x[0]);archive=archive[:12]
                if row['loss']<best:
                    best=row['loss'];print(json.dumps(dict(BEST=label,loss=best,A1=row['A1'],stage='lns')),flush=True)
            count+=len(batch)
            (HERE/'alap_progress.json').write_text(json.dumps(dict(done=count,greedy=len(jobs),best=[dict(loss=v,label=l) for v,t,l in archive]),indent=2)+'\n')
    (HERE/'alap_results.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(DONE=True,variants=len(summary),best=[dict(loss=v,label=l) for v,t,l in archive])),flush=True)

if __name__=='__main__':main()
