"""Whole-window retiming driven by the full cubic idle-channel derivative."""
import sys,math,json,time,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import directed as d
import numpy as np
from concurrent.futures import ProcessPoolExecutor,as_completed

def derivatives(c):
    ev=d.C.exact2.Eval(d.C.textof(c),c['meta']['data_qubits']);fp=ev.fp.copy();R=c['meta']['R'];slopes={};rows=[]
    for cid,ch in enumerate(ev.m.chans):
        if not ch['gap']:continue
        q,first,n=ch['gap']
        if first>=R:continue
        ix=np.flatnonzero(ev.fch==cid);eps=.1
        ev.fp=fp.copy();ev.fp[ix]*=1+eps;plus=d.mom.evaluate(ev)['total']
        ev.fp=fp.copy();ev.fp[ix]*=1-eps;minus=d.mom.evaluate(ev)['total']
        deriv=(plus-minus)/(2*eps*ch['prob'])
        dpdn=-.75*math.log(1-4*.001/3)*(1-4*.001/3)**n
        slope=deriv*dpdn
        seq=[i for i,u in enumerate(c['u']) if q in u.qs]
        ia=max((i for i in seq if c['t'][i]<first),key=lambda i:c['t'][i])
        ib=min((i for i in seq if c['t'][i]>=first+n),key=lambda i:c['t'][i],default=None)
        if ib is None:continue
        slopes[(q,ia,ib)]=slope;rows.append(dict(q=q,first=first,n=n,ia=ia,ib=ib,slope=slope))
    ev.fp=fp
    return slopes,rows

def propose(c,slopes,trust,focus,seed):
    c=d.C.clone(c);old=c['t'];R=c['meta']['R'];us=c['u'];rng=random.Random(seed)
    m=d.pywraplp.Solver.CreateSolver('GLOP');tv=[m.NumVar(t if t>=R else max(0,t-trust),t if t>=R else min(R-1,t+trust),f't{i}') for i,t in enumerate(old)]
    pred,_=d.C.S.build_dag(us)
    for j,ps in enumerate(pred):
        for i in ps:m.Add(tv[j]>=tv[i]+1)
    w=[0.]*len(us)
    for q in range(36):
        seq=[i for i,u in enumerate(us) if q in u.qs]
        for ia,ib in zip(seq,seq[1:]):
            if old[ia]>=R:continue
            weight=slopes.get((q,ia,ib),2e-8)
            if focus=='data' and q in d.C.D:weight*=2
            if focus=='A' and q in d.C.A:weight*=2
            if focus=='prefix' and old[ib]<32:weight*=2
            if focus=='jitter':weight*=rng.uniform(.6,1.5)
            w[ib]+=weight;w[ia]-=weight
    dev=[]
    for i,t in enumerate(old):
        v=m.NumVar(0,m.infinity(),f'd{i}');m.Add(v>=tv[i]-t);m.Add(v>=t-tv[i]);dev.append(v)
    m.Minimize(sum(a*b*1e8 for a,b in zip(w,tv))+.01*sum(dev));st=m.Solve()
    if st!=m.OPTIMAL:return None
    nt=[math.floor(v.solution_value()+1e-6) for v in tv]
    if nt==old:return None
    c['t']=nt;return d.normalize(c)

def main():
    out=d.H/'gradient_run';out.mkdir(exist_ok=True);seen=set();jobs=[];rng=random.Random(61)
    for idx in [0,3,2]:
        c=d.normalize(d.C.read(d.H/f'directed_seed{idx}'));print('derivatives',idx,flush=True)
        slopes,rows=derivatives(c);(out/f'derivatives_seed{idx}.json').write_text(json.dumps(rows,indent=2))
        for trust in [1,2,4,8]:
            for focus in ['all','data','A','prefix','jitter']:
                x=propose(c,slopes,trust,focus,rng.randrange(100000))
                if x is None:continue
                fp=d.digest(x)
                if fp in seen:continue
                seen.add(fp);p=out/f's{idx}_{trust}_{focus}_{fp}';d.save(x,p)
                jobs.append((str(p),f'directed_seed{idx}',[dict(family='cubic_gradient_window',trust=trust,focus=focus)]))
        print('generated',idx,len(jobs),flush=True)
    print('evaluating',len(jobs),flush=True);results=[]
    with ProcessPoolExecutor(2) as pool:
        for f in as_completed([pool.submit(d.score_job,j) for j in jobs]):
            r=f.result();results.append(r);(out/(r['stem']+'.score.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
    results.sort(key=lambda r:r.get('allorders',1));(out/'results.json').write_text(json.dumps(results,indent=2));print('DONE',results[0],flush=True)
if __name__=='__main__':main()
