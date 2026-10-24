from a35_funding import reset_checks,save
from a35_guard_patches import *
patches=json.loads((D/'guard_patches.json').read_text());base=json.loads((D/'candidates/frontier_004.json').read_text())['options'];enc=base['enc'];ss=[];errors=[];seen=set()
for checks in [enc['pivots'],A,[1,9,16],[8,16],[1,9],[16],[]]:
 for change in ['reset','H']:
  try:s,m=make(enc,checks,[2,14],change,delay=1)
  except (ValueError,AssertionError) as ex:errors.append([checks,change,repr(ex)]);continue
  stem=D/'candidates'/f'local_{len(ss):03}_base';stem.with_suffix('.qasm').write_text(s);stem.with_suffix('.json').write_text(json.dumps(m,indent=2))
  for tag in ['headroom','guard_gain']:
   try:body,md=apply(stem,patches[tag])
   except (ValueError,AssertionError) as ex:errors.append([tag,repr(ex)]);continue
   parent=D/'candidates'/f'local_{len(ss):03}_{tag}';parent.with_suffix('.qasm').write_text(body);parent.with_suffix('.json').write_text(json.dumps(md,indent=2))
   for n in ([5,8] if tag=='headroom' else [10]):
    body,md=reset_checks(parent,[181,182,188,186,187,185,183,184,271,3][:n]);out=D/'candidates'/f'refine_{len(ss):03}';out.with_suffix('.qasm').write_text(body);out.with_suffix('.json').write_text(json.dumps(md,indent=2));key=physical_key(out)
    if key in seen:out.with_suffix('.qasm').unlink();out.with_suffix('.json').unlink();continue
    seen.add(key);ss.append(str(out.relative_to(H)))
(D/'refine.json').write_text(json.dumps(ss,indent=2));(D/'refine_errors.json').write_text(json.dumps(errors,indent=2));print('refinements',len(ss),'invalid schedules',len(errors),flush=True)
