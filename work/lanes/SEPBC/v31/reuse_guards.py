"""A heralded guard output can already be the resource's known-zero input."""
from build import *
import wide_moments,itertools
base=json.loads((V/'guard5_timing_1.plan.json').read_text());rows=[]
for qs in [(5,),(11,),(5,11),(19,),(13,)]:
 c=copy.deepcopy(base);name='reuse_'+''.join(str(q)+'_'for q in qs).rstrip('_');removed=[]
 for q in qs:
  seq=[o for o in c['ops']if q in unit(o).qs]
  last_guard=max(i for i,o in enumerate(seq)if o.get('tag')=='wait_guard')
  o=seq[last_guard+1];assert unit(o).name in ('MEASURE','RESET'),o
  if unit(o).name=='MEASURE':
   b=int(re.findall(r'c\[(\d+)\]',o['lines'][0])[0]);refs=[l for l in c['tail']if b in map(int,re.findall(r'c\[(\d+)\]',l))];assert refs==[f'// DETECTOR c[{b}]'],refs;c['tail'].remove(refs[0])
  removed.append(o);c['ops'].remove(o)
 st=save(fix(c),'v31/'+name);r=wide_moments.evaluate(exact2.Eval(st.with_suffix('.qasm').read_text(),c['meta']['data_qubits']));st.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));row=dict(stem=name,removed=removed,screen=r);rows.append(row);append_result(name,row,'Use the heralded Z-zero guard output directly for the resource, removing only the next init and its singleton check if present. Full remaining predicate and noise repriced.');print(name,json.dumps(r),flush=True)
(V/'reuse_guards.json').write_text(json.dumps(rows,indent=2))
