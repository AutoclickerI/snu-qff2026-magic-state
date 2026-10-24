from build import *
from schedules import placement

def commute(x,y):
 if not set(x.qs)&set(y.qs):return True
 if x.name==y.name=='CX':
  c,t=map(int,S.QRE.findall(x.lines[0]));d,s=map(int,S.QRE.findall(y.lines[0]));return c!=s and d!=t
 return False
for base in ['watch9','hop_early']:
 h,u,ts,tail,meta=read(OUT/base);pre=set(meta['prefix_unit_indices']);removed=set();pairs=[]
 for i,x in enumerate(u):
  if i in pre or i in removed or ts[i]>=45 or x.name!='CX':continue
  for j in range(i+1,len(u)):
   if j in removed:continue
   y=u[j]
   if j not in pre and ts[j]<45 and x.lines==y.lines:removed|={i,j};pairs.append((x.lines,ts[i],ts[j]));break
   if not commute(x,y):break
 nu=[x for i,x in enumerate(u)if i not in removed];nt=[t for i,t in enumerate(ts)if i not in removed];meta['prefix_unit_indices']=[j for j,i in enumerate(i for i in range(len(u))if i not in removed)if i in pre];meta['cancelled']=pairs
 for mode in ['keep','alap']:
  save(base+'_cancel_'+mode,h,nu,nt if mode=='keep'else placement(nu),tail,meta)
