from a30_common import *
import subprocess,concurrent.futures,time
jobs=[('baseline_exact',[sys.executable,str(ROOT/'work/lanes/EVAL/exact2.py'),str(D/'inputs/v30f.qasm'),'--third','--procs','8','--top','10','--json',str(D/'baseline_exact.json')]),('baseline_allorders',[sys.executable,str(D/'sparse/sparse_walsh.py'),str(D/'inputs/v30f'),'72','canonical'])]
def run(item):
 tag,cmd=item;print(tag,os.cpu_count(),os.getloadavg(),flush=True)
 with (D/'runs'/(tag+'.log')).open('w') as log:r=subprocess.run(cmd,cwd=D,stdout=log,stderr=subprocess.STDOUT)
 print(tag,'EXIT',r.returncode,flush=True);assert r.returncode==0
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:list(e.map(run,jobs))
