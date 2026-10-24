from pathlib import Path
import sys,json,collections
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));from common import *
V=H/'v30'
def graph(c,commute=False):
 ops=c['ops'];us=[unit(o)for o in ops];pre=[{}for o in ops];last={}
 def comm(a,b):
  if a.name==b.name=='CX':
   ac,at=map(int,S.QRE.findall(a.lines[0]));bc,bt=map(int,S.QRE.findall(b.lines[0]));return ac!=bt and bc!=at
  return False
 for j,u in enumerate(us):
  if commute:
   for i in range(j):
    overlap=set(us[i].qs)&set(u.qs)
    if overlap and not comm(us[i],u):pre[j][i]=sorted(overlap)
  else:
   for q in u.qs:
    if q in last:pre[j].setdefault(last[q],[]).append(q)
    last[q]=j
 return pre
def analyze(c,commute=False):
 ops=c['ops'];R=c['meta']['R'];pre=graph(c,commute);es=[];succ=[[]for _ in ops]
 for j,p in enumerate(pre):
  es.append(max((es[i]+1 for i in p),default=0))
  for i in p:succ[i].append(j)
 bound=max([es[i]+1 for i,o in enumerate(ops)if o['t']<R]+[es[i]-(o['t']-R)for i,o in enumerate(ops)if o['t']>=R]);ls=[R-1 if o['t']<R else o['t']for o in ops]
 for i in reversed(range(len(ops))):
  if succ[i]:ls[i]=min(ls[i],min(ls[j]-1 for j in succ[i]))
 records=[dict(i=i,t=o['t'],es=es[i],ls=ls[i],slack=ls[i]-es[i],lines=o['lines'],predecessors=pre[i])for i,o in enumerate(ops)]
 terminal=max(range(len(ops)),key=lambda i:es[i]-(max(0,ops[i]['t']-R)))
 paths=[]
 def trace(j,path):
  parents=[i for i in pre[j]if es[i]+1==es[j]]
  if not parents:paths.append(list(reversed(path+[j])));return
  for i in parents[:3]:
   if len(paths)<100:trace(i,path+[j])
 trace(terminal,[])
 return dict(R=R,minimum_R=bound,commuting_cx=commute,operations=records,longest_paths=paths)
if __name__=='__main__':
 c=read(Path(sys.argv[1])if len(sys.argv)>1 else H/'inputs/v30f')
 for comm in (False,True):
  d=analyze(c,comm);(V/('critical_commute.json'if comm else'critical.json')).write_text(json.dumps(d,indent=2))
  print('COMM',comm,'minimumR',d['minimum_R'],'paths',len(d['longest_paths']))
  for i in d['longest_paths'][0]:
   z=d['operations'][i];print(i,'old',z['t'],'ES',z['es'],'LS',z['ls'],'/'.join(z['lines']))
  print('LAST BEFORE ROUND')
  for q in range(36):
   seq=[z for z,o in zip(d['operations'],c['ops'])if q in unit(o).qs and o['t']<c['meta']['R']]
   if seq:print(q,seq[-1]['i'],seq[-1]['es']+1,'ready slack',48-seq[-1]['es']-1,'/'.join(seq[-1]['lines']))
