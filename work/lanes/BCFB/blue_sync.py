import subprocess,json
from pathlib import Path
from blue_report import report
H=Path(__file__).resolve().parent;D=H/'blue';ssh='ssh -q -o ControlMaster=no -o ControlPath=none';remote='owl:'+str(D)
subprocess.run(['rsync','-az','-e',ssh,'--exclude=*.verify.json',remote+'/finalists/',str(D/'finalists')+'/'],check=True)
inc=D/'verification_incoming';inc.mkdir(exist_ok=True)
subprocess.run(['rsync','-az','-e',ssh,'--include=*.verify.json','--exclude=*',remote+'/finalists/',str(inc)+'/'],check=True)
for f in inc.glob('*.json'):
 dest=D/'finalists'/f.name;a=json.loads(dest.read_text()) if dest.exists() else {};b=json.loads(f.read_text())
 for k,v in b.items():
  if k.startswith('exact_') or k not in a:a[k]=v
 dest.write_text(json.dumps(a,indent=2));f.unlink()
inc.rmdir()
subprocess.run(['rsync','-az','-e',ssh,remote+'/runs/',str(D/'runs')+'/'],check=True)
from blue_metadata import main as normalize
normalize();report()
