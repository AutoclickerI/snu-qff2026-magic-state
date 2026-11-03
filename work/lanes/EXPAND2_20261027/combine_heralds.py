"""Combine the measured idle-herald improvements on the relaxed incumbent."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import itertools,json,sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
from qtools import price,write_stem
from qtools.evaluator import frontend as f
from joint import emit
BASE=HERE/'accept_cand/combined_0'


def one(specs):
    text=BASE.with_suffix('.qasm').read_text()
    data=json.loads(BASE.with_suffix('.json').read_text())['data_qubits']
    ops,ds=f.parse_current(text);bit=max(o.bit or 0 for o in ops)+1
    for i,(q,t) in enumerate(specs):
        ops.append(f.Op('M',(q,),t,bit+i));ds.append({bit+i})
    out=write_stem(emit(ops,ds),data,HERE/'combined_cand',
                   'combined_'+('_'.join(f'{q}t{t}' for q,t in specs) or 'control'),
                   source={'parent':str(BASE.relative_to(ROOT)),'heralds':specs})
    val=price(out,1)
    return dict(stem=str(out.relative_to(ROOT)),heralds=specs,**val)


if __name__=='__main__':
    jobs=[]
    for a,b,c,d in itertools.product([None,(13,34)],[None,(31,37),(31,41)],
                                     [None,(33,39)],[None,(7,39)]):
        jobs.append([v for v in [a,b,c,d] if v is not None])
    rows=[]
    with ProcessPoolExecutor(max_workers=2) as pool:
        fs=[pool.submit(one,job) for job in jobs]
        for fut in as_completed(fs):
            row=fut.result();rows.append(row)
            print(json.dumps({k:row[k] for k in ['heralds','loss','acceptance','stem']}),flush=True)
            (HERE/'combined_herald_results.json').write_text(json.dumps(rows,indent=2)+'\n')
    eligible=[r for r in rows if r['acceptance']>=.5002]
    best=min(eligible,key=lambda r:r['loss'])
    (HERE/'working_candidate.json').write_text(json.dumps(best,indent=2)+'\n')
    print('BEST',json.dumps(best),flush=True)
