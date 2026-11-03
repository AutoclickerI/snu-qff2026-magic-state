import json,sys,time
from pathlib import Path
from collections import defaultdict
from qtools.evaluator import frontend as f
stem=Path(sys.argv[1]);text=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
f.DATA=data;ops,dets=f.parse_current(text);m=f.make_model(ops,dets);eng=f.Engine(m)
cache={};total=0;rows=[]
for ff in m.faults:
    key=(ff['s'],ff['d']);val=cache.get(key)
    if val is None:
        a,n=eng.ntable(*key);val=(a,n);cache[key]=val
    a,n=val
    loss=0. if n is None else float(n[ff['e']])
    if loss>1e-10:
        contribution=ff['p']*loss;total+=contribution
        op=ops[ff['ins']];rows.append(dict(p=ff['p'],loss=loss,contribution=contribution,t=op.time,k=op.kind,qs=ff['qs'],pauli=ff['pauli'],s=ff['s'],d=ff['d'],e=ff['e'],label=ff['label']))
rows.sort(key=lambda r:-r['contribution'])
out=dict(first_order=total,channels=len(m.chans),faults=len(m.faults),harmful=len(rows),rows=rows)
Path(str(stem)+'.singles.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(first_order=total,harmful=len(rows),top=rows[:20]),indent=2))
