"""Native schedule edits for acceptance-efficient v35a storage protection."""
import os,sys,json,re,copy,hashlib,itertools
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;V=H/'v35';ROOT=H.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(V/'.xtim_cache')
sys.path[:0]=[str(V/'sparse'),str(ROOT/'work/lanes/EVAL')]
import frontend as fa,exact2,xtim
xtim.cache_dir=str(V/'.xtim_cache')
DATA=json.loads((V/'base.json').read_text())['data_qubits']
TEXT=(V/'base.qasm').read_text();BASE_SHA=hashlib.sha256(TEXT.encode()).hexdigest()
L0=4.393527676042078e-5;A0=.5012369386242203
ops,dets=fa.parse_current(TEXT)
BASE=dict(ops=[dict(kind=o.kind,qs=list(o.qs),t=o.time,bit=o.bit) for o in ops],dets=[sorted(d)for d in dets])
GUARDS=[dict(q=0,h=6,axis='Z',init=34,first=35,last=39,end=40,bit=273),
dict(q=20,h=19,axis='X',init=13,first=18,last=31,end=32,bit=274),
dict(q=7,h=13,axis='X',init=19,first=20,last=23,end=24,bit=275),
dict(q=10,h=11,axis='X',init=18,first=19,last=28,end=29,bit=276),
dict(q=4,h=5,axis='X',init=17,first=18,last=32,end=33,bit=277)]
PATHS={0:[(0,16,46)],20:[(20,16,46)],7:[(7,16,46)],3:[(3,16,46)],
10:[(4,16,32),(10,35,46)],22:[(15,18,30),(16,34,34),(22,37,46)],
21:[(8,16,32),(9,35,35),(15,37,37),(21,39,46)]}
def clone(c=BASE):return copy.deepcopy(c)
def nb(c):return 1+max(o['bit'] for o in c['ops'] if o['bit'] is not None)
def add(c,kind,qs,t,bit=None):c['ops'].append(dict(kind=kind,qs=list(qs),t=t,bit=bit))
def find(c,**kw):
 found=[o for o in c['ops'] if all(o[k]==v for k,v in kw.items())]
 assert len(found)==1,(kw,found)
 return found[0]
def lines(o):
 k,q,b=o['kind'],o['qs'],o['bit'];a=q[0]
 if k=='CX':return [f'cx q[{a}],q[{q[1]}];']
 if k in ('R','RX'):return [f'reset q[{a}];']+([f'h q[{a}];']if k=='RX'else[])
 if k in ('M','MX'):return ([f'h q[{a}];']if k=='MX'else[])+[f'measure q[{a}] -> c[{b}];']+([f'h q[{a}];']if k=='MX'else[])
 return [f'{dict(TDG="tdg",T_DAG="tdg",I="id").get(k,k.lower())} q[{a}];']
