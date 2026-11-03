"""Native copied-row checks targeted by the exact pair ledger.

A Bell meter placed on the other edge of a grid plaquette measures adjacent
data ZZ using three CX. Recycled source helper7 is truly unused before its
discarded zero herald, so replacing that lifetime needs no extra reset/tick.
"""
import os,sys,json,copy
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'T14'))
sys.path.insert(0,str(H.parent/'PREFIX20261027'))
from qcirc import parse,emit,adjacent
from qtools import write_stem,price
from qtools.validity import raw_check
from search_phase import singles

BASE=H.parent/'PREFIX20261027/cand/final_phase_random_1'

def build(base,specs,name):
    base=Path(base);units,dets=parse(base.with_suffix('.qasm').read_text())
    meta=json.loads(base.with_suffix('.json').read_text());data=meta['data_qubits']
    bit=max(u['b'] for u in units if u['b'] is not None)+1
    for sp in specs:
        # Apply insertion before native operation at 'cut'.
        shift=sp.get('shift',0);cut=sp.get('cut',0)
        if shift:
            for u in units:
                if u['t']>=cut:u['t']+=shift
        if sp.get('reuse7'):
            assert all(u['q']!=(7,) or (u['t'],u['k']) in [(0,'R'),(16+shift,'M'),(17+shift,'R')] or u['t']>17+shift for u in units)
            gone={u['b'] for u in units if u['q']==(7,) and u['t']<17+shift and u['b'] is not None}
            units=[u for u in units if not (u['q']==(7,) and u['t']<17+shift)]
            assert all(not(set(d)&gone) or set(d)<=gone for d in dets)
            dets=[d for d in dets if not set(d)&gone]
        t,a,b,h1,h2=[sp[k] for k in ['t','a','b','h1','h2']]
        assert adjacent(a,h1) and adjacent(b,h2) and adjacent(h1,h2)
        units += [dict(k='RX',q=(h1,),t=t-2,b=None),dict(k='R',q=(h2,),t=t-2,b=None),dict(k='CX',q=(h1,h2),t=t-1,b=None)]
        units += [dict(k='CX',q=(a,h1),t=t,b=None),dict(k='CX',q=(b,h2),t=t,b=None)]
        units += [dict(k='M',q=(q,),t=t+1,b=bit+j) for j,q in enumerate([h1,h2])]
        dets.append([bit,bit+1]);bit+=2
    text=emit(units,dets)
    return write_stem(text,data,H/'cand',name,source=dict(parent=str(base),checks=specs))

def main():
    tests=[
       ('q14',BASE,[dict(t=6,a=8,b=14,h1=7,h2=13,reuse7=True)]),
       ('q15',BASE,[dict(t=2,a=9,b=15,h1=10,h2=16,cut=2,shift=2)]),
       ('q14_q16',BASE,[dict(t=6,a=8,b=14,h1=7,h2=13,reuse7=True),dict(t=8,a=15,b=16,h1=21,h2=22)]),
    ]
    results=[]
    for name,base,specs in tests:
        try:
            st=build(base,specs,'target_'+name)
            raw=raw_check(st.with_suffix('.qasm').read_text(),json.loads(st.with_suffix('.json').read_text())['data_qubits'])
            ans=dict(name=name,stem=str(st),raw=raw)
            if raw['ok']:
                c1,n=singles(st);ans.update(c1=c1,harmful=n)
                if c1<1e-5:ans['price']=price(st,1)
            print(json.dumps(ans),flush=True);results.append(ans)
        except Exception as e:
            print(name,repr(e),flush=True);results.append(dict(name=name,error=repr(e)))
        (H/'targeted_results.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
