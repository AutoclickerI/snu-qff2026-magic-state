from r37 import *
OUT=HERE/'r36';pre=json.loads((OUT/'prefix_release.json').read_text());sat=json.loads((OUT/'dual_sat_prefix_44.json').read_text())[-1]
A=[1,14,8,9,2,16,15];B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28];data=pre['meta']['data_qubits']
oo=[f.Op(o['kind'],tuple(o['qs']),o['time'],o['bit'],o['line']) for o in pre['ops']];dd=[set(row) for row in pre['dets']]
starts={6:41,26:32,13:25,11:33,4:36,23:32,27:32,12:37,25:33,19:33,17:32,5:35,29:32,28:32}
for o in oo:
 if o.kind in ('T','TDG'):o.kind='TDG' if o.kind=='T' else 'T'
 if o.kind=='CX' and ((o.qs in list(zip(data,A)) and o.time>=43) or(o.qs in list(zip(B,data)) and o.time==45) or(o.time>=44 and set(o.qs)<=set(A)) or (o.qs==(17,16) and o.time==45)):o.qs=o.qs[::-1]
 elif o.bit is not None and o.bit in range(14,21):o.kind='M' if o.kind=='MX' else 'MX'
 elif set(o.qs)<=set(B+C) and all(o.time>=starts[q] for q in o.qs):
  if o.kind=='CX':o.qs=o.qs[::-1]
  elif o.kind in ('R','RX','M','MX'):o.kind={'R':'RX','RX':'R','M':'MX','MX':'M'}[o.kind]
 elif o.time>=44 and (set(o.qs)&{18,31,35,34}):
  if o.kind=='CX':o.qs=o.qs[::-1]
  elif o.kind in ('R','M'):o.kind={'R':'RX','M':'MX'}[o.kind]
# Dual of a deterministic Z preparation requires a plus preparation, not a random virgin MX.
removed_init=[]
for o in oo:
 if len(o.qs)==1 and o.qs[0] in starts and o.time==starts[o.qs[0]] and o.kind=='MX':
  removed_init.append(o.bit);o.kind='RX';o.bit=None
for row in dd:row.difference_update(removed_init)
dd=[row for row in dd if row]
for q in data:
 at=42 if q in (10,21) else 43
 for o in oo:
  if o.qs==(q,) and o.time==at and o.kind in ('T','TDG'):o.time-=1
 oo.append(f.Op('SDG',(q,),at))
for q,t in sat['release'].items():
 q=int(q)
 if q in sat['pivots'] or q in (2,14):oo.append(f.Op('RX' if q in sat['pivots'] else 'R',(q,),t-1))
oo.extend(f.Op('CX',(a,b),t) for a,b,t in sat['ops'])
s=emit37('full_dual',oo,dd,pre['meta'],dict(base='v35b prefix release witness',architecture='dual A/B/C round, conjugated prefix T signs, Sdg data restores T'))
r=audit(s);print('AUDIT',json.dumps({k:v for k,v in r.items() if k not in ('ideal','static','harmful_singles','trace')}),flush=True);print('STATIC',r.get('static',{}).get('prediction'),r.get('static',{}).get('general_atoms'),flush=True)
if r.get('harmful_singles'):print('HARM',r['harmful_singles'][:5],flush=True)
if r.get('c1',1)<1e-12:print('PRICE',price(s,1),flush=True)
