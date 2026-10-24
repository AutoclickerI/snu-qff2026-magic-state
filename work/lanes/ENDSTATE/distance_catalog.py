from native import *
from fast_templates import AUT

def compute(stem):
 d=json.loads(Path(str(stem)+'.json').read_text());rows=[]
 for name in ['v23h_c2c9','v29c']:
  p=json.loads((H/(name+'.prefix.json')).read_text())
  for ei,em in enumerate(p['embeddings']):
   mp={int(q):v for q,v in em['mapping'].items()};start=[mp[q]for q in p['data_qubits']];choices=[]
   for aut in AUT:
    end=[d['final']['d'][j]for j in aut];dist=[abs(q//6-v//6)+abs(q%6-v%6)for q,v in zip(start,end)];lb=max(p['last_data_asap'][str(q)]+1+2*dd for q,dd in zip(p['data_qubits'],dist));choices.append((lb,sum(dist),max(dist),aut,dist))
   x=min(choices);rows.append(dict(prefix=name,embedding=ei,sym=em['sym'],row=em['row'],col=em['col'],data_start=start,R_lower_bound=x[0],total_hops_lower_bound=x[1],max_hops_lower_bound=x[2],automorphism=x[3],per_label_hops_lower_bound=x[4]))
 out=dict(candidate=str(stem),scope='Manhattan geometric lower bounds; 48 prefix embeddings and all 168 common Steane automorphisms; no routing collisions or ancillary preparation time included',rows=rows)
 Path(str(stem)+'.prefix_distances.json').write_text(json.dumps(out,indent=2))
 for n in ['v23h_c2c9','v29c']:print(n,sorted([r for r in rows if r['prefix']==n],key=lambda r:(r['R_lower_bound'],r['total_hops_lower_bound']))[:2])
if __name__=='__main__':compute(Path(sys.argv[1]))
