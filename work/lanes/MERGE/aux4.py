"""Evaluate a remote-queued tail locally, syncing exact cache receipts on completion events."""
from pass4 import *
import subprocess
SSH=['ssh','-q','-o','ControlMaster=no','-o','ControlPath=none']
if __name__=='__main__':
 rnd=int(sys.argv[1]);stem=Path(sys.argv[2]);basis=Path(sys.argv[3]);E.configure(basis,12);menuf=R/f'wide_r{rnd}_menu.json';tasks=json.loads((R/f'wide_r{rnd}_joint_tasks.json').read_text())[-1600:];init(stem,menuf,json.loads(stem.with_suffix('.json').read_text()).get('loss',TAU))
 tag=f'assist_r{rnd}';out=R/(tag+'.jsonl');done={tuple(json.loads(x)['edits'])for x in out.read_text().splitlines()}if out.exists()else set();tasks=[x for x in tasks if tuple(x)not in done];pending=set();start=time.monotonic();count=0
 def sync():
  if not pending:return
  subprocess.run(['rsync','-a','--exclude','.submit_credentials','-e',' '.join(SSH),*[str(p)for p in sorted(pending)],'hippo:'+str(CACHE)+'/'],check=True,stdin=subprocess.DEVNULL);pending.clear()
 with out.open('a')as f,get_context('fork').Pool(3)as pool:
  for count,r in enumerate(pool.imap_unordered(job,tasks),1):
   r['stage']=tag;f.write(json.dumps(r)+'\n');f.flush()
   if 'cache_key'in r:pending.add(CACHE/(hashlib.sha256(r['cache_key'].encode()).hexdigest()+'.json'))
   if count%50==0:sync();print(json.dumps(dict(event='aux',round=rnd,done=count,total=len(tasks),seconds=time.monotonic()-start)),flush=True)
  sync()
 print(json.dumps(dict(event='aux_complete',round=rnd,done=count,seconds=time.monotonic()-start)),flush=True)
