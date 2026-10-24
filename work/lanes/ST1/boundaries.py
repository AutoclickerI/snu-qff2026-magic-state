from common import *
import bc_build as BC
import argparse
p=argparse.ArgumentParser();p.add_argument('stem');a=p.parse_args();stem=Path(a.stem).resolve();base=score(stem)
HBC=ROOT/'work/lanes/BCPOL';names=['endpoint_5_s712_00601','endpoint_5_s712_00138','endpoint_4_s711_00035'];c6={}
for path in(HBC/'finalists').glob('c6_[0-6]_*.screen.json'):
 row=json.loads(path.read_text());tag=path.name.removesuffix('.screen.json');pos=int(tag.split('_')[1])
 if row.get('total',1)<c6.get(pos,(1,None))[0]:c6[pos]=(row['total'],tag)
names +=[r[1]for r in sorted(c6.values())]
# Mandatory baseline transplant recovery through the same builder.
prep=json.loads((HBC/'inputs/base.prep.json').read_text());prep.update(kind='policy',value=9)
md,head,units,times,tail,init,rem=BC.source(base=str(stem));mx=[q for q,i in init.items()if units[i].name=='MX']
txt,meta=BC.build(prep,dict(base=str(stem),timing='project',mx=mx));(H/'boundary_control.qasm').write_text(txt);(H/'boundary_control.json').write_text(json.dumps(meta,indent=2));control=score(H/'boundary_control');err=max(abs(control[k]-base[k])for k in['second','third','total']);assert err<1e-14,(base,control,err)
(H/'boundary_control.validation.json').write_text(json.dumps(dict(error=err,reference=base,control=control),indent=2));print('recovery',err,flush=True)
for tag in names:
 d=json.loads((HBC/'finalists'/f'{tag}.json').read_text())['prep']
 for shift in [0,-1]:
  name='boundary_'+tag+f'_r{shift}';options=dict(base=str(stem),timing='alap',mx=[q for q in d['pivots']if q!=19],round_shift=shift,retime_window=2 if shift else 0)
  try:
   txt,meta=BC.build(d,options);(H/(name+'.qasm')).write_text(txt);(H/(name+'.json')).write_text(json.dumps(meta,indent=2));r=score(H/name)
  except Exception as e:r=dict(error=str(e))
  append_result(name,r,'Joint moving-prefix exterior plus BCPOL reduced endpoint/C6 contract; full exact objective, independent B/C predicate from BCPOL. '+json.dumps(options));print(name,r,flush=True)
