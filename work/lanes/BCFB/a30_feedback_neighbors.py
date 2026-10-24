"""Exhaustive initialization/check masks and commuting orders around the feedback winner."""
from a30_search import *
from a30_reuse2 import worker

def main(procs):
 e=json.loads((D/'finalists/a30_fb_s810_00837.json').read_text())['options']['encoder'];rng=random.Random(819);enc=[];seen=set()
 for v in [e]+[reordered(e,rng) for _ in range(128)]:
  key=repr([(q,[ab for ab in v['ops'] if q in ab]) for q in A])
  if key not in seen:seen.add(key);enc.append(v)
 def tasks():
  for v in enc:
   for mask in range(128):
    checks=[q for i,q in enumerate(A) if mask>>i&1]
    for reuse in [[],[2],[14],[2,14],[1,2,14],[1,2,8,9,14,15,16]]:yield dict(enc=v,reuse=reuse,checks=checks,R=48)
 db=sqlite3.connect(D/'feedback_neighbors.sqlite');db.execute('create table if not exists results(id integer primary key,row text,witness blob,qasm blob,md text)');n=0;best=1.
 print('ENCODERS',len(enc),flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=procs) as pool:
  for r,text,md,t in pool.map(worker,tasks(),chunksize=4):
   n+=1;db.execute('insert into results values(?,?,?,?,?)',(n,json.dumps(r),zlib.compress(json.dumps(t).encode()),zlib.compress(text.encode()) if text else None,json.dumps(md)))
   if n%500==0:db.commit();print('COUNT',n,flush=True)
   if r.get('exp_minus_A1',0)>=.5002 and r.get('total',1)<best:
    best=r['total'];stem=D/'finalists'/f'a30_fbn_{n:05}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print('BEST',stem.name,json.dumps(r),flush=True)
 db.commit();print('DONE',n,best,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=12);main(p.parse_args().procs)
