from release import *
import subprocess
jobs=[];r=release(getbase(0))
for family in [5,4]:
 for mode in [2,1]:
  for R in [42,43]:
   rx=[r[q]['earliest']+2+int(mode==1 and q in(1,2,8))for q in A];rz=[r[q]['earliest']+1+int(q in(2,14))for q in A];jobs.append([family,mode,R,*rx,*rz])
req=str(len(jobs))+'\n'+'\n'.join(' '.join(map(str,j))for j in jobs)+'\n';(V/'measure_request.txt').write_text(req)
subprocess.run(['g++','-O3','-std=c++20',str(V/'measure_search.cpp'),'-o',str(V/'measure_search')],check=True,env={**os.environ,'TMPDIR':str(V)})
with(V/'measure_recipes.json').open('w')as f:subprocess.run([str(V/'measure_search')],input=req,text=True,stdout=f,check=True)
print('measurement recipes',len(json.loads((V/'measure_recipes.json').read_text())),flush=True)
