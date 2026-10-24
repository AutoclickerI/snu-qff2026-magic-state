"""Re-evaluate valid first-pass parity couplings as explicit physical recipes.

The first frame-init pass used declaration order instead of converter order.
Corrected frame2 receipts diagnose that mistake. These retained first-pass
circuits independently pass exact correctness, so their actual parity choices
remain legitimate detector-budget items; no intended-frame claim is made.
"""
from search import *

def main():
 source='final_m2c_l2';base=loadc(OUT/source);rows={r['stem']:r for r in map(json.loads,(OUT/'frameinit_results.jsonl').read_text().splitlines())};sites=[147,47,42,43];jobs=[]
 for mask in range(16):
  c=copy.deepcopy(base);c['t'][68]=10;rec=[]
  for j,i in enumerate(sites):
   if not(mask>>j&1):continue
   item=rows[f'frameinit_u{i}']['recipe'];u=c['u'][i];q=u.qs[0];b=230+j
   c['u'][i]=Unit(([f'h q[{q}];']if u.name=='RX'else[])+[f'measure q[{q}] -> c[{b}];']+([f'h q[{q}];']if u.name=='RX'else[]))
   d=0
   for k,line in enumerate(c['tail']):
    if line.startswith('// DETECTOR'):
     if item['detector_mask']>>d&1:c['tail'][k]=line+f' c[{b}]'
     d+=1
   rec.append(dict(unit=i,record=b,declaration_mask=item['detector_mask']))
  try:jobs.append(write(c,f'parity_{mask:02x}',dict(kind='explicit_parity_combo',source=source,gate_time=dict(unit=68,time=10),items=rec)))
  except Exception as e:print(mask,'error',repr(e),flush=True)
 (OUT/'parity_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n');print('parity combos',len(jobs),flush=True)

if __name__=='__main__':main()
