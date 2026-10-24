from library import *
import collections
L=json.loads((H/'library_input.json').read_text());ENC=json.loads((H/'library_encoders.json').read_text())
def pure_z(ops,pivots,labels):
 sig={q:1<<labels.index(q)for q in labels};bad=[]
 def check(v,at):
  syndrome=0
  for i in range(7):
   if v>>i&1:syndrome^=i+1
  if not syndrome and v.bit_count()%2:bad.append(at)
 for j in range(len(ops)-1,-1,-1):
  u,v=ops[j]
  for z in(sig[u],sig[v],sig[u]^sig[v]):check(z,('cx',j))
  sig[v]^=sig[u]
 for q in pivots:check(sig[q],('init',q))
 return len(bad)
def make():
 out=[];rep={}
 for r in L['permutations']:rep.setdefault(r[0],r[1:])
 for sid,es in enumerate(ENC):
  for cid,b in enumerate(es):
   p=rep[cid];rev={v:i for i,v in enumerate(p)};zero=dict(ops=[[rev[u],rev[v]]for u,v in b['ops']],pivots=[rev[q]for q in b['pivots']]);plus=dict(ops=[[v,u]for u,v in zero['ops']],pivots=[i for i in range(7)if i not in zero['pivots']]);bad=pure_z(plus['ops'],plus['pivots'],list(range(7)))
   edges=sorted({tuple(sorted(e))for e in zero['ops']});depth=[0]*7
   for u,v in zero['ops']:depth[u]=depth[v]=max(depth[u],depth[v])+1
   out.append(dict(id=f's{sid}c{cid}',shape=sid,code_class=cid,shape_cells=L['shapes'][sid],label_to_shape=p,zero=zero,plus=plus,cx=b['cx'],depth=max(depth),pure_z_sources=bad,edges=edges))
 out.sort(key=lambda x:(bool(x['pure_z_sources']),x['cx'],x['depth'],max(max(r,c)for r,c in x['shape_cells'])))
 (H/'templates.json').write_text(json.dumps(out));print('clean A by CX',collections.Counter(x['cx']for x in out if x['pure_z_sources']==0));print('top',[(x['id'],x['cx'],x['depth'])for x in out[:20]])
if __name__=='__main__':make()