def textof(c):
 out=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{max(278,nb(c))}];'];busy=set()
 for t in range(47):
  for o in c['ops']:
   if o['t']!=t:continue
   for q in o['qs']:
    assert (t,q)not in busy,('conflict',t,q)
    busy.add((t,q))
   if o['kind']=='CX':
    a,b=o['qs'];assert abs(a//6-b//6)+abs(a%6-b%6)==1
   out.extend(lines(o))
  if t<46:out.append('barrier '+','.join(f'q[{q}]'for q in range(36))+';')
 out.extend('// DETECTOR '+' '.join(f'c[{b}]'for b in row) for row in c['dets'])
 return '\n'.join(out)+'\n'
def signature(c):
 return dict(ops=sorted(c['ops'],key=lambda o:(o['t'],tuple(o['qs']),o['kind'],o['bit'] or -1)),dets=sorted(c['dets']))
def emit(name,c,desc):
 text=textof(c);p=V/name;p.parent.mkdir(parents=True,exist_ok=True);p.with_suffix('.qasm').write_text(text)
 qasm_sha=hashlib.sha256(text.encode()).hexdigest()
 md=dict(data_qubits=DATA,R=44,native_depth=47,cx=sum(o['kind']=='CX'for o in c['ops']),base_sha256=BASE_SHA,description=desc,signature_sha256=hashlib.sha256(json.dumps(signature(c),sort_keys=True).encode()).hexdigest(),qasm_sha256=qasm_sha)
 p.with_suffix('.json').write_text(json.dumps(md,indent=2)+'\n')
 return dict(stem=name,description=desc,sha256=qasm_sha)
def replace_guard_init(c,g,mode):
 o=find(c,t=g['init'],qs=[g['h']],kind='R')
 if mode=='late':o['t']=g['first']-1
 elif mode=='mz_parity':
  bit=nb(c);o.update(kind='M',bit=bit)
  c['dets']=[sorted(row+[bit]) if row==[g['bit']] else row for row in c['dets']]
 elif mode=='omit':c['ops'].remove(o)
 return c
def drop_guard(c,g):
 target=[o for o in c['ops'] if g['h']in o['qs'] and g['init']<=o['t']<=g['end'] and (len(o['qs'])==1 or g['q']in o['qs'])]
 assert len(target)==4
 c['ops']=[o for o in c['ops'] if o not in target];c['dets']=[r for r in c['dets']if r!=[g['bit']]]
 return c
def adjacent(q):return [h for h in range(36)if abs(h//6-q//6)+abs(h%6-q%6)==1]
def templates(c=BASE):
 out=[];windows=[]
 qops={q:sorted([o for o in c['ops']if q in o['qs']],key=lambda o:o['t'])for q in range(36)}
 for q in DATA+[4,15,16,8,9]:
  for a,b in zip(qops[q],qops[q][1:]):
   lo,hi=max(18,a['t']+1),min(43,b['t']-1)
   if hi<lo:continue
   rr=dict(q=q,idle=[lo,hi],helpers=[]);windows.append(rr)
   for h in adjacent(q):
    seq=[dict(kind='UNUSED',t=-1)]+qops[h]+[dict(kind='END',t=47)]
    for prev,nxt in zip(seq,seq[1:]):
     if prev['kind']not in ('UNUSED','M','MX'):continue
     flo,fhi=prev['t']+1,nxt['t']-1
     if max(lo,flo)>min(hi,fhi):continue
     rr['helpers'].append(dict(h=h,free=[flo,fhi],previous=prev['kind'],next=nxt['kind']))
     for axis in ('Z','X'):
      restore=axis=='Z' and nxt['kind']=='M'
      start=max(lo,flo+1);end=min(hi,fhi-1-int(restore))
      if end<=start:continue
      logical=next((d for d,path in PATHS.items()for cell,t0,t1 in path if cell==q and t0<=start<=end<=t1),None)
      out.append(dict(q=q,h=h,axis=axis,init=start-1,first=start,last=end,end=end+1,restore=end+2 if restore else None,logical=logical,gap=[lo,hi],free=[flo,fhi]))
 return out,windows
def gadget(c,g):
 bit=nb(c);z=g['axis']=='Z';edge=[g['h'],g['q']]if z else[g['q'],g['h']]
 add(c,'RX'if z else'R',[g['h']],g['init']);add(c,'CX',edge,g['first']);add(c,'CX',edge,g['last']);add(c,'MX'if z else'M',[g['h']],g['end'],bit);c['dets'].append([bit])
 if g.get('restore')is not None:add(c,'R',[g['h']],g['restore'])
 return c
def build_initial():
 jobs=[]
 def put(name,c,**desc):jobs.append(emit(name,c,desc))
 put('canonical_base',clone(),family='baseline')
 for q,t,new in [(19,13,17),(13,25,33)]:
  c=clone();find(c,t=t,qs=[q],kind='R')['t']=new
  put(f'late_reset_q{q}',c,family='reset_timing',q=q,old=t,new=new)
 c=clone();find(c,t=13,qs=[19],kind='R')['t']=17;find(c,t=25,qs=[13],kind='R')['t']=33
 put('late_resets_joint',c,family='reset_timing_joint')
 for g in GUARDS[1:]:
  for mode in ['mz_parity']+(['omit']if g['h']in(19,11,5)else[]):
   c=replace_guard_init(clone(),g,mode);put(f'guard{g["bit"]}_{mode}',c,family='guard_initialization',guard=g,mode=mode)
 for g in GUARDS:
  width=g['last']-g['first']
  choices={(g['first'],g['last']-1),(g['first']+1,g['last']), (g['first'],g['first']+max(1,width//2)),(g['last']-max(1,width//2),g['last'])}
  for first,last in sorted(choices):
   if first>=last:continue
   c=clone();edge=[g['h'],g['q']]if g['axis']=='Z'else[g['q'],g['h']]
   find(c,t=g['first'],qs=edge,kind='CX')['t']=first;find(c,t=g['last'],qs=edge,kind='CX')['t']=last
   ini=find(c,t=g['init'],qs=[g['h']],kind='RX'if g['axis']=='Z'else'R');ini['t']=first-1
   find(c,t=g['end'],qs=[g['h']],kind='MX'if g['axis']=='Z'else'M')['t']=last+1
   put(f'guard{g["bit"]}_w{first}_{last}',c,family='guard_partial',guard=g,first=first,last=last)
 ts,ws=templates();(V/'windows.json').write_text(json.dumps(dict(data_paths=PATHS,windows=ws,gadgets=ts),indent=2))
 # ST2 already prices these exact native gadgets. Import its receipts later.
 covered={(20,26,'Z',20,30),(10,16,'X',21,22),(15,21,'X',20,29)}
 for i,g in enumerate(ts):
  if (g['q'],g['h'],g['axis'],g['first'],g['last'])in covered:continue
  c=gadget(clone(),g)
  put(f'new_{i:02}_{g["axis"]}_q{g["q"]}_h{g["h"]}',c,family='new_window',gadget=g)
 (V/'initial_jobs.json').write_text(json.dumps(jobs,indent=2));print(json.dumps(dict(jobs=len(jobs),templates=len(ts),windows=len(ws))))
if __name__=='__main__':build_initial()
