"""Physical cultivation relayouts preserving the accepted logical construction."""
from common import *
BASE_PD=[0,20,7,4,3,15,8]
def transform(pre,det,variant):
 pre=copy.deepcopy(pre);det=det[:];data=BASE_PD[:];tokens=set(variant.split('+'))-{'base'}
 assert tokens<=set(['flag12','cats13','cats6','m20to19','m20to21','m20to26','m15to16','release20','release15']),tokens
 if 'flag12'in tokens:
  pre=[Unit(rename(u.lines,{19:12}))for u in pre]
 if tokens&{'cats13','cats6'}:
  target=13 if 'cats13'in tokens else 6
  start1=max(i for i,u in enumerate(pre)if u.name=='RX'and u.qs==(1,));start6=min(i for i,u in enumerate(pre)if 6 in u.qs)
  new=[]
  for i,u in enumerate(pre):
   mp={}
   if i>=start1:mp[1]=target
   if i>=start6:mp[6]=1
   new.append(Unit(rename(u.lines,mp)))
  pre=new
 moves=[]
 for token in sorted(tokens):
  if token.startswith('m20to'):moves.append((20,14,int(token[5:]),80))
  if token=='m15to16':moves.append((15,9,16,81))
 for src,cat,dst,bit in moves:
  ti=next(i for i,u in enumerate(pre)if u.lines==[f't q[{src}];']);first=next(i for i in range(ti+1,len(pre))if pre[i].lines==[f'cx q[{cat}],q[{src}];']);last=max(i for i in range(first+1,len(pre))if pre[i].lines==[f'cx q[{cat}],q[{src}];']);mi=next(i for i in range(last+1,len(pre))if pre[i].name=='MX'and pre[i].qs==(cat,));mb=int(re.findall(r'c\[(\d+)\]',' '.join(pre[mi].lines))[0]);new=[]
  release=f'release{src}'in tokens
  if release:det.append(f'// DETECTOR c[{bit+2}]')
  for i,u in enumerate(pre):
   if i==last:
    if release:new.append(Unit([f'reset q[{src}];']))
    new.extend([Unit([f'cx q[{cat}],q[{src}];']),Unit([f'h q[{cat}];',f'measure q[{cat}] -> c[{bit}];',f'h q[{cat}];']),Unit([f'cx q[{src}],q[{dst}];'])]);continue
   if i==mi:u=Unit(rename(u.lines,{cat:src}))
   if u.lines==[f'tdg q[{src}];']:u=Unit([f'tdg q[{dst}];'])
   new.append(u)
   if i==first:
    new.extend([Unit([f'reset q[{dst}];']),Unit([f'cx q[{src}],q[{dst}];']),Unit([f'cx q[{dst}],q[{src}];'])])
    if release:new.append(Unit([f'measure q[{src}] -> c[{bit+2}];']))
  pre=new;data[data.index(src)]=dst
  det=[l+f' c[{bit}]'if re.search(r'c\['+str(mb)+r'\](?!\d)',l)else l for l in det]
 return pre,det,data
