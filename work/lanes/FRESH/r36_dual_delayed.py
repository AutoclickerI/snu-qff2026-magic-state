from round35 import *
from r36_static import diagnostic
OUT=HERE/'r36';pre=json.loads((OUT/'prefix_release.json').read_text());sat=json.loads((OUT/'dual_sat_prefix_44.json').read_text())[-1];A=[1,14,8,9,2,16,15];data=pre['meta']['data_qubits'];B=[6,26,13,11,4,23,27]
ops=[f.Op(o['kind'],tuple(o['qs']),o['time'],o['bit'],o['line']) for o in pre['ops']];dets=[set(row) for row in pre['dets']];md=pre['meta']
ops=[o for o in ops if not(o.kind=='CX' and o.qs==(17,16) and o.time==45)]
for row in dets:
 if row&set(range(14,21)):row.discard(24)
for o in ops:
 if o.kind=='CX' and o.qs in list(zip(data,A)) and o.time>=43:o.qs=o.qs[::-1];o.time=44
 elif o.kind=='CX' and o.time>=44 and set(o.qs)<=set(A):o.qs=o.qs[::-1];o.time+=1
 elif o.kind=='CX' and o.qs in list(zip(B,data)) and o.time==45:o.time=46
 elif o.kind in ('M','MX') and o.bit in range(14,21):o.kind='M' if o.kind=='MX' else 'MX';o.time=47
 elif o.kind=='MX' and o.qs[0] in B and o.time==46:o.time=47
 elif o.kind=='TDG' and o.qs[0] in (10,20) and o.time>=42:o.time=42
for q in data:ops.extend([f.Op('SDG',(q,),43),f.Op('S',(q,),45)])
for q,t in sat['release'].items():
 q=int(q)
 if q in sat['pivots'] or q in (2,14):ops.append(f.Op('RX' if q in sat['pivots'] else 'R',(q,),t-1))
ops.extend(f.Op('CX',(a,b),t) for a,b,t in sat['ops'])
s=emit('dualY_delayed',ops,dets,md,dict(base='MAIN/v35b',prefix_moves=pre['moves'],encoder=sat,Y_check_time=44,phase_restoration=45,B_coupling_time=46,removed_prep_bits=pre['removed_prep_bits'],removed_readout_edge=[17,16]))
print('BUILT',s,flush=True);print('IDEAL',certify(s),flush=True);r=diagnostic(s);(OUT/'dualY_delayed.static.json').write_text(json.dumps(r,indent=2));print('STATIC',r['failed_atoms'],r['bad_gates'],flush=True);print('SPEED',speed(s,10000),flush=True);print('PRICE',price(s,7),flush=True)
