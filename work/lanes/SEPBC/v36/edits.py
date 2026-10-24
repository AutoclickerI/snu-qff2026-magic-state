from core import *
import collections
def zero(c,b):
 piv={}
 for line in c['tail']:
  v=sum(1<<int(x)for x in re.findall(r'c\[(\d+)\]',line))
  while v:
   h=v.bit_length()-1
   if h in piv:v^=piv[h]
   else:piv[h]=v;break
 v=1<<b
 while v:
  h=v.bit_length()-1
  if h not in piv:return False
  v^=piv[h]
 return True
def remove_check(c,b,mode):
 c=copy.deepcopy(c);assert zero(c,b),b;o=next(o for o in c['ops']if f'-> c[{b}];'in' '.join(o['lines']));u=unit(o);q=u.qs[0]
 if mode=='detector':c['tail'].remove(f'// DETECTOR c[{b}]');return c
 if mode=='omit':c['ops'].remove(o)
 elif mode=='reset':o['lines']=[f'reset q[{q}];']+([f'h q[{q}];']if u.name=='MX'else[])
 else:raise ValueError(mode)
 tail=[]
 for line in c['tail']:
  bs=[int(x)for x in re.findall(r'c\[(\d+)\]',line)if int(x)!=b]
  if bs:tail.append('// DETECTOR '+' '.join(f'c[{x}]'for x in bs))
 c['tail']=tail;return fix(c)
def prep_options(c):
 out=[]
 for q in range(36):
  seq=[o for o in c['ops']if q in unit(o).qs]
  for a,b in zip(seq,seq[1:]):
   u,v=unit(a),unit(b)
   if u.name not in('RESET','RX')or v.name not in('MEASURE','MX')or b['t']<=a['t']+1:continue
   if(u.name=='RX')!=(v.name=='MX'):continue
   rec=int(re.findall(r'c\[(\d+)\]',' '.join(b['lines']))[0])
   if zero(c,rec):out.append(dict(q=q,old=a['t'],new=b['t']-1,bit=rec,lines=a['lines']))
 return out
def delay_preps(c,selected):
 c=copy.deepcopy(c)
 for r in selected:
  o=next(o for o in c['ops']if o['t']==r['old']and o['lines']==r['lines']);o['t']=r['new']
 return fix(c)
def patch(c,edit,shift=0):
 c=copy.deepcopy(c);oldbits={int(x)for o in read(V/'inputs/v35a')['ops']for x in re.findall(r'c\[(\d+)\]',' '.join(o['lines']))};newbits=sorted({int(x)for o in edit.get('add',[])for x in re.findall(r'-> c\[(\d+)\]',' '.join(o['lines']))}-oldbits);b=bit(c);mp={x:b+i for i,x in enumerate(newbits)}
 remap=lambda line:re.sub(r'c\[(\d+)\]',lambda m:f'c[{mp.get(int(m[1]),int(m[1]))}]',line)
 for r in edit.get('remove',[]):
  matches=[o for o in c['ops']if o['lines']==r['lines']]
  if not matches:raise ValueError(('missing removal',r))
  o=min(matches,key=lambda o:abs(o['t']-r['t']));c['ops'].remove(o)
 for line in edit.get('detector_remove',[]):
  if line not in c['tail']:raise ValueError(('missing detector',line))
  c['tail'].remove(line)
 for r in edit.get('add',[]):
  t=r['t']+shift
  if not 0<=t<=46:raise ValueError(('outside incumbent depth',r,shift))
  c['ops'].append(dict(lines=[remap(l)for l in r['lines']],t=t,tag='integration',id=10000+len(c['ops'])))
 c['tail'] += [remap(l)for l in edit.get('detector_add',[])]
 return fix(c)
