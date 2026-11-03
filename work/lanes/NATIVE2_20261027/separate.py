"""Native fresh injection and W checks with post-interaction cat decoding.

Undoing the local GHZ tree after its data interaction exposes six deterministic
Z flags and the W measurement in one root X readout. It requires neither a
separate flag block nor correlated correction/frame updates.
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,json
from pathlib import Path
from late_cat import ROOT,HERE,A,D,TREE,emit,Circuit
from qtools import write_stem,price
from qtools.validity import raw_check
from qtools.evaluator.frontend import parse_current


def build(checks=2,prechecks='',uncompute='full',magic_file='linear_magic_d8_s1.json',reuse=False,jit=False,partial='',phase_time=None):
    source=ROOT/'work/lanes/PREFIX20261027/cand/final_phase_random_1'
    ops,dets=parse_current(source.with_suffix('.qasm').read_text())
    magic=json.loads((HERE/magic_file).read_text())
    layers=[v for v in magic['layers'] if v['cx'] or v['rx']]
    c=Circuit();c.bit=max(o.bit for o in ops if o.bit is not None)+1
    def is_source(o):
        return (o.time<16 or (o.time==16 and o.bit in (500,501)) or
                (17<=o.time<=19 and set(o.qs)<=set(A+D)) or
                (o.time==20 and o.kind=='M' and o.qs[0] in A and o.bit>=500))
    tail=[o for o in ops if not is_source(o)]
    dropped={o.bit for o in ops if is_source(o) and o.bit is not None}
    c.dets=[sorted(row) for row in dets if not row&dropped]
    initial=dict(magic['initial'])
    qm=next(q for q,j in magic['initial'] if j==3)
    first=next(i+1 for i,l in enumerate(layers) if any(qm in e for e in l['cx']))
    if first==1:
        encoder_start=2
    else:encoder_start=1
    phase_tick=(first+encoder_start-2) if jit else 1
    if phase_time is not None:phase_tick=phase_time
    for q in A:
        first_use=next(t for t,l in enumerate(layers,encoder_start) if any(q in e for e in l['cx']))
        reset_tick=min(first_use,phase_tick)-1 if q==qm else first_use-1
        c.reset(reset_tick if jit else 0,q,q in initial)
        if q==qm:c.add(phase_tick,f't q[{qm}];')
    rows={q:1<<initial[q] if q in initial else 0 for q in A}
    for t,layer in enumerate(layers,encoder_start):
        if t==phase_tick:assert rows[qm]==8 and not any(qm in e for e in layer['cx'])
        for u,v in layer['cx']:rows[v]^=rows[u]
    for t,layer in enumerate(layers,encoder_start):
        for u,v in layer['cx']:c.cx(t,u,v)
    end=encoder_start+len(layers)-1
    for q in D:c.reset(end,q)
    for a,d in zip(A,D):c.cx(end+1,a,d);c.cx(end+2,d,a)
    for q in A:c.dets.append([c.read(end+3,q)])
    cat_start=end+4
    if partial:
        assert partial in ('X2','Y2','Z2')
        block=[14,8,16,15];data_block=[D[A.index(q)] for q in block]
        for q in block:c.reset(cat_start,q,q==14)
        c.cx(cat_start+1,14,15);c.cx(cat_start+2,14,8);c.cx(cat_start+2,15,16)
        if partial[0] in 'XY':
            before,after=('h','h') if partial[0]=='X' else ('sdg','s')
            for d in data_block:c.add(cat_start+2,f'{before} q[{d}];');c.add(cat_start+4,f'{after} q[{d}];')
        for a,d in zip(block,data_block):c.cx(cat_start+3,a,d)
        c.dets.append([c.read(cat_start+4,a,True) for a in block])
        cat_start+=5
    for kind in prechecks:
        assert kind in 'XYZ'
        rows={q:(1<<initial[q] if q in initial and initial[q]<3 else 0) for q in A}
        initial_rows=rows.copy();gates=[]
        for j,layer in enumerate(layers,1):
            for u,v in layer['cx']:
                if rows[u]:
                    gates.append((j,v if kind=='X' else u,u if kind=='X' else v))
                    rows[v]^=rows[u]
        for q in A:
            first_use=next(j for j,u,v in gates if q in (u,v))
            c.reset(cat_start+first_use-1 if jit else cat_start,q,(initial_rows[q]!=0) ^ (kind=='X'))
        for j,u,v in gates:c.cx(cat_start+j,u,v)
        tick=cat_start+len(layers)+1
        if kind=='Y':
            # Conjugate native controlled-X to controlled-Y. Both Clifford
            # layers replace existing data-idle slots; no depth is added.
            for d in D:c.add(tick-1,f'sdg q[{d}];');c.add(tick+1,f's q[{d}];')
        for a,d in zip(A,D):c.cx(tick,d if kind=='X' else a,a if kind=='X' else d)
        c.readblock(tick+1,A,x=(kind!='X'))
        cat_start=tick+2
    decode={'none':[],'matching':[[(1,2),(8,14),(15,16)]],'full':list(reversed(TREE))}[uncompute]
    length=6+len(decode)
    assert not reuse or uncompute=='full'
    for rep in range(checks):
        t=cat_start if rep==0 else rt+int(not reuse)
        if rep==0 or not reuse:
            for q in A:c.reset(t,q,q==8)
        for j,layer in enumerate(TREE,1):
            for u,v in layer:c.cx(t+j,u,v)
        if rep==0:
            for d in D:c.add(t+3,f't q[{d}];')
        for a,d in zip(A,D):c.cx(t+4,a,d)
        if rep==checks-1:
            for d in D:c.add(t+5,f'tdg q[{d}];')
        rows={q:1 for q in A}
        for j,layer in enumerate(decode,5):
            for u,v in layer:c.cx(t+j,u,v);rows[v]^=rows[u]
        rt=t+5+len(decode);parity=[]
        for q in A:
            bit=c.read(rt,q,x=bool(rows[q]))
            if reuse and rows[q]:c.add(rt,f'h q[{q}];')
            if rows[q]:parity.append(bit)
            else:c.dets.append([bit])
        c.dets.append(parity)
    a_start=rt+int(not reuse);delta=a_start-20
    if not reuse:
        for q in (1,15):c.reset(a_start,q)
    for o in tail:
        if reuse and o.time==20 and o.qs[0] in (8,2) and o.kind in ('R','RX'):continue
        emit(c,o.time+delta,o)
    parser=parse_current
    if 'Y' in prechecks+partial:
        from frontend_clifford import parse_current as parser
    nops,nds=parser(c.text());used=set()
    for o in nops:
        keys={(o.time,q) for q in o.qs};assert not used&keys,(o,used&keys);used|=keys
        if o.kind=='CX':assert abs(o.qs[0]//6-o.qs[1]//6)+abs(o.qs[0]%6-o.qs[1]%6)==1
    meta=dict(data_qubits=D,checks=checks,prechecks=prechecks,partial_precheck=partial,phase_time=phase_tick,uncompute=uncompute,reuse=reuse,jit=jit,magic_file=magic_file,
              cat_start=cat_start,cat_final_read=rt,round_tick=28+delta,
              ticks=max(o.time for o in nops)+1,cx=sum(o.kind=='CX' for o in nops),
              T=sum(o.kind in ('T','TDG') for o in nops))
    return c,meta


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checks',type=int,default=2)
    ap.add_argument('--prechecks',default='');ap.add_argument('--uncompute',choices=('none','matching','full'),default='full')
    ap.add_argument('--price',action='store_true');ap.add_argument('--reuse',action='store_true')
    ap.add_argument('--jit',action='store_true');ap.add_argument('--magic-file',default='linear_magic_d8_s1.json')
    ap.add_argument('--partial',default='');ap.add_argument('--phase-time',type=int);args=ap.parse_args()
    c,meta=build(args.checks,args.prechecks,args.uncompute,args.magic_file,reuse=args.reuse,jit=args.jit,partial=args.partial,phase_time=args.phase_time)
    name=f'separate_w{args.checks}_{args.uncompute}'+(f'_pc{args.prechecks}' if args.prechecks else '')+('_reuse' if args.reuse else '')
    name+=('_jit' if args.jit else '')+('_'+Path(args.magic_file).stem if args.magic_file!='linear_magic_d8_s1.json' else '')
    name+=(f'_partial{args.partial}' if args.partial else '')+(f'_phase{args.phase_time}' if args.phase_time is not None else '')
    stem=write_stem(c.text(),D,HERE/'cand',name,source=meta)
    out=dict(stem=str(stem),**meta,raw=raw_check(c.text(),D));print(json.dumps(out,indent=2),flush=True)
    if args.price and out['raw']['ok']:
        if 'Y' in args.prechecks+args.partial:
            from clifford_price import price as extended_price
            out['price']=extended_price(stem)
        else:out['price']=price(stem,processes=1)
        print(json.dumps(out['price'],indent=2),flush=True)
    (HERE/f'{name}.result.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':main()
