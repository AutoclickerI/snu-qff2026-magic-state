"""Finish capacity-deferred endpoints; await exits, not polling intervals."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
import subprocess,ctypes,select,json,time
libc=ctypes.CDLL(None,use_errno=True);pending=[(3,0),(4,7)];running={};receipts=[]
def pidfd(pid):
 fd=libc.syscall(434,int(pid),0)
 if fd<0:raise OSError(ctypes.get_errno(),os.strerror(ctypes.get_errno()))
 return fd
while pending or running:
 rows=[line.split() for line in subprocess.check_output(['ps','-u',str(os.getuid()),'-o','pid=,pcpu=,stat='],text=True).splitlines()]
 used=sum(float(r[1]) for r in rows if 'T' not in r[2] and int(r[0]) not in running)/100+len(running)
 while pending and len(running)<2 and used+1<=47.8 and os.getloadavg()[0]<64:
  rank,value=pending.pop(0);f=(H/f'rank{rank}_{value}.log').open('w');p=subprocess.Popen([str(ROOT/'.venv/bin/python'),str(H/'endpoint_family.py'),str(rank),str(value)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);running[p.pid]=(p,f,rank,value);used+=1;print(json.dumps(dict(event='start',pid=p.pid,rank=rank,value=value,used=used)),flush=True)
 fds={}
 for pid in list(running)+[int(r[0]) for r in rows if int(r[0]) not in running and int(r[0])!=os.getpid() and float(r[1])>15]:
  try:fds[pidfd(pid)]=pid
  except OSError:pass
 if not fds:raise RuntimeError('Capacity unavailable without a live completion event')
 ready,_,_=select.select(list(fds),[],[])
 for fd in ready:
  pid=fds[fd]
  if pid in running:
   p,f,rank,value=running.pop(pid);rc=p.wait();f.close();r=dict(rank=rank,value=value,rc=rc);receipts.append(r);print(json.dumps(dict(event='exit',**r)),flush=True)
 for fd in fds:os.close(fd)
(H/'endpoint_family.retry.json').write_text(json.dumps(receipts,indent=2))
