import sys,json
sys.dont_write_bytecode=True
from synth import B,C,nb,verify
from pathlib import Path
H=Path(__file__).resolve().parent;cells=B+C;adj={q:set(nb(q))&set(cells) for q in cells};maps=[]
def rec(mp,used):
 if len(mp)==len(cells):maps.append(mp.copy());return
 rem=[q for q in cells if q not in mp];q=max(rem,key=lambda q:(len(adj[q]&set(mp)),len(adj[q])))
 for v in cells:
  if v in used or len(adj[v])!=len(adj[q]):continue
  if any((a in adj[q])!=(b in adj[v]) for a,b in mp.items()):continue
  mp[q]=v;rec(mp,used|{v});del mp[q]
rec({},set());d=json.loads((H/'inputs/fb_s401_0035.prep.json').read_text());good=[]
for mp in maps:
 dd=dict(d,pivots=[mp[q] for q in d['pivots']],ops=[[[mp[a],mp[b]] for a,b in l] for l in d['ops']]);v=verify(dd)
 if v['stim_target_pass'] and v['clean_pass']:good.append(mp)
out=dict(graph_count=len(maps),code_clean=good);(H/'automorphisms.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
