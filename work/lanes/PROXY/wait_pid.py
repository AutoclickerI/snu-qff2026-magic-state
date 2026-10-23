"""Linux pidfd readiness: wait on process exit, without timed polling."""
import ctypes,sys,select,errno
pid=int(sys.argv[1]);lib=ctypes.CDLL(None,use_errno=True);fd=lib.syscall(434,pid,0)
if fd<0:
 err=ctypes.get_errno()
 if err==errno.ESRCH:print(f'{pid} already exited');raise SystemExit(0)
 raise OSError(err,'pidfd_open')
p=select.poll();p.register(fd,select.POLLIN);p.poll();print(f'{pid} exited',flush=True)
