"""Re-derive WAITPROT's menu on v36a, remapping records and checking slots."""
from edits import *
menu=json.loads((V/'inputs/menu_v35a.json').read_text());rows=json.loads((V/'wait_builds.json').read_text())if(V/'wait_builds.json').exists()else[];seen={r['screen']['sha256']:r['stem']for r in rows if'screen'in r};done={r['stem']for r in rows}
for i,item in enumerate(menu['entries']):
 name=item.get('integration_name',f'wait_{i:03d}')
 if name in done:continue
 edit=item.get('lines');family=item['description']['family'];attempts=[];chosen=None
 if edit is None:
  src=ROOT/(item['stem']+'.qasm')
  if src.exists():
   old=read(V/'inputs/v35a');new=read(src.with_suffix(''));a=collections.Counter((o['t'],tuple(o['lines']))for o in old['ops']);b=collections.Counter((o['t'],tuple(o['lines']))for o in new['ops'])
   edit=dict(remove=[dict(t=t,lines=list(ls))for t,ls in(a-b).elements()],add=[dict(t=t,lines=list(ls))for t,ls in(b-a).elements()],detector_remove=sorted(set(old['tail'])-set(new['tail'])),detector_add=sorted(set(new['tail'])-set(old['tail'])))
  else:
   rows.append(dict(stem=name,gadget=item['gadget'],family=family,status='menu has no physical delta and source file is absent',source=item['stem']));(V/'wait_builds.json').write_text(json.dumps(rows,indent=2));continue
 # Preserve the specified slot where possible; for a conflict, try nearby
 # whole-gadget translations, keeping the existing v36a schedule fixed.
 for shift in [0,-1,1,-2,2,-3,3]:
  try:
   c=patch(base(),edit,shift);_,txt=normalized(c)
   ev=exact2.Eval(txt,c['meta']['data_qubits'])
   chosen=(c,shift,txt);break
  except Exception as e:attempts.append(dict(shift=shift,error=repr(e)[:1200]))
 row=dict(stem=name,gadget=item['gadget'],family=family,source=item['stem'],source_description=item['description'],patch=edit,attempts=attempts)
 if chosen:
  c,shift,txt=chosen;row['shift']=shift;key=hashlib.sha256(txt.encode()).hexdigest()
  if key in seen:row['byte_identical_to']=seen[key];print(name,'alias',seen[key],flush=True)
  else:
   try:st,r=write(c,name,dict(family='WAITPROT_reprice',gadget=item['gadget'],native_shift=shift));row['screen']=r;seen[key]=name
   except Exception as e:row['error']=repr(e);print(name,repr(e),flush=True)
 else:row['status']='no valid port in tested translations';print(name,row['status'],flush=True)
 rows.append(row);(V/'wait_builds.json').write_text(json.dumps(rows,indent=2))
