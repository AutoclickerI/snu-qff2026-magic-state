"""Synthesize and build separate connected blocks with one-CX teleports."""
from reschedule import *
from collections import deque
import exenc

def path(src,dst,occupied):
 q=deque([[src]]);seen={src}
 while q:
  p=q.popleft()
  if p[-1]==dst:return p
  for u,v in EDGES:
   if u==p[-1] and v not in occupied and v not in seen:seen.add(v);q.append(p+[v])
 return None

def data_routes(target):
 # Exact search over the order of shortest direct-to-target routes. Seven data
 # tokens are sparse; do not overwrite any token, even if it later moves.
 best=None
 def rec(pos,done,paths,cost):
  nonlocal best
  if best is not None and cost>=best[0]:return
  if len(done)==7:best=(cost,paths);return
  for i in range(7):
   if i in done:continue
   p=path(pos[i],target[i],set(pos[:i]+pos[i+1:]))
   if p is not None:
    pp=pos[:];pp[i]=target[i];rec(pp,done|{i},paths+[(i,p)],cost+len(p)-1)
 rec(D0[:],set(),[],0)
 if best is None:raise RuntimeError('No sequential shortest-path data routing found')
 return best[1]

def main(a):
 g=json.loads(Path(a.geometry).read_text());name=a.out;out=HERE/name
 initial=g['initial'];final=g['final'];enc={}
 for k in 'abc':
  ep=HERE/f'{name}_prep_{k}.json'
  if not ep.exists():
   exenc.run(initial[k],'plus' if k=='a' else 'zero',[],a.extra if k=='a' else 0,ep,a.workers,False,k=='a',10000000)
  enc[k]=json.loads(ep.read_text())
 pre,dets=prefix();ops=[]
 def add(lines,region,**kw):ops.append(dict(lines=lines,region=region,**kw))
 for u in pre:
  lines=list(u.lines)
  if u.name=='MX' and not lines[-1].startswith('h '):lines.append(f'h q[{u.qs[0]}];')
  add(lines,'pre')
 routes=data_routes(final['d'])
 for i,p in routes:
  for src,dst in zip(p,p[1:]):
   add([f'reset q[{dst}];'],'moves');add([f'cx q[{src}],q[{dst}];'],'moves');add([f'cx q[{dst}],q[{src}];'],'moves')
 for k in 'abc':
  for q in initial[k]:add([f'reset q[{q}];']+([f'h q[{q}];'] if q in enc[k]['pivots'] else []),f'prep_{k}')
  for L in enc[k]['ops']:
   for u,v in L:add([f'cx q[{u}],q[{v}];'],f'prep_{k}')
 bit=64;frame={k:[set() for i in range(7)] for k in 'abc'};moves=[]
 # Topologically order relocation chains. Destination must be empty, and source
 # remains live through measurement. A cycle is a routing failure, not a proof.
 occupancy={q:(k,i) for k in 'dabc' for i,q in enumerate(initial[k])}
 todo={(k,i) for k in 'abc' for i in range(7) if initial[k][i]!=final[k][i]}
 while todo:
  ready=[(k,i) for k,i in sorted(todo) if final[k][i] not in occupancy]
  if not ready:raise RuntimeError('Relocation cycle: extra buffer move required')
  for k,i in ready:
   src,dst=initial[k][i],final[k][i];assert (src,dst) in EDGES
   add([f'reset q[{dst}];']+([f'h q[{dst}];'] if k=='a' else []),'moves')
   u,v=(dst,src) if k=='a' else (src,dst);add([f'cx q[{u}],q[{v}];'],'moves')
   add(([f'h q[{src}];'] if k!='a' else [])+[f'measure q[{src}] -> c[{bit}];']+([f'h q[{src}];'] if k!='a' else []),'moves')
   frame[k][i].add(bit);bit+=1;moves.append(dict(block=k,index=i,src=src,dst=dst));del occupancy[src];occupancy[dst]=(k,i);todo.remove((k,i))
 bits={}
 for i in range(7):
  add([f"cx q[{final['d'][i]}],q[{final['a'][i]}];"],'round',round_offset=0)
  add([f"cx q[{final['b'][i]}],q[{final['c'][i]}];"],'round',round_offset=0)
 for k in 'ac':
  for i,q in enumerate(final[k]):bits[k,i]=bit;add([f'measure q[{q}] -> c[{bit}];'],'round',round_offset=1);bit+=1
 for i in range(7):add([f"cx q[{final['b'][i]}],q[{final['d'][i]}];"],'round',round_offset=1)
 for i,q in enumerate(final['b']):bits['b',i]=bit;add([f'h q[{q}];',f'measure q[{q}] -> c[{bit}];'],'round',round_offset=2);bit+=1
 for k in 'abc':
  for gen in GENS+([list(range(7))] if k=='c' else []):
   bs={bits[k,i] for i in gen}
   for i in gen:
    if k=='a':bs^=frame['a'][i]
    elif k=='b':bs^=frame['b'][i]^frame['c'][i]
   dets.append('// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bs)))
 details=dict(source_geometry=str(Path(a.geometry).resolve()),initial=initial,final=final,encoders=enc,data_routes=routes,data_hops=sum(len(p)-1 for i,p in routes),block_moves=len(moves),teleports=moves)
 schedule_build(ops,dets,final['d'],out,a.workers,details)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('geometry');p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=2);p.add_argument('--extra',type=int,default=1);main(p.parse_args())
