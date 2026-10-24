import os,sys,json,itertools,collections
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;P=H.parent;sys.path.insert(0,str(P))
from library import rowkey
from templates import pure_z
L=json.loads((P/'library_input.json').read_text());ED=json.loads((P/'library_depth_encoders.json').read_text());EC=json.loads((P/'library_encoders.json').read_text());KEY={v:i for i,v in enumerate(L['targets'])};SETS={}
for r in L['embeddings']:SETS.setdefault(tuple(sorted(r[1:])),r)
PERMS=np.array(list(itertools.permutations(range(7))),dtype=int);GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
rows=[];seen=set()
for f in sorted(H.glob('enum_v30f*.jsonl')):
 receipt=json.loads(f.with_suffix('.receipt.json').read_text());prefix=json.loads((P/(receipt['prefix']+'.prefix.json')).read_text());em=prefix['embeddings'][receipt['embedding']];mp={int(q):v for q,v in em['mapping'].items()};start=[mp[q]for q in prefix['data_qubits']];release={mp[int(q)]:t for q,t in prefix['release_asap'].items()};last=[prefix['last_data_asap'][str(q)]for q in prefix['data_qubits']]
 for gi,line in enumerate(f.read_text().splitlines()):
  raw=json.loads(line);base=raw['final'];key=(receipt['embedding'],tuple(raw['region']))
  if key in seen:continue
  seen.add(key);sid,*native=SETS[tuple(sorted(base['a']))];baseperm=[native.index(q)for q in base['a']];classes=collections.defaultdict(list)
  dist=np.array([[abs(q//6-v//6)+abs(q%6-v%6)for v in base['d']]for q in start]);dd=dist[np.arange(7)[None,:],PERMS];rlb=np.max(np.array(last)[None,:]+1+2*dd,axis=1);total=dd.sum(axis=1)
  for j,p in enumerate(PERMS):
   perm=[baseperm[i]for i in p];cid=KEY[rowkey([sum(1<<perm[i]for i in g)for g in GENS])];classes[cid].append((int(rlb[j]),int(total[j]),j))
  for cid,values in classes.items():
   lb,td,j=min(values);perm=PERMS[j].tolist();end={k:[vs[i]for i in perm]for k,vs in base.items()};preps=[]
   for kind,lib in [('depth',ED),('cx',EC)]:
    e=lib[sid][cid];ops=[[native[v],native[u]]for u,v in e['ops']];piv=[q for q in native if native.index(q)not in e['pivots']]
    if pure_z(ops,piv,end['a']):continue
    times={q:release.get(q,0)for q in end['a']}
    for q,t in zip(start,last):
     if q in times:times[q]=t+4
    for q in times:times[q]+=1
    for u,v in ops:times[u]=times[v]=max(times[u],times[v])+1
    ar=max(times.values());preps.append((ar,e['cx'],kind,dict(ops=ops,pivots=piv,cx=e['cx'],shape=sid,code_class=cid,selection=kind)))
   if not preps:continue
   ar,_,_,ap=min(preps,key=lambda z:z[:3]);avail=max(release.get(q,0)for q in raw['region']);base_lb=max(lb,ar)
   row=dict(prefix='v30f',embedding=receipt['embedding'],mapping=mp,initial_data=start,final=end,region=raw['region'],a_prep=ap,resource_available_from=avail,data_distances=dd[j].tolist(),data_ready_lb=lb,a_finish_lb=ar,R_lower_bounds={str(d):max(base_lb,avail+d+1)for d in[9,10,11]},data_hops_lb=td,source_region=f.name,source_region_index=gi,label_permutation=perm)
   row['name']=f'e{receipt["embedding"]}_r{sum(1<<q for q in raw["region"]):x}_s{sid}c{cid}';rows.append(row)
rows.sort(key=lambda x:(x['R_lower_bounds']['11'],x['data_hops_lb'],x['a_prep']['cx']))
(H/'labelled_regions.json').write_text(json.dumps(rows,indent=1));print('regions',len(seen),'labelled candidates',len(rows));print([(r['name'],r['R_lower_bounds'],r['data_hops_lb'])for r in rows[:12]])
