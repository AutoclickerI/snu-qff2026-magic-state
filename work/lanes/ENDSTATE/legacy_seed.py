from native import *
from library import rowkey
L=json.loads((H/'library_input.json').read_text());E=json.loads((H/'library_encoders.json').read_text());d=json.loads((ROOT/'work/lanes/SEP2T/abstract_h2_snapshot.solver.json').read_text());initial={k:[d['tokens'][f'{k}{i}']['pos'][0]for i in range(7)]for k in'abc'};final={k:[d['tokens'][f'{k}{i}']['pos'][-1]for i in range(7)]for k in'dabc'};blocks={}
for k,cells in initial.items():
 row=next(r for r in L['embeddings']if set(r[1:])==set(cells));sid=row[0];native=row[1:];p=[native.index(q)for q in cells];cid=L['targets'].index(rowkey([sum(1<<p[i]for i in g)for g in[[0,2,4,6],[1,2,5,6],[3,4,5,6]]]));b=E[sid][cid];ops=[[native[u],native[v]]for u,v in b['ops']];piv=[native[i]for i in b['pivots']]
 if k=='a':ops=[[v,u]for u,v in ops];piv=[q for q in cells if q not in piv]
 blocks[k]=dict(cx=b['cx'],ops=ops,pivots=piv,shape=sid,code_class=cid)
out=dict(initial=initial,final=final,blocks=blocks,source='SEP2T abstract_h2_snapshot; exact minimum-CX encoders resynthesized',seed_paths={k:t['pos']for k,t in d['tokens'].items()},seed=d)
(H/'legacy_staticA_h2.json').write_text(json.dumps(out,indent=2));print({k:b['cx']for k,b in blocks.items()})
