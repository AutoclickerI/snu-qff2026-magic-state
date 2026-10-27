"""Native two-contact Z-parity guards for long, unchanged source rows.

A zero helper records the same computational parity at two different times.
Its final zero read rejects intervening X/Y faults. On the guarded polynomial,
the helper's Z backaction is a safe T-axis error when both contacts use one of
the15 target rows. Helpers occupy cells not used by the active source, and their
entire storage interval precedes the original resource/data initialization.
"""
import os,sys,json,copy
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import flag6 as f6
from qcirc import parse,emit,adjacent
from qtools import write_stem,price
from qtools.validity import raw_check
from search_phase import singles
H=Path(__file__).resolve().parent;CELLS=f6.CELLS

def specs(stem):
    stem=Path(stem);meta=json.loads(stem.with_suffix('.json').read_text());units,dets=parse(stem.with_suffix('.qasm').read_text())
    stop=min(u['t'] for u in units if u['b']==500)
    busy={(u['t'],q) for u in units for q in u['q']}
    first={q:min([u['t'] for u in units if q in u['q']]+[999]) for q in range(36)}
    seed=dict(zip(CELLS,meta['synthesis']['rows']));rows={q:0 for q in CELLS};history=[]
    for t in range(stop):
        history.append(dict(rows))
        for u in units:
            if u['t']!=t or not set(u['q'])<=set(CELLS):continue
            if u['k'] in ('R','RX'):rows[u['q'][0]]=seed[u['q'][0]]
            elif u['k']=='CX':a,b=u['q'];rows[b]^=rows[a]
    history.append(dict(rows));out=[]
    for q in CELLS:
        for h in range(36):
            if h in CELLS or not adjacent(q,h):continue
            limit=min(stop-1,first[h]-2)
            start=1
            while start<limit:
                r=history[start][q]
                if r not in f6.GOALS:start+=1;continue
                end=start+1
                while end<=limit and history[end][q]==r:end+=1
                times=[t for t in range(start,end) if (t,q) not in busy]
                if len(times)>=2:
                    a,b=times[0],times[-1]
                    if b-a>=3 and a>=1 and first[h]>b+1:
                        out.append(dict(q=q,h=h,start=a,end=b,row=r,duration=b-a))
                start=end
    uniq={tuple(s.values()):s for s in out}
    return sorted(uniq.values(),key=lambda s:-s['duration'])

def build(base,selected,name):
    base=Path(base);units,dets=parse(base.with_suffix('.qasm').read_text());meta=json.loads(base.with_suffix('.json').read_text())
    bit=max(u['b'] for u in units if u['b'] is not None)+1
    for sp in selected:
        q,h,a,b=[sp[k] for k in ['q','h','start','end']]
        units += [dict(k='R',q=(h,),t=a-1,b=None),dict(k='CX',q=(q,h),t=a,b=None),
                  dict(k='CX',q=(q,h),t=b,b=None),dict(k='M',q=(h,),t=b+1,b=bit)]
        dets.append([bit]);bit+=1
    text=emit(units,dets)
    return write_stem(text,meta['data_qubits'],H/'cand',name,source=dict(parent=str(base),temporal_guards=selected))

def main():
    base=Path(sys.argv[1]);ss=specs(base);print('specs',json.dumps(ss),flush=True)
    results=[];selected=[];best=price(base,1)
    for round in range(5):
        winner=None
        for i,sp in enumerate(ss):
            if any(s['h']==sp['h'] or s['q']==sp['q'] for s in selected):continue
            try:
                st=build(base,selected+[sp],f'guarded_temporal_r{round}_i{i}')
                raw=raw_check(st.with_suffix('.qasm').read_text(),f6.D)
                row=dict(stem=str(st),specs=selected+[sp],raw=raw)
                if raw['ok']:
                    c1,n=singles(st);row.update(c1=c1,harmful=n)
                    if c1<1e-5:
                        p=price(st,1);row.update(loss=p['loss'],acceptance=p['acceptance'])
                        if p['acceptance']>=.5002 and p['loss']<best['loss'] and (winner is None or p['loss']<winner[1]['loss']):winner=(sp,p,st)
                print(json.dumps(row),flush=True);results.append(row)
            except Exception as ex:
                print('ERROR',sp,repr(ex),flush=True);results.append(dict(spec=sp,error=repr(ex)))
            (H/'temporal_guard_results.json').write_text(json.dumps(results,indent=2)+'\n')
        if winner is None:break
        sp,best,st=winner;selected.append(sp)
        (H/'temporal_guard_best.json').write_text(json.dumps(dict(stem=str(st),specs=selected,**best),indent=2)+'\n')

if __name__=='__main__':main()
