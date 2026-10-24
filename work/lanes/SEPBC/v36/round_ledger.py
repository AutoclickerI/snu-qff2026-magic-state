"""Resolve the dominant round region into coupling types and output-data idle."""
from ledger import *
original_region=region
PARTS=['DA_coupling','BC_check','BD_coupling','final_data_idle','other_round']
def detail(qs,t,idle=False):
 r=original_region(qs,t,idle)
 if r!='round':return'outside_round'
 if idle:return'final_data_idle'
 qs=tuple(sorted(qs))
 for name,pairs in [('DA_coupling',zip(D,A)),('BC_check',zip(B,C)),('BD_coupling',zip(B,D))]:
  if qs in[tuple(sorted(x))for x in pairs]:return name
 return'other_round'
import ledger
ledger.region=detail
if __name__=='__main__':
 for part in PARTS[:-1]:
  old=sw.fa.noise_blocks;sw.fa.noise_blocks=masked(old,sw.fa.schedule,set(PARTS+['outside_round'])-{part});od=V/'ledger'/('detail_'+part);od.mkdir(parents=True,exist_ok=True);sw.__file__=str(od/'sparse_walsh.py')
  try:
   with(od/'sparse.log').open('w')as f,contextlib.redirect_stdout(f):r=sw.run(V/'base',72,True,procs=4)
  finally:sw.fa.noise_blocks=old
  r['part']=part;(V/'ledger'/f'detail_{part}.json').write_text(json.dumps(r,indent=2));print(part,r['loss'],r['acceptance'],flush=True)
