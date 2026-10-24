from round35 import *
from r36_static import diagnostic
OUT=HERE/'r36';pre=json.loads((OUT/'prefix_release.json').read_text());sat=json.loads((OUT/'dual_sat_prefix_44.json').read_text())[-1];assert sat['status'] in ('FEASIBLE','OPTIMAL')
A=[1,14,8,9,2,16,15];data=pre['meta']['data_qubits']
oo=[f.Op(o['kind'],tuple(o['qs']),o['time'],o['bit'],o['line']) for o in pre['ops']]
oo=[o for o in oo if not (o.time>=43 and (o.bit in range(14,21) if o.bit is not None else False)) and not (o.time>=44 and o.kind=='CX' and (set(o.qs)<=set(A) or o.qs==(17,16)))]
for o in oo:
 if o.kind=='CX' and o.qs in list(zip(data,A)) and o.time>=43:o.time=44
for q,t in sat['release'].items():
 q=int(q)
 if q in sat['pivots'] or q in (2,14):oo.append(f.Op('RX' if q in sat['pivots'] else 'R',(q,),t-1))
oo.extend(f.Op('CX',(a,b),t) for a,b,t in sat['ops'])
dd=[set(row) for row in pre['dets'] if not(set(row)&set(range(14,21)))]
for j,q in enumerate(data):oo.append(f.Op('MX',(q,),46,400+j))
dd += [{400+j for j in row} for row in f.SUPPORTS]
s=emit('teleport0_sat',oo,dd,dict(data_qubits=A,R=44),dict(base='MAIN/v35b',encoder=sat,prefix_moves=pre['moves'],architecture='encoded identity teleport with A0',output=A))
with s.with_suffix('.qasm').open('a') as ff:ff.write('// FRAME_Z(0) '+' '.join(f'c[{400+j}]' for j in range(7))+'\n')
f.FRAME_Z=list(range(400,407));print('IDEAL',certify(s),flush=True);r=diagnostic(s);print('STATIC',r['failed_atoms'],r['bad_gates'],flush=True);print('SPEED',speed(s,5000),flush=True)
