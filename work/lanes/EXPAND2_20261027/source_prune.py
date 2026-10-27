"""Release source cells earlier while keeping raw state and zero single loss.

This is a first-order-safe contraction experiment. Whole noisy ranking is
performed after contraction; first-order safety does not certify pair quality.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,copy,json,sys,time
from pathlib import Path
import source_contract as sc
from qtools.evaluator import frontend as f,sparse_walsh as sw
from partial_square import prep,prep_shortened_c
import partial_contract as pc

HERE=Path(__file__).resolve().parent


def zero_singles(ops,ds):
    cut=max(o.time for o in ops)+1;allops=copy.deepcopy(ops)
    prep(allops,pc.A,cut,True);prep(allops,pc.B,cut,False);prep_shortened_c(allops,cut)
    allops.extend(f.Op('CX',(b,c),cut+4) for b,c in zip(pc.B,pc.C))
    for kind,qs,t,bit in pc.terminal():
        allops.append(f.Op(kind,qs,cut+5+t,None if bit is None else bit+400))
    dets=list(ds)+[{b+400 for b in r} for r in pc.DETECTORS]
    f.DATA=list(pc.D);m=f.make_model(*f.parse_current(sc.emit(allops,dets)))
    eng=f.Engine(m);sw.canonicalize_detector_rows(m,eng);eng=f.Engine(m)
    cache={};bad=[]
    for ff in m.faults:
        o=m.labels[ff['ins']]
        if cut<=o.time<cut+5:continue
        k=ff['s'],ff['d']
        if k not in cache:cache[k]=eng.ntable(*k)
        _,nn=cache[k]
        if nn is not None and nn[ff['e']]>1e-10:
            bad.append(dict(kind=o.kind,time=o.time,qubits=o.qs,pauli=ff['pauli']))
            return False,bad
    return True,[]


def contract(max_checks=250,input_stem=None,modes=('CX','READ','CX'),name='first_order_pruned'):
    if input_stem:
        ops,ds=f.parse_current(Path(input_stem).with_suffix('.qasm').read_text());pairs=[]
    else:
        original,ds,_=sc.pb.extract(True);ops,pairs=sc.cancel(sorted(original,key=lambda o:o.time))
        ops,_=sc.drop_dead_preparations(ops);ops=sc.schedule(ops)
    ledger=[];checks=0;started=time.perf_counter()
    assert zero_singles(ops,ds)[0]
    # Remove raw identities and final spectator reads, late operations first.
    # Recompute scheduling after each accepted mutation.
    for mode in modes:
        changed=True
        while changed and checks<max_checks:
            changed=False
            for i in range(len(ops)-1,-1,-1):
                if checks>=max_checks:break
                o=ops[i]
                if mode=='CX' and o.kind!='CX':continue
                if mode=='READ':
                    if o.kind not in ('M','MX') or o.qs[0] in pc.D:continue
                    if any(o.qs[0] in u.qs for u in ops[i+1:]):continue
                checks+=1
                candidate=sc.schedule(ops[:i]+ops[i+1:])
                dd=ds if o.bit is None else [r for r in ds if o.bit not in r]
                raw=sc.raw_check(sc.emit(candidate,dd),pc.D)
                if not raw['ok']:continue
                okay,bad=zero_singles(candidate,dd)
                if not okay:continue
                record=dict(kind=o.kind,qubits=o.qs,time=o.time,bit=o.bit,
                            remaining_cx=sum(u.kind=='CX' for u in candidate),
                            source_ticks=max(u.time for u in candidate)+1)
                ledger.append(record);ops=candidate;ds=dd;changed=True
                print('accepted',json.dumps(record),flush=True)
                if checks>=max_checks:break
            print('pass',mode,'checks',checks,'mutations',len(ledger),flush=True)
    changes=dict(canceled_pairs=pairs,first_order_safe_deletions=ledger,
                 checks=checks,seconds=time.perf_counter()-started)
    result=sc.one(name,ops,ds,changes)
    (HERE/(name+'_result.json')).write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--checks',type=int,default=250)
    ap.add_argument('--input');ap.add_argument('--modes',default='CX,READ,CX')
    ap.add_argument('--name',default='first_order_pruned')
    a=ap.parse_args();contract(a.checks,a.input,a.modes.split(','),a.name)
