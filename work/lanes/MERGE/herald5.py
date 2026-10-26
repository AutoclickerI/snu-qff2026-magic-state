"""Atomic reset heralds, bounded joint retiming, and detector-span completion."""
import copy,itertools,json,re
from functools import lru_cache
import menu as M

OLD_APPLY=M.apply_edit
M.ORDER.update(herald=3.5,detparity=8.5)

def apply_edit(c,e):
 if e['fam']=='polishguard' and 'offset'in e:
  d=e['offset']
  if e.get('remove28',True):c=OLD_APPLY(c,dict(fam='rmcx',a=28,b=22,t=29+d))
  c=OLD_APPLY(c,dict(fam='shift',name='RESET',qs=[23],t=29+d,nt=28+d))
  c=OLD_APPLY(c,dict(fam='cx',a=23,b=22,t=29+d))
  if e['switch21']:
   c=OLD_APPLY(c,dict(fam='rmcx',a=21,b=20,t=30+d));c=OLD_APPLY(c,dict(fam='cx',a=21,b=22,t=30+d))
  return c
 if e['fam']=='detparity':
  c['tail'].append('// DETECTOR '+' '.join(f'c[{b}]' for b in e['bits']));return c
 if e['fam']!='herald':return OLD_APPLY(c,e)
 for prior in e.get('prefix',[]):c=OLD_APPLY(c,prior)
 o=M._find(c,e['t'],e['q'],e['name'])
 if e.get('prepend'):
  for p in c['ops']:p['t']+=1
  o['t']=0;mt=1
 else:
  # Joint moves are simultaneous, so an occupied predecessor cell can be freed.
  references=[(next(x for x in c['ops'] if x['t']==move['t'] and x['lines']==move['lines']),move['nt']) for move in e['moves']]
  for p,nt in references:p['t']=nt
  if e.get('reuse'):c['ops'].remove(o)
  else:o['t']=e['t']-1
  mt=e['t']
 b=M.bit(c);q=e['q'];lines=[f'measure q[{q}] -> c[{b}];']
 if e['name']=='RX':lines=[f'h q[{q}];']+lines+[f'h q[{q}];']
 c['ops'].append(dict(t=mt,lines=lines));c['tail'].append(f'// DETECTOR c[{b}]')
 # The emitter's native-time check also enforces no same-qubit collision.
 return c
M.apply_edit=apply_edit

def cascades(c,index,target,limit=5):
 """Unique minimal order-preserving predecessor cascade, at most two ticks per op."""
 ops=c['ops'];times={i:o['t'] for i,o in enumerate(ops)};moved=set()
 def move(i,nt):
  if nt<0 or ops[i]['t']-nt>2 or M.unit(ops[i]).name not in ('RESET','RX','CX','MX','MEASURE'):raise ValueError('retiming boundary')
  if i not in moved and len(moved)>=limit:raise ValueError('cascade exceeds five neighbouring units')
  moved.add(i)
  for q in M.unit(ops[i]).qs:
   pred=[j for j,o in enumerate(ops) if q in M.unit(o).qs and o['t']<ops[i]['t']]
   if pred:
    j=max(pred,key=lambda j:ops[j]['t'])
    if times[j]>=nt:move(j,nt-1)
  times[i]=nt
 move(index,target)
 return [dict(t=ops[i]['t'],nt=times[i],lines=ops[i]['lines']) for i in sorted(moved,key=lambda i:ops[i]['t'])]

