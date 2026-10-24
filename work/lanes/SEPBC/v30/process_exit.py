"""Linux process-exit events, including zombies held by a stopped parent."""
import ctypes,os,select,platform
assert platform.machine()in('x86_64','aarch64'),platform.machine()
def wait_exit(pid):
 libc=ctypes.CDLL(None,use_errno=True);fd=libc.syscall(434,int(pid),0)
 if fd<0:
  e=ctypes.get_errno()
  if e==3:return
  raise OSError(e,os.strerror(e))
 try:select.select([fd],[],[])
 finally:os.close(fd)
if __name__=='__main__':
 import sys
 wait_exit(int(sys.argv[1]))
