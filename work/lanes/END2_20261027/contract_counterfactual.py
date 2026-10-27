"""Exact noisy-source comparison for an explicitly ideal partial-square resource."""
import argparse
import json
import sys
from pathlib import Path
from partial_contract import HERE, make_four_square_contract, make_contract
from partial_square import ROOT, D, ENC, PIV, emit, f, sw, ideal_contract_check


def ideal_prep(pc,start):
    rows=[sum(1<<q for q in row) for row in pc.FULL_ROWS]
    piv={};r=0
    for q in range(36):
        i=next((i for i in range(r,len(rows)) if rows[i]>>q&1),None)
        if i is None:continue
        rows[r],rows[i]=rows[i],rows[r]
        for j in range(len(rows)):
            if j!=r and rows[j]>>q&1:rows[j]^=rows[r]
        piv[q]=r;r+=1
    piv={q:rows[j] for q,j in piv.items()}
    assert len(piv)==len(rows)
    ops=[f.Op('RX' if q in piv else 'R',(q,),start) for q in pc.CELLS]
    ready={q:start+1 for q in pc.CELLS}
    for q,v in piv.items():
        for a in pc.CELLS:
            if a==q or not(v>>a&1):continue
            assert a not in piv
            t=max(ready[q],ready[a]);ops.append(f.Op('CX',(q,a),t));ready[q]=ready[a]=t+1
    R=max(o.time for o in ops)+1
    if pc.post_h:
        ops.extend(f.Op('H',(q,),R) for q in pc.post_h);R+=1
    return ops,R


def build(pc,source=True):
    if source:
        prefix_meta=json.loads((ROOT/'work/lanes/NATIVE2_20261027/prefix_release.json').read_text())
        prefix=Path(prefix_meta['stem'])
        ops,dets=f.parse_current(prefix.with_suffix('.qasm').read_text())
        first=max(o.time for o in ops)+1
        ideal_source=[]
    else:
        ops=[];dets=[];first=7
        for i,q in enumerate(pc.D):ops.append(f.Op('RX' if i in PIV|{2} else 'R',(q,),0))
        ops += [f.Op('T',(pc.D[2],),1),f.Op('CX',(pc.D[2],pc.D[4]),2),f.Op('CX',(pc.D[2],pc.D[5]),3)]
        for k,layer in enumerate(ENC):ops.extend(f.Op('CX',(pc.D[a],pc.D[b]),4+k) for a,b in layer)
        ideal_source=list(range(first))
    new,R=ideal_prep(pc,first);ops+=new
    for kind,qs,t,bit in pc.terminal():ops.append(f.Op(kind,qs,R+t,None if bit is None else 400+bit))
    dets += [{400+b for b in row} for row in pc.DETECTORS]
    text=emit(ops,dets);raw=ideal_contract_check(text,pc.D)
    stem=HERE/'counterfactual'/f'{pc.kind}_m{pc.square_mask:02x}_{"source251" if source else "tail"}'
    meta=dict(data_qubits=pc.D,roles=pc.roles,kind=pc.kind,square_mask=pc.square_mask,
        ideal_contract=raw,diagnostic_only=True,gate_valid=False,
        source=str(prefix.relative_to(ROOT)) if source else 'synthetic ideal logicalT',
        source_noisy=source,first_inserted_tick=first,round=R,inserted_ticks=list(range(first,R)),
        ideal_source_ticks=ideal_source,
        scope='Noisy source251 (or perfect logicalT control), ideal instantaneous resource, native terminal.',
        full_resource_rows=[sorted(row) for row in pc.FULL_ROWS])
    stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return stem


def evaluate(stem):
    meta=json.loads(stem.with_suffix('.json').read_text());assert meta['ideal_contract']['ok'],meta['ideal_contract']
    m,e,groups,nd,ks,psi,where,_=sw.prepare(stem,True)
    inserted=set(meta['inserted_ticks']);perfect=inserted|set(meta['ideal_source_ticks'])
    for cid,ch in enumerate(m.chans):
        if m.labels[ch['ins']].time in perfect:
            ch['p']=0
            for ff in groups[cid]:ff['p']=0
    resized=[]
    for ins,q,start,n in f.schedule(m.native)[2]:
        cut=len(set(range(start,start+n))&inserted)
        if not cut or m.labels[ins].time in perfect:continue
        matches=[(cid,ch) for cid,ch in enumerate(m.chans) if ch['ins']==ins and ch['qs']==[q] and ch['name']=='DEPOLARIZE1']
        cid,ch=max(matches,key=lambda item:item[1]['jl'])
        assert abs(ch['p']-.75*(1-(1-4*.001/3)**n))<1e-12
        ch['p']=.75*(1-(1-4*.001/3)**(n-cut))
        for ff in groups[cid]:ff['p']=ch['p']/3
        resized.append(dict(q=q,source_time=m.labels[ins].time,old_wait=n,retained_wait=n-cut))
    cache={};c1=0.;harm=[]
    for ff in m.faults:
        if not ff['p']:continue
        key=ff['s'],ff['d']
        if key not in cache:cache[key]=e.ntable(*key)
        _,N=cache[key];v=0. if N is None else max(0.,float(N[ff['e']]))
        c1+=ff['p']/.001*v
        if v>1e-10:
            o=m.labels[ff['ins']];harm.append(dict(time=o.time,kind=o.kind,qs=o.qs,pauli=ff['pauli'],numerator=v))
    compiled,elim=sw.compile_best(m,e,groups,nd,ks,save=False)
    sw._CTX.update(eng=e,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
    try:
        vals=[sw._row(k) for k in [None]+e.keys]
        acc=vals[0]['value'];obs=sum(w*b*v['value'] for w,b,v in zip(e.W,e.beta,vals[1:]))
        out=dict(stem=str(stem.relative_to(ROOT)),loss=(acc-obs)/(2*acc),acceptance=acc,
            single_fault_numerator=c1,harmful_single_components=harm,ideal_contract=meta['ideal_contract'],
            removed_artificial_idle=resized,scope=meta['scope'],source=meta['source'])
    finally:sw._CTX.clear();sw.COLUMNS.clear()
    stem.with_suffix('.diagnostic.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('removed_artificial_idle','harmful_single_components')}),flush=True)
    return out


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--four',action='store_true');a=ap.parse_args()
    pc=make_four_square_contract() if a.four else make_contract(0,True)
    evaluate(build(pc,False));evaluate(build(pc,True))
