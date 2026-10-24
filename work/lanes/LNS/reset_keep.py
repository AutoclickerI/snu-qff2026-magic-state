from moves import *
cs=[]
for fam in ['h','w']:
 orig=read(ROOT/f'work/lanes/MAIN/v22{fam}_c2c9')
 pivot=next(c for c,d in init_moves(orig)if d['move']=='mx_init_pivots'and len(d['units'])==6)
 for sw in [False,True]:
  for watch in [False,True]:
   c=clone(pivot)
   if sw:
    ix=[next(i for i,u in enumerate(c['u'])if u.lines==[line]and c['t'][i]==t)for line,t in [('cx q[9],q[10];',20),('cx q[9],q[15];',21)]]
    i,j=ix;c['u'][i],c['u'][j]=c['u'][j],c['u'][i];c=retime(c)
   if watch:
    i=next(i for i,u in enumerate(c['u'])if u.lines==['reset q[2];']and c['t'][i]<15);b=bit(c);t=c['t'][i]
    c['u'].insert(i,Unit(['h q[2];',f'measure q[2] -> c[{b}];']));c['t'].insert(i,t-1);adddet(c,b);c=retime(c)
   cs.append((c,dict(family='init',move='reset_preserved_combo',base=fam,bc_mx=True,swap=sw,watch_q2=watch)))
if __name__=='__main__':batch(cs,'reset_keep',4)
