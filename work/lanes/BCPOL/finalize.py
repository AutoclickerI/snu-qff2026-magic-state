"""Run the required unmodified reference checks; every receipt is lane-local."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import ctypes
def pidfd_open(pid):
 libc=ctypes.CDLL(None,use_errno=True);fd=libc.syscall(434,int(pid),0)
 if fd<0:raise OSError(ctypes.get_errno(),os.strerror(ctypes.get_errno()))
 return fd
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
import argparse,json,time,subprocess,re,hashlib,select,math
p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--procs',type=int,default=1);p.add_argument('--mc',action='store_true');a=p.parse_args()
py=str(ROOT/'.venv/bin/python')
def run(cmd,log):
 t=time.monotonic();requested=int(cmd[cmd.index('--procs')+1]) if '--procs' in cmd else 1
 while True:
  rows=[l.split() for l in subprocess.check_output(['ps','-u',str(os.getuid()),'-o','pid=,pcpu=,stat='],text=True).splitlines()]
  used=sum(float(r[1]) for r in rows if 'T' not in r[2])/100;available=math.floor(.75*os.cpu_count()-used-1)
  if available>=1:break
  fds=[]
  for r in rows:
   if int(r[0])!=os.getpid() and float(r[1])>15:
    try:fds.append(pidfd_open(int(r[0])))
    except ProcessLookupError:pass
  if not fds:raise RuntimeError('Capacity unavailable with no process exit source')
  select.select(fds,[],[])
  for fd in fds:os.close(fd)
 if '--procs' in cmd:cmd[cmd.index('--procs')+1]=str(min(requested,available))
 load=os.getloadavg()
 with log.open('w') as f:r=subprocess.run([py,*cmd],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
 assert r.returncode==0,(cmd,r.returncode,log)
 return dict(command=cmd,seconds=time.monotonic()-t,log=str(log),load_before=load,user_cpu_before=used)
cal=H/'inputs/v22h_c2c9';calrec=run([str(ROOT/'work/fast_check.py'),str(cal)+'.qasm',str(cal)+'.json','1000000','1'],H/'calibration.speed.log')
caltext=(H/'calibration.speed.log').read_text();calval=float(re.search(r'\(([0-9.]+)s, 1 procs',caltext)[1]);threshold=20*calval/2.3
for stem in a.stems:
 stem=Path(stem);r=dict(stem=str(stem),host=os.uname().nodename,calibration_s_per_1e6=calval,speed_threshold=threshold,qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest())
 r['speed']=run([str(ROOT/'work/fast_check.py'),str(stem)+'.qasm',str(stem)+'.json','1000000','1'],stem.with_suffix('.speed.log'))
 s=stem.with_suffix('.speed.log').read_text();r['s_per_1e6']=float(re.search(r'\(([0-9.]+)s, 1 procs',s)[1]);r['judge_pass']='passed=True' in s;r['speed_pass']=r['s_per_1e6']<=threshold
 r['exact']=run([str(ROOT/'work/lanes/EVAL/exact2.py'),str(stem)+'.qasm','--third','--procs',str(a.procs),'--top','12'],stem.with_suffix('.exact.log'))
 if a.mc and r['judge_pass'] and r['speed_pass']:
  original=ROOT/'work/lanes/MAIN/spec/mc3.py';mc=original if original.exists() else H/'inputs/mc3.py'
  r['mc_script_sha256']=hashlib.sha256(mc.read_bytes()).hexdigest();r['mc']=run([str(mc),str(stem),'--procs',str(a.procs)],stem.with_suffix('.mc.log'))
 stem.with_suffix('.verified.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
