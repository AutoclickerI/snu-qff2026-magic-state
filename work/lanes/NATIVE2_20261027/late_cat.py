"""Native late logical-W checks on the recycled seven-cell encoder footprint.

The compact prefix already transfers its encoded data off a connected seven-
cell patch. A GHZ state grown directly on that patch needs six local CX gates,
and its seven data interactions are all native. No routing or bridge gates.
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/NATIVE20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/EXPAND2_20261027'))
from qtools import write_stem
from qtools.validity import raw_check
from qtools.evaluator.frontend import parse_current
from rebuild import Circuit

HERE=Path(__file__).resolve().parent
A=[1,14,8,9,2,16,15]
D=[0,20,7,10,3,22,21]
TREE=[[(8,9)],[(8,2),(9,15)],[(2,1),(15,16),(8,14)]]
FLAG_SETS={
    'none':[],
    'two':[(2,8),(14,15)],
    'cross':[(2,8),(9,15)],
    'three':[(1,2),(8,9),(14,15)],
    'leaves':[(2,1),(8,14),(15,16)],
}

def emit(c,t,o):
    if o.kind=='CX':c.cx(t,*o.qs)
    elif o.kind in ('R','RX'):c.reset(t,o.qs[0],o.kind=='RX')
    elif o.kind in ('M','MX'):
        if o.kind=='MX':c.add(t,f'h q[{o.qs[0]}];')
        c.add(t,f'measure q[{o.qs[0]}] -> c[{o.bit}];')
        if o.kind=='MX':c.add(t,f'h q[{o.qs[0]}];')
    else:c.add(t,f'{o.kind.lower()} q[{o.qs[0]}];')

def build(checks=1,flags='none',source=None,tree=None,root=8):
    if source is None:source=ROOT/'work/lanes/PREFIX20261027/cand/final_phase_random_1'
    ops,dets=parse_current(source.with_suffix('.qasm').read_text())
    meta=json.loads(source.with_suffix('.json').read_text())
    assert meta['data_qubits']==D
    c=Circuit();c.bit=max(o.bit for o in ops if o.bit is not None)+1;c.dets=[sorted(d) for d in dets]
    flag_pairs=FLAG_SETS[flags]
    one_check_len=6+(3 if flag_pairs else 0)
    # Cat reset/three CX layers/control/read occupy six native ticks.
    cat_start=21
    last_read=cat_start+checks*one_check_len-1
    shift=last_read+1-20
    kept=[];shifted=[]
    for o in ops:
        keep=(o.time<16 or (o.time==16 and o.bit in (500,501)) or
              (17<=o.time<=19 and set(o.qs)<=set(A+D)) or
              (o.time==20 and o.kind=='M' and o.qs[0] in A and o.bit>=500))
        emit(c,o.time if keep else o.time+shift,o)
        (kept if keep else shifted).append(o)
    # The original source heralds five vacated cells; check the other two too.
    measured={o.qs[0] for o in kept if o.time==20 and o.kind=='M'}
    for q in A:
        if q not in measured:c.dets.append([c.read(20,q)])
    # Two encoder inputs previously reused the known-zero transfer source.
    # GHZ readout changes that state, so explicitly restore those zero inputs.
    for q in A:
        first=next(o for o in shifted if q in o.qs)
        if first.kind not in ('R','RX'):c.reset(last_read+1,q)
    for rep in range(checks):
        start=cat_start+rep*one_check_len
        for q in A:c.reset(start,q,q==root)
        for k,layer in enumerate(TREE if tree is None else tree):
            for u,v in layer:c.cx(start+1+k,u,v)
        tick=start+4
        if flag_pairs:
            for u,v in flag_pairs:c.cx(tick,u,v)
            for _,v in flag_pairs:c.dets.append([c.read(tick+1,v)])
            for u,v in flag_pairs:c.cx(tick+2,u,v)
            tick+=3
        if rep==0:
            for d in D:c.add(tick-1,f't q[{d}];')
        for a,d in zip(A,D):c.cx(tick,a,d)
        c.dets.append([c.read(tick+1,a,True) for a in A])
        if rep==checks-1:
            for d in D:c.add(tick+1,f'tdg q[{d}];')
    # Every local layer must be a native matching, counting folded RX/MX once.
    newops,_=parse_current(c.text());used=set()
    for o in newops:
        keys={(o.time,q) for q in o.qs}
        assert not used&keys,(o,used&keys)
        used|=keys
        if o.kind=='CX':assert abs(o.qs[0]//6-o.qs[1]//6)+abs(o.qs[0]%6-o.qs[1]%6)==1
    return c,dict(data_qubits=D,checks=checks,flags=flags,tail_shift=shift,cat_start=cat_start,
                  cat_final_read=last_read,ticks=max(o.time for o in newops)+1,
                  cx=sum(o.kind=='CX' for o in newops),T=sum(o.kind in ('T','TDG') for o in newops))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checks',type=int,default=1);ap.add_argument('--flags',choices=FLAG_SETS,default='none');ap.add_argument('--price',action='store_true');args=ap.parse_args()
    c,meta=build(args.checks,args.flags)
    stem=write_stem(c.text(),D,HERE/'cand',f'late_w{args.checks}_{args.flags}',source=meta)
    result=dict(stem=str(stem),**meta,raw=raw_check(c.text(),D))
    print(json.dumps(result,indent=2),flush=True)
    if args.price and result['raw']['ok']:
        import analytic_price
        result['price']=analytic_price.price(stem)
        print(json.dumps(result['price'],indent=2),flush=True)
    (HERE/f'result_w{args.checks}_{args.flags}.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
