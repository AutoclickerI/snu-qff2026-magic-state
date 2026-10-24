"""Process-exit-driven portfolio launcher with host/process capacity gates."""
from pathlib import Path
import os,sys,json,subprocess,ctypes,select,time
V=Path(__file__).resolve().parent;ROOT=V.parents[3]
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
kind=sys.argv[1];limit=int(sys.argv[2]);jobs=[]
if kind=='contracts':
    for i in range(1,8):jobs.append(['rank4',str(i),'--seed',str(1100+i),'--depth','11','--cap','68'])
    for i in range(9,16):jobs.append(['policy',str(i),'--seed',str(1100+i),'--depth','10','--cap','57'])
elif kind=='helpermx':
    jobs=[['helpermx','0','--seed','1301','--depth','9','--cap','57','--helpers','18,24,30,31,32,33,34,35'],['helpermx','0','--seed','1302','--depth','10','--cap','55','--helpers','18,24']]
else:
    jobs=[['bell4','0','--seed','1201','--depth','13','--cap','86'],['bell7','0','--seed','1202','--depth','15','--cap','114']]
    for j,(D,helpers) in enumerate([(10,'18,24'),(10,'30,31,32,33,34,35'),(9,'18,24,30,31,32,33,34,35')]):jobs.append(['helper','0','--seed',str(1210+j),'--depth',str(D),'--cap','57','--helpers',helpers])
    for i in range(7):jobs.append(['c6',str(i),'--seed',str(1220+i),'--depth','11','--cap','64'])
libc=ctypes.CDLL(None,use_errno=True);running={};results=[]
while jobs or running:
    ps=[r.split() for r in subprocess.check_output(['ps','-u',str(os.getuid()),'-o','pid=,pcpu=,stat='],text=True).splitlines()];used=sum(float(r[1]) for r in ps if 'T' not in r[2])/100
    while jobs and len(running)<limit and used+1<=.75*os.cpu_count() and os.getloadavg()[0]<os.cpu_count():
        args=jobs.pop(0);tag=args[0]+'_'+args[1]+'_'+args[3];f=(V/(tag+'.log')).open('w');p=subprocess.Popen([str(ROOT/'.venv/bin/python'),str(V/'search30.py'),*args],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT);running[p.pid]=(p,f,args);used+=1;print(json.dumps(dict(event='launch',pid=p.pid,args=args,used=used)),flush=True)
    fds={}
    for pid in set(running)|{int(r[0]) for r in ps if float(r[1])>15 and 'T' not in r[2]}:
        fd=libc.syscall(434,pid,0)
        if fd>=0:fds[fd]=pid
    if not fds:raise RuntimeError('No process-exit source for capacity')
    select.select(list(fds),[],[])
    for fd in fds:os.close(fd)
    for pid,(p,f,args) in list(running.items()):
        rc=p.poll()
        if rc is not None:f.close();results.append(dict(args=args,returncode=rc));del running[pid];print(json.dumps(results[-1]),flush=True)
(V/(kind+'.portfolio.json')).write_text(json.dumps(results,indent=2))
