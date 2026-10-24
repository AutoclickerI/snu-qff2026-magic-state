"""Stationary endpoint audit and explicit free-cell library staging transplants."""
from a30_search import *
from collections import deque
from synth import nb
FREE=sorted(set(range(36))-set(A+B+C+DATA))

def stationary():
 available=set(range(36))-set(B+C+DATA);opts=[[q for q in nb(d) if q in available] for d in DATA];matches=[]
 def go(v):
  if len(v)==7:matches.append(v);return
  for q in opts[len(v)]:
   if q not in v:go(v+[q])
 go([])
 return dict(free=FREE,neighbor_options=dict(zip(DATA,opts)),stationary_matches=matches,A_to_free_edges=[(a,f) for a in A for f in FREE if f in nb(a)])

def stage_candidates():
 info=json.loads((D/'inputs/library_input.json').read_text());libs=[json.loads((D/'inputs'/f'{kind}.json').read_text()) for kind in ['library_encoders','library_depth_encoders']];seen=set()
 for emb in info['embeddings']:
  sid,*qs=emb
  if not set(qs)<=set(FREE):continue
  # Both exact library families and all 30 code classes; choose the closest code automorphism.
  for cid in range(30):
   perms=[p[1:] for p in info['permutations'] if p[0]==cid]
   p=min(perms,key=lambda p:sum(abs(qs[p[i]]//6-A[i]//6)+abs(qs[p[i]]%6-A[i]%6) for i in range(7)))
   endpoints=[qs[p[i]] for i in range(7)]
   for kind,lib in enumerate(libs):
    e=lib[sid][cid];key=(tuple(endpoints),tuple(map(tuple,e['ops'])),tuple(e['pivots']))
    if key in seen:continue
    seen.add(key)
    yield dict(name=f'stage_{sid}_{cid}_{kind}',pivots=[qs[i] for i in range(7) if i not in e['pivots']],ops=[[qs[b],qs[a]] for a,b in e['ops']],endpoints=endpoints,cells=qs)

def path(a,b):
 d=deque([[a]]);seen={a}
 while d:
  p=d.popleft()
  if p[-1]==b:return p
  for q in nb(p[-1]):
   if q not in seen:seen.add(q);d.append(p+[q])

def build_stage(e):
 text,md,h,us,ts,tail,init,owned,clean=source();keep=[i for i in range(len(us)) if i not in owned and ts[i]<48];units=[us[i] for i in keep];times=[ts[i] for i in keep]
 last={q:max([t for u,t in zip(units,times) if q in u.qs],default=-1) for q in range(36)}
 def add(u,lower=0):
  at=max([lower]+[last[q]+1 for q in u.qs]);units.append(u);times.append(at)
  for q in u.qs:last[q]=at
 for q in e['cells']:add(initu(q,q in e['pivots']))
 for ab in e['ops']:add(cx(*ab))
 for q in A:add(initu(q,False))
 route=[]
 for src,dst in sorted(zip(e['endpoints'],A),key=lambda ab:len(path(*ab))):
  p=path(src,dst);edges=list(zip(p,p[1:]));swaps=edges+list(reversed(edges[:-1]));route.append(dict(src=src,dst=dst,path=p,swaps=len(swaps)))
  # Other operations may run concurrently only outside the whole endpoint transposition.
  barrier=max(last[q] for q in p)+1
  for u,v in swaps:
   add(cx(u,v),barrier);add(cx(v,u));add(cx(u,v));barrier=max(last[u],last[v])+1
 R=max(last[q] for q in A+B+C+DATA)+1
 for u,t in zip(us,ts):
  if t>=48:units.append(u);times.append(t+R-48)
 return finish(h,units,times,clean,md,dict(kind='stage',encoder=e,routes=route,R=R))
def worker(e):
 try:
  text,md=build_stage(e);ev=exact2.Eval(text,md['data_qubits']);assert ev.e.A0>1-1e-10;c1=float(ev.fp@ev.n_single)
  r=dict(evaluate(ev),status='SCREENED') if abs(c1)<1e-12 else dict(c1=c1,status='INVALID_C1');r.update(CX=md['CX'],R=md['R'],native_depth=md['native_depth']);return r,text,md,e
 except Exception as x:return dict(status='INVALID',error=repr(x)),None,None,e

def main(procs):
 audit=stationary();candidates=list(stage_candidates());audit['staging_candidates']=len(candidates);(D/'geometry_audit.json').write_text(json.dumps(audit,indent=2));print(audit,flush=True)
 db=sqlite3.connect(D/'geometry.sqlite');db.execute('create table if not exists results(id integer primary key,row text,witness blob,qasm blob,md text)');n=0
 with concurrent.futures.ProcessPoolExecutor(max_workers=procs) as pool:
  for r,text,md,e in pool.map(worker,candidates,chunksize=1):
   n+=1;db.execute('insert into results values(?,?,?,?,?)',(n,json.dumps(r),zlib.compress(json.dumps(e).encode()),zlib.compress(text.encode()) if text else None,json.dumps(md)))
   print(n,json.dumps(r),flush=True)
 db.commit();print('DONE',n,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=8);main(p.parse_args().procs)
