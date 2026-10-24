"""Mirror verified search improvements to the local REPORT at process output events."""
from core import *
import argparse,subprocess,shlex
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('script',choices=['fast_follow.py','matchings.py','closure.py','cone_close.py']);ap.add_argument('stem');ap.add_argument('label');ap.add_argument('--workers',type=int,default=12);a=ap.parse_args();assert re.fullmatch(r'[a-z0-9_]+',a.label)
 stem=Path(a.stem).resolve();assert stem.parent==OUT
 ssh=['ssh','-q','-o','ControlMaster=no','-o','ControlPath=none'];transport='ssh -q -o ControlMaster=no -o ControlPath=none'
 cmd='cd '+shlex.quote(str(ROOT))+' && nproc && uptime && env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python '+shlex.quote(str(OUT/a.script))+' '+shlex.quote(str(stem))+' --label '+a.label+' --workers '+str(a.workers)
 proc=subprocess.Popen(ssh+['jerry',cmd],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 with (OUT/(a.label+'.log')).open('w')as log,(OUT/(a.label+'.jsonl')).open('a')as trace:
  for line in proc.stdout:
   log.write(line);log.flush()
   try:r=json.loads(line)
   except ValueError:continue
   if not isinstance(r,dict)or 'desc'not in r:continue
   trace.write(json.dumps(r)+'\n');trace.flush()
   if r.get('stem'):
    subprocess.run(['rsync','-a','-e',transport,'jerry:'+str(OUT/r['stem'])+'.*',str(OUT)+'/'],check=True)
    report();print('VERIFIED',r['stem'],r['total'],r['exp_minus_A1'],flush=True)
 code=proc.wait();report();assert code==0,code;print('DONE',a.label,flush=True)
