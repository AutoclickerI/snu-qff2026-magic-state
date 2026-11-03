"""Screen native deterministic one-qubit heralds in existing idle slots.

Candidates preserve the physical clock. Only noiseless deterministic reads
passing the independent raw-state check enter first-/second-order screening;
the final decision uses complete all-orders loss and acceptance.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse, collections, copy, json, sys, time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/REBUILD20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
from qtools import price, write_stem
from qtools.validity import raw_check
from qtools.evaluator import frontend as f,sparse_walsh as sw
from record_contract import model,singles
from joint import emit


def pair_coefficient(m):
    e=f.Engine(m);sw.canonicalize_detector_rows(m,e);e=f.Engine(m)
    active=sum(1<<i for i,p in enumerate(e.projs) if p[:2]!=(0,0))
    groups=collections.defaultdict(lambda:collections.defaultdict(float))
    for ff in m.faults:groups[ff['s'],ff['d'],ff['e']][ff['chan']]+=ff['p']/.001
    buckets=collections.defaultdict(list)
    for key,channels in groups.items():buckets[key[1]&~active].append((key,sum(channels.values()),dict(channels)))
    total=0.;cache={}
    for gs in buckets.values():
        for i,(ka,wa,ca) in enumerate(gs):
            for kb,wb,cb in gs[i+1:]:
                k=ka[0]^kb[0],ka[1]^kb[1]
                if k not in cache:cache[k]=e.ntable(*k)
                _,nn=cache[k]
                if nn is None:continue
                loss=max(0.,float(nn[ka[2]^kb[2]]))
                if loss<1e-12:continue
                total+=(wa*wb-sum(p*cb.get(c,0.) for c,p in ca.items()))*loss
    return total


def screen(job):
    stem,spec=job;stem=Path(stem)
    data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    ops,ds=f.parse_current(stem.with_suffix('.qasm').read_text())
    kind,q,t=spec;b=max(o.bit or 0 for o in ops)+1
    ops.append(f.Op(kind,(q,),t,b));ds.append({b})
    text=emit(ops,ds);raw=raw_check(text,data)
    row=dict(spec=list(spec),raw=raw)
    if not raw['ok']:return row
    m,_=model(text,data);audit=singles(m)
    row['c1']=audit['c1']
    if audit['c1']>1e-10:return row
    row['c2']=pair_coefficient(m)
    out=write_stem(text,data,HERE/'herald_cand',f'herald_{kind}_{q}_{t}',source={'parent':str(stem),'herald':list(spec)})
    row['stem']=str(out.relative_to(ROOT))
    return row


def full(row):
    return row,price(ROOT/row['stem'],1)


def run(stem,lo,hi,finalists,processes):
    stem=Path(stem).resolve();ops,_=f.parse_current(stem.with_suffix('.qasm').read_text())
    specs=[]
    for q in sorted({q for o in ops for q in o.qs}):
        touches=sorted((o for o in ops if q in o.qs),key=lambda o:o.time)
        for t in range(lo,hi):
            if any(o.time==t for o in touches):continue
            prior=[o for o in touches if o.time<t];after=[o for o in touches if o.time>t]
            if not prior or not after or after[0].kind in ('R','RX'):continue
            # Repeated reads of an untouched eigenstate only add an error check
            # on a spectator; the meaningful windows end at a non-reset use.
            for kind in ('M','MX'):specs.append((kind,q,t))
    rows=[];started=time.perf_counter()
    with ProcessPoolExecutor(max_workers=processes) as pool:
        for row in pool.map(screen,[(str(stem),s) for s in specs]):
            rows.append(row)
            if 'stem'in row:print('screen',json.dumps({k:v for k,v in row.items() if k!='raw'}),flush=True)
    (HERE/'herald_screen.json').write_text(json.dumps(dict(parent=str(stem),rows=rows,seconds=time.perf_counter()-started),indent=2)+'\n')
    good=sorted((r for r in rows if 'stem'in r),key=lambda r:r['c2'])
    print('screen_complete',len(rows),'valid_c1zero',len(good),flush=True)
    results=[]
    with ProcessPoolExecutor(max_workers=processes) as pool:
        fs=[pool.submit(full,r) for r in good[:finalists]]
        for fut in as_completed(fs):
            row,val=fut.result();row['price']=val;results.append(row)
            print('price',row['spec'],val['loss'],val['acceptance'],flush=True)
            (HERE/'herald_prices.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem')
    ap.add_argument('--lo',type=int,default=29);ap.add_argument('--hi',type=int,default=47)
    ap.add_argument('--finalists',type=int,default=24);ap.add_argument('--processes',type=int,default=2)
    a=ap.parse_args();run(a.stem,a.lo,a.hi,a.finalists,a.processes)
