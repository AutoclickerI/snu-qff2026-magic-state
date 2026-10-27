"""Reconstruct a native contracted source from explicit operator identities.

The complete resource completion remains a separately labeled counterfactual.
No ideal preparation is used in the saved source circuit itself.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import copy,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/REBUILD20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/NATIVE2_20261027'))
import prefix_boundary as pb
from partial_incumbent import diagnose
from joint import emit
from qtools.validity import raw_check
from qtools import write_stem


def commutes(gate,other):
    a,b=gate.qs
    if not(set(gate.qs)&set(other.qs)):return True
    if other.kind=='CX':
        c,d=other.qs
        return a!=d and b!=c
    if other.kind in ('T','TDG','Z','S','SDG','M') and other.qs==(a,):return True
    if other.kind in ('X','SX','SXDG','MX') and other.qs==(b,):return True
    return other.kind=='ID'


def cancel(ops):
    ops=copy.deepcopy(ops);removed=[]
    while True:
        found=False
        for i,o in enumerate(ops):
            if o.kind!='CX':continue
            for j in range(i+1,len(ops)):
                p=ops[j]
                if p.kind=='CX' and p.qs==o.qs:
                    removed.append([dict(time=g.time,qubits=list(g.qs)) for g in [o,p]])
                    ops=ops[:i]+ops[i+1:j]+ops[j+1:];found=True;break
                if not commutes(o,p):break
            if found:break
        if not found:return ops,removed


def drop_dead_preparations(ops):
    keep=[];removed=[]
    for i,o in enumerate(ops):
        if o.kind in ('R','RX'):
            nxt=next((u for u in ops[i+1:] if o.qs[0] in u.qs),None)
            if nxt is not None and nxt.kind in ('R','RX'):
                removed.append(dict(time=o.time,qubit=o.qs[0],kind=o.kind));continue
        keep.append(o)
    return keep,removed


def schedule(ops,jit=True):
    out=copy.deepcopy(ops);last={q:-1 for q in range(36)}
    for o in out:
        o.time=max(last[q] for q in o.qs)+1
        for q in o.qs:last[q]=o.time
    if jit:
        for i,o in enumerate(out):
            if o.kind not in ('R','RX'):continue
            nxt=next((u for u in out[i+1:] if o.qs[0] in u.qs),None)
            if nxt is not None:o.time=nxt.time-1
    return sorted(out,key=lambda o:o.time)


def one(name,ops,ds,changes):
    text=emit(ops,ds);raw=raw_check(text,pb.D)
    assert raw['ok'],(name,raw)
    releases={q:1+max((o.time for o in ops if q in o.qs),default=-1) for q in range(36) if q not in pb.D}
    meta=dict(data_qubits=pb.D,source_ticks=max(o.time for o in ops)+1,
              cx=sum(o.kind=='CX' for o in ops),T=sum(o.kind in ('T','TDG') for o in ops),
              raw=raw,release=releases,changes=changes)
    folder=HERE/'source_variants'/name;folder.mkdir(parents=True,exist_ok=True)
    source=write_stem(text,pb.D,folder,'source',source=meta)
    (folder/'release.json').write_text(json.dumps(dict(stem=str(source.relative_to(ROOT)),**meta),indent=2)+'\n')
    # Isolate imported builder output into this variant's directory.
    pb.HERE=folder
    diagnostic=pb.ideal_completion(ops,ds,meta)
    result=diagnose(diagnostic)
    result['scope']=f'Actual noisy {name} source; perfect instantaneous correlated partial-square resource at tick{meta["source_ticks"]}; artificial resource preparation and elapsed-time noise excluded.'
    diagnostic.with_suffix('.diagnostic.json').write_text(json.dumps(result,indent=2)+'\n')
    out=dict(name=name,source=str(source.relative_to(ROOT)),metadata=meta,
             diagnostic=str(diagnostic.relative_to(ROOT)),loss=result['loss'],
             acceptance=result['acceptance'],c1=result['single_fault_numerator'])
    print('RESULT',json.dumps(out),flush=True)
    return out


if __name__=='__main__':
    ops,ds,meta=pb.extract(True)
    ops=sorted(ops,key=lambda o:o.time)
    canceled,pairs=cancel(ops)
    clean,dead=drop_dead_preparations(canceled)
    jobs=[('pairs_fixed',clean,dict(canceled_pairs=pairs,dead_preparations=dead)),
          ('pairs_asap_jit',schedule(clean),dict(canceled_pairs=pairs,dead_preparations=dead,scheduling='ASAP then just-in-time preparations')),
          ('original_asap_jit',schedule(ops),dict(scheduling='ASAP then just-in-time preparations'))]
    rows=[]
    for name,oo,changes in jobs:
        rows.append(one(name,oo,ds,changes))
        (HERE/'source_contract_results.json').write_text(json.dumps(rows,indent=2)+'\n')
