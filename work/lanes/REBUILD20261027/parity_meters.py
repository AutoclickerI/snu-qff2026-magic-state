"""Synthesize local temporal Z-parity meters inside a phase network.

Only pre-existing idle slots are used. Meter qubits have deterministic zero
computational rows; the two sampled data rows must be equal, even when the
two contacts occur at different times. Each candidate then passes independent
raw verification and is ranked by the complete noisy evaluator.
"""
import argparse, copy, json, os, sys, time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
WORK=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(WORK/'tools'))
sys.path.insert(0,str(WORK/'lanes/T14'))
from qcirc import parse,emit,adjacent
from qtools import price,write_stem
from qtools.validity import raw_check
from record_contract import model,singles
HERE=Path(__file__).resolve().parent

def candidates(text):
    units,dets=parse(text)
    stop=min(u['t'] for u in units if u['k']=='MX')
    busy={(u['t'],q) for u in units for q in u['q']}
    by={t:[u for u in units if u['t']==t] for t in range(stop)}
    rows=[0]*36;nextvar=0;history={}
    for t in range(stop):
        history[t]=tuple(rows)
        for u in by[t]:
            q=u['q'][0]
            if u['k']=='RX':rows[q]=1<<nextvar;nextvar+=1
            elif u['k']=='R':rows[q]=0
            elif u['k']=='CX':rows[u['q'][1]]^=rows[q]
            elif u['k']=='M':
                if rows[q]:raise ValueError('Prefix contains a nondeterministic Z measurement')
            elif u['k'] not in ('T','TDG'):raise ValueError(u)
    specs=[]
    for t in range(1,stop-2):
        for h in range(36):
            if history[t-1][h] or any((s,h) in busy for s in range(t-1,t+3)):continue
            ns=[q for q in range(36) if adjacent(q,h)]
            for a in ns:
                if (t,a) in busy or not history[t][a]:continue
                for b in ns:
                    if (t+1,b) in busy or history[t+1][b]!=history[t][a]:continue
                    specs.append((t,h,a,b))
    return units,dets,specs

def run(stem,budget=48,rounds=3):
    stem=Path(stem);data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    lane=HERE/'meters';lane.mkdir(exist_ok=True)
    current=stem;best=price(current,1)
    ledger=lane/'results.jsonl'
    for iteration in range(rounds):
        text=current.with_suffix('.qasm').read_text();units,dets,specs=candidates(text)
        # Spread the fixed budget across time/geometry instead of taking only
        # early slots. Candidates that lower a nonzero c1 are also prioritized.
        print('iteration',iteration,'parent',str(current),'loss',best['loss'],'specs',len(specs),flush=True)
        if not specs:break
        nextbit=max(u['b'] for u in units if u['b'] is not None)+1
        screened=[]
        for i,spec in enumerate(specs):
            t,h,a,b=spec
            extra=[dict(k='R',q=(h,),t=t-1,b=None),dict(k='CX',q=(a,h),t=t,b=None),
                   dict(k='CX',q=(b,h),t=t+1,b=None),dict(k='M',q=(h,),t=t+2,b=nextbit)]
            newtext=emit(units+extra,dets+[[nextbit]])
            raw=raw_check(newtext,data)
            if not raw['ok']:
                raise AssertionError(('symbolically deterministic meter failed independent check',spec,raw))
            mm,_=model(newtext,data);single=singles(mm)
            screened.append((single['c1'],spec,newtext))
        minc=min(x[0] for x in screened)
        front=[x for x in screened if x[0]<=minc+1e-12]
        if len(front)>budget:
            front=[front[round(j*(len(front)-1)/(budget-1))] for j in range(budget)]
        winner=None
        for c1,spec,newtext in front:
            name='meter_'+str(iteration)+'_'+'_'.join(map(str,spec))
            out=write_stem(newtext,data,lane/'candidates',name)
            val=price(out,1)
            row=dict(parent=str(current),stem=str(out),spec=list(spec),c1=c1,**val)
            with ledger.open('a') as f:f.write(json.dumps(row)+'\n')
            print(name,val['loss'],val['acceptance'],flush=True)
            if val['acceptance']>=.5002 and val['loss']<best['loss']:
                if winner is None or val['loss']<winner[1]['loss']:winner=(out,val)
        if winner is None:break
        current,best=winner
        (lane/'best.json').write_text(json.dumps(dict(stem=str(current),**best),indent=2)+'\n')
    return current,best

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('stem')
    ap.add_argument('--budget',type=int,default=48);ap.add_argument('--rounds',type=int,default=3)
    a=ap.parse_args();st,r=run(a.stem,a.budget,a.rounds);print(st,json.dumps(r),flush=True)
