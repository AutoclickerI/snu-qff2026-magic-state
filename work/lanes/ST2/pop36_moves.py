"""Native mutation families; generated schedules retain exact judge validation."""
import sys,json,random,re,itertools,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop36_support as v
C=v.C;d=v.d;a=v.a
import moves as M
FAMILIES=['timing','commute','init','basis','guard_window','guard_helper','guard_exchange','menu','detector','new_echo','macro','readout','phase','seed_edit']

def choose(gen,rng):
 result=None
 for j,item in enumerate(gen,1):
  if rng.randrange(j)==0:result=item
 return result

def guards(c):
 result=[];singles={a.bits(s)[0]for s in c['tail']if len(a.bits(s))==1}
 for i,(u,t)in enumerate(zip(c['u'],c['t'])):
  bs=a.bits(' '.join(u.lines))
  if u.name not in ('MEASURE','MX')or len(bs)!=1 or bs[0]not in singles:continue
  h=u.qs[0];prev=[j for j in range(i)if h in c['u'][j].qs]
  if len(prev)<3:continue
  j,k=prev[-2:]
  if c['u'][j].name!='CX'or c['u'][k].lines!=c['u'][j].lines:continue
  ini=prev[-3]
  if c['u'][ini].name not in ('RESET','RX','MEASURE','MX'):continue
  q=next(z for z in c['u'][j].qs if z!=h)
  result.append(dict(q=q,h=h,bit=bs[0],axis='Z'if u.name=='MX'else'X',indices=[ini,j,k,i],times=[c['t'][x]for x in [ini,j,k,i]]))
 return result

def drop(c,g):
 x=C.clone(c);a.remove_units(x,set(g['indices']));a.strip_bits(x,[g['bit']]);return d.normalize(x)

def timing(c,rng):
 # FRESH has priced v35a's complete standalone slack sweep. Here mutations
 # act on v35b populations and combinations, especially changed helper sites.
 r=choose(M.timing_moves(c,True),rng)
 if r is None:return None,{}
 return r

def commute(c,rng):
 us=c['u'];pairs=[]
 for i,u in enumerate(us):
  if u.name!='CX':continue
  for j in range(i+1,len(us)):
   w=us[j]
   if not C.commute(u,w):break
   if w.name=='CX'and set(u.qs)&set(w.qs)and all(C.commute(w,z)for z in us[i+1:j]):pairs.append((i,j))
 if not pairs:return None,{}
 i,j=rng.choice(pairs);x=C.clone(c);x['u'][i],x['u'][j]=x['u'][j],x['u'][i];x=C.retime(x)
 return x,dict(family='commute',indices=[i,j],ops=[us[i].lines,us[j].lines])

def init(c,rng):
 options=[i for i,(u,t)in enumerate(zip(c['u'],c['t']))if u.name in ('RESET','RX','MEASURE','MX')and t<44]
 i=rng.choice(options);u=c['u'][i];x=C.clone(c);q=u.qs[0];b=a.bits(' '.join(u.lines))
 if u.name in ('RESET','RX'):
  bit=C.bit(x);ls=[f'measure q[{q}] -> c[{bit}];']
  if u.name=='RX':ls=[f'h q[{q}];']+ls+[f'h q[{q}];']
  x['u'][i]=C.Unit(ls);x['tail'].append(f'// DETECTOR c[{bit}]')
 else:
  form=rng.choice(['omit','reset','reset'])
  if form=='omit':a.remove_units(x,{i})
  else:x['u'][i]=C.Unit([f'reset q[{q}];']+([f'h q[{q}];']if u.name=='MX'else[]))
  a.strip_bits(x,b)
 return x,dict(family='init',q=q,time=c['t'][i],old=u.lines)

