"""Constructive vacancy routing of separate B/C blocks; A prepared after routing.

Every physical relocation is one CX plus measurement into a reset empty cell.
Other live tokens are moved explicitly while clearing a path. No SWAP through an
unknown state is hidden. Randomized goal order is verified by replay.
"""
from reschedule import *
from collections import deque
import random,itertools
FIND={'d':[0,20,7,10,3,22,21],'a':AC,'b':BCELLS,'c':CCELLS}
NB={q:[v for u,v in EDGES if u==q] for q in range(36)}

def find_path(src,goals,blocked,rng):
 queue=deque([[src]]);seen={src}
 while queue:
  p=queue.popleft()
  if p[-1] in goals:return p
  nn=list(NB[p[-1]]);rng.shuffle(nn)
  for v in nn:
   if v not in blocked and v not in seen:seen.add(v);queue.append(p+[v])
 return None

def route(initial,goals,rng,diagnostics=None):
 pos=dict(initial);occ={v:k for k,v in pos.items()};fixed=set(FIND['d']);todo=set(pos);moves=[]
 def move(k,v):
  u=pos[k];assert v not in occ and v not in fixed and v in NB[u]
  del occ[u];occ[v]=k;pos[k]=v;moves.append((k,u,v))
 # Prefer goals whose occupation preserves connectivity for all remaining work.
 while todo:
  candidates=[]
  for k in todo:
   path=find_path(pos[k],{goals[k]},fixed,rng)
   if path is None:continue
   blocked=fixed|{goals[k]}
   reachable=True
   for j in todo-{k}:
    if pos[j]==goals[k]:continue
    if find_path(pos[j],{goals[j]},blocked,rng) is None:reachable=False;break
   if reachable:candidates.append((len(path)+rng.random()*12,k,path))
  if not candidates:
   if diagnostics is not None:diagnostics.append(dict(reason='no_goal_order',pos=pos,todo=sorted(todo),moves=len(moves),fixed=sorted(fixed)))
   return None
  _,k,p=min(candidates)
  goal=goals[k]
  if goal in occ and occ[goal]!=k:
   clear=find_path(goal,set(range(36))-fixed-set(occ)-set(p),fixed|{pos[k]},rng)
   if clear is None:return None
   for src,dst in reversed(list(zip(clear,clear[1:]))):
    if src in occ:move(occ[src],dst)
  for at,v in enumerate(p[1:],1):
   if v in occ:
    # Move the vacancy through a corridor if necessary, but leave the target
    # empty so a blocker cannot be trapped ahead of the routed token.
    empty=set(range(36))-fixed-set(occ)-set(p[at+1:])
    clear=find_path(v,empty,fixed|{pos[k],goal},rng)
    if clear is None:
     if diagnostics is not None:diagnostics.append(dict(reason='clear_path',pos=pos,todo=sorted(todo),moves=len(moves),fixed=sorted(fixed),token=k,path=p,at=at,blocked=v))
     return None
    for src,dst in reversed(list(zip(clear,clear[1:]))):
     if src in occ:move(occ[src],dst)
   move(k,v)
  assert pos[k]==goals[k];fixed.add(goals[k]);todo.remove(k)
 return moves

