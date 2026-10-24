import os,time,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent
now=time.monotonic();ticks=os.sysconf('SC_CLK_TCK');pids={}
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  if p.stat().st_uid!=os.getuid():continue
  s=(p/'stat').read_text().rsplit(')',1)[1].split();pids[p.name]=int(s[11])+int(s[12])
 except (OSError,ValueError):continue
f=H/('load_'+os.uname().nodename+'.json');out=dict(time=now,pids=pids,load=os.getloadavg()[0],cores=os.cpu_count())
if f.exists():
 old=json.loads(f.read_text());dt=now-old['time'];out['owner_cores']=sum(max(0,n-old['pids'].get(p,n))for p,n in pids.items())/ticks/dt;out['interval']=dt
f.write_text(json.dumps(out));print(json.dumps({k:v for k,v in out.items()if k!='pids'}))
