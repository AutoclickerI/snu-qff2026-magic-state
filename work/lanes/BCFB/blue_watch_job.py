"""Stream a Docker process; mirror completed receipts on output events, not polling."""
import os,sys
sys.dont_write_bytecode=True
import argparse,subprocess,json,shlex
from pathlib import Path
H=Path(__file__).resolve().parent;D=H/'blue'
p=argparse.ArgumentParser();p.add_argument('--procs',type=int,required=True);p.add_argument('--log',required=True);p.add_argument('script');p.add_argument('args',nargs=argparse.REMAINDER);a=p.parse_args()
docker=['docker','run','--rm','--name','bcfb_'+a.log,'-u','1010:1012','-e','HOME=/home/jihoon','-e','PYTHONDONTWRITEBYTECODE=1','-e','OMP_NUM_THREADS=1','-e','OPENBLAS_NUM_THREADS=1','-e','MKL_NUM_THREADS=1','-v','/home/jihoon:/home/jihoon','-w',str(D),'--cpus='+str(a.procs),'fnc-build:22.04','/home/jihoon/competitions/quantumn/.venv/bin/python',str(H/a.script),*a.args]
cmd=['ssh','-q','-o','ControlMaster=no','-o','ControlPath=none','owl','nproc; uptime; '+shlex.join(docker)];errors=[]
with (D/(a.log+'.log')).open('w') as log:
 pr=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 for line in pr.stdout:
  log.write(line);log.flush();print(line,end='',flush=True)
  try:r=json.loads(line)
  except ValueError:continue
  if isinstance(r,dict) and (r.get('exact_verified') or ('mean' in r and ('seeds' in r or 'draws' in r))):
   rc=subprocess.run([sys.executable,str(H/'blue_sync.py')]).returncode
   if rc:errors.append(rc);print(json.dumps(dict(event='LOCAL_REPORT_SYNC_FAILED',returncode=rc)),flush=True)
 rc=pr.wait();print(json.dumps(dict(event='REMOTE_PROCESS_EXIT',returncode=rc)),flush=True)
assert rc==0 and not errors,(rc,errors)
subprocess.run([sys.executable,str(H/'blue_sync.py')],check=True)
