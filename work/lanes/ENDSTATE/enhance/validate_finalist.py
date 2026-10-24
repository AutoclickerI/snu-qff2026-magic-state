from common import *
import subprocess
name=sys.argv[1];procs=int(sys.argv[2]);receipts=[]
for mode in('speed','check','mc3'):
 with(H/(name+'.'+mode+'.log')).open('w')as f:
  r=subprocess.run([str(ROOT/'.venv/bin/python'),str(H/'gate.py'),mode,str(H/name),'--procs',str(procs)],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
 receipts.append(dict(mode=mode,exit_code=r.returncode));print(name,receipts[-1],flush=True)
 if r.returncode:break
 if mode=='speed'and json.loads((H/(name+'.speed.json')).read_text())['classification']!='FAST':break
 if mode=='check'and not json.loads((H/(name+'.check.json')).read_text())['passed']:break
(H/(name+'.validation.json')).write_text(json.dumps(receipts,indent=2))
