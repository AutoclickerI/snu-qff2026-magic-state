from common import *
import itertools,collections
G=[sum(1<<i for i in r)for r in[[0,2,4,6],[1,2,5,6],[3,4,5,6]]]
def audit(ops,piv):
 faults=[]
 for loc in range(-1,len(ops)):
  masks=[1<<i for i in range(7)if i not in piv]if loc<0 else[1<<ops[loc][0],1<<ops[loc][1],(1<<ops[loc][0])^(1<<ops[loc][1])]
  for e in masks:
   for u,v in ops[loc+1:]:
    if e>>u&1:e^=1<<v
   sy=sum(((e&r).bit_count()%2)<<i for i,r in enumerate(G));bad=(e.bit_count()%2)^int(sy!=0)
   if bad:faults.append(dict(gate=loc,mask=e,syndrome=sy))
 return dict(harmful_syndromes=sorted({f['syndrome']for f in faults}),missing=[i for i in range(1,8)if all(f['syndrome']!=i for f in faults)],pure_logical=any(f['syndrome']==0 for f in faults),faults=faults)
x=json.loads((ROOT/'work/lanes/ENDSTATE/templates.json').read_text());rows=[]
for t in x:
 if t['cx']>12:continue
 z=t['zero'];r=audit(z['ops'],z['pivots'])
 if r['missing']and not r['pure_logical']:rows.append(dict(id=t['id'],cx=t['cx'],depth=t['depth'],shape=t['shape'],zero=z,**r))
rows.sort(key=lambda r:(r['cx'],r['depth'],-len(r['missing'])));out=dict(eligible_templates=len(rows),by_cx=dict(collections.Counter(r['cx']for r in rows)),templates=rows);(H/'b_two_check_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items()if k!='templates'}));print(json.dumps(rows[:8]))
append_result('B_two_check_single_fault_audit',dict(eligible_templates=len(rows),by_cx=out['by_cx'],best=[{k:r[k]for k in('id','cx','depth','missing','harmful_syndromes')}for r in rows[:8]]),'Complete X-component single-fault propagation for native unitary B preparation; missing syndrome permits a rank-two Z-check projection at first order only. Double/triple faults and complete-circuit performance remain unmeasured.')
