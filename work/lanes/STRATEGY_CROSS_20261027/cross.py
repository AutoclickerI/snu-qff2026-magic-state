"""Bounded source/ending decision experiment with every physical channel noisy.

This is an ABSTRACT diagnostic: adjacency is explicitly relaxed. No result is a
submission or evidence of native performance. Source and ending are crossed so
an attractive source cannot conceal its resource-preparation or terminal cost.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse, concurrent.futures, hashlib, json, sys, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/lanes/CAT3_20261027'))
import smallcat as s
from multicat import color
s.HERE=HERE


def source(kind,tag):
    name=kind+'_original'if tag=='original'else kind+'_seed_'+tag
    if kind=='bell2':
        rounds=[s.GROUPS[2]]*2
        stem,meta=s.build(ncat=2,interleaved=True,round_groups=rounds,
                          coupling_layers=color(rounds,0),name=name)
    elif kind=='bell4':
        triples=[[0,1,3],[0,2,4],[0,3,6],[1,2,3]]
        rounds=[[g,sorted(set(range(7))-set(g))]for g in triples]
        stem,meta=s.build(ncat=2,interleaved=True,round_groups=rounds,
                          coupling_layers=color(rounds,3),name=name)
    elif kind=='cat133':
        stem,meta=s.build(ncat=3,groups=[[5],[0,1,3],[2,4,6]],
                          interleaved=True,name=name)
    else:raise ValueError(kind)
    ops,dets=s.f.parse_current(stem.with_suffix('.qasm').read_text())
    return stem,meta,ops,dets


def css_prep(block,rows,end):
    """Systematic positive CSS encoder; actual resets/CX are all retained."""
    rr=list(rows);pivots=[];k=0
    for c in range(7):
        found=next((i for i in range(k,len(rr))if rr[i]>>c&1),None)
        if found is None:continue
        rr[k],rr[found]=rr[found],rr[k]
        for i in range(len(rr)):
            if i!=k and rr[i]>>c&1:rr[i]^=rr[k]
        pivots.append(c);k+=1
    rr=rr[:k];pairs=[(p,c)for p,row in zip(pivots,rr)
                    for c in range(7)if c!=p and row>>c&1]
    layers=[]
    for a,b in pairs:
        layer=next((x for x in layers if all(a not in z and b not in z for z in x)),None)
        if layer is None:layer=[];layers.append(layer)
        layer.append((a,b))
    start=end-len(layers)
    ops=[s.f.Op('RX'if i in pivots else'R',(q,),start)for i,q in enumerate(block)]
    for j,layer in enumerate(layers,1):
        ops += [s.f.Op('CX',(block[a],block[b]),start+j)for a,b in layer]
    return ops


def make(kind,ending):
    stem,meta,ops,dets=source(kind,ending)
    meta['source_kind']=kind
    meta['ending_kind']=ending
    if ending=='original':return stem,meta
    resource=set(s.A+s.B+s.C)
    # All precheck resources and reads are at clocks <=9. Only the later
    # terminal resource factory and its instrument are replaced.
    ops=[o for o in ops if not(o.time>9 and set(o.qs)&resource)]
    r=meta['tail_start']
    if ending.startswith('bflag') and r<16:
        shift=16-r
        ops=[s.f.Op(o.kind,o.qs,o.time+shift if o.time>9 else o.time,o.bit)for o in ops]
        r+=shift
        meta['tail_start']=r
        meta['source_delay_for_B_verifier']=shift
    s.prep(ops,s.A,r-4,True)
    s.prep(ops,s.B,r-6 if ending.startswith('bflag')else r-4,False)
    if ending=='square':
        s.prep(ops,s.C,r-4,True)
        ops += [s.f.Op('CX',(b,c),r)for b,c in zip(s.B,s.C)]
        ops += [s.f.Op('CX',(c,a),r+1)for c,a in zip(s.C,s.A)]
        ops += [s.f.Op('MX',(c,),r+2,100+i)for i,c in enumerate(s.C)]
    elif ending in ('comp6','comp4'):
        mask=63 if ending=='comp6'else 29
        # The shortened C space compensates the missing C-to-A positions.
        # For this diagnostic an actual encoder prepares it, followed by
        # the actual inverse BC pre-entangler required by that resource.
        rows=[];basis={}
        for v in range(1,128):
            if v&~mask or any((v&g).bit_count()%2 for g in (85,102,120)):continue
            w=v
            while w:
                p=w.bit_length()-1
                if p not in basis:basis[p]=w;rows.append(v);break
                w^=basis[p]
        rows += [1<<i for i in range(7)if not(mask>>i&1)]
        ops += css_prep(s.C,rows,r-2)
        # B must be ready for the pre-entangler; shift its actual encoder.
        ops=[s.f.Op(o.kind,o.qs,o.time-1,o.bit)if set(o.qs)<=set(s.B)and o.time>9 else o for o in ops]
        ops += [s.f.Op('CX',(b,c),r-1)for b,c in zip(s.B,s.C)]
        ops += [s.f.Op('CX',(b,c),r)for b,c in zip(s.B,s.C)]
        ops += [s.f.Op('CX',(s.C[i],s.A[i]),r+1)for i in range(7)if mask>>i&1]
        ops += [s.f.Op('MX',(c,),r+2,100+i)for i,c in enumerate(s.C)]
    elif ending.startswith('bflag'):
        lines={'bflag146':[[1,4,6]],'bflag236':[[2,3,6]],
               'bflag_both':[[1,4,6],[6,2,3]]}[ending]
        for j,line in enumerate(lines):
            flag=s.C[j]
            ops.append(s.f.Op('R',(flag,),r-3))
            ops += [s.f.Op('CX',(s.B[i],flag),r-2+k)for k,i in enumerate(line)]
            ops.append(s.f.Op('M',(flag,),r+1,100+j))
        meta['B_verification_lines']=lines
    elif ending!='noC':raise ValueError(ending)
    ops += [s.f.Op('CX',(d,a),r)for d,a in zip(s.D,s.A)]
    ops += [s.f.Op('CX',(b,d),r+1)for b,d in zip(s.B,s.D)]
    ops += [s.f.Op('M',(a,),r+2,107+i)for i,a in enumerate(s.A)]
    ops += [s.f.Op('MX',(b,),r+2,114+i)for i,b in enumerate(s.B)]
    ops.sort(key=lambda o:o.time)
    used=set()
    for o in ops:
        keys={(o.time,q)for q in o.qs}
        assert not used&keys,(o,used&keys)
        used|=keys
    s.f.DATA=s.D
    contract=s.record_contract.complete(s.f.make_model(ops,[]),[])
    assert all(not row['reference']for row in contract['missing'])
    text=s.emit(ops,[set(row['bits'])for row in contract['missing']])
    stem=HERE/'cand'/f'{kind}_{ending}'
    stem.with_suffix('.qasm').write_text(text)
    meta.update(raw=s.ideal_contract_check(text,s.D),record_contract=contract,
                cx=sum(o.kind=='CX'for o in ops),ticks=max(o.time for o in ops)+1,
                qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
                diagnostic_only=True,grid_valid=False,
                scope='Complete abstract circuit with every reset, gate, read, and idle noisy. Only adjacency is relaxed.')
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return stem,meta


def run(job):
    kind,ending=job;started=time.perf_counter()
    try:
        stem,meta=make(kind,ending)
        row=dict(name=stem.name,source=kind,ending=ending,cx=meta['cx'],ticks=meta['ticks'],raw=meta['raw']['ok'],
                 diagnostic_only=True,grid_valid=False)
        if row['raw']:
            s.f.DATA=s.D
            ops,dets=s.f.parse_current(stem.with_suffix('.qasm').read_text())
            singles=s.record_contract.singles(s.f.make_model(ops,dets))
            # Singles are recorded diagnostically, never used as an eligibility veto.
            result=s.exact(stem)
            row.update(c1=singles['c1'],harmful_singles=len(singles['harmful_faults']),
                       loss=result['loss'],acceptance=result['acceptance'])
            meta.update(singles=singles,exact=result)
        meta['completed']=True
        stem.with_suffix('.result.json').write_text(json.dumps(meta,indent=2)+'\n')
        row['seconds']=time.perf_counter()-started
        return row
    except Exception as exc:
        import traceback
        return dict(source=kind,ending=ending,error=str(exc),traceback=traceback.format_exc(),seconds=time.perf_counter()-started)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--sources',default='bell2,bell4,cat133')
    ap.add_argument('--endings',default='original,square,noC,comp6,comp4')
    ap.add_argument('--workers',type=int,default=2)
    ap.add_argument('--output',default='cross_results.json')
    args=ap.parse_args()
    HERE.mkdir(exist_ok=True)
    jobs=[(a,b)for a in args.sources.split(',')for b in args.endings.split(',')]
    rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers)as pool:
        for row in pool.map(run,jobs):
            rows.append(row);print(json.dumps(row),flush=True)
            (HERE/args.output).write_text(json.dumps(dict(completed=False,jobs=len(jobs),rows=rows),indent=2)+'\n')
    (HERE/args.output).write_text(json.dumps(dict(completed=True,jobs=len(jobs),rows=rows),indent=2)+'\n')


if __name__=='__main__':main()
