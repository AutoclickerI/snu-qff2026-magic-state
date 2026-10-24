"""Launch only within measured host and owner CPU headroom; never wait on files."""
import os,sys,json
import load
n=int(sys.argv[1]);d=load.out;owner=d.get('owner_cores')
if owner is None or d['load']+n>d['cores'] or owner+n>.75*d['cores']:
 print(json.dumps(dict(capacity_blocked=True,requested=n,load=d['load'],owner_cores=owner,cores=d['cores'])),flush=True);sys.exit(75)
os.execv(sys.executable,[sys.executable,*sys.argv[2:]])
