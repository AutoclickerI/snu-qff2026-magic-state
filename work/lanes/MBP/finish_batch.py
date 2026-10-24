"""Stop only a named batch launcher, then await its in-flight children by pidfd."""
import os,sys,signal,select,subprocess,json,ctypes
from pathlib import Path
pid=int(sys.argv[1]);cmd=Path(f'/proc/{pid}/cmdline').read_bytes().decode().replace('\0',' ')
assert any('work/lanes/MBP/'+name+'.py ' in cmd for name in ['batch','reprice']),cmd
children=[]
for line in subprocess.check_output(['ps','-eo','pid=,ppid='],text=True).splitlines():
    q,p=map(int,line.split())
    if p==pid:children.append(q)
fds=[]
libc=ctypes.CDLL(None,use_errno=True)
for q in children:
    fd=libc.syscall(434,ctypes.c_int(q),ctypes.c_uint(0))
    if fd>=0:fds.append(fd)
    elif ctypes.get_errno()!=3:raise OSError(ctypes.get_errno(),'pidfd_open')
os.kill(pid,signal.SIGTERM)
while fds:
    ready,_,_=select.select(fds,[],[])
    for fd in ready:os.close(fd);fds.remove(fd)
receipt=dict(parent=pid,children=children,status='launcher stopped; in-flight experiments exited naturally')
(Path(__file__).resolve().parent/'batch_handoff.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
