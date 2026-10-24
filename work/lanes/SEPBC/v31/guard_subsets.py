"""Exhaustive joint price of the five native-slot WAITPROT guards."""
from build import *
import itertools
# Load definitions without executing waitport's scan again.
ns={};exec((V/'waitport.py').read_text().split('rows=[]')[0],ns)
add=ns['add'];base=ns['base'];singles=json.loads((V/'waitport_singles.json').read_text())
rows=[]
for k in range(2,len(singles)+1):
 for subset in itertools.combinations(singles,k):
  name='guards_'+''.join(x['stem'].split('_')[-1]for x in subset);c=copy.deepcopy(base)
  try:
   for row in subset:c=add(c,row['recipe'])
   c,txt=normalized(c);r=mom.evaluate(exact2.Eval(txt,c['meta']['data_qubits']))
   row=dict(stem=name,guards=[x['stem']for x in subset],screen=r)
   if r['exp_minus_A1']>=.5002 and r['total']<5.063e-5:
    st=save(c,'v31/'+name);row['screen']=score(st)
   rows.append(row);print(name,json.dumps(row),flush=True)
  except Exception as e:
   row=dict(stem=name,error=repr(e));rows.append(row);print(name,json.dumps(row),flush=True)
(V/'guard_subsets.json').write_text(json.dumps(rows,indent=2))