def _menu(c,only=None):
 es={};audit=[]
 for idx,o in enumerate(c['ops']):
  if only is not None and idx not in only:continue
  u=M.unit(o)
  if u.name not in ('RESET','RX'):continue
  q=u.qs[0];t=o['t'];base=dict(fam='herald',q=q,t=t,name=u.name,moves=[])
  variants=[];errors=[]
  prev=[(j,p)for j,p in enumerate(c['ops'])if q in M.unit(p).qs and p['t']<t]
  if t==0:variants.append(dict(base,prepend=True))
  elif not prev or max(p['t']for _,p in prev)<t-1:variants.append(base)
  else:
   j,p=max(prev,key=lambda jp:jp[1]['t'])
   if M.unit(p).name==u.name:variants.append(dict(base,reuse=True))
   for nt in (t-2,t-3):
    try:variants.append(dict(base,moves=cascades(c,j,nt)))
    except ValueError as ex:errors.append(dict(target=nt,error=str(ex)))
  if prev and max(p['t']for _,p in prev)==t-1:
   for moves in joint_cpsat(c,idx):
    if moves not in [e['moves']for e in variants]:variants.append(dict(base,moves=moves,solver='CP-SAT commuting local schedule'))
  if not variants:
   # A deletion can both buy acceptance and unlock the missing preparation slot.
   for removal in M.removals(c):
    if removal['fam']!='rm':continue
    cells=M.touched(c,removal)
    if not any(qq in ({q}|set(M.ADJ[q])) and t-4<=tt<t for qq,tt in cells):continue
    try:
     d=OLD_APPLY(copy.deepcopy(c),removal)
     ii=next(i for i,p in enumerate(d['ops'])if p['t']==t and p['lines']==o['lines'])
     for moves in joint_cpsat(d,ii,1):variants.append(dict(base,moves=moves,prefix=[removal],solver='CP-SAT with acceptance-buyer ejection'))
    except (ValueError,StopIteration,M.Invalid) as ex:errors.append(dict(removal=removal['id'],error=repr(ex)))
  for k,e in enumerate(variants):
   e['id']=f'herald:{u.name}{q}@{t}:v{k}'
   try:M.apply_bundle(c,[e]);es[e['id']]=e
   except Exception as ex:errors.append(dict(id=e['id'],error=repr(ex)))
  audit.append(dict(q=q,t=t,name=u.name,attempted=len(variants),available=[i for i in es if i.startswith(f'herald:{u.name}{q}@{t}:')],blocked=errors))
 return es,audit

@lru_cache(maxsize=128)
def detgap(text):
 """Clifford-surrogate kernel, independently sampled then exact-priced downstream."""
 import stim,numpy as np
 circ=stim.Circuit();bits=[]
 for line in text.splitlines():
  s=line.strip()
  if not s or s.startswith(('//','OPENQASM','include','qreg','creg','barrier')):continue
  name=s.split()[0];qs=list(map(int,re.findall(r'q\[(\d+)\]',s)))
  if name=='measure':circ.append('M',qs);bits.append(int(re.findall(r'c\[(\d+)\]',s)[0]))
  elif name in ('reset','h','cx'):circ.append({'reset':'R','h':'H','cx':'CX'}[name],qs)
  elif name not in ('t','tdg','id'):raise ValueError(s)
 samp=circ.compile_sampler(seed=7).sample(20000);rows=[int.from_bytes(row.tobytes(),'little')for row in np.packbits(samp,axis=1,bitorder='little')]
 def reduce(v,sp):
  while v:
   h=v.bit_length()-1
   if h not in sp:return v
   v^=sp[h]
  return 0
 piv={}
 for v in rows:
  v=reduce(v,piv)
  if v:piv[v.bit_length()-1]=v
 red=dict(piv)
 for h in sorted(red):
  for k in red:
   if k!=h and red[k]>>h&1:red[k]^=red[h]
 kernel=[]
 for f in range(len(bits)):
  if f not in red:
   v=1<<f
   for h,r in red.items():
    if r>>f&1:v|=1<<h
   kernel.append(v)
 col={b:i for i,b in enumerate(bits)};dets=[list(map(int,re.findall(r'c\[(\d+)\]',l)))for l in text.splitlines()if l.startswith('// DETECTOR')];span={};nondet=[]
 for d in dets:
  v=0
  for b in d:v^=1<<col[b]
  if any((v&r).bit_count()%2 for r in piv.values()):nondet.append(d)
  v=reduce(v,span)
  if v:span[v.bit_length()-1]=v
 rank=len(span);extra=[]
 for k in kernel:
  r=reduce(k,span)
  if r:span[r.bit_length()-1]=r;extra.append([bits[i]for i in range(len(bits))if r>>i&1])
 assert not nondet,nondet
 return dict(measurements=len(bits),detector_rank=rank,kernel_dimension=len(kernel),extra=extra,surrogate='T/TDG -> I, 20000 noiseless samples; all proposals independently exact-validated')

def detector_menu(c,text):
 gap=detgap(text);es={}
 for bs in gap['extra']:
  i='det:'+','.join(map(str,bs));es[i]=dict(id=i,fam='detparity',bits=bs)
 return es,gap


