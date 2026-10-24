from a35_guard_patches import *
from a35_funding import reset_checks
patches=json.loads((D/'guard_patches.json').read_text());ss=[];seen={physical_key(p.with_suffix('')) for p in (D/'candidates').glob('f0_*.qasm')};counts=collections.Counter()
for k,r in enumerate(json.loads((D/'exenc14_shortfrontier.json').read_text())):
 enc=dict(r['circuit'],name=f'shortfrontier_{k}')
 for checks in [[],enc['pivots']]:
  try:body,md=make(enc,checks,[2,14],'reset',1)
  except (ValueError,AssertionError) as e:counts[str(e)]+=1;continue
  base=D/'candidates'/f'shortlocal_{k}_{len(checks)}';base.with_suffix('.qasm').write_text(body);base.with_suffix('.json').write_text(json.dumps(md,indent=2))
  for tag,n in [('headroom',8),('guard_gain',10)]:
   try:body,md=apply(base,patches[tag])
   except (ValueError,AssertionError) as e:counts[str(e)]+=1;continue
   par=D/'candidates'/f'shortlocal_{k}_{len(checks)}_{tag}';par.with_suffix('.qasm').write_text(body);par.with_suffix('.json').write_text(json.dumps(md,indent=2))
   body,md=reset_checks(par,[181,182,188,186,187,185,183,184,271,3][:n]);out=D/'candidates'/f'shortfront_{len(ss):03}';out.with_suffix('.qasm').write_text(body);out.with_suffix('.json').write_text(json.dumps(md,indent=2));key=physical_key(out)
   if key in seen:out.with_suffix('.qasm').unlink();out.with_suffix('.json').unlink();continue
   seen.add(key);ss.append(str(out.relative_to(H)))
(D/'shortfrontier.json').write_text(json.dumps(ss,indent=2));print('generated',len(ss),dict(counts),flush=True)
