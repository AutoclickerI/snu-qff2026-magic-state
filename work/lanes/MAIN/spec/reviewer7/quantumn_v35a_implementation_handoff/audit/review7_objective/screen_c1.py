"""Look for sub-p/30 harmful single-fault contributions after legal detector deletion.
This does not seek or claim a competitive circuit; it tests a purported universal quantum.
"""
from pathlib import Path
import sys,json,time,copy
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'audit/review6_tail'))
import frontend as f
src=ROOT/'audit/review6_architecture/v31s_a_decode'
f.DATA=json.loads(src.with_suffix('.json').read_text())['data_qubits']
text=src.with_suffix('.qasm').read_text();ops,ds=f.parse_current(text)
indices=list(map(int,sys.argv[1:])) or list(range(14))
results=[]
for drop in indices:
    dets=ds[:drop]+ds[drop+1:] if drop>=0 else []
    m=f.make_model(ops,dets);e=f.Engine(m)
    a0,n0=e.ntable(0,0);assert a0>1-1e-9 and abs(n0[0])<1e-9
    cache={};rows=[]
    for fault in m.faults:
        k=(fault['s'],fault['d'])
        if k not in cache:cache[k]=e.ntable(*k)
        a,n=cache[k]
        if n is None:continue
        loss=float(n[fault['e']])
        if loss>1e-10:
            rows.append(dict(fault,accepted_mass=float(a),unnormalized_loss=loss,
                             conditional_loss=loss/a,first_order_contribution=fault['p']*loss))
    out=dict(drop_detector=drop,removed_bits=sorted(ds[drop]) if drop>=0 else "ALL",harmful_count=len(rows),
             first_order_loss=sum(x['first_order_contribution'] for x in rows),
             minimum=min(rows,key=lambda x:x['first_order_contribution']) if rows else None,
             small=[r for r in rows if r['first_order_contribution']<1/30000-1e-12])
    results.append(out)
    print(json.dumps(out),flush=True)
    if out['small']:
        stem=HERE/f'v31s_a_decode_drop{drop}'
        lines=[l for l in text.splitlines() if not l.startswith('// DETECTOR')]
        lines += ['// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(d)) for d in dets]
        stem.with_suffix('.qasm').write_text('\n'.join(lines)+'\n')
        stem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=f.DATA,scope=__doc__,dropped_detector=drop),indent=2)+'\n')
        break
(HERE/'c1_screen.json').write_text(json.dumps(results,indent=2)+'\n')
