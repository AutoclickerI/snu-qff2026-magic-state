from native import *
def d4(q,k):
 r,c=divmod(q,6);rr,cc=[(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k];return rr*6+cc
for f in H.glob('*.catalog.prefix_distances.json'):
 x=json.loads(f.read_text());summary={}
 for name in ['v23h_c2c9','v29c']:
  p=json.loads((H/(name+'.prefix.json')).read_text());reps={f'r{em["row"]}c{em["col"]}':em for em in p['embeddings']if em['sym']==0};groups=collections.defaultdict(list)
  for row in x['rows']:
   if row['prefix']!=name:continue
   mp=p['embeddings'][row['embedding']]['mapping'];matches=[]
   for label,em in reps.items():
    for g in range(8):
     if all(d4(int(v),g)==mp[q]for q,v in em['mapping'].items()):matches.append(label)
   assert len(matches)==1;row['embedding_class']=matches[0];groups[matches[0]].append(row)
  summary[name]={k:dict(min_sum_hops=min(r['total_hops_lower_bound']for r in rs),max_sum_hops=max(r['total_hops_lower_bound']for r in rs),min_R_lower_bound=min(r['R_lower_bound']for r in rs),max_R_lower_bound=max(r['R_lower_bound']for r in rs))for k,rs in groups.items()}
 x['class_summary']=summary;f.write_text(json.dumps(x,indent=2))
print('updated prefix distance classes')
