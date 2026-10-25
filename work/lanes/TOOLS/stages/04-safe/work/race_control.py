"""Stop precisely the registered controller at a chunk boundary, then await exit."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import platform


def syscall(number, *args):
    # The installed uv Python and glibc expose no pidfd wrappers, although the
    # Linux kernel supports them. These syscall numbers match both hosted ISAs.
    if platform.machine() not in ('x86_64','aarch64'):
        raise RuntimeError('pidfd syscall ABI not defined for this architecture')
    libc = ctypes.CDLL(None,use_errno=True)
    libc.syscall.restype = ctypes.c_long
    result = libc.syscall(number,*args)
    if result == -1:
        error = ctypes.get_errno()
        raise OSError(error,os.strerror(error))
    return result


def process_identity(pid):
    root = Path('/proc')/str(pid)
    return dict(pid=pid,uid=root.stat().st_uid,
                start_ticks=root.joinpath('stat').read_text().rsplit(')',1)[1].split()[19],
                command_sha256=hashlib.sha256(root.joinpath('cmdline').read_bytes()).hexdigest())


def register_controller(path, stem):
    obj = dict(process_identity(os.getpid()),stem=stem)
    tmp = Path(str(path)+'.tmp')
    tmp.write_text(json.dumps(obj)+'\n')
    os.replace(tmp,path)


def request_stop(path):
    if not Path(path).exists():
        print(f'no registered racer for {path}; host may have been skipped',flush=True)
        return False
    obj = json.loads(Path(path).read_text())
    pid = obj['pid']
    # Hold the process reference before revalidating its identity; no PID reuse race.
    try:
        fd = syscall(434,pid,0)  # pidfd_open
    except ProcessLookupError:
        print(f'controller {pid} already exited',flush=True)
        return False
    try:
        try:
            current = process_identity(pid)
        except FileNotFoundError:
            return False  # exited after pidfd_open; its fd cannot refer to a reused PID
        if obj['uid'] != os.getuid() or current != {k:obj[k] for k in current}:
            raise ValueError('controller identity mismatch; no signal sent')
        try:
            syscall(424,fd,signal.SIGUSR1,ctypes.c_void_p(),0)  # pidfd_send_signal
        except ProcessLookupError:
            return False  # already exited between identity validation and the signal
        poll = select.poll()
        poll.register(fd,select.POLLIN)
        poll.poll()  # actual process exit; never wait on an output file
    finally:
        os.close(fd)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pid_record',type=Path)
    args = parser.parse_args()
    request_stop(args.pid_record)
