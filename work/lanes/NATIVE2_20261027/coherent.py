"""Merge a native logical-W cat with the final Steane A resource.

The cat-to-code map preserves the cat's arbitrary logical computational bit.
Three zero wires exposed by its first CX matching can be measured before RX
injection, yielding native post-interaction GHZ hook flags without helper cells.
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,json,sys
from pathlib import Path
from late_cat import ROOT,HERE,A,D,TREE,emit,Circuit
from qtools import write_stem,price
from qtools.validity import raw_check
from qtools.evaluator.frontend import parse_current


def build(fresh=True,checks=1,extract=True,source=None,prechecks=''):
    source=Path(source) if source else ROOT/'work/lanes/PREFIX20261027/cand/final_phase_random_1'
    ops,dets=parse_current(source.with_suffix('.qasm').read_text())
    conv=json.loads((HERE/'linear_cat_d8_s1.json').read_text())
    magic=json.loads((HERE/'linear_magic_d8_s1.json').read_text())
    conv_layers=[v for v in conv['layers'] if v['cx'] or v['rx']]
    magic_layers=[v for v in magic['layers'] if v['cx'] or v['rx']]
    assert conv['map_verified'] and magic['map_verified']
    c=Circuit();c.bit=max(o.bit for o in ops if o.bit is not None)+1

    def is_source(o):
        return (o.time<16 or (o.time==16 and o.bit in (500,501)) or
                (17<=o.time<=19 and set(o.qs)<=set(A+D)) or
                (o.time==20 and o.kind=='M' and o.qs[0] in A and o.bit>=500))

    def is_aprep(o):
        return 20<=o.time<=27 and set(o.qs)<=set(A) and not is_source(o)

    kept=[o for o in ops if is_source(o)]
    tail=[o for o in ops if not is_source(o) and not is_aprep(o)]
    dropped_bits={o.bit for o in ops if is_aprep(o) and o.bit is not None}
    if fresh:dropped_bits|={o.bit for o in kept if o.bit is not None}
    c.dets=[sorted(row) for row in dets if not (row&dropped_bits)]
    if fresh:
        initials=dict(magic['initial'])
        for q in A:c.reset(0,q,q in initials)
        qmagic=next(q for q,j in magic['initial'] if j==3)
        first_use=next(t+1 for t,l in enumerate(magic_layers) if any(qmagic in e for e in l['cx']))
        assert first_use>1
        c.add(1,f't q[{qmagic}];')
        for t,layer in enumerate(magic_layers,1):
            for u,v in layer['cx']:c.cx(t,u,v)
        finish=len(magic_layers)
        for q in D:c.reset(finish,q)
        for a,d in zip(A,D):c.cx(finish+1,a,d);c.cx(finish+2,d,a)
        herald=finish+3
        for q in A:c.dets.append([c.read(herald,q)])
        cat_start=herald+1
    else:
        for o in kept:emit(c,o.time,o)
        measured={o.qs[0] for o in kept if o.time==20 and o.kind=='M'}
        for q in A:
            if q not in measured:c.dets.append([c.read(20,q)])
        cat_start=21

    # Recycle A for native Steane syndrome prechecks before the W basis change.
    # Z means detect data Z errors using |0_L>, A->D, and X readout; X is its
    # transversal-H dual. Remove CX gates whose control is identically zero
    # in this state-specific |0_L> preparation.
    for kind in prechecks:
        assert kind in 'XZ'
        initial=dict(magic['initial']);rows={q:(1<<initial[q] if q in initial and initial[q]<3 else 0) for q in A}
        for q in A:c.reset(cat_start,q,(rows[q]!=0) ^ (kind=='X'))
        for j,layer in enumerate(magic_layers,1):
            for u,v in layer['cx']:
                if rows[u]:
                    c.cx(cat_start+j,v if kind=='X' else u,u if kind=='X' else v)
                    rows[v]^=rows[u]
        tick=cat_start+len(magic_layers)+1
        for a,d in zip(A,D):c.cx(tick,d if kind=='X' else a,a if kind=='X' else d)
        c.readblock(tick+1,A,x=(kind=='Z'))
        cat_start=tick+2

    for rep in range(checks):
        t=cat_start+6*rep
        for q in A:c.reset(t,q,q==8)
        for j,layer in enumerate(TREE,1):
            for u,v in layer:c.cx(t+j,u,v)
        if rep==0:
            for d in D:c.add(t+3,f't q[{d}];')
        for a,d in zip(A,D):c.cx(t+4,a,d)
        if rep<checks-1:c.dets.append([c.read(t+5,a,True) for a in A])
    control=cat_start+6*(checks-1)+4
    start=control+1
    for d in D:c.add(start,f'tdg q[{d}];')
    rows={q:8 for q in A}
    exposed=[]
    for j,layer in enumerate(conv_layers):
        t=start+j+int(extract and j>0)
        for q,var in layer['rx']:
            assert rows[q]==0
            c.reset(t,q,True);rows[q]=1<<var
        for u,v in layer['cx']:c.cx(t,u,v);rows[v]^=rows[u]
        if j==0:
            exposed=[q for q in A if rows[q]==0]
            if extract:
                for q in exposed:c.dets.append([c.read(start+1,q)])
    end=start+len(conv_layers)-1+int(extract)
    round_tick=end+2
    delta=round_tick-28
    assert 16+delta>=0
    for o in tail:emit(c,o.time+delta,o)
    newops,newdets=parse_current(c.text());used=set()
    for o in newops:
        keys={(o.time,q) for q in o.qs}
        assert not used&keys,(o,used&keys)
        used|=keys
        if o.kind=='CX':assert abs(o.qs[0]//6-o.qs[1]//6)+abs(o.qs[0]%6-o.qs[1]%6)==1
    bits={o.bit for o in newops if o.bit is not None}
    assert all(set(row)<=bits for row in newdets)
    meta=dict(data_qubits=D,fresh_source=fresh,checks=checks,extract_cat_flags=extract,prechecks=prechecks,
              cat_start=cat_start,cat_control=control,converter_start=start,
              exposed_zero_cells=exposed,round_tick=round_tick,tail_shift=delta,
              ticks=max(o.time for o in newops)+1,cx=sum(o.kind=='CX' for o in newops),
              T=sum(o.kind in ('T','TDG') for o in newops))
    return c,meta


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--old-source',action='store_true')
    ap.add_argument('--checks',type=int,default=1);ap.add_argument('--no-extract',action='store_true')
    ap.add_argument('--source');ap.add_argument('--price',action='store_true');ap.add_argument('--prechecks',default='');args=ap.parse_args()
    c,meta=build(not args.old_source,args.checks,not args.no_extract,args.source,args.prechecks)
    name=f'coherent_{"old" if args.old_source else "fresh"}_w{args.checks}_flag{int(not args.no_extract)}'+(f'_pc{args.prechecks}' if args.prechecks else '')
    stem=write_stem(c.text(),D,HERE/'cand',name,source=meta)
    result=dict(stem=str(stem),**meta,raw=raw_check(c.text(),D))
    print(json.dumps(result,indent=2),flush=True)
    if args.price and result['raw']['ok']:
        if meta['T']<=20:result['price']=price(stem,processes=1)
        else:
            import analytic_price
            result['price']=analytic_price.price(stem)
        print(json.dumps(result['price'],indent=2),flush=True)
    (HERE/f'{name}.result.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
