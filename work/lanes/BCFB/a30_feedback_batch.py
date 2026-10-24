from a30_common import *
import subprocess,concurrent.futures
jobs=[(810+i,6+i%4,14+i%3*2) for i in range(8)]
def run(j):
 seed,depth,cap=j
 print('START',j,os.cpu_count(),os.getloadavg(),flush=True)
 with (D/'runs'/f'feedback_{seed}.log').open('w') as f:r=subprocess.run([sys.executable,str(H/'a30_feedback.py'),'--seed',str(seed),'--depth',str(depth),'--cap',str(cap),'--seconds','1200'],cwd=D,stdout=f,stderr=subprocess.STDOUT)
 print('EXIT',j,r.returncode,flush=True);assert r.returncode==0
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as e:list(e.map(run,jobs))
