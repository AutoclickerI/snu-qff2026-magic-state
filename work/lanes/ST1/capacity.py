"""Measure host/account CPU use over a sampling interval, not ps lifetime averages."""
import os,time,json,sys,datetime
from pathlib import Path
uid=os.getuid();hz=os.sysconf('SC_CLK_TCK');n=os.cpu_count()
def snapshot():
 out={}
 for p in Path('/proc').iterdir():
  if p.name.isdigit():
   try:
    v=(p/'stat').read_text().rsplit(')',1)[1].split();out[int(p.name)]=(p.stat().st_uid,(int(v[11])+int(v[12]))/hz)
   except(OSError,ValueError):pass
 return out
st=time.monotonic();a=snapshot();time.sleep(.5);b=snapshot();dt=time.monotonic()-st
own=sum(max(0,v[1]-a[k][1])for k,v in b.items()if k in a and v[0]==uid)/dt
allcpu=sum(max(0,v[1]-a[k][1])for k,v in b.items()if k in a)/dt
tasks={}
for pp in Path('/proc').iterdir():
 if not pp.name.isdigit()or int(pp.name)==os.getpid():continue
 try:
  args=(pp/'cmdline').read_bytes().split(b'\0');stat=(pp/'stat').read_text().rsplit(')',1)[1].split()
  if pp.stat().st_uid!=uid or len(args)<2 or not Path(args[0].decode()).name.startswith('python'):continue
  if not any(b'work/lanes/ST1/'in arg for arg in args[1:])or args[1].endswith(b'capacity.py'):continue
  workers=1
  for flag in (b'--workers',b'--procs'):
   if flag in args:workers=max(workers,int(args[args.index(flag)+1]))
  tasks[int(pp.name)]=(int(stat[1]),workers)
 except(OSError,ValueError,UnicodeDecodeError,IndexError):pass
roots={p:w for p,(parent,w)in tasks.items()if parent not in tasks};reserved=sum(roots.values());kst=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)));lane_limit=(24 if kst>=datetime.datetime(2026,10,25,2,20,tzinfo=kst.tzinfo)else 16)if n==96 else 8
headroom=min(.75*n-own,n-max(allcpu,os.getloadavg()[0]),lane_limit-reserved)
print(json.dumps(dict(cores=n,own=own,total=allcpu,load=os.getloadavg(),lane_reserved=reserved,lane_limit=lane_limit,lane_processes=roots,headroom=headroom)),flush=True)
if len(sys.argv)>1 and headroom<float(sys.argv[1]):sys.exit(75)