def echo(c,q,h,axis,init,first,last,end):
 b=bit(c);e=(h,q)if axis=='Z'else(q,h)
 add=[dict(t=init,lines=[f'reset q[{h}];']+([f'h q[{h}];']if axis=='Z'else[])),dict(t=first,lines=[f'cx q[{e[0]}],q[{e[1]}];']),dict(t=last,lines=[f'cx q[{e[0]}],q[{e[1]}];']),dict(t=end,lines=([f'h q[{h}];']if axis=='Z'else[])+[f'measure q[{h}] -> c[{b}];']+([f'h q[{h}];']if axis=='Z'else[]))]
 # The caller owns the new bit; do not pass it through old-base remapping.
 c=copy.deepcopy(c)
 for o in add:o.update(tag='integration',id=10000+len(c['ops']));c['ops'].append(o)
 c['tail'].append(f'// DETECTOR c[{b}]');return fix(c)
def st2(c,which='both',fund=True,mz19=True):
 if fund:
  for b in[39,40,41]:c=remove_check(c,b,'reset')
  for b in[42,43,46]:c=remove_check(c,b,'omit')
 if which in('15','both'):
  c=remove_check(c,45,'reset');o=next(o for o in c['ops']if o['lines']==['reset q[21];']);o['t']=32;c=echo(c,15,21,'X',19,20,29,30)
 if which in('20','both'):c=echo(c,20,26,'Z',19,20,30,31)
 if mz19:
  c=copy.deepcopy(c);o=next(o for o in c['ops']if o['lines']==['reset q[19];']and o['t']>=30);b=bit(c);o['lines']=[f'measure q[19] -> c[{b}];'];c['tail'].append(f'// DETECTOR c[{b}]')
 return fix(c)
def exchange(c,direction=0,edge=True,append=False):
 c=copy.deepcopy(c);R=c['meta']['R']
 if not append:
  for q,h,b in[(28,34,268),(29,35,267)]:
   c['ops']=[o for o in c['ops']if h not in unit(o).qs];c['tail'].remove(f'// DETECTOR c[{27 if q==28 else 26}] c[{b}]')
 if edge:
  u,v=(28,29)if direction==0 else(29,28);old,target=(27,26)if direction==0 else(26,27);t=R+2 if append else R+1
  if append:
   for o in c['ops']:
    if o['t']>=R and unit(o).name=='MEASURE'and unit(o).qs[0]in(28,29):o['t']=R+3
  c['ops'].append(dict(lines=[f'cx q[{u}],q[{v}];'],t=t,tag='integration',id=10000));parity(c,target,old)
 return fix(c)
def emit(c,n,description,rows):
 try:
  st,r=write(c,n,description);rows.append(dict(stem=n,description=description,screen=r))
 except Exception as e:rows.append(dict(stem=n,description=description,error=repr(e)));print(n,repr(e),flush=True)
if __name__=='__main__':
 c=base();rows=[];opts=prep_options(c);(V/'prep_options.json').write_text(json.dumps(opts,indent=2));print('neutral preparation candidates',opts,flush=True)
 for i,r in enumerate(opts):emit(delay_preps(c,[r]),f'prep_delay_{i}',dict(family='isolated_checked_prep',edit=r),rows)
 if opts:emit(delay_preps(c,opts),'prep_delay_all',dict(family='isolated_checked_prep',edits=opts),rows)
 for b in[39,40,41,42,43,45,46,181,182,183,184,185,186,187,188,264,269,270,271,278]:
  for mode in['omit','reset','detector']:
   try:emit(remove_check(c,b,mode),f'{mode}_{b}',dict(family='check_reprice',bit=b,mode=mode),rows)
   except Exception as e:rows.append(dict(stem=f'{mode}_{b}',error=repr(e)))
 for which in['15','20','both']:
  emit(st2(c,which,True,True),'st2_'+which,dict(family='ST2_v35b',echoes=which,funding='39/40/41 reset;42/43/46 omit;45 reset for echo15;MZ19'),rows)
 for direction in[0,1]:emit(exchange(c,direction),'c_exchange_'+str(direction),dict(family='C_copy_exchange',direction=direction),rows)
 emit(exchange(c,edge=False),'c_uncopy',dict(family='C_copy_exchange',edge=False),rows)
 emit(exchange(c,append=True),'c_append',dict(family='C_edge_extra_tick',edge=[28,29]),rows)
 (V/'initial_builds.json').write_text(json.dumps(rows,indent=2))
