import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,signal,time
from pathlib import Path
H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);a=p.parse_args()
for f in sorted((H/'runs').glob(a.prefix+'*.process.json')):
 d=json.loads(f.read_text());pid=d['pid'];stem=str(f)[:-len('.process.json')]
 try:
  cmd=Path(f'/proc/{pid}/cmdline').read_text();assert 'synth.py' in cmd and Path(stem).name in cmd,(pid,cmd)
  st=Path(f'/proc/{pid}/stat').read_text().split();rec=dict(status='STOPPED_AFTER_MC_WIN',pid=pid,cpu_seconds=(int(st[13])+int(st[14]))/os.sysconf('SC_CLK_TCK'),elapsed_wall=time.time()-d['start'] if 'start' in d else None,reason='Completion branch 1 met: fb_s401_0009 MC mean 7.245945e-5 < 7.282e-5, seed-0 acceptance .54702; no claim of timeout/UNSAT')
  os.kill(pid,signal.SIGTERM);Path(stem+'.completion_stop.json').write_text(json.dumps(rec,indent=2));print(Path(stem).name,rec,flush=True)
 except FileNotFoundError:print(f.name,'already exited')
