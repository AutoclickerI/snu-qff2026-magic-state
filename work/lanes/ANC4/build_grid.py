import os,sys,re,json
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work'));sys.path.insert(0,str(ROOT/'work/lanes/DR'));sys.path.insert(0,str(ROOT/'work/lanes/BC2'))
from steane_full import GENS
import tprep.qasm as tq,tprep.noise as tn
QRE=re.compile(r'q\[(\d+)\]')
P0={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}

def prefix(tag):
 src=(ROOT/'work/lanes/MAIN/spec/v17a.qasm').read_text().splitlines();end=next(i for i,l in enumerate(src) if l=='measure q[6] -> c[13];')+1;raw=src[:end]
 k,tr,tc=map(int,re.match(r's(\d+)_r(\d+)_c(\d+)',tag).groups())
 def tf(q):
  r,c=divmod(q,6);return [(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
 mr=min(tf(q)[0] for q in P0);mc=min(tf(q)[1] for q in P0)
 def mp(q):r,c=tf(q);return 6*(r-mr+tr)+c-mc+tc
 mapped=[]
 for l in raw:
  if l.startswith('barrier'):l='barrier '+','.join(f'q[{mp(q)}]' for q in map(int,QRE.findall(l)) if q in P0)+';'
  elif not l.startswith('qreg'):l=QRE.sub(lambda m:f'q[{mp(int(m.group(1)))}]',l)
  mapped.append(l)
 p=HERE/'prefix.qasm';p.write_text('\n'.join(mapped)+'\n');p.with_suffix('.json').write_text(json.dumps(dict(data_qubits=list(map(mp,[0,20,7,4,3,15,8])),prefix_only=True)))
 import merge
 merge.PREFIX=str(p);merge.CUT=len(mapped);head,stmts=merge.prefix_steps()
 prebits={int(v) for l in raw for v in re.findall(r'-> c\[(\d+)\]',l)}
 det=[l for l in src if l.startswith('// DETECTOR') and set(map(int,re.findall(r'c\[(\d+)\]',l)))<=prebits]
 return head,stmts,det

def build(stem,bfile='grid_B_d12.json',checkfile='grid_checker.json'):
 lay=json.loads((HERE/'grid_layout.json').read_text());a,b,f,d=(lay[k] for k in ['a','b','f','d'])
 A=json.loads((HERE/'grid_A.json').read_text());B=json.loads((HERE/bfile).read_text());C=json.loads((HERE/checkfile).read_text())
 head,pre,det=prefix(lay['pre_transform']);by={};rel={}
 for s,t in pre:
  by.setdefault(t,[]).append(s)
  for q in map(int,QRE.findall(s)):rel[q]=max(rel.get(q,0),t+1)
 units=[]
 def add(ss,qs):units.append((ss,qs))
 for p in lay['moves']:
  for u,v in zip(p,p[1:]):add([f'reset q[{v}];'],[v]);add([f'cx q[{u}],q[{v}];'],[u,v]);add([f'cx q[{v}],q[{u}];'],[u,v])
 for prep,cells in [(A,a),(B,b+f)]:
  for q in cells:add([f'reset q[{q}];']+([f'h q[{q}];'] if q in prep['pivots'] else []),[q])
  for l in prep['ops']:
   for u,v in l:add([f'cx q[{u}],q[{v}];'],[u,v])
 for q in f:add([f'reset q[{q}];'],[q])
 checkerfirst=len(units)
 for l in C['ops']:
  for u,v in l:add([f'cx q[{u}],q[{v}];'],[u,v])
 def sched(R):
  latest={q:R for q in a+d};latest.update({q:R+1 for q in b+f});when=[None]*len(units)
  for i in reversed(range(len(units))):
   ss,qs=units[i];t=min(latest.get(q,R) for q in qs)-1;when[i]=t
   for q in qs:latest[q]=t
  return when,all(t>=max(rel.get(q,0) for q in qs) for t,(ss,qs) in zip(when,units))
 R=33
 while not sched(R)[1]:R+=1
 when,_=sched(R)
 for t,(ss,qs) in zip(when,units):by.setdefault(t,[]).extend(ss)
 by.setdefault(R,[]).extend(f'cx q[{d[i]}],q[{a[i]}];' for i in range(7));n=47;bits={}
 for key,qs in [('a',a),('f',f)]:
  for i,q in enumerate(qs):bits[key,i]=n;by.setdefault(R+1,[]).append(f'measure q[{q}] -> c[{n}];');n+=1
 by.setdefault(R+1,[]).extend(f'cx q[{b[i]}],q[{d[i]}];' for i in range(7))
 for i,q in enumerate(b):bits['b',i]=n;by.setdefault(R+2,[]).extend([f'h q[{q}];',f'measure q[{q}] -> c[{n}];']);n+=1
 for key in ['a','b']:
  for g in GENS:det.append('// DETECTOR '+' '.join(f'c[{bits[key,i]}]' for i in g))
 for i in range(4):det.append(f'// DETECTOR c[{bits["f",i]}]')
 out=head+[f'creg c[{n}];'];bar='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
 for t in range(R+3):out+=by.get(t,[])+[bar]
 out=out[:-1]+det;text='\n'.join(out)+'\n'
 # Native resource collisions and all physical edges are checked before emission.
 for t,ss in by.items():
  busy=set()
  for s in ss:
   if s.startswith('h'):continue
   qs=set(map(int,QRE.findall(s)));assert not (qs&busy),(t,s,qs&busy);busy|=qs
 stem=HERE/stem;stem.with_suffix('.qasm').write_text(text);meta=dict(data_qubits=d,R=R,cx=text.count('\ncx '),A=A,B=B,checker=C,layout=lay,prefix_source='v17a through prefix c[13], native schedule re-extracted',checker_first=min(when[checkerfirst:]),checker_last=max(when[checkerfirst:]),pre_last=max(t for s,t in pre))
 stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n');print(stem.name,'R',R,'CX',meta['cx'],flush=True)
 return stem
if __name__=='__main__':build(sys.argv[1] if len(sys.argv)>1 else 'grid_routed',checkfile=sys.argv[2] if len(sys.argv)>2 else 'grid_checker.json')
