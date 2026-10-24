"""Exact quadratic local search with every idle boundary represented."""
import os,sys,json,math,random,argparse,pickle,time,re
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import numpy as np
import schedule as S
from exact2 import Eval,run
from schedules import write,placement
from util import native_times

class Quadratic(S.Quadratic):
    def __init__(self,text,data,units,header,suffix):
        self.units=units;self.header=header;self.suffix=suffix
        # A spectator ID between every operation exposes all possible gaps.
        # q35 is unused in these circuits; its faults affect no observable.
        assert all(35 not in u.qs for u in units)
        wu=[]
        for u in units:wu.extend([u,S.Unit(['id q[35];'],[])])
        serial=S.emit(header,wu,list(range(len(wu))),suffix)
        self.ev=ev=Eval(serial,data)
        self.p0=np.array([c['prob']for c in ev.m.chans]);self.frac=ev.fp/self.p0[ev.fch];self.idle={}
        hh,rr,tt=S.qasm_ops(serial);uu=S.fold_units(rr);labels=S.native_qasm_index(serial)
        rawmap={k:i for i,u in enumerate(uu)for k in u.raw_indices}
        for c,ch in enumerate(ev.m.chans):
            if ch['gap']is None:continue
            q=int(ch['gap'][0])
            if q==35:continue
            lab=ev.m.labels[ev.m.prog[ch['ins']].line_no-1];raw=labels[int(re.match(r'instruction (\d+)',lab)[1])];wi=rawmap[raw]
            assert wi%2==0
            self.idle[wi//2,q]=c
        self._prepare()
        assert not self.no_gap and not self.no_tail,(self.no_gap,self.no_tail)
        self.K=self.K+self.K.T
        self.spectator=[i for i,c in enumerate(ev.m.chans)if c['qubits']==[35]]
        assert max(abs(self.alin[self.spectator]),default=0)<1e-12
        self.base_nonidle[self.spectator]=0

    def score(self,ts):
        p=self.probabilities(ts);a=float(p@self.alin)
        return dict(loss2=float(.5*p@self.K@p+(p*p)@self.same),loss1=float(p@self.nlin),A1=a,exp_minus_A1=math.exp(-a))

def search(q,start,seed,iterations,maxa,horizon):
    rng=random.Random(seed);pred,succ=S.build_dag(q.units);ts=list(start);cur=q.score(ts)
    best=(cur['loss2'],ts[:],cur)if cur['A1']<=maxa else None
    n=len(ts)
    for it in range(iterations):
        i=rng.randrange(n);lo=max((ts[j]+1 for j in pred[i]),default=0);hi=min((ts[j]-1 for j in succ[i]),default=horizon)
        if lo>=hi:continue
        nt=ts[:];nt[i]=rng.randint(lo,hi)
        if nt[i]==ts[i]:continue
        nt=S.compress(nt)
        v=q.score(nt)
        if cur['A1']>maxa:
            delta=v['A1']-cur['A1'];temp=.001*(1-it/iterations)**2
        else:
            if v['A1']>maxa:continue
            temp=cur['loss2']*.004*(1-it/iterations)**2;delta=v['loss2']-cur['loss2']
        if delta<=0 or rng.random()<math.exp(-delta/max(temp,1e-18)):ts,cur=nt,v
        if cur['A1']<=maxa and(best is None or cur['loss2']<best[0]):best=(cur['loss2'],ts[:],cur)
    if best is None:raise RuntimeError(f'No placement reached A1 <= {maxa}; final A1={cur["A1"]}')
    return best[1],best[2]

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--seeds',type=int,default=4);p.add_argument('--iterations',type=int,default=20000);p.add_argument('--max-a1',type=float,default=-math.log(.506));p.add_argument('--slack',type=int,default=0);a=p.parse_args()
    src=OUT/a.stem;text=src.with_suffix('.qasm').read_text();meta=json.loads(src.with_suffix('.json').read_text());h,r,t=S.qasm_ops(text);u=S.fold_units(r);ts=native_times(text,u)
    print('build',a.stem,flush=True);q=Quadratic(text,meta['data_qubits'],u,h,t);print('built',len(q.K),flush=True)
    # Cross-check three independently placed schedules against exact2.
    checks=[]
    for method in ('source','alap'):
        nt=ts if method=='source'else placement(u,method);pred=q.score(nt);txt=S.emit(h,u,nt,t);ev=Eval(txt,meta['data_qubits']);ex=run(ev,1,keep_thr=1)
        rel=abs(pred['loss2']-ex['loss2'])/ex['loss2'];assert rel<1e-9,(method,pred,ex['loss2'])
        checks.append(dict(method=method,predicted=pred,exact_second=ex['loss2'],relative_error=rel))
    (OUT/(a.stem+'.quadratic_checks.json')).write_text(json.dumps(checks,indent=2)+'\n');print('validated',checks,flush=True)
    for seed in range(a.seeds):
        start=ts if seed==0 else placement(u,'alap' if seed%2 else 'priority',seed,a.slack)
        nt,v=search(q,start,seed,a.iterations,a.max_a1,max(ts)+a.slack)
        stem=write(a.stem,f'{a.stem}_quad{seed}_s{a.slack}',nt,u,h,t,meta)
        stem.with_suffix('.quadratic.json').write_text(json.dumps(v,indent=2)+'\n');print(seed,v,flush=True)
