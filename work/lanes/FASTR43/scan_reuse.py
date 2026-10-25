# Static screen: for each reset that directly follows a measurement on the same qubit (nothing in between),
# remove the reset (reuse the measured state) and run the static general-atom screen. Timing unchanged.
from fr import *
import general_atoms as g
ops,dets,md=load(V36F)
byq={}
for o in sorted(ops,key=lambda o:o.time):
    for q in o.qs: byq.setdefault(q,[]).append(o)
rows=[]
for q,seq in byq.items():
    for a,b in zip(seq,seq[1:]):
        if a.kind in ('M','MX') and b.kind in ('R','RX'):
            o2=copy.deepcopy(ops); o2.remove(find(o2,b.kind,b.qs,b.time))
            s=emit(f'scan_reuse_q{q}_{b.time}',o2,copy.deepcopy(dets),md,dict(removed=f'{b.kind}{q}@{b.time}'))
            r=g.analyze(str(s),True)
            bad=sorted({a_['first_bad_gate'] for a_ in r.get('atoms',[])})
            row=dict(q=q,meas=f'{a.kind}@{a.time}(c{a.bit})',reset=f'{b.kind}@{b.time}',pred=r['prediction'],atoms=r['general_atoms'],bad_gates=[x['instruction'] for x in r['offending_gates']])
            rows.append(row);print(json.dumps(row),flush=True)
            for ext in ('.qasm','.json'): s.with_suffix(ext).unlink()
Path('scan_reuse.json').write_text(json.dumps(rows,indent=1))
