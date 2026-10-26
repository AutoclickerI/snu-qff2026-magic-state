"""Mirror publication events; terminate on the actual remote main PID exit."""
import os,sys,json,subprocess
from pathlib import Path
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
H=Path(__file__).resolve().parent;PID=int(sys.argv[1]);ssh=['ssh','-q','hippo'];transport='ssh -q';remote='hippo:'+str(H)+'/'
def sync(final=False):
 subprocess.run(['rsync','-a','-e',transport,'--exclude','.submit_credentials','--include','merge5*','--exclude','*',remote+'cand/',str(H/'cand')+'/'],check=True,stdin=subprocess.DEVNULL)
 subprocess.run(['rsync','-a','-e',transport,'--exclude','.submit_credentials',remote+'res37h/',str(H/'res37h')+'/'],check=True,stdin=subprocess.DEVNULL)
 subprocess.run(['rsync','-a','-e',transport,'--exclude','.submit_credentials',remote+'REPORT.md',remote+'results.json',str(H)+'/'],check=True,stdin=subprocess.DEVNULL)
 if final:subprocess.run(['rsync','-a','-e',transport,'--exclude','.submit_credentials',remote+'v37h/',str(H/'v37h')+'/'],check=True,stdin=subprocess.DEVNULL)
p=subprocess.Popen(ssh+[f'tail --pid={PID} -n 0 -f {H}/res37h/run.log'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,text=True)
sync()
for line in p.stdout:
 try:r=json.loads(line)
 except json.JSONDecodeError:continue
 if r.get('event')in ('candidate_published','round_selected') or (r.get('event')=='batch' and r['done']==r['total']):
  sync();print(json.dumps(dict(event='mirrored',source_event=r.get('event'),stage=r.get('stage'),stem=r.get('stem'),loss=r.get('loss'))),flush=True)
code=p.wait();assert code==0,code
sync(final=True);print(json.dumps(dict(event='mirror_complete',remote_pid=PID)),flush=True)
