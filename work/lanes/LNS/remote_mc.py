"""Stream an unchanged remote mc3 run into the local lane and update its report."""
from core import *
import subprocess,shlex,argparse
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--procs',type=int,default=12);a=ap.parse_args();stem=Path(a.stem).resolve();assert stem.parent==OUT
 before=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
 stem.with_suffix('.mc_input.json').write_text(json.dumps(dict(sha256=before,data_qubits=data,shots_per_seed=10**8,seeds=[0,1000,2000],host='jerry',procs=a.procs),indent=2))
 cmd='cd '+shlex.quote(str(ROOT))+' && nproc && uptime && env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python work/lanes/LNS/mc.py '+shlex.quote(str(stem))+' --procs '+str(a.procs)
 proc=subprocess.Popen(['ssh','-q','-o','ControlMaster=no','-o','ControlPath=none','jerry',cmd],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 with stem.with_suffix('.mc.log').open('w')as f:
  for line in proc.stdout:
   f.write(line);f.flush();print(line,end='',flush=True)
   if ' mean 'in line:report()
 code=proc.wait();assert code==0,code;assert hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest()==before;report()
