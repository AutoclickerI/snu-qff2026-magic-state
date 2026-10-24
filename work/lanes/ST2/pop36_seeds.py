"""Re-derive useful v35 mechanisms against v36b's actual native release slots."""
import sys,json,itertools,random,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop36_support as v
C=v.C;a=v.a;d=v.d

def single(c,q,t):return next(i for i,(u,tt)in enumerate(zip(c['u'],c['t']))if tt==t and u.qs==(q,))
def bybit(c,b):return next(i for i,u in enumerate(c['u'])if b in a.bits(' '.join(u.lines)))
def remove(c,ix):a.remove_units(c,set(ix))
def detector(c,b):c['tail'].append(f'// DETECTOR c[{b}]')
def add(c,t,ls):c['u'].append(C.Unit(ls));c['t'].append(t)
def measured(c,q,t):
 i=single(c,q,t);u=c['u'][i];assert u.name in('RESET','RX');b=C.bit(c);ls=[f'measure q[{q}] -> c[{b}];'];c['u'][i]=C.Unit([f'h q[{q}];']+ls+[f'h q[{q}];']if u.name=='RX'else ls);detector(c,b)

def q7_echo(c,mode):
 b=C.bit(c)
 if mode=='Zshort':spec=[(26,['reset q[13];','h q[13];']),(27,['cx q[13],q[7];']),(28,['cx q[13],q[7];']),(29,['h q[13];',f'measure q[13] -> c[{b}];','h q[13];'])]
 elif mode=='Xlong':spec=[(26,['reset q[13];']),(27,['cx q[7],q[13];']),(31,['cx q[7],q[13];']),(32,[f'measure q[13] -> c[{b}];'])]
 elif mode=='Zretime':
  i=single(c,7,29);assert c['u'][i].name=='TDG';c['t'][i]=32
  spec=[(26,['reset q[13];','h q[13];']),(27,['cx q[13],q[7];']),(31,['cx q[13],q[7];']),(32,['h q[13];',f'measure q[13] -> c[{b}];','h q[13];'])]
 else:raise ValueError(mode)
 for t,ls in spec:add(c,t,ls)
 detector(c,b)

def fold15(c,t=31,virgin=True):
 i=bybit(c,279);remove(c,[i]);a.strip_bits(c,[279])
 if virgin:remove(c,[single(c,21,19)])
 c['t'][bybit(c,45)]=t
 # Extend the data edge through the now-later helper readout where free.
 i=next(i for i,(u,tt)in enumerate(zip(c['u'],c['t']))if tt==28 and u.lines==['cx q[15],q[21];']);c['t'][i]=29

def q20_short(c):
 fold15(c,31)
 # q20 has a native data gate at35. The re-derived echo uses33/34.
 add(c,32,['reset q[21];']);add(c,33,['cx q[20],q[21];']);add(c,34,['cx q[20],q[21];']);b=C.bit(c);add(c,35,[f'measure q[21] -> c[{b}];']);detector(c,b)

def remove20z(c):
 ix=[single(c,26,18),bybit(c,280)]+[i for i,(u,t)in enumerate(zip(c['u'],c['t']))if t in(19,30)and u.lines==['cx q[26],q[20];']];assert len(ix)==4;remove(c,ix);a.strip_bits(c,[280])

def parity(c,bit):
 q,t={274:(19,17),275:(13,19)}[bit];i=single(c,q,t);assert c['u'][i].name=='RESET';b=C.bit(c);c['u'][i]=C.Unit([f'measure q[{q}] -> c[{b}];']);j=c['tail'].index(f'// DETECTOR c[{bit}]');c['tail'][j]=f'// DETECTOR c[{bit}] c[{b}]'

def early(c,b):
 q={40:8,41:14,42:20}[b];i=next(i for i,u in enumerate(c['u'])if q in u.qs);assert c['u'][i].name=='RESET';c['u'][i]=C.Unit([f'measure q[{q}] -> c[{b}];']);detector(c,b)

def phase(c):
 i=single(c,16,34);assert c['u'][i].name=='TDG';c['u'][i]=C.Unit(['tdg q[22];']);c['t'][i]=37

