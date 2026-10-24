"""Resume this lane's paused validation tree only when a process exit frees capacity."""
import os,sys,json,signal,select,subprocess,time
from pathlib import Path
import ctypes
def pidfd_open(pid):
 libc=ctypes.CDLL(None,use_errno=True);fd=libc.syscall(434,int(pid),0)
 if fd<0:raise OSError(ctypes.get_errno(),os.strerror(ctypes.get_errno()))
 return fd
H=Path(__file__).resolve().parent;p=H/'final_capacity_paused.json';d=json.loads(p.read_text());paused=set(d['pids']);fds={}
while True:
 rows=[line.split(None,3) for line in subprocess.check_output(['ps','-u',str(os.getuid()),'-o','pid=,pcpu=,stat=,comm='],text=True).splitlines()]
 used=sum(float(r[1]) for r in rows if 'T' not in r[2])/100
 if used+len(paused)<48 and os.getloadavg()[0]<64:
  for pid in sorted(paused):
   try:os.kill(pid,signal.SIGCONT)
   except ProcessLookupError:pass
  d.update(resumed=time.time(),pause_seconds=time.time()-d['time'],resume_user_cpu=used);p.with_name('final_capacity_pause.receipt.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True);break
 watch=[int(r[0]) for r in rows if int(r[0]) not in paused and float(r[1])>15 and int(r[0])!=os.getpid()]
 for fd in fds:os.close(fd)
 fds={}
 for pid in watch:
  try:fds[pidfd_open(pid)]=pid
  except ProcessLookupError:pass
 if not fds:raise RuntimeError('No live capacity event source')
 ready,_,_=select.select(list(fds),[],[])
 print(json.dumps(dict(event='process_exit',pids=[fds[fd] for fd in ready],user_cpu=used)),flush=True)
