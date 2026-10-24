from r37 import *
# Whole-round dual: A0 measures X syndromes, B+ measures Z syndromes.
# Conjugate all prefix T signs, and Sdg transversally maps |T*_L> back to |T_L>.
orig,dets,md=load(BASE);A=[1,14,8,9,2,16,15];B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28];data=md['data_qubits']
sat=json.loads((HERE/'r36/dual_sat_prefix_44.json').read_text())[-1];pre=json.loads((HERE/'r36/prefix_release.json').read_text())
# Apply only the certified commuting prefix moves identifiable by logical op/bit.
oo=copy.deepcopy(orig)
for move in pre['moves']:
 if move['old']<28:continue
 if move['bit'] is not None:matches=[o for o in oo if o.bit==move['bit']]
 else:matches=[o for o in oo if o.kind==move['kind'] and o.qs==tuple(move['qs']) and o.time==move['old']]
 if len(matches)==1:
  target=matches[0];at=move['new']
  # Fixed schedule changed in v36b. Only independent legal source changes considered.
  if not any(o is not target and o.time==at and set(o.qs)&set(target.qs) for o in oo):target.time=at
# Restore source releases to safe actual times and synthesize encoder ALAP may need slot adjustment.
# Strip actual v36b A preparation after each source boundary, while preserving source flags.
init={1:38,14:37,8:36,9:38,2:36,16:39,15:40}
owned=[o for o in oo if set(o.qs)<=set(A) and all(o.time>=init[q] for q in o.qs) and o.time<=43]
assert sum(o.kind=='CX' for o in owned)==12
bits={o.bit for o in owned if o.bit is not None};oo=[o for o in oo if o not in owned];dd=[row.copy() for row in dets if not(row&bits)]
# Use the earlier complete prefix schedule for source gates that need enough release slack.
# Match each source segment through its own bit identity and three CX path edges.
for q,bit in {1:64,14:12,8:54,9:56,2:67,16:55,15:57}.items():
 match=next(o for o in oo if o.bit==bit);print('RELEASE',q,match.time,'wanted',pre['release'][str(q)],flush=True)
# Rather than silently violate a release, delay encoder/round as a whole if needed.
encops=[f.Op('CX',(a,b),t) for a,b,t in sat['ops']]
for q,t in sat['release'].items():
 q=int(q)
 if q in sat['pivots'] or q in (2,14):encops.append(f.Op('RX' if q in sat['pivots'] else 'R',(q,),t-1))
for o in encops:
 conflict=[x for x in oo if set(x.qs)&set(o.qs) and x.time==o.time]
 assert not conflict,(o,conflict)
# Exact resource dual on the B/C region only (preparation, verification, readout).
starts={6:41,26:32,13:33,11:33,4:36,23:32,27:32,12:37,25:33,19:33,17:32,5:35,29:32,28:32}
for o in oo:
 if o.kind in ('T','TDG'):o.kind='TDG' if o.kind=='T' else 'T'
 if o.kind=='CX' and o.qs in list(zip(data,A)) and o.time>=43:o.qs=o.qs[::-1]
 elif o.kind=='CX' and o.qs in list(zip(B,data)) and o.time==45:o.qs=o.qs[::-1]
 elif o.kind=='CX' and o.time>=44 and set(o.qs)<=set(A):o.qs=o.qs[::-1]
 elif o.bit in range(14,21) if o.bit is not None else False:o.kind='M' if o.kind=='MX' else 'MX'
 elif o.kind=='CX' and o.qs==(17,16) and o.time==45:o.qs=(16,17)
 elif set(o.qs)<=set(B+C) and all(o.time>=starts[q] for q in o.qs):
  if o.kind=='CX':o.qs=o.qs[::-1]
  elif o.kind in ('R','RX','M','MX'):o.kind={'R':'RX','RX':'R','M':'MX','MX':'M'}[o.kind]
 elif o.time>=44 and (set(o.qs)&{18,31,35,34}):
  if o.kind=='CX':o.qs=o.qs[::-1]
  elif o.kind in ('R','M'):o.kind={'R':'RX','M':'MX'}[o.kind]
# Phase at43; preceding q10/q20 non-Clifford gates move earlier one tick.
for q in data:
 for o in oo:
  if o.qs==(q,) and o.time==(42 if q in (10,21) else 43) and o.kind in ('T','TDG'):o.time-=1
 oo.append(f.Op('SDG',(q,),42 if q in (10,21) else 43))
s=emit37('dual_frame',oo+encops,dd,md,dict(base='MAIN/v36b',architecture='A0/B+ dual round, conjugated prefix, transversal Sdg restore'))
r=audit(s);print('AUDIT',json.dumps({k:v for k,v in r.items() if k not in ('ideal','static','harmful_singles','trace')}),flush=True);print('STATIC',r.get('static',{}).get('prediction'),r.get('static',{}).get('general_atoms'),flush=True)
if r.get('c1',1)<1e-12:print('PRICE',price(s,7),flush=True)
