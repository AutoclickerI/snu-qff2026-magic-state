from release import *
import subprocess
r=release(getbase(0));jobs=[]
for mode in [1,2]:
 for a,b,h in [(1,8,7),(8,1,7),(2,9,3),(9,2,3),(16,9,10),(9,16,10)]:
  for start in [35,36,37,38]:
   for gap in [1,2,3]:
    v=start+gap
    if v+2>42:continue
    rx=[r[q]['earliest']+2+int(mode==1 and q in(1,2,8))for q in A];rz=[r[q]['earliest']+1+int(q in(2,14))for q in A];jobs.append([mode,43,*rx,*rz,A.index(a),A.index(b),h,start,v])
request=str(len(jobs))+'\n'+'\n'.join(' '.join(map(str,j))for j in jobs)+'\n';(V/'bus_request.txt').write_text(request)
subprocess.run(['g++','-O3','-std=c++20',str(V/'layer_search.cpp'),'-o',str(V/'layer_search')],check=True,env={**os.environ,'TMPDIR':str(V)})
with(V/'bus_recipes.json').open('w')as f:subprocess.run([str(V/'layer_search')],input=request,text=True,stdout=f,check=True)
recs=json.loads((V/'bus_recipes.json').read_text());print('bus recipes',len(recs),flush=True)
