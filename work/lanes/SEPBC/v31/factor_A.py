from near_A import *
import itertools,collections
cells=[q for q in A if q!=9];n=6
G=[[0,2,4,6],[1,2,5,6],[3,4,5,6],[0,1,2]];span={0}
for g in G:
 row=sum(1<<A[i]for i in g);span|={x^row for x in list(span)}
target=tuple(sorted(sum(((x>>q)&1)<<j for j,q in enumerate(cells))for x in span if not(x>>9&1)))
assert len(target)==8
edges=[(i,j)for i in range(n)for j in range(n)if abs(cells[i]//6-cells[j]//6)+abs(cells[i]%6-cells[j]%6)==1]
def transform(state,e):
 u,v=e;return tuple(sorted(x^(((x>>u)&1)<<v)for x in state))
starts={tuple(sorted(sum(((x>>j)&1)<<q for j,q in enumerate(p))for x in range(8))):p for p in itertools.combinations(range(n),3)}
dist={target:0};todo=collections.deque([target]);parent={}
while todo:
 s=todo.popleft()
 for e in edges:
  t=transform(s,e)
  if t not in dist:dist[t]=dist[s]+1;parent[t]=(s,e);todo.append(t)
recipes=[]
for st,p in starts.items():
 cur=st;g=[]
 while cur!=target:
  nxt,e=parent[cur];g.append([cells[e[0]],cells[e[1]]]);cur=nxt
 recipes.append(dict(pivots=[cells[i]for i in p],gates=g,cx=len(g)))
recipes.sort(key=lambda r:r['cx']);(V/'factor_A_library.json').write_text(json.dumps(dict(cells=cells,target=target,states=len(dist),min_cx=min(r['cx']for r in recipes),recipes=recipes),indent=2));print('six-cell rank-three states',len(dist),'minimum CX',recipes[0]['cx'],flush=True)

def assemble(base,rec):
 c=copy.deepcopy(base);ops=c['ops'];R=c['meta']['R'];drop=[o for o in ops if o.get('tag')=='encoder_a'and not any(' -> c['+str(b)+'];'in' '.join(o['lines'])for b in(54,55))]
 removed_bits={int(x)for o in drop for x in re.findall(r' -> c\[(\d+)\];',' '.join(o['lines']))}
 for b in removed_bits:
  refs=[l for l in c['tail']if re.search(rf'c\[{b}\]',l)];assert refs==[f'// DETECTOR c[{b}]'],(b,refs);c['tail'].remove(refs[0])
 rest=[o for o in ops if o not in drop];piv=set(rec['pivots'])|{9};init=[]
 for q in A:
  # Cleared Z source states can be reused; all X inputs are explicit RX.
  if q not in piv and q in(1,8,15,16):continue
  init.append(dict(lines=[f'reset q[{q}];']+([f'h q[{q}];']if q in piv else[]),t=R-10,tag='encoder_a'))
 new=[dict(lines=[f'cx q[{u}],q[{v}];'],t=R-8+j//2,tag='encoder_a')for j,(u,v)in enumerate(rec['gates'])]
 new += [dict(lines=[f'cx q[9],q[{q}];'],t=R-2+i,tag='encoder_a')for i,q in enumerate([8,15])]
 assert max(o['t']for o in new)<R
 c['ops']=[o for o in rest if o['t']<R]+init+new+[o for o in rest if o['t']>=R]
 for i,o in enumerate(c['ops']):o['id']=i
 return c
if __name__=='__main__':
 base=json.loads((V/'full_timing_0.plan.json').read_text());models=[]
 for k,rec in enumerate(recipes):
  if rec['cx']>recipes[0]['cx']+1:continue
  c=assemble(base,rec);d,r=solve(c,27,4,1);models.append(dict(recipe=k,solver=r));print('schedule',k,r.get('R'),rec['cx'],flush=True)
  if d and r['R']<=44:
   # Distinct input choices remain distinct physical fault recipes.
   name=f'factor_A_{k}';st=save(d,'v31/'+name)
   try:r['screen']=score(st)
   except Exception as e:r['error']=repr(e)
   (V/(name+'.build.json')).write_text(json.dumps(r,indent=2));append_result(name,r,'Prepare the q9=0 rank-three A subspace on six cells, then inject the remaining amplitude with RX9 and fanout9→8,9→15.');print(name,r.get('screen',r.get('error')),flush=True)
 (V/'factor_A_models.json').write_text(json.dumps(models,indent=2))
