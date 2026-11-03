import os,sys,json,time,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import run_legacy_suffix,synth
from qtools.evaluator import frontend as f
from qtools import price
from qtools.validity import raw_check
H=synth.HERE
rec=json.loads((H/'legacy_8_0.network.json').read_text())
def singles(stem):
    text=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    f.DATA=data;ops,dets=f.parse_current(text);m=f.make_model(ops,dets);eng=f.Engine(m)
    cache={};total=0;rows=[]
    for ff in m.faults:
        key=(ff['s'],ff['d']);val=cache.get(key)
        if val is None:
            a,n=eng.ntable(*key);val=(a,n);cache[key]=val
        a,n=val;loss=0. if n is None else float(n[ff['e']])
        if loss>1e-10:total+=ff['p']*loss;rows.append(ff)
    return total,len(rows)
if __name__=='__main__':
    records=[];best=1
    for mode,i in [('first',0),('last',0)]+[('random',i) for i in range(120)]:
        r=dict(rec,phase_mode=mode,phase_seed=i);name=f'phase_{mode}_{i}'
        try:
            stem=synth.build(r,name);c1,n=singles(stem)
            ans=dict(name=name,c1=c1,harmful=n)
            if c1<2e-5:
                pr=price(stem,1);ans.update(loss=pr['loss'],acceptance=pr['acceptance'])
                if pr['loss']<best:
                    best=pr['loss'];(H/'phase_best.json').write_text(json.dumps(dict(stem=str(stem),**ans),indent=2))
            print(json.dumps(ans),flush=True);records.append(ans)
            (H/'phase_results.json').write_text(json.dumps(records,indent=2))
        except Exception as ex:
            print('ERROR',name,repr(ex),flush=True)
