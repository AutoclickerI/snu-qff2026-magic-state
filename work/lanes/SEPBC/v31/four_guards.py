from build import *
import wide_moments,itertools
ns={};exec((V/'waitport.py').read_text().split('rows=[]')[0],ns)
base=ns['base'];add=ns['add'];singles=json.loads((V/'waitport_singles.json').read_text());rows=[]
for k in [4,5]:
 for subset in itertools.combinations(singles,k):
  name='guards_'+''.join(x['stem'].split('_')[-1]for x in subset);c=copy.deepcopy(base)
  for row in subset:c=add(c,row['recipe'])
  st=save(c,'v31/'+name);r=wide_moments.evaluate(exact2.Eval(st.with_suffix('.qasm').read_text(),c['meta']['data_qubits']))
  r['batching']='wide_moments.py: exact identity-projector rejection; no detector removed'
  st.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));rows.append(dict(stem=name,screen=r));print(name,json.dumps(r),flush=True)
(V/'four_guards.json').write_text(json.dumps(rows,indent=2))
