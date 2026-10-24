from construct_route import *

def prune(initial,moves):
 moves=list(moves);changed=True
 while changed:
  changed=False
  for i,(key,src,dst) in enumerate(moves):
   for j in range(i+1,len(moves)):
    other,u,v=moves[j]
    if other!=key and src in (u,v):break
    if other==key and v==src:
     moves=[x for k,x in enumerate(moves) if not (i<=k<=j and x[0]==key)];changed=True;break
   if changed:break
 occ={q:k for k,q in initial.items()};pos=dict(initial)
 for key,u,v in moves:
  assert pos[key]==u and v not in occ and v not in FIND['d'] and (u,v) in EDGES
  del occ[u];occ[v]=key;pos[key]=v
 assert all(pos[f'{k}{i}']==FIND[k][i] for k in 'bc' for i in range(7))
 return moves

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('route');p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=2);p.add_argument('--exact-encoders',action='store_true');a=p.parse_args();x=json.loads(Path(a.route).read_text());FIND.update(x.get('final',{}));ms=prune(x['initial'],x['moves']);print('pruned',len(x['moves']),'->',len(ms),flush=True);out=HERE/a.out
 out.with_suffix('.route.json').write_text(json.dumps(dict(x,moves=ms,source=a.route),indent=1));build(x['initial'],ms,out,a.workers,a.exact_encoders)
