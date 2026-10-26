from cont37 import *
import subprocess,shlex
SSH=['ssh','-q','-o','ControlMaster=no','-o','ControlPath=none'];PY=str(ROOT/'.venv/bin/python')
def sync(paths):
 rel=['work/./lanes/MERGE/'+str(Path(p).relative_to(H)) for p in paths]
 subprocess.run(['rsync','-a','--exclude','.submit_credentials','--exclude','__pycache__','--relative','-e',' '.join(SSH),*rel,'hippo:'+str(ROOT/'work')+'/'],cwd=ROOT,check=True)
def pull():
 for folder in ['res37c','v37c','cache37c','logs37c']:
  filters=[]
  if folder=='res37c':
   filters=['--include','*_s1.jsonl','--include','*_b2.jsonl','--include','*_g*.jsonl','--include','*_contexts.json','--include','*_menu.json','--include','*_b2_tasks.json','--exclude','*']
  subprocess.run(['rsync','-a','--exclude','.submit_credentials',*filters,'-e',' '.join(SSH),'hippo:'+str(H/folder)+'/',str(H/folder)+'/'],check=True)
def remote(script,args,log):
 env='OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1'
 command=env+' '+shlex.join([PY,str(H/script),*map(str,args)])+' > '+shlex.quote(str(H/'logs37c'/log))+' 2>&1'
 p=subprocess.run([*SSH,'hippo',command],stdin=subprocess.DEVNULL)
 if p.returncode:raise RuntimeError(('remote job failed',script,args,p.returncode))
def local(script,args):
 subprocess.run([PY,str(H/script),*map(str,args)],check=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
def run_batch(stem,tag,stage,workers):
 tasks=R/f'{stage}_tasks.json';n=len(json.loads(tasks.read_text()))
 if not n:
  (R/f'{stage}.jsonl').touch();print('empty stage',stage,flush=True);return
 sync([H/'cont37.py',H/'search37.py',H/'menu.py',H/'lib.py',H/'schedule_local.py',H/'util_local.py',H/'sparse_v37/basis_warm.json',R/f'{tag}_menu.json',tasks,Path(stem).with_suffix('.qasm'),Path(stem).with_suffix('.json')])
 remote('cont37.py',['batch',stem,R/f'{tag}_menu.json',tasks,stage,workers],stage+'.log');pull()
def search(tag,stem,workers,from_singles=False):
 if not from_singles:
  local('cont37.py',['menu',stem,tag]);shutil.copyfile(R/f'{tag}_tasks.json',R/f'{tag}_s1_tasks.json');run_batch(stem,tag,tag+'_s1',workers)
 local('search37.py',['pairs',tag,stem]);sync([H/'cont37.py',H/'search37.py',R/f'{tag}_eligible.json',R/f'{tag}_b2_tasks.json',R/f'{tag}_menu.json'])
 remote('search37.py',['contexts',tag,stem,workers],tag+'_contexts.log');pull()
 run_batch(stem,tag,tag+'_b2',workers)
 for rnd in itertools.count(1):
  local('search37.py',['prepare',tag,stem,rnd]);run_batch(stem,tag,f'{tag}_g{rnd}',workers)
  local('search37.py',['fund',tag,rnd]);run_batch(stem,tag,f'{tag}_g{rnd}_fund',workers)
  local('search37.py',['select',tag,rnd]);history=json.loads((R/f'{tag}_history.json').read_text())
  from report37 import report
  report()
  if history[-1]['stop']:
   out=history[-1]['price'];dump(R/f'{tag}_outcome.json',dict(base=str(stem),price=out,history=history,complete=True));return out
if __name__=='__main__':
 tag=sys.argv[1];stem=Path(sys.argv[2]).resolve();workers=int(sys.argv[3]);pull();print(json.dumps(search(tag,stem,workers,'--singles-done'in sys.argv)),flush=True)
