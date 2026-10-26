from pass3 import *
def job(task):return record(Path(task['stem']),task['why'])
if __name__=='__main__':
 tasks=json.loads(Path(sys.argv[1]).read_text());out=R/(sys.argv[2]+'.jsonl');workers=int(sys.argv[3]);done=set()
 if out.exists():done={r['sha256']for r in (json.loads(l)for l in out.read_text().splitlines())}
 tasks=[t for t in tasks if sha(t['stem'])not in done]
 with out.open('a')as f,get_context('fork').Pool(workers)as pool:
  for k,r in enumerate(pool.imap_unordered(job,tasks),1):
   r['stage']=sys.argv[2];f.write(json.dumps(r)+'\n');f.flush()
   if k%20==0 or k==len(tasks):print(json.dumps(dict(stage=sys.argv[2],done=k,total=len(tasks))),flush=True)
