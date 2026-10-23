import sys,json,random
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/DR'); import poc_grid as p
s={int(k):[(t,typ,frozenset(S)) for t,typ,S in v] for k,v in json.load(open('/home/jihoon/competitions/quantumn/work/lanes/DR/sched_zfirst.json')).items()}
# generic bip check/odd measure

def bip(E):
 adj={}
 for a,c in E:adj.setdefault(a,set()).add(c);adj.setdefault(c,set()).add(a)
 col={}
 for v in adj:
  if v in col:continue
  col[v]=0;st=[v]
  while st:
   a=st.pop()
   for z in adj[a]:
    if z in col:
     if col[z]==col[a]:return False
    else:col[z]=1-col[a];st.append(z)
 return True
# try various chain trees and verifier pairing with same builder by source transform; mutate partner and tree strings
orig=open('/home/jihoon/competitions/quantumn/work/lanes/DR/poc.py').read()
variants=[]
for par in [{0:1,1:2,2:3,3:2},{0:2,1:3,2:0,3:1},{0:3,1:2,2:1,3:0},{0:1,1:3,2:0,3:2}]:
 for tree in [(('m[2], m[3]','m[1], m[2]','m[0], m[1]')),(('m[0], m[3]','m[0], m[2]','m[0], m[1]')),(('m[1],m[3]','m[0],m[2]','m[0],m[1]'))]:
  q=orig.replace('partner = {0: 1, 1: 2, 2: 3, 3: 2}',f'partner = {par}')
  old='''t3 = place(t_end, "cx", cxo(m[2], m[3]))
            t2 = place(t3 - 1, "cx", cxo(m[1], m[2]))
            t1 = place(t2 - 1, "cx", cxo(m[0], m[1]))'''
  new=f'''t3 = place(t_end, "cx", cxo({tree[0]}))
            t2 = place(t3 - 1, "cx", cxo({tree[1]}))
            t1 = place(t2 - 1, "cx", cxo({tree[2]}))'''
  q=q.replace(old,new)
  open('/tmp/pg.py','w').write(q)
  sys.path.insert(0,'/tmp'); import importlib.util
  sp=importlib.util.spec_from_file_location('pg','/tmp/pg.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  b,_,_=m.build_clean(s,clean_z=True);E=set(tuple(qs) for t,k,kind,qs,tag in b.ops if kind=='cx')
  if bip(E):
   print('BIP',par,tree,b.next_q,len(E));
   try:print('proxy',m.proxy(s,builder=lambda s:m.build_clean(s,clean_z=True))[0])
   except Exception as e:print('proxyfail',e)
