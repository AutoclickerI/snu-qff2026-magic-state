"""All 128 input-reuse masks × all 128 initialization-check masks on the best order."""
from a30_search import *
from a30_reuse2 import worker

def main(procs):
 e=json.loads((D/'finalists/a30_fbn_08352.json').read_text())['options']['spec']['enc']
 def tasks():
  for rm in range(128):
   reuse=[q for i,q in enumerate(A) if rm>>i&1]
   for cm in range(128):yield dict(enc=e,reuse=reuse,checks=[q for i,q in enumerate(A) if cm>>i&1],R=48)
 db=sqlite3.connect(D/'full_masks.sqlite');db.execute('create table if not exists results(id integer primary key,row text,witness blob,qasm blob,md text)');n=0;best=1.;seen=set()
 with concurrent.futures.ProcessPoolExecutor(max_workers=procs) as pool:
  for r,text,md,t in pool.map(worker,tasks(),chunksize=8):
   n+=1;db.execute('insert into results values(?,?,?,?,?)',(n,json.dumps(r),zlib.compress(json.dumps(t).encode()),zlib.compress(text.encode()) if text else None,json.dumps(md)))
   if n%500==0:db.commit();print('COUNT',n,flush=True)
   if r.get('exp_minus_A1',0)>=.5002 and r.get('total',1)<best-1e-13:
    best=r['total'];stem=D/'finalists'/f'a30_masks_{n:05}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print('BEST',stem.name,json.dumps(r),flush=True)
 db.commit();print('DONE',n,best,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=12);main(p.parse_args().procs)
