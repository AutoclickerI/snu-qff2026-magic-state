"""Integrate a native joint ABC solution with the certified incumbent prefix.

Resource time in a solver file is absolute T0+layer.  Known measured inputs
may be reused at their release tick; every other input is reset immediately
before its first gate.  Late product preparations, including the rank-10
construction's RX14, are ordinary noisy operations in the emitted candidate.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/tools'));sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'));sys.path.insert(0,str(HERE))
sys.path.insert(0,str(ROOT/'work/lanes/REBUILD20261027'))
from qtools import write_stem,price
from qtools.validity import raw_check
from qtools.evaluator import frontend as f
from joint import emit
from partial_contract import D,A,B,C,CELLS,HELPERS,COLS,ROWS,terminal,DETECTORS,make_contract
from record_contract import complete
import prefix_boundary as pb

def integrate(sol,name,prefix_path=None,states_path=None,complete_records=True):
    if prefix_path:
        p=Path(prefix_path);text=p.with_suffix('.qasm').read_text();prefix,dets=f.parse_current(text)
        boundary=json.loads(p.with_suffix('.json').read_text())
    else:prefix,dets,boundary=pb.extract()
    release={q:max((o.time for o in prefix if q in o.qs),default=-1)+1 for q in range(36) if q not in D}
    certified=json.loads(Path(states_path or HERE/'prefix_product_states.json').read_text())
    states={r['q']:r for r in certified['cells']}
    if prefix_path:assert Path(certified['prefix_stem']).with_suffix('.qasm').read_text()==text,'A new prefix requires its own product-state certificate.'
    ops=copy.deepcopy(prefix);dets=copy.deepcopy(dets)
    contract=make_contract(sol.get('orientation',0),sol.get('late_c14',False));roles=sol.get('roles',contract.roles)
    role_A=list(map(int,roles.get('A',sol.get('A',A))));role_B=list(map(int,roles.get('B',sol.get('B',B))));role_C=list(map(int,roles.get('C',sol.get('C',C))))
    cells=list(map(int,sol.get('cells',CELLS+HELPERS)));t0=int(sol.get('T0',0))
    layers=[[tuple(e) for e in layer] for layer in sol['ops']]
    piv={int(q):int(v) for q,v in sol['pivots'].items()};rows={q:piv.get(q,0) for q in cells}
    target={int(q):int(v) for q,v in sol.get('target_columns',contract.COLS).items() if int(q) in cells}
    for layer in layers:
        used=set()
        for a,b in layer:
            assert a in cells and b in cells and not used&{a,b}
            assert abs(a//6-b//6)+abs(a%6-b%6)==1
            used.update((a,b));rows[b]^=rows[a]
    assert rows==target,(rows,target)
    assert sum(bool(v) for v in piv.values())==int(sol.get('state_rank',contract.rank))
    late={int(r['qubit']):r for r in sol.get('late_initializations',[])}
    initializations=[];reused=[]
    for q in cells:
        touches=[t0+t for t,layer in enumerate(layers) if any(q in e for e in layer)]
        if not touches:
            if q in late or q not in CELLS:continue
            touches=[max(max(o.time for o in prefix)+1,t0+len(layers))]
        first=min(touches);kind='RX' if piv.get(q,0) else 'R';axis='X' if kind=='RX' else 'Z'
        known=states[q].get('product_axis')==axis and not states[q].get('phase_xor') and not states[q].get('phase_constant')
        conditional=(q==17 and axis=='X' and states[q].get('phase_xor')==[311] and not states[q].get('phase_constant') and not(piv[q]&15))
        if conditional and first==release[q]:
            assert complete_records,'Conditional resource phases require recomputing the complete affine record contract.'
            reused.append(dict(qubit=q,time=first,axis=axis,phase_xor=[311]));continue
        if first==release[q] and known:
            reused.append(dict(qubit=q,time=first,axis=axis));continue
        assert first-1>=release[q],('input initialization before release',q,first,release[q])
        ops.append(f.Op(kind,(q,),first-1));initializations.append(dict(qubit=q,time=first-1,kind=kind))
    for t,layer in enumerate(layers):ops.extend(f.Op('CX',e,t0+t) for e in layer)
    for q,r in late.items():
        t=int(r['time']);assert t>=release[q]
        assert not any(q in o.qs and o.time>=t for o in ops if o not in prefix),('late init overlaps resource lifetime',q,t)
        ops.append(f.Op(r['kind'],(q,),t))
    R=max(max(o.time for o in ops)+1,max(o.time for o in prefix)+1)
    firstbit=max((o.bit for o in prefix if o.bit is not None),default=-1)+1
    for i,(d,a,b,c) in enumerate(zip(D,role_A,role_B,role_C)):
        ops.extend([f.Op('CX',(d,a),R),f.Op('CX',(b,c),R),f.Op('CX',(b,d),R+1)])
        if int(sol.get('square_mask',63))>>i&1:ops.append(f.Op('CX',(c,a),R+1))
    for offset,block,kind in [(0,role_A,'M'),(7,role_B,'MX'),(14,role_C,'MX')]:
        ops.extend(f.Op(kind,(q,),R+2,firstbit+offset+i) for i,q in enumerate(block))
    if not complete_records:dets += [{firstbit+b for b in row} for row in DETECTORS]
    helpers=[q for q in HELPERS if any(q in e for layer in layers for e in layer)]
    for j,q in enumerate(helpers):
        ops.append(f.Op('M',(q,),R,firstbit+21+j));dets.append({firstbit+21+j})
    seen={}
    for o in ops:
        for q in o.qs:
            key=o.time,q
            assert key not in seen,('collision',key,seen.get(key),o)
            seen[key]=o
    ops.sort(key=lambda o:o.time)
    added=[]
    if complete_records:
        f.DATA=list(D);model=f.make_model(*f.parse_current(emit(ops,dets)));affine=complete(model,dets)
        added=[r for r in affine['missing'] if any(b>=firstbit for b in r['bits'])]
        assert all(not r['reference'] for r in added),added
        dets += [set(r['bits']) for r in added]
    text=emit(ops,dets);raw=raw_check(text,D)
    meta=dict(source_boundary=boundary,resource_solution=sol,roles=dict(D=D,A=role_A,B=role_B,C=role_C),release=release,resource_initializations=initializations,
        reused_product_inputs=reused,late_initializations=list(late.values()),terminal_start=R,helper_checks=helpers,
        extra_record_checks=added,raw=raw,full_native_assembly=True,
        noise_scope='Full official operation and idle noise; no idealized resources or removed elapsed time.')
    stem=write_stem(text,D,HERE/'boundary',name,source=meta)
    stem.with_suffix('.integration.json').write_text(json.dumps(dict(stem=str(stem),**meta),indent=2)+'\n')
    print(json.dumps(dict(stem=str(stem),raw=raw,terminal_start=R,cx=sum(o.kind=='CX' for o in ops),ticks=R+3,
        reused=reused,late_initializations=list(late.values())),indent=2),flush=True)
    return stem,raw

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('solution');ap.add_argument('--name');ap.add_argument('--prefix');ap.add_argument('--states');ap.add_argument('--price',action='store_true');a=ap.parse_args()
    p=Path(a.solution);sol=json.loads(p.read_text());stem,raw=integrate(sol,a.name or 'partial_'+p.stem,a.prefix,a.states)
    if a.price and raw['ok']:print(json.dumps(price(stem,processes=1),indent=2),flush=True)
