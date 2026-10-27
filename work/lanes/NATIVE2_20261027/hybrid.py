"""Price the synthesized early-W-read / concurrent A preparation module."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json
from pathlib import Path
from late_cat import ROOT,HERE,A,D,emit,Circuit
from qtools import write_stem,price
from qtools.validity import raw_check
from qtools.evaluator.frontend import parse_current

def build(stem,all_flags=False,solution='hybrid_d10_m4_s1.json'):
    stem=Path(stem);meta=json.loads(stem.with_suffix('.json').read_text())['source']
    ops,dets=parse_current(stem.with_suffix('.qasm').read_text())
    sol=json.loads((HERE/solution).read_text());assert sol['map_verified']
    layers=sol['layers']
    while not layers[-1]['cx'] and not layers[-1]['rx']:layers=layers[:-1]
    assert meta['uncompute']=='full' and meta['reuse']
    oldR=meta['round_tick'];control=meta['cat_final_read']-4;start=control+1
    # This solution exposes the last missing zero at layer boundary3.
    insert=3 if all_flags else len(layers)+1
    time_of=lambda t:start+t+int(t>=insert)
    end=time_of(len(layers)-1)
    busy_last={q for e in layers[-1]['cx'] for q in e}|{q for q,j in layers[-1]['rx']}
    R=end+1+int(bool(busy_last&{9,15}));delta=R-oldR
    resource={6,26,13,11,4,23,27,12,25,19,17,5,29,28,18,31,35,34}
    removed=[o for o in ops if set(o.qs)<=set(A) and control<o.time<oldR]
    removed_ids={id(o) for o in removed};rbits={o.bit for o in removed if o.bit is not None}
    c=Circuit();c.bit=max(o.bit for o in ops if o.bit is not None)+1
    c.dets=[sorted(row) for row in dets if not row&rbits]
    for o in ops:
        if id(o) in removed_ids:continue
        retime=bool(set(o.qs)&resource) or o.time>=oldR-1
        emit(c,o.time+delta if retime else o.time,o)
    # Required pre-RX zero measurements, plus any other exposed zero whose
    # wire is free. These are deterministic parity checks of the original cat.
    flags={}
    for t,l in enumerate(layers):
        for q,j in l['rx']:flags[q]=time_of(t-1)
    rows={q:8 for q in A};snaps=[]
    for t,l in enumerate(layers):
        snaps.append(rows.copy());busy={q for e in l['cx'] for q in e}|{q for q,j in l['rx']}
        if t==sol['mid']:busy.add(sol['mx_root'])
        for q in A:
            if q not in flags and rows[q]==0 and q not in busy:flags[q]=time_of(t)
        for q,j in l['rx']:assert rows[q]==0;rows[q]=1<<j
        for u,v in l['cx']:rows[v]^=rows[u]
    if all_flags:
        for q in A:
            if q not in flags and snaps[insert][q]==0:flags[q]=start+insert
        assert len(flags)==6,flags
    for q,t in flags.items():c.dets.append([c.read(t,q)])
    for t,l in enumerate(layers):
        tick=time_of(t)
        for q,j in l['rx']:c.reset(tick,q,True)
        for u,v in l['cx']:c.cx(tick,u,v)
        if t==sol['mid']:
            q=sol['mx_root'];c.dets.append([c.read(tick,q,True)]);c.add(tick,f'h q[{q}];')
    nops,nds=parse_current(c.text());used=set()
    for o in nops:
        keys={(o.time,q) for q in o.qs};assert not used&keys,(o,used&keys);used|=keys
        if o.kind=='CX':assert abs(o.qs[0]//6-o.qs[1]//6)+abs(o.qs[0]%6-o.qs[1]%6)==1
    bits={o.bit for o in nops if o.bit is not None};assert all(row<=bits for row in nds)
    out=dict(meta);out.update(round_tick=R,hybrid_solution=solution,source_stem=str(stem),
        early_W_read=time_of(sol['mid']),zero_flags=flags,all_flags=all_flags,
        cx=sum(o.kind=='CX' for o in nops),ticks=max(o.time for o in nops)+1)
    return c,out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--all-flags',action='store_true');ap.add_argument('--price',action='store_true');a=ap.parse_args()
    c,meta=build(a.stem,a.all_flags);name='hybrid_early_flag'+str(len(meta['zero_flags']))
    stem=write_stem(c.text(),D,HERE/'cand',name,source=meta);out=dict(stem=str(stem),**meta,raw=raw_check(c.text(),D));print(json.dumps(out,indent=2),flush=True)
    if a.price and out['raw']['ok']:out['price']=price(stem,processes=1);print(json.dumps(out['price'],indent=2),flush=True)
    stem.with_suffix('.result.json').write_text(json.dumps(out,indent=2)+'\n')
