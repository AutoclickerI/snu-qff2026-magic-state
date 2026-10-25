"""Generate QASM witnesses from exhaustive logical CSS instruments.
Every emitted record parity/frame is derived in search.cpp. Preparation here
is a physical 9-CX CSS encoder, optionally with logical-resource verification.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import json,sys,hashlib,itertools,copy
from pathlib import Path
from build_rounds import Circuit,GENS,ENC,PIV,H
sys.path.insert(0,str(H/'sparse'))
from frontend import parse_current

def rref(rows):
    rows=[v for v in rows if v]; k=0;piv=[]
    for p in range(5):
        j=next((j for j in range(k,len(rows)) if rows[j]>>p&1),None)
        if j is None:continue
        rows[k],rows[j]=rows[j],rows[k]
        for j in range(len(rows)):
            if j!=k and rows[j]>>p&1:rows[j]^=rows[k]
        piv.append(p);k+=1
    return list(zip(piv,rows[:k]))

def finish(c,t,blocks,R):
    last={b:max((k for k,l in enumerate(t['layers']) if any(b in edge for edge in l)),default=-1) for b in range(t['n'])}
    for k,l in enumerate(t['layers']):
        for a,b in l:
            for qa,qb in zip(blocks[a],blocks[b]):c.cx(R+k,qa,qb)
    reads={}
    for b in range(t['n']):
        if (t['read_x']|t['read_z'])>>b&1:reads[b]=c.readblock(R+last[b]+1,blocks[b],bool(t['read_x']>>b&1))
    for mask in t['logical_detectors']:
        c.dets.append([v for b,rr in reads.items() if mask>>b&1 for v in rr])
    for k in ('x','z'):
        bits=[v for b,rr in reads.items() if t['frame_'+k]>>b&1 for v in rr]
        if bits:c.frames.append('// FRAME_'+k.upper()+'(0) '+' '.join(f'c[{v}]' for v in bits))

def save(c,name,t,blocks,**kwargs):
    c.save(name,template=t,**kwargs)
    p=H/'builds'/f'{name}.json';m=json.loads(p.read_text());m['data_qubits']=blocks[t['output']];m['roles']=blocks
    p.write_text(json.dumps(m,indent=2)+'\n')
    ops,_=parse_current(p.with_suffix('.qasm').read_text()); used=set()
    for o in ops:
        ks={(o.time,q) for q in o.qs};assert not ks&used,(name,o,ks&used);used|=ks
    return name

def perfect(t,name):
    c=Circuit();c.magic();blocks=[list(range(7*b,7*b+7)) for b in range(t['n'])]
    rows=rref(t['resource_x']);pivs={p for p,v in rows}
    for b in range(1,t['n']):c.prep(blocks[b],3,b in pivs)
    R=7
    for p,v in rows:
        for b in range(1,t['n']):
            if b!=p and v>>b&1:
                for qa,qb in zip(blocks[p],blocks[b]):c.cx(R,qa,qb)
                R+=1
    finish(c,t,blocks,R)
    return save(c,name,t,blocks,noise_start=R,round_start=R,change='enumerated template; perfect encoded resources and input')

def prefix():
    stem=H/'inputs/v37b';meta=json.loads(stem.with_suffix('.json').read_text());D=meta['data_qubits']
    ops,dets=parse_current(stem.with_suffix('.qasm').read_text());measure={o.bit:o for o in ops if o.bit is not None}
    # The common input boundary is before any final-round coupling, tick44.
    pd=[d for d in dets if max(measure[b].time for b in d)<44];target=set().union(*pd)
    live=set(D);keep=[]
    for o in reversed(ops):
        if o.time>=44:continue
        if o.bit in target or set(o.qs)&live:
            keep.append(o)
            if o.kind in ('R','RX'):live.difference_update(o.qs)
            else:live.update(o.qs)
    keep.reverse();release={q:max((o.time for o in keep if q in o.qs),default=-1)+1 for q in range(36)}
    c=Circuit();c.bit=max(measure)+1;c.dets=[sorted(d) for d in pd]
    for o in keep:
        if o.kind=='CX':c.cx(o.time,*o.qs)
        elif o.kind in ('R','RX'):c.reset(o.time,o.qs[0],o.kind=='RX')
        elif o.kind in ('M','MX'):
            if o.kind=='MX':c.add(o.time,f'h q[{o.qs[0]}];')
            c.add(o.time,f'measure q[{o.qs[0]}] -> c[{o.bit}];')
            if o.kind=='MX':c.add(o.time,f'h q[{o.qs[0]}];')
        else:c.add(o.time,f'{o.kind.lower()} q[{o.qs[0]}];')
    return c,D,release

def suffix(t,name,jit=False):
    c,D,release=prefix();available=sorted((q for q in range(36) if q not in D),key=lambda q:(release[q],q));a=t['n']-1
    danger={v//4 for v in t['dangerous_resource_paulis']}
    order=sorted(range(1,t['n']),key=lambda b:(b not in danger,min(k for k,l in enumerate(t['layers']) if any(b in e for e in l))))
    blocks=[D]+[None]*a
    for j,b in enumerate(order):blocks[b]=available[7*j:7*j+7]
    helper=available[7*a];endh=release[helper]
    rows=rref(t['resource_x']);pivs={p for p,v in rows}
    if t['product_plus_mask']<0:danger=set(range(1,t['n']))
    # Prepare early, verify every required logical axis, then synchronize.
    ready={0:44};checks=[];plans={};deadlines={}
    for b in range(1,t['n']):
        best=None
        for cells in itertools.permutations(blocks[b]):
            ends={q:release[q]+1 for q in cells};ops=[]
            for layer in ENC:
                for i,j in layer:
                    qa,qb=cells[i],cells[j]
                    tt=max(ends[qa],ends[qb]);ops.append((tt,qa,qb));ends[qa]=ends[qb]=tt+1
            score=(max(ends.values()),sum(ends.values()))
            if best is None or score<best[0]:best=(score,cells,ops)
        ready[b]=best[0][0];blocks[b]=list(best[1]);plans[b]=best[2]
    for b in sorted(range(1,t['n']),key=lambda b:(b not in danger,max(release[q] for q in blocks[b]))):
        if b in danger:
            tt=max(ready[b],endh+1);c.reset(tt-1,helper,b in pivs)
            deadlines[b]=tt
            for j,i in enumerate((0,1,2)):
                c.cx(tt+j,helper,blocks[b][i]) if b in pivs else c.cx(tt+j,blocks[b][i],helper)
            c.dets.append([c.read(tt+3,helper,b in pivs)]);endh=tt+4;ready[b]=tt+3;checks.append(b)
    firstuse={b:min(k for k,l in enumerate(t['layers']) if any(b in edge for edge in l)) for b in range(t['n'])}
    R=max(ready[b]-firstuse[b] for b in ready) if jit and t['product_plus_mask']>=0 else max(ready.values())
    for b in range(1,t['n']):
        end={q:deadlines.get(b,R+(firstuse[b] if jit else 0)) for q in blocks[b]};scheduled=[]
        for _,qa,qb in reversed(plans[b]):
            tt=min(end[qa],end[qb])-1;end[qa]=end[qb]=tt;scheduled.append((tt,qa,qb))
        for i,q in enumerate(blocks[b]):
            assert end[q]-1>=release[q]
            c.reset(end[q]-1,q,(i not in PIV) if b in pivs else (i in PIV))
        for tt,qa,qb in scheduled:c.cx(tt,qb,qa) if b in pivs else c.cx(tt,qa,qb)
    for p,v in rows:
        for b in range(1,t['n']):
            if b!=p and v>>b&1:
                for qa,qb in zip(blocks[p],blocks[b]):c.cx(R,qa,qb)
                R+=1
    finish(c,t,blocks,R)
    return save(c,name,t,blocks,round_start=R,change='v37b causal prefix + enumerated suffix, noisy physical preparations and required logical checks',logical_checks=checks,release=release,just_in_time_preparations=jit)

if __name__=='__main__':
    mode=sys.argv[1]; rows=[]
    for p in sorted((H/'logs').glob('search_*.jsonl')):
        rows.extend(json.loads(l) for l in p.read_text().splitlines() if l.strip())
    # All category-frontier witnesses, identical circuits deduplicated by content.
    seen=set();manifest=[]
    for t in sorted(rows,key=lambda t:(t['second_order_p2'],t['n'],t['depth'])):
        key=json.dumps({k:t[k] for k in ('n','layers','output','resource_x','read_x','read_z','frame_x','frame_z')},sort_keys=True)
        if key in seen:continue
        seen.add(key);t['id']=hashlib.sha256(key.encode()).hexdigest()[:12]
        name=f'round_{t["id"]}';perfect(t,name);manifest.append(dict(name=name,template=t))
    (H/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(candidates=len(manifest))))
