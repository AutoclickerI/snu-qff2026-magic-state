"""Event-driven remote confirmation: update local report on subprocess output."""
import os,sys
sys.dont_write_bytecode=True
import subprocess,json
from pathlib import Path
H=Path(__file__).resolve().parent;D=H/'blue'
cmd=['ssh','-q','-o','ControlMaster=no','-o','ControlPath=none','owl','docker attach --no-stdin b47a99fef4c1']
with (D/'remaining_exact_console.log').open('w') as log:
 pr=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 for line in pr.stdout:
  log.write(line);log.flush();print(line,end='',flush=True)
  try:r=json.loads(line)
  except ValueError:continue
  if isinstance(r,dict) and r.get('exact_verified'):subprocess.run([sys.executable,str(H/'blue_sync.py')],check=True)
 rc=pr.wait();assert rc==0,rc