def candidates(autos=False):
 em=json.loads((HERE/'inputs/l5_11.embeddings.json').read_text());avail=set(range(36))-P0-set(FIND['d'])
 em=[e for e in em if set(e)<=avail]
 out=[]
 def dist(e,k):return sum(abs(u//6-v//6)+abs(u%6-v%6) for u,v in zip(e,FIND[k]))
 choices={k:em for k in 'bc'}
 if autos:
  choices={}
  perms=automorphisms()
  for k in 'bc':
   best={}
   for e in em:
    key=tuple(sorted(e))
    for p in perms:
     ee=[e[i] for i in p];v=(dist(ee,k),ee)
     if key not in best or v<best[key]:best[key]=v
   choices[k]=[v[1] for v in best.values()]
 for b in choices['b']:
  for c in choices['c']:
   if set(b).isdisjoint(c):out.append((dist(b,'b')+dist(c,'c'),b,c))
 return sorted(out)

def build(initial,moves,out,workers,exact_encoders=False):
 pre,dets=prefix();ops=[]
 def add(lines,region,**kw):ops.append(dict(lines=lines,region=region,**kw))
 for u in pre:
  lines=list(u.lines)
  if u.name=='MX' and not lines[-1].startswith('h '):lines.append(f'h q[{u.qs[0]}];')
  add(lines,'pre')
 from construct import data_routes
 routes=[p for i,p in data_routes(FIND['d'])]
 for p in routes:
  for src,dst in zip(p,p[1:]):
   add([f'reset q[{dst}];'],'moves');add([f'cx q[{src}],q[{dst}];'],'moves');add([f'cx q[{dst}],q[{src}];'],'moves')
 enc={}
 def prep(k,cells):
  if exact_encoders and (k in 'bc' or cells!=AC):
   import exenc
   ep=Path(str(out)+f'_prep_{k}.json')
   if not ep.exists():exenc.run(cells,'plus' if k=='a' else 'zero',[],1 if k=='a' else 0,ep,workers,False,k=='a',10000000)
   p=json.loads(ep.read_text());enc[k]=dict(cells=cells,**p)
   for q in cells:add([f'reset q[{q}];']+([f'h q[{q}];'] if q in p['pivots'] else []),f'prep_{k}')
   for L in p['ops']:
    for u,v in L:add([f'cx q[{u}],q[{v}];'],f'prep_{k}')
   return
  p=template('l5_11',k);enc[k]=dict(cells=cells,**p)
  for i,q in enumerate(cells):add([f'reset q[{q}];']+([f'h q[{q}];'] if i in p['pivots'] else []),f'prep_{k}')
  for L in p['ops']:
   for u,v in L:add([f'cx q[{cells[u]}],q[{cells[v]}];'],f'prep_{k}')
 for k in 'bc':prep(k,[initial[f'{k}{i}'] for i in range(7)])
 bit=64;frame={k:[set() for i in range(7)] for k in 'abc'}
 pos=dict(initial);occupied=set(pos.values())|set(FIND['d'])
 for key,src,dst in moves:
  assert pos[key]==src and dst not in occupied and (src,dst) in EDGES
  add([f'reset q[{dst}];'],'moves');add([f'cx q[{src}],q[{dst}];'],'moves');add([f'h q[{src}];',f'measure q[{src}] -> c[{bit}];',f'h q[{src}];'],'moves')
  frame[key[0]][int(key[1:])].add(bit);bit+=1;occupied.remove(src);occupied.add(dst);pos[key]=dst
 assert all(pos[f'{k}{i}']==FIND[k][i] for k in 'bc' for i in range(7))
 assert set(FIND['a']).isdisjoint(occupied);prep('a',FIND['a'])
 bits={}
 for i in range(7):
  add([f"cx q[{FIND['d'][i]}],q[{FIND['a'][i]}];"],'round',round_offset=0);add([f"cx q[{FIND['b'][i]}],q[{FIND['c'][i]}];"],'round',round_offset=0)
 for k in 'ac':
  for i,q in enumerate(FIND[k]):bits[k,i]=bit;add([f'measure q[{q}] -> c[{bit}];'],'round',round_offset=1);bit+=1
 for i in range(7):add([f"cx q[{FIND['b'][i]}],q[{FIND['d'][i]}];"],'round',round_offset=1)
 for i,q in enumerate(FIND['b']):bits['b',i]=bit;add([f'h q[{q}];',f'measure q[{q}] -> c[{bit}];'],'round',round_offset=2);bit+=1
 for k in 'abc':
  for gen in GENS+([list(range(7))] if k=='c' else []):
   bs={bits[k,i] for i in gen}
   if k=='b':
    for i in gen:bs^=frame['b'][i]^frame['c'][i]
   dets.append('// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bs)))
 return schedule_build(ops,dets,FIND['d'],out,workers,dict(encoders=enc,initial=initial,final=FIND,data_hops=sum(len(p)-1 for p in routes),block_moves=len(moves),teleports=moves))

def main(a):
 rng=random.Random(a.seed);cs=candidates(a.automorphisms);print('placements',len(cs),flush=True);best=None;goals={f'{k}{i}':q for k in 'bc' for i,q in enumerate(FIND[k])};out=HERE/a.out
 diagnostics=[]
 for trial in range(a.trials):
  rank=trial%min(a.placements,len(cs));cost,b,c=cs[rank];initial={f'{k}{i}':q for k,arr in [('b',b),('c',c)] for i,q in enumerate(arr)}
  ms=route(initial,goals,rng,diagnostics if trial<100 else None)
  if ms is not None and (best is None or len(ms)<len(best['moves'])):
   best=dict(initial=initial,moves=ms,trial=trial,static_distance=cost,rank=rank);out.with_suffix('.route.json').write_text(json.dumps(best,indent=1));print('route',trial,len(ms),'distance',cost,flush=True)
 out.with_suffix('.route_failures.json').write_text(json.dumps(diagnostics,indent=1))
 if best is None:raise RuntimeError('No constructive route found')
 build(best['initial'],best['moves'],out,a.workers,a.automorphisms)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',default='route_l5');p.add_argument('--trials',type=int,default=500);p.add_argument('--placements',type=int,default=40);p.add_argument('--seed',type=int,default=0);p.add_argument('--workers',type=int,default=2);p.add_argument('--automorphisms',action='store_true');main(p.parse_args())
