"""Run the unchanged MAIN mc3 source, capture gates, and retain exact receipts."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import subprocess,argparse,json,re,hashlib,time
H=Path(__file__).resolve().parent;D=H/'blue';os.environ['XTIM_TWIRL_CACHE_DIR']=str(D/'.xtim_cache')
p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--procs',type=int,default=6);p.add_argument('--procs-file');a=p.parse_args()
code=H/'inputs/mc3.py';assert hashlib.sha256(code.read_bytes()).hexdigest()=='dc79b517931ed6cdb797870b0960a7e66076db9b29bd151c3d0f12235c08eb6b'
for name in a.stems:
 procs=int(Path(a.procs_file).read_text()) if a.procs_file else a.procs
 f=D/'finalists'/name;v=json.loads(f.with_suffix('.verify.json').read_text());assert v.get('exact_verified') and v.get('gates_pass'),(name,v)
 print(json.dumps(dict(event='capacity',cores=os.cpu_count(),load=os.getloadavg(),procs=procs)),flush=True);start=time.monotonic()
 with f.with_suffix('.mc.log').open('w') as log:
  pr=subprocess.Popen([sys.executable,str(code),str(f),'--procs',str(procs)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=D,text=True)
  for line in pr.stdout:log.write(line);log.flush();print(line,end='',flush=True)
  rc=pr.wait()
 txt=f.with_suffix('.mc.log').read_text();assert rc==0 and str(f)+' check True' in txt,(name,rc,txt[-1000:]);rows=[]
 for line in txt.splitlines():
  m=re.search(r'^'+re.escape(str(f))+r' (0|1000|2000) (\S+) ± (\S+) acc (\S+)',line)
  if m:rows.append(dict(seed=int(m[1]),score=float(m[2]),sem=float(m[3]),acceptance=float(m[4])))
 assert [r['seed'] for r in rows]==[0,1000,2000] and rows[0]['acceptance']>=.5
 out=dict(stem=name,procs=procs,seeds=rows,mean=sum(r['score'] for r in rows)/3,seconds=time.monotonic()-start,source_sha256=hashlib.sha256(code.read_bytes()).hexdigest(),source='byte-identical MAIN/spec/mc3.py copied into BCFB/inputs')
 f.with_suffix('.mc.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
