"""Stop only the named GLOBAL runner and its descendants, using numeric PIDs."""
import os,shlex,signal,subprocess,sys
base,tag=sys.argv[1:3]
script=sys.argv[3] if len(sys.argv)>3 else 'greedy_run.py'
rows={}
for line in subprocess.check_output(['ps','-eo','pid=,ppid=,args='],text=True).splitlines():
    pid,ppid,args=line.strip().split(None,2);rows[int(pid)]=(int(ppid),args)
roots=[]
for pid,(ppid,args) in rows.items():
    try:a=shlex.split(args)
    except ValueError:continue
    if len(a)>=4 and a[1].endswith(script) and a[2:4]==[base,tag]:roots.append(pid)
selected=set(roots)
while True:
    enlarged=selected|{pid for pid,(ppid,args) in rows.items() if ppid in selected}
    if enlarged==selected:break
    selected=enlarged
for pid in sorted(selected-set(roots),reverse=True)+roots:
    try:os.kill(pid,signal.SIGTERM)
    except ProcessLookupError:pass
print(dict(roots=roots,terminated=sorted(selected)))
