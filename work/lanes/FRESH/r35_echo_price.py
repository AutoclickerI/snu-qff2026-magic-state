from r35_echo import *
import itertools
if __name__=='__main__':
 source=D/'feedback_best';gen(source);stems=json.loads((D/'echo_stems.json').read_text());rows=[]
 for s in stems:
  stem=Path(s);r=price(stem,7);r['stem']=s;rows.append(r);print('SINGLE',json.dumps(r),flush=True)
 (D/'echo_results.json').write_text(json.dumps(rows,indent=2))
 # Keep the best window on each protected qubit before pricing combinations.
 best={}
 for row in rows:
  stem=Path(row['stem']);e=json.loads(stem.with_suffix('.json').read_text())['recipe']['echo'];q=e[0]
  if q not in best or row['loss']<best[q][0]['loss']:best[q]=(row,e)
 ops,dets,md=load(source)
 for n in range(2,len(best)+1):
  for keys in itertools.combinations(sorted(best),n):
   oo,dd=copy.deepcopy(ops),copy.deepcopy(dets);recipe=[]
   try:
    for q in keys:
     e=best[q][1];oo,dd=add(oo,dd,*e);recipe.append(e)
    target=emit('echo_combo_'+'_'.join(map(str,keys)),oo,dd,md,dict(source=str(source),echoes=recipe));certify(target);r=price(target,7);r['stem']=str(target);rows.append(r);print('COMBO',json.dumps(r),flush=True)
   except Exception as e:print('REJECT_COMBO',keys,repr(e),flush=True)
 (D/'echo_results.json').write_text(json.dumps(rows,indent=2));print('DONE',flush=True)