def funding(c,kind):
 if kind in('known','rich'):
  for b in(43,46):i=bybit(c,b);remove(c,[i]);a.strip_bits(c,[b])
 if kind=='rich':
  for b in(39,181,182,188):
   i=bybit(c,b);u=c['u'][i];q=u.qs[0];c['u'][i]=C.Unit([f'reset q[{q}];']+([f'h q[{q}];']if u.name=='MX'else[]));a.strip_bits(c,[b])
  i=single(c,20,7);assert c['u'][i].name=='RESET';remove(c,[i])

def edits(c,name):
 if name.startswith('q7_'):q7_echo(c,name[3:])
 elif name=='fold15':fold15(c)
 elif name=='fold15_reset':fold15(c,31,False)
 elif name=='q20_short':q20_short(c)
 elif name=='replace20':remove20z(c);q20_short(c)
 elif name=='drop20z':remove20z(c)
 elif name=='parity274':parity(c,274)
 elif name=='parity275':parity(c,275)
 elif name=='parities':parity(c,274);parity(c,275)
 elif name.startswith('restore'):early(c,int(name[7:]))
 elif name=='q1_mx7':measured(c,1,7)
 elif name=='phase22':phase(c)
 elif name.startswith('fund_'):funding(c,name[5:])
 elif name=='mz19_33':measured(c,19,33)
 else:raise ValueError(name)
 return c

def candidates():
 base=C.read(v.OUT/'base');yield'base',base,dict(family='baseline')
 names=['q7_Zshort','q7_Xlong','q7_Zretime','fold15','fold15_reset','q20_short','replace20','drop20z','parity274','parity275','parities','restore40','restore41','restore42','q1_mx7','phase22','fund_known','fund_rich','mz19_33']
 for n in names:yield n,edits(C.clone(base),n),dict(family='rederived_single',edits=[n])
 # Re-derived previous winner, acceptance-rich lineage, and factorial trades.
 for fund,echo,port in itertools.product(['none','known','rich'],['none','Zshort','Xlong'],['keep','fold15','replace20']):
  chosen=([]if fund=='none'else['fund_'+fund])+([]if echo=='none'else['q7_'+echo])+([]if port=='keep'else[port])+['q1_mx7','phase22']
  c=C.clone(base)
  for n in chosen:edits(c,n)
  yield f'bundle_{fund}_{echo}_{port}',c,dict(family='rederived_bundle',edits=chosen)
 for echo in ['Zshort','Xlong']:
  for restored in [[],[40],[40,41],[40,41,42]]:
   chosen=['replace20','q7_'+echo,'parities','q1_mx7','phase22']+['restore'+str(b)for b in restored];c=C.clone(base)
   for n in chosen:edits(c,n)
   yield 'winner_'+echo+'_'+('_'.join(map(str,restored))or'no_restore'),c,dict(family='previous_winner_rederived',edits=chosen)

if __name__=='__main__':
 import shutil
 for ext in('.qasm','.json'):shutil.copyfile(v.ROOT/'work/lanes/MAIN'/('v36b'+ext),str(v.OUT/'base')+ext)
 d.save(C.read(v.OUT/'base'),v.OUT/'base');ga=v.ga;ga.executable();jobs=[[],[]];seen=set();patches=[];rejected=[];base=C.read(v.OUT/'base')
 for name,c,desc in candidates():
  try:
   c=d.normalize(c);fp=d.digest(c)
   if fp in seen:continue
   seen.add(fp);part=(len(seen)-1)%2;od=v.OUT/f'seed{part}';od.mkdir(exist_ok=True);p=od/name;d.save(c,p);jobs[part].append(dict(stem=str(p.relative_to(v.H)),description=dict(desc,budget_screen=True)));patches.append(v.save_patch(name,base,c,desc))
  except Exception as e:rejected.append(dict(name=name,error=repr(e)))
 for part,rows in enumerate(jobs):(v.OUT/f'seed{part}/jobs.json').write_text(json.dumps(rows,indent=2))
 (v.OUT/'patches.json').write_text(json.dumps(patches,indent=2));(v.OUT/'seed_build.json').write_text(json.dumps(dict(counts=list(map(len,jobs)),rejected=rejected),indent=2));print('BUILT',list(map(len,jobs)),'rejected',rejected)