def commute(a,b):
 ua,ub=M.unit(a),M.unit(b)
 if not set(ua.qs)&set(ub.qs):return True
 if ua.name==ub.name=='CX':
  x,y=M.cx_qs(a);z,w=M.cx_qs(b);return x!=w and y!=z
 if ub.name=='CX':a,b=b,a;ua,ub=ub,ua
 if ua.name=='CX' and ub.name in ('MX','MEASURE'):
  x,y=M.cx_qs(a);return ub.qs[0]==(y if ub.name=='MX' else x)
 return False


def joint_cpsat(c,index,count=4):
 """Exact local rescheduling model: commuting exchanges, <=8 moves, +/-2 ticks."""
 from ortools.sat.python import cp_model
 ops=c['ops'];prep=ops[index];t=prep['t'];q=M.unit(prep).qs[0]
 if t<2:return []
 # All nearby CX/measurement units are potential helpers; fixed boundaries remain exact.
 active={q}|set(M.ADJ[q]);movable={i for i,o in enumerate(ops)if t-4<=o['t']<=t and set(M.unit(o).qs)&active and M.unit(o).name in ('CX','MX','MEASURE')}
 model=cp_model.CpModel();v={};changed=[];dist=[]
 for i,o in enumerate(ops):
  if i==index:v[i]=model.new_constant(t-1)
  elif i in movable:
   v[i]=model.new_int_var(max(0,o['t']-2),min(M.depth(c)-1,o['t']+2),f't{i}')
   ch=model.new_bool_var(f'ch{i}');model.add(v[i]!=o['t']).only_enforce_if(ch);model.add(v[i]==o['t']).only_enforce_if(ch.Not());changed.append(ch)
   d=model.new_int_var(0,2,f'd{i}');model.add_abs_equality(d,v[i]-o['t']);dist.append(d)
  else:v[i]=model.new_constant(o['t'])
 # Pairwise native occupancy and all noncommuting per-qubit precedences.
 for qq in range(36):
  seq=sorted([i for i,o in enumerate(ops)if qq in M.unit(o).qs],key=lambda i:ops[i]['t'])
  if not any(i in movable or i==index for i in seq):continue
  model.add_all_different([v[i]for i in seq]+([model.new_constant(t)]if qq==q else []))
  for ii,i in enumerate(seq):
   for j in seq[ii+1:]:
    if not commute(ops[i],ops[j]):model.add(v[i]<v[j])
 model.add(sum(changed)<=8);model.minimize(sum(changed)*100+sum(dist))
 solver=cp_model.CpSolver();solver.parameters.num_search_workers=1
 out=[]
 for _ in range(count):
  status=solver.solve(model)
  if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):break
  moves=[dict(t=ops[i]['t'],nt=solver.value(v[i]),lines=ops[i]['lines'])for i in sorted(movable)if solver.value(v[i])!=ops[i]['t']]
  out.append(moves)
  # Enumerate distinct complete local schedules; no lossy single-fault scoring.
  model.add_forbidden_assignments([v[i]for i in sorted(movable)],[[solver.value(v[i])for i in sorted(movable)]])
 return out

# A prepended global tick must be applied after every move expressed in base ticks.
# This keeps its combinations with later heralds and CX/M retimings well-defined.
def canon(bundle):
 return sorted(bundle,key=lambda e:(100 if e.get('prepend') else M.ORDER[e['fam']],e['id']))
M.canon=canon


MENU_WORKERS=1
_MENU_CACHE={}
_HERALD_PLAN=None

def _menu_job(index):
 return index,_menu(_HERALD_PLAN,{index})

def menu(c):
 global _HERALD_PLAN
 import hashlib
 from multiprocessing import get_context
 key=hashlib.sha256(json.dumps(dict(ops=c['ops'],tail=c['tail']),sort_keys=True).encode()).hexdigest()
 if key not in _MENU_CACHE:
  if MENU_WORKERS==1:result=_menu(c)
  else:
   _HERALD_PLAN=c
   ids=[i for i,o in enumerate(c['ops'])if M.unit(o).name in ('RESET','RX')]
   with get_context('fork').Pool(MENU_WORKERS)as pool:parts=sorted(pool.imap_unordered(_menu_job,ids))
   es={};audit=[]
   for _,(entries,coverage)in parts:es.update(entries);audit.extend(coverage)
   result=es,audit
  _MENU_CACHE[key]=result
 return copy.deepcopy(_MENU_CACHE[key])
