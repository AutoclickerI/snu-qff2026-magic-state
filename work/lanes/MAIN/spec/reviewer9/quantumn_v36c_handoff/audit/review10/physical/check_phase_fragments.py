"""Independently replay emitted CNOT/TDG fragments over all 32 input assignments."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'phase_route_certificate.json').read_text())
valid=[r for r in r['results']if r['form']=='f14_1'and'error'not in r]
bestcx=min(valid,key=lambda r:(r['compute_uncompute_CX'],r['phase_fragment_ASAP_ticks']))
bestdepth=min(valid,key=lambda r:(r['phase_fragment_ASAP_ticks'],r['compute_uncompute_CX']))
data=[0,20,7,4,3,15,8];labels=[2,31,4,21,14,19,8]
receipts=[]
for name,rec in [('min_cx',bestcx),('min_depth',bestdepth)]:
 rows={q:0 for q in [0,1,2,3,4,6,7,8,9,10,13,14,15,19,20]};rows.update(zip(data,labels));initial=rows.copy()
 phase=[0]*32;lines=['// INCOMPLETE PHASE FRAGMENT: requires encoded input and enclosing verified circuit.','// Historical TREP coordinates: logical target=25; all helper input rows=0.']
 for op,a,b in rec['operations']:
  if op=='cx':
   assert abs(a//6-b//6)+abs(a%6-b%6)==1
   rows[b]^=rows[a];lines.append(f'cx q[{a}],q[{b}];')
  else:
   assert rows[a]==b
   sign=1 if op=='t'else-1
   phase=[(v+sign*((rows[a]&y).bit_count()%2))%8 for y,v in enumerate(phase)]
   lines.append(f'{op} q[{a}];')
 assert rows==initial
 assert phase==[(25&y).bit_count()%2 for y in range(32)]
 path=ROOT/f'phase14_{name}.qasm.inc';path.write_text('\n'.join(lines)+'\n')
 receipts.append({'name':name,'seed':rec['seed'],'CX':rec['compute_uncompute_CX'],'T':14,'ASAP_fragment_ticks':rec['phase_fragment_ASAP_ticks'],'symbolic_row_restoration':True,'phase_equal_all_32_assignments':True,'all_CX_grid_adjacent':True,'fragment':path.name})
(ROOT/'phase_fragment_verification.json').write_text(json.dumps(receipts,indent=2))
print(json.dumps(receipts,indent=2))