def basis(c,rng):
 gg=guards(c)
 if gg and rng.random()<.7:
  g=rng.choice(gg);x=C.clone(c);ini,j,k,m=g['indices'];q,h=g['q'],g['h'];ax='X'if g['axis']=='Z'else'Z';b=g['bit']
  x['u'][ini]=C.Unit([f'reset q[{h}];']+([f'h q[{h}];']if ax=='Z'else[]))
  edge=f'cx q[{q}],q[{h}];'if ax=='X'else f'cx q[{h}],q[{q}];'
  x['u'][j]=C.Unit([edge]);x['u'][k]=C.Unit([edge]);ls=[f'measure q[{h}] -> c[{b}];'];x['u'][m]=C.Unit(([f'h q[{h}];']+ls+[f'h q[{h}];'])if ax=='Z'else ls)
  return x,dict(family='guard_axis',guard=g,axis=ax)
 opts=[i for i,u in enumerate(c['u'])if u.name in ('MX','MEASURE')and u.qs[0]not in C.D];i=rng.choice(opts);u=c['u'][i];q=u.qs[0];b=a.bits(' '.join(u.lines))[0];x=C.clone(c);ls=[f'measure q[{q}] -> c[{b}];'];x['u'][i]=C.Unit(ls if u.name=='MX'else[f'h q[{q}];']+ls+[f'h q[{q}];'])
 return x,dict(family='readout_basis',q=q,bit=b,old=u.name)

def guard_window(c,rng):
 gg=guards(c)
 if not gg:return None,{}
 g=rng.choice(gg);x=C.clone(c);ini,j,k,m=g['indices'];chosen=rng.choice([ini,j,k,m]);qset=set(x['u'][chosen].qs);occupied={t for ii,(u,t)in enumerate(zip(x['u'],x['t']))if ii!=chosen and set(u.qs)&qset}
 times=g['times'];pos=g['indices'].index(chosen);lo=0 if pos==0 else times[pos-1]+1;hi=43 if pos==3 else times[pos+1]-1
 if pos==0:lo=max([t+1 for ii,(u,t)in enumerate(zip(x['u'],x['t']))if ii not in g['indices']and g['h']in u.qs and t<times[0]]+[0])
 if pos==3:hi=min([t-1 for ii,(u,t)in enumerate(zip(x['u'],x['t']))if ii not in g['indices']and g['h']in u.qs and t>times[3]]+[43])
 ts=[t for t in range(lo,hi+1)if t not in occupied and t!=x['t'][chosen]]
 if not ts:return None,{}
 new=rng.choice(ts);x['t'][chosen]=new;return x,dict(family='guard_window',guard=g,slot=pos,new=new)

