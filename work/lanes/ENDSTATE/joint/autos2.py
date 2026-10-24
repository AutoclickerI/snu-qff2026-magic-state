"""Enumerate all168 common Steane automorphisms on the promising fixed BC region."""
import itertools,json,copy
from pathlib import Path
from timing import schedule
H=Path(__file__).resolve().parent;row=json.loads((H/'labelled_regions.json').read_text())[2];ap=json.loads((H/'A2_top2.json').read_text());row['a_prep']=dict(ap,ops=[e for layer in ap['ops']for e in layer]);gens=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
def span(gs):
 s={0}
 for g in gs:s|={x^g for x in list(s)}
 return s
target=span([sum(1<<i for i in g)for g in gens]);autos=[p for p in itertools.permutations(range(7))if span([sum(1<<p[i]for i in g)for g in gens])==target];assert len(autos)==168
out=[]
for ai,perm in enumerate(autos):
 r=copy.deepcopy(row);r['name']=f'row2_auto{ai}';r['final']={k:[v[i]for i in perm]for k,v in row['final'].items()};r['common_automorphism']=perm
 try:t=schedule(r,11,0,8)
 except Exception as e:t=dict(error=repr(e))
 out.append(dict(auto=ai,row=r,schedule=t));print(ai,t.get('R'),t.get('data_hops'),t.get('status',t.get('error')),flush=True)
(H/'autos2.json').write_text(json.dumps(out,indent=1))
