"""Validate and price a native joint resource with an ideal incoming data state.

This is a factory/terminal diagnostic. Its synthetic data encoder is explicitly
perfect and may be nonlocal; a complete incumbent integration is required for
any promotion claim.
"""
import argparse
import collections
import json
import sys
from pathlib import Path
from partial_contract import HERE, A, B, C, D, CELLS, HELPERS, COLS, ROWS, terminal, DETECTORS, make_contract, make_four_square_contract
from partial_square import ROOT, ENC, PIV, emit, f, sw, ideal_contract_check


def make(sol, name):
    contract=make_four_square_contract(True,sol.get('dual_a',False)) if sol.get('contract_kind')=='four_square' else make_contract(sol.get('orientation',0),sol.get('late_c14',False))
    cells = list(map(int,sol.get('cells',CELLS+HELPERS)))
    piv = {int(q):int(v) for q,v in sol['pivots'].items()}
    layers = [[tuple(e) for e in layer] for layer in sol['ops']]
    # Independent exact state-vector-label check, including helper clearing.
    rows = {q:piv.get(q,0) for q in cells}
    for layer in layers:
        seen = set()
        for a,b in layer:
            assert a in cells and b in cells and not seen & {a,b}
            assert abs(a//6-b//6)+abs(a%6-b%6)==1, (a,b)
            seen.update((a,b))
            rows[b] ^= rows[a]
    target={int(q):int(v) for q,v in sol.get('target_columns',contract.COLS).items() if int(q) in cells}
    assert target=={q:contract.COLS[q] for q in cells}
    assert rows == target, (rows,target)
    assert sum(v!=0 for v in piv.values())==sol.get('state_rank',len(ROWS))
    ops=[]
    for i,q in enumerate(D):
        ops.append(f.Op('RX' if i in PIV|{2} else 'R',(q,),0))
    ops += [f.Op('T',(D[2],),1),f.Op('CX',(D[2],D[4]),2),f.Op('CX',(D[2],D[5]),3)]
    for k,layer in enumerate(ENC):
        ops.extend(f.Op('CX',(D[a],D[b]),4+k) for a,b in layer)
    inits=[]
    for q in cells:
        touch=[t for t,layer in enumerate(layers) if any(q in e for e in layer)]
        if not touch:
            assert piv.get(q,0)==target[q]
            if q not in CELLS:
                continue
            if any(int(z['qubit'])==q for z in sol.get('late_initializations',[])):
                continue
            touch=[max(6,len(layers))]
        init=dict(qubit=q,time=min(touch),kind='RX' if piv.get(q,0) else 'R')
        inits.append(init)
        ops.append(f.Op(init['kind'],(q,),init['time']))
    for t,layer in enumerate(layers):
        ops.extend(f.Op('CX',e,t+1) for e in layer)
    for init in sol.get('late_initializations',[]):
        ops.append(f.Op(init['kind'],(int(init['qubit']),),int(init['time'])-int(sol.get('T0',0))+1))
    for gate in sol.get('late_cliffords',[]):
        ops.append(f.Op(gate['kind'],(int(gate['qubit']),),int(gate['time'])-int(sol.get('T0',0))+1))
    R=max(7,len(layers)+1)
    for kind,qs,t,bit in contract.terminal():
        ops.append(f.Op(kind,qs,R+t,bit))
    helpers=[q for q in HELPERS if any(q in e for layer in layers for e in layer)]
    ds=[set(row) for row in contract.DETECTORS]
    for j,q in enumerate(helpers):
        ops.append(f.Op('M',(q,),R,21+j))
        ds.append({21+j})
    # Sorting by time is required because the record indices are arbitrary,
    # and the physical circuit has independent blocks running in parallel.
    ops.sort(key=lambda o:o.time)
    text=emit(ops,ds)
    raw=ideal_contract_check(text,D)
    stem=HERE/'counterfactual'/f'factory_{name}'
    stem.with_suffix('.qasm').write_text(text)
    meta=dict(data_qubits=D,ideal_contract=raw,diagnostic_only=True,
        native_resource=True,resource_cx=sum(len(l) for l in layers),R=R,
        scope='Perfect synthetic input data and its waits; all native resource and terminal channels noisy.',
        solution=sol)
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    module=dict(D=contract.D,A=contract.A,B=contract.B,C=contract.C,helpers=helpers,
                initializations=[dict(v,time=v['time']-1) for v in inits],layers=layers,
                late_initializations=sol.get('late_initializations',[]),
                late_cliffords=sol.get('late_cliffords',[]),
                terminal=contract.terminal(),detectors=contract.DETECTORS,
                last_resource_layer=len(layers)-1,
                helper_zero_checks=helpers)
    return stem,module


def evaluate(stem, exact=False):
    meta=json.loads(stem.with_suffix('.json').read_text())
    assert meta['ideal_contract']['ok'],meta['ideal_contract']
    m,e,groups,nd,ks,psi,where,_=sw.prepare(stem,True)
    # The expansion uses linear idle weights, while all-orders contraction
    # below retains the exact repeated-depolarizing strengths from prepare.
    linear=f.make_model(*f.parse_current(stem.with_suffix('.qasm').read_text()))
    assert len(linear.chans)==len(m.chans)
    # All source operations are confined to D before R; attached waits are
    # ideal as well, representing an input delivered just before the round.
    for cid,ch in enumerate(m.chans):
        o=m.labels[ch['ins']]
        if o.time<meta['R'] and set(o.qs)<=set(D):
            ch['p']=0
            for ff in groups[cid]:ff['p']=0
    cache={}
    def loss(s,d,err):
        if (s,d) not in cache:cache[s,d]=e.ntable(s,d)
        _,n=cache[s,d]
        return 0. if n is None else max(0.,float(n[err]))
    def label(ff):
        o=m.labels[ff['ins']]
        return dict(time=o.time,kind=o.kind,qubits=o.qs,pauli=ff['pauli'],label=ff['label'])
    fs=[ff for ff in m.faults if ff['p']]
    def weight(ff):
        cid=ff['chan']
        return ff['p']/m.chans[cid]['p']*linear.chans[cid]['p']/.001
    harm=[];first=0.
    for ff in fs:
        w=weight(ff)*loss(ff['s'],ff['d'],ff['e'])
        first+=w
        if w>1e-10:harm.append(dict(weight=w,**label(ff)))
    active=sum(1<<i for i,p in enumerate(e.projs) if p[:2]!=(0,0))
    bins=collections.defaultdict(list)
    for ff in fs:bins[ff['d']&~active].append(ff)
    second=0.;scopes=collections.defaultdict(float)
    for faults in bins.values():
        for i,a in enumerate(faults):
            for b in faults[i+1:]:
                if a['chan']==b['chan']:continue
                val=weight(a)*weight(b)*loss(a['s']^b['s'],a['d']^b['d'],a['e']^b['e'])
                second+=val
                key=' + '.join(sorted('resource' if m.labels[ff['ins']].time<meta['R'] else 'terminal' for ff in (a,b)))
                scopes[key]+=val
    out=dict(stem=str(stem.relative_to(ROOT)),ideal_contract=meta['ideal_contract'],
             c1=first,harmful=harm,pair_numerator=second,c2_loss_valid=first<1e-10,
             pair_scopes=dict(scopes),scope=meta['scope'])
    print('audit',json.dumps({k:v for k,v in out.items() if k!='harmful'}),flush=True)
    if exact:
        compiled,elim=sw.compile_best(m,e,groups,nd,ks,save=False)
        sw._CTX.update(eng=e,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
        try:
            vals=[sw._row(k) for k in [None]+e.keys]
            acc=vals[0]['value'];obs=sum(w*b*v['value'] for w,b,v in zip(e.W,e.beta,vals[1:]))
            out.update(loss=(acc-obs)/(2*acc),acceptance=acc)
        finally:sw._CTX.clear();sw.COLUMNS.clear()
    stem.with_suffix('.diagnostic.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='harmful'}),flush=True)
    return out


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('solution');ap.add_argument('--exact',action='store_true')
    args=ap.parse_args();p=Path(args.solution);sol=json.loads(p.read_text())
    stem,module=make(sol,p.stem);sol['module']=module
    sol['factory_diagnostic']=evaluate(stem,args.exact)
    p.write_text(json.dumps(sol,indent=2)+'\n')
