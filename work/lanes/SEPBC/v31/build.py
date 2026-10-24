"""Compose v30g mechanisms on the native v31s ordering without undoing R45."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));from common import *
V=H/'v31'
def fix(c):
 c['ops'].sort(key=lambda o:(o['t'],o.get('id',0)))
 for i,o in enumerate(c['ops']):o['id']=i
 n=max(int(b)for o in c['ops']for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines'])))+1
 c['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{n}]',l)for l in c['h']];return c

def bit(c):return 1+max(int(b)for o in c['ops']for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines'])))
def parity(c,target,control):
 for j,line in enumerate(c['tail']):
  if line.startswith('// DETECTOR'):
   bs=set(map(int,re.findall(r'c\[(\d+)\]',line)))
   if target in bs:bs^={control}
   c['tail'][j]='// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs))
def repair(c):
 # Native order is explicit, and old timing is the target; R and readout
 # offsets are fixed, including moved readouts in the structural edit.
 ops=c['ops'];us=[unit(o)for o in ops];old=[o['t']for o in ops];R=c['meta']['R'];mx=max(old);m=cp_model.CpModel();tv=[m.NewIntVar(0,mx,f't{i}')for i in range(len(ops))];last={}
 for i,u in enumerate(us):
  for q in u.qs:
   if q in last:m.Add(tv[i]>tv[last[q]])
   last[q]=i
  if old[i]>=R:m.Add(tv[i]==old[i])
  else:m.Add(tv[i]<R)
 dev=[]
 for i,t in enumerate(old):
  z=m.NewIntVar(0,mx,f'd{i}');m.AddAbsEquality(z,tv[i]-t);dev.append(z)
 m.Minimize(sum(dev));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=5;st=s.Solve(m)
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):raise ValueError('native order cannot fit fixed R')
 for i,o in enumerate(ops):o['t']=s.Value(tv[i])
 return fix(c)
def edit(c,name):
 c=copy.deepcopy(c);ops=c['ops'];R=c['meta']['R'];b=bit(c)
 def add(lines,t,tag='round'):ops.append(dict(lines=lines,t=t,id=10000+len(ops),tag=tag))
 if name=='copy4':
  o=max((o for o in ops if o['lines']==['cx q[19],q[25];']),key=lambda o:o['t']);t=o['t'];assert t==R+1;ops.remove(o);parity(c,22,23)
  for k,(q,h,rec)in enumerate([(19,18,23),(25,31,22),(29,35,26),(28,34,27)]):
   assert not any(h in unit(o).qs for o in ops)
   o=next(o for o in ops if o['lines']==[f'measure q[{q}] -> c[{rec}];']);o['t']=R+2
   add([f'reset q[{h}];'],R);add([f'cx q[{q}],q[{h}];'],R+1);add([f'measure q[{h}] -> c[{b+k}];'],R+2);c['tail'].append(f'// DETECTOR c[{rec}] c[{b+k}]')
 elif name=='edge14':
  for q,rec in [(14,15),(15,20)]:next(o for o in ops if o['lines']==[f'measure q[{q}] -> c[{rec}];'])['t']=R+2
  add(['cx q[14],q[15];'],R+1);parity(c,20,15)
 elif name.startswith('mz'):
  q=int(name[2:]);o=next(o for o in ops if o['lines']==[f'reset q[{q}];']);o['lines']=[f'measure q[{q}] -> c[{b}];'];c['tail'].append(f'// DETECTOR c[{b}]')
 elif name=='instrument':
  mi=next(i for i,o in enumerate(ops)if 'measure q[9] -> c[9];'in o['lines']);ci=max(i for i in range(mi)if ops[i]['lines']==['cx q[9],q[15];']);t=ops[ci]['t'];drop={ci,mi}
  # R45 commuted other cat fanout past 9->15. Complete that fanout before
  # replacing the terminal cat/data instrument, preserving its Kraus contract.
  fanout=[o for o in ops[ci+1:mi]if unit(o).name=='CX'and int(S.QRE.findall(o['lines'][0])[0])==9]
  for o in fanout:
   j=ops.index(o);u,v=map(int,S.QRE.findall(o['lines'][0]))
   for x in ops[ci:j]:
    w=unit(x)
    if set(w.qs)&{u,v}:
     assert w.name=='CX',('noncommuting fanout crossing',o,x)
     a,b=map(int,S.QRE.findall(x['lines'][0]));assert u!=b and a!=v,(o,x)
   ops.pop(j);ops.insert(ci,o);ci+=1
  mi=next(i for i,o in enumerate(ops)if 'measure q[9] -> c[9];'in o['lines']);ci=max(i for i in range(mi)if ops[i]['lines']==['cx q[9],q[15];']);drop={ci,mi};b=bit(c)
  for line in ['tdg q[15];','measure q[16] -> c[43];','cx q[15],q[16];','cx q[16],q[15];','measure q[15] -> c[53];']:drop.add(next(i for i,o in enumerate(ops)if line in o['lines']))
  new=[dict(lines=['measure q[16] -> c[43];'],t=t-1,tag='prefix')]
  for j,(u,v)in enumerate([(9,15),(15,16),(16,15),(15,16)]):new.append(dict(lines=[f'cx q[{u}],q[{v}];'],t=t+j,tag='prefix'))
  for lines in [['h q[9];','measure q[9] -> c[9];'],[f'measure q[15] -> c[{b}];'],['tdg q[16];']]:new.append(dict(lines=lines,t=t+4,tag='prefix'))
  c['ops']=[o for i,o in enumerate(ops[:ci])if i not in drop]+new+[o for i,o in enumerate(ops[ci:],ci)if i not in drop];c['tail']=[l for l in c['tail']if l!='// DETECTOR c[53]']+[f'// DETECTOR c[{b}]'];c=repair(c)
 else:raise ValueError(name)
 c['meta']['ported_edits']=c['meta'].get('ported_edits',[])+[name];return fix(c)

def build(ks,name):
 c=json.loads((H/'v30/sensitivity_tail.plan.json').read_text());assert c['meta']['R']==45
 for k in ks:c=edit(c,k)
 st=save(c,'v31/'+name);r=score(st);r['edits']=ks;st.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));append_result(name,r,'v30g structural and measured-initialization mechanisms composed on v31s, R45 retained.');return r
if __name__=='__main__':
 cases=[('mz5_12',['mz5','mz12']),('mz11_5_12',['mz11','mz5','mz12']),('copy4',['copy4']),('edge14',['edge14']),('instrument',['instrument']),('readout_mz',['copy4','edge14','mz11','mz5','mz12']),('full_port',['instrument','copy4','edge14','mz11','mz5','mz12'])]
 for name,ks in cases:
  try:r=build(ks,name);print(name,json.dumps(r),flush=True)
  except Exception as e:append_result(name,dict(error=repr(e)),'Structural port failed; not a physical performance closure.');print(name,repr(e),flush=True)