def guard_helper(c,rng):
 gg=guards(c)
 if not gg:return None,{}
 g=rng.choice(gg);q,h=g['q'],g['h'];ns=[z for z in range(36)if z!=h and z not in C.D and abs(z//6-q//6)+abs(z%6-q%6)==1]
 rng.shuffle(ns)
 for hh in ns:
  busy={t for u,t in zip(c['u'],c['t'])if hh in u.qs};qbusy={t for i,(u,t)in enumerate(zip(c['u'],c['t']))if q in u.qs and i not in g['indices']}
  candidates=[]
  for start in range(g['times'][0],g['times'][-1]-2):
   for end in range(start+3,g['times'][-1]+1):
    if not(set(range(start,end+1))&busy)and start+1 not in qbusy and end-1 not in qbusy:candidates.append((start,end))
  if not candidates:continue
  start,end=max(candidates,key=lambda z:z[1]-z[0]);nxt=[u for u,t in zip(c['u'],c['t'])if hh in u.qs and t>end]
  if nxt and nxt[0].name not in ('RESET','RX','MEASURE','MX'):continue
  x=C.clone(c)
  for i,t in zip(g['indices'],[start,start+1,end-1,end]):x['u'][i]=C.Unit([s.replace(f'q[{h}]',f'q[{hh}]')for s in x['u'][i].lines]);x['t'][i]=t
  return x,dict(family='guard_helper',guard=g,new_helper=hh,window=[start,end])
 return None,{}

def detector(c,rng):
 x=C.clone(c)
 if rng.random()<.65:
  i=rng.randrange(len(x['tail']));line=x['tail'].pop(i);return x,dict(family='detector_drop',line=line)
 measured={b for u in x['u']for s in u.lines for b in a.bits(s)};base=C.read(v.OUT/'base')
 options=[s for s in base['tail']if s not in x['tail']and set(a.bits(s))<=measured]
 options += [f'// DETECTOR c[{b}]'for b in measured if f'// DETECTOR c[{b}]'not in x['tail']]
 if not options:return None,{}
 s=rng.choice(options);x['tail'].append(s);return x,dict(family='detector_add',line=s)

def menu(c,rng):
 menu=json.loads((v.OUT/'patches.json').read_text());r=rng.choice(menu);p={key:{(x[0],tuple(x[1]))if key in ('add','remove')else x for x in val}for key,val in r['patch'].items()};x=v.apply_patch(c,v.renumber_patch(p,c),True);return x,dict(family='menu',source=r['name'])

def new_echo(c,rng):
 # Include intermediate data carriers before the final transfers.
 saved=C.D
 try:
  C.D=list(dict.fromkeys(saved+[4,8,15,16]));return d.idle_protect(c,rng)
 finally:C.D=saved
def guard_exchange(c,rng):
 gg=guards(c);choices=[g for g in gg if g['bit']==274]or gg
 if not choices:return None,{}
 g=rng.choice(choices);x=drop(c,g);history=[dict(family='drop_guard',guard=g)]
 for _ in range(rng.choice([1,2,3])):
  xx,dd=rng.choice([new_echo,new_echo,menu,init,guard_window])(x,rng)
  if xx is not None:x=d.normalize(xx);history.append(dd)
 return x,dict(family='guard_exchange',moves=history)
def macro(c,rng):
 x=d.weighted_window(c,rng,rng.choice(['prefix_mix','release','A_wait','idle_mix']))
 return x

def readout(c,rng):
 # First use an idle terminal slot. Delaying every output by a full tick
 # was repeatedly measured to roughly double the loss in this architecture.
 last={u.qs[0]:i for i,u in enumerate(c['u'])if u.name=='MEASURE'and c['t'][i]>=44};fits=[]
 for q,i in last.items():
  for h,j in last.items():
   if q==h or abs(q//6-h//6)+abs(q%6-h%6)!=1:continue
   t=min(c['t'][i],c['t'][j])-1
   if any(set(u.qs)&{q,h}and tt==t for u,tt in zip(c['u'],c['t'])):continue
   fits.append((q,h,i,j,t))
 if fits:
  q,h,i,j,t=rng.choice(fits);x=C.clone(c);ba=a.bits(' '.join(x['u'][i].lines))[0];bb=a.bits(' '.join(x['u'][j].lines))[0]
  x['u'].append(C.Unit([f'cx q[{q}],q[{h}];']));x['t'].append(t)
  for k,s in enumerate(x['tail']):
   bits=set(a.bits(s))
   if bb in bits:bits^={ba};x['tail'][k]='// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bits))
  return x,dict(family='terminal_edge_in_slack',q=q,h=h,t=t)
 # Full existing move-set readout enumeration can fail if old terminal edges
 # are absent; retain every yielded new edge before that legacy removal branch.
 gg=M.readout_moves(c);out=[]
 try:
  for item in gg:out.append(item)
 except (KeyError,ValueError):pass
 out=[z for z in out if max(z[0]['t'])<=max(c['t'])]
 return rng.choice(out)if out else(None,{})

def mutate(c,rng,fam):
 return globals()[fam](c,rng)


def phase(c,rng):
 opts=[]
 for source,target,t in [(16,22,37),(10,4,31),(8,21,39)]:
  ix=[i for i,u in enumerate(c['u'])if u.name=='TDG'and u.qs==(source,)]
  if ix and not any(target in u.qs and tt==t for u,tt in zip(c['u'],c['t'])):opts.append((ix[0],target,t))
 if not opts:return None,{}
 i,q,t=rng.choice(opts);x=C.clone(c);old=x['u'][i].lines;x['u'][i]=C.Unit([f'tdg q[{q}];']);x['t'][i]=t
 return x,dict(family='phase_hop',old=old,new=q,time=t)

def seed_edit(c,rng):
 import pop36_seeds as seeds
 name=rng.choice(['q7_Zshort','q7_Xlong','q7_Zretime','fold15','fold15_reset','q20_short','replace20','drop20z','parity274','parity275','parities','restore40','restore41','restore42','q1_mx7','phase22','fund_known','fund_rich','mz19_33'])
 return seeds.edits(C.clone(c),name),dict(family='rederived_edit',name=name)
