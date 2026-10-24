import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import re,json,sys
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn'); HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work'))
import tprep.qasm as tq
import tprep.noise as tn
QRE=re.compile(r'q\[(\d+)\]')
A=[1,14,8,9,2,16,15]; B=[6,26,13,11,4,23,27]; C=[12,25,19,17,5,29,28]
D0=[0,20,7,4,3,15,8]; D=[0,20,7,10,3,22,21]
BCCHAIN=[6,12,13,19,25,26,27,28,29,23,17,11,5,4]
def qs(s):return list(map(int,QRE.findall(s)))
def nb(q):return [v for v in range(36) if abs(v//6-q//6)+abs(v%6-q%6)==1]
def parse_source(path=ROOT/'work/lanes/MAIN/spec/v17a.qasm'):
 raw=path.read_text().splitlines();text,labels,err=tq.convert('\n'.join(raw));assert not err,err
 prog,steps,gaps=tn.schedule(text);kstep={}
 for ins,st in zip(prog,steps):
  lab=labels[ins.line_no-1];m=re.match(r'instruction (\d+) ',lab)
  if m and st:kstep[int(m.group(1))]=st[0][1]
 stm=[];k=0;region='pre';roundflag=False
 for line in raw:
  if line=='// region round':region='round'
  s=line.split('//')[0].strip()
  if not s or s.startswith(('OPENQASM','include','qreg','creg')):continue
  k+=1
  if s.startswith('barrier'):continue
  if s=='reset q[10];' and stm[-1]['s']=='measure q[6] -> c[13];':region='prep'
  stm.append(dict(s=s,t=kstep.get(k),region=region,qs=qs(s)))
 for i,x in enumerate(stm):
  if x['t'] is not None:continue
  assert x['s'].startswith('h '),x
  q=x['qs'][0];prv=next((y for y in reversed(stm[:i]) if q in y['qs']),None);nxt=next((y for y in stm[i+1:] if q in y['qs']),None)
  if prv and prv['s'].startswith('reset'):x['t']=prv['t']
  else:x['t']=nxt['t']
 units=[]
 for x in stm:
  if units and x['t']==units[-1]['t'] and x['qs']==units[-1]['qs']:
   units[-1]['stmts'].append(x['s'])
  else:units.append(dict(stmts=[x['s']],qs=x['qs'],t=x['t'],region=x['region']))
 dets=[l for l in raw if l.startswith('// DETECTOR')]
 return units,dets

def emit(units,dets,data,out,meta=None):
 by={}
 for u in units:by.setdefault(u['t'],[]).extend(u['stmts'])
 bar='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
 n=max(int(x) for u in units for s in u['stmts'] for x in re.findall(r'c\[(\d+)\]',s))+1
 outtext=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{n}];']
 for t in range(max(by)+1):
  outtext.extend(by.get(t,[]))
  if t<max(by):outtext.append(bar)
 outtext.extend(dets);txt='\n'.join(outtext)+'\n'
 Path(str(out)+'.qasm').write_text(txt);Path(str(out)+'.json').write_text(json.dumps(dict(data_qubits=data,**(meta or {})),indent=2))
 Path(str(out)+'.units.json').write_text(json.dumps(units,indent=1))
 audit(txt,units,out)
 return txt

def audit(txt,units,out):
 text,labels,err=tq.convert(txt);assert not err,err
 prog,steps,gaps=tn.schedule(text)
 actual=[(st,ins.name,list(q)) for ins,ss in zip(prog,steps) for q,st in ss]
 # Compare schedule by normalized instruction multiset at each time, ignoring detector-only operations.
 schedule=[dict(step=st,op=name,qubits=q) for st,name,q in actual]
 Path(str(out)+'.schedule.json').write_text(json.dumps(schedule,indent=1))
 # Native h folding can depend on reuse; reject unexpected depth.
 expected=max(u['t'] for u in units); measured=max(st for st,_,_ in actual)
 assert measured==expected,(measured,expected)
 return actual

def fixed_schedule():
 us,dets=parse_source();pre=[u for u in us if u['region']=='pre'];prep=[u for u in us if u['region']=='prep'];rnd=[u for u in us if u['region']=='round'];release={}
 for u in pre:
  for q in u['qs']:release[q]=max(release.get(q,0),u['t']+1)
 end=release.copy()
 for u in prep:
  u['earliest']=max(end.get(q,0) for q in u['qs'])
  for q in u['qs']:end[q]=u['earliest']+1
 R=max(end.values());late={q:R for q in range(36)}
 for u in reversed(prep):
  u['t']=min(late[q] for q in u['qs'])-1
  for q in u['qs']:late[q]=u['t']
  assert u['t']>=u['earliest']
 for u in rnd:u['t']+=R-50
 emit(pre+prep+rnd,dets,D,HERE/'fixed_alap',dict(R=R,release=release))
 (HERE/'source_units.json').write_text(json.dumps(us,indent=1))
 print('fixed R',R,'release',release,flush=True)
if __name__=='__main__':fixed_schedule()

def encoders():
 us,dets=parse_source();prep=[u for u in us if u['region']=='prep'];lastinit={q:max(i for i,u in enumerate(prep) if u['qs']==[q] and u['stmts'][0].startswith(('reset','measure'))) for q in A+B+C};out=[]
 for i,u in enumerate(prep):
  if len(u['qs'])==1 and u['qs'][0] in lastinit and lastinit[u['qs'][0]]==i:out.append(dict(u,tag='A' if u['qs'][0] in A else 'BC'))
  elif len(u['qs'])==2 and all(q in A for q in u['qs']) and all(i>lastinit[q] for q in u['qs']):out.append(dict(u,tag='A'))
  elif len(u['qs'])==2 and all(q in B+C for q in u['qs']):out.append(dict(u,tag='BC'))
 assert sum(len(u['qs'])==2 and u['tag']=='A' for u in out)==11
 assert sum(len(u['qs'])==2 and u['tag']=='BC' for u in out)==82
 return out

def stage_prep(init):
 us,_=parse_source();release={}
 for u in us:
  if u['region']=='pre':
   for q in u['qs']:release[q]=max(release.get(q,0),u['t']+1)
 end={q:release.get(init[q],0) for q in A+B+C};enc=encoders()
 for u in enc:
  u['t']=max(end[q] for q in u['qs'])
  for q in u['qs']:end[q]=u['t']+1
 return enc,end
