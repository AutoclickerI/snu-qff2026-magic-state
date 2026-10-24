from a30_common import *
import subprocess,concurrent.futures,argparse
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--procs',type=int,default=8);a=p.parse_args();stem=Path(a.stem).resolve()
jobs=[('exact',[sys.executable,str(ROOT/'work/lanes/EVAL/exact2.py'),str(stem)+'.qasm','--third','--procs',str(a.procs),'--top','10','--json',str(stem)+'.exact.json']),('mc3',[sys.executable,str(H/'inputs/mc3.py'),str(stem),'--procs',str(a.procs)])]
def run(j):
 tag,cmd=j;print('START',tag,os.cpu_count(),os.getloadavg(),flush=True)
 with Path(str(stem)+'.'+tag+'.log').open('w') as log:r=subprocess.run(cmd,cwd=D,stdout=log,stderr=subprocess.STDOUT)
 print('EXIT',tag,r.returncode,flush=True);assert r.returncode==0
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:list(e.map(run,jobs))
