from release import *
import subprocess
from mutations import route14
jobs=[]
for route in [0,1]:
 r=release(route14(getbase(0))if route else getbase(0))
 for mode in [0,1,2,3,4]:
  for R in [42,43,44]:
   rx=[r[q]['earliest']+2-int(mode>=3 and q in((2,9)if route else(2,14)))+int(mode==0 or(mode in(1,3)and q in(1,2,8)))for q in A]
   rz=[r[q]['earliest']+1+int(q in((2,9)if route else(2,14)))for q in A];jobs.append([10*route+mode,R,*rx,*rz,-1,-1,-1,-1,-1])
request=str(len(jobs))+'\n'+'\n'.join(' '.join(map(str,j))for j in jobs)+'\n';(V/'layer_request.txt').write_text(request)
subprocess.run(['g++','-O3','-std=c++20',str(V/'layer_search.cpp'),'-o',str(V/'layer_search')],check=True,env={**os.environ,'TMPDIR':str(V)})
with(V/'layer_recipes.json').open('w')as f:subprocess.run([str(V/'layer_search')],input=request,text=True,stdout=f,check=True)
recipes=json.loads((V/'layer_recipes.json').read_text());print('recipes',len(recipes),flush=True)
