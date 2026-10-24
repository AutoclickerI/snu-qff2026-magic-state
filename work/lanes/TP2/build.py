"""Build judge QASM from a fullroute witness and three exact seven-cell encoders.
Preserves every native v16 prefix operation/record through step 32.
"""
import os,sys,json,re,argparse,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'DR'))
from steane_full import GENS
from packing import D,nb
QRE=re.compile(r'q\[(\d+)\]')

def prefix():
 raw=(HERE.parents[1]/'candidates/v16_bc2m.qasm').read_text().splitlines()
 by={};t=0;bits=set();det=[]
 for s in raw:
  if s.startswith('barrier'):t+=1;continue
  if s.startswith('// DETECTOR'):
   rec={int(x) for x in re.findall(r'c\[(\d+)\]',s)}
   if rec<=bits:det.append(s)
  if t>32 or s.startswith(('OPENQASM','include','qreg','creg','//')) or not s.strip():continue
  by.setdefault(t,[]).append(s)
  if s.startswith('measure'):bits.update(map(int,re.findall(r'c\[(\d+)\]',s)))
 return by,det,max(bits)+1

def build(route,preps):
 by,dets,n=prefix();prefix_hash=hashlib.sha256(json.dumps(by,sort_keys=True).encode()).hexdigest()
 def op(t,s):by.setdefault(t,[]).append(s)
 tokens=route['tokens'];rt=[];bits={}
 if 'bc' in preps:
  for i,q in enumerate(route['c']):
   tokens[f'c{i}']=dict(pos=[q],mv=[],ts=[],en=[],tc=30)
   tokens[f'b{i}']['atC']=route['b'][i]
 def ro(t,s):rt.append((t,s))
 for key,v in tokens.items():
  for j,yes in enumerate(v['mv']):
   if not yes:continue
   u,w=v['pos'][j:j+2];t=v['ts'][j]
   ro(t-1,f'reset q[{w}];')
   ro(t,f'cx q[{u}],q[{w}];');ro(t+1,f'cx q[{w}],q[{u}];')
 for i in range(7):
  o,b,c=(tokens[f'{k}{i}'] for k in 'obc')
  assert b['tc']>=o['en'][-1]
  ro(o['tc'],f'cx q[{o["atD"]}],q[{D[i]}];')
  bits['d',i]=n;ro(o['tc']+1,f'measure q[{D[i]}] -> c[{n}];');n+=1
  ro(c['tc'],f'cx q[{b["atC"]}],q[{c["pos"][-1]}];')
  bits['c',i]=n;ro(c['tc']+1,f'measure q[{c["pos"][-1]}] -> c[{n}];');n+=1
  ro(b['tc'],f'cx q[{b["pos"][-1]}],q[{o["atB"]}];')
  bits['b',i]=n;ro(b['tc']+1,f'h q[{b["pos"][-1]}];');ro(b['tc']+1,f'measure q[{b["pos"][-1]}] -> c[{n}];');n+=1
 deadlines={}
 for t,s in rt:
  for q in map(int,QRE.findall(s)):deadlines[q]=min(deadlines.get(q,999),t)
 prep_schedule=[]
 for k in preps:
  p=preps[k];cells=(route['b']+route['c']) if k=='bc' else route[k]
  assert set(p['pivots'])<=set(cells)
  jobs=[([f'reset q[{q}];']+([f'h q[{q}];'] if q in p['pivots'] else []),[q]) for q in cells]
  jobs += [([f'cx q[{u}],q[{v}];'],[u,v]) for lay in p['ops'] for u,v in lay]
  latest={q:deadlines[q] for q in cells};sched=[]
  for ss,qs in reversed(jobs):
   t=min(latest[q] for q in qs)-1
   assert t>=0,(k,t)
   for q in qs:latest[q]=t
   sched.append((t,ss,qs))
  for t,ss,qs in reversed(sched):
   for s in ss:op(t,s)
   prep_schedule.append(dict(block=k,step=t,stmts=ss))
 for t,s in rt:op(t,s)
 end=max(by);bar='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
 out=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{n}];']
 for t in range(end+1):
  if not by.get(t):
   v=tokens['o0'];q=v['pos'][0]
   for j,e in enumerate(v['en']):
    if e<=t:q=v['pos'][j+1]
   by[t]=[f'id q[{q}];']
  out.append(f'// step {t}')
  out+=by[t]
  if t<end:out.append(bar)
 for k in 'dbc':
  for S in GENS:dets.append('// DETECTOR '+' '.join(f'c[{bits[k,i]}]' for i in S))
 dets.append('// DETECTOR '+' '.join(f'c[{bits["c",i]}]' for i in range(7)))
 out+=dets
 out.append('// FRAME_X(0) '+' '.join(f'c[{bits["d",i]}]' for i in range(7)))
 out.append('// FRAME_Z(0)')
 text='\n'.join(out)+'\n'
 meta=dict(data_qubits=[tokens[f'o{i}']['pos'][-1] for i in range(7)],R=route['R'],Rmax=route['Rmax'],last_step=end,O=route['o'],B=route['b'],C=route['c'],moves=route['moves'],cx=text.count('cx '),prefix_sha256=prefix_hash,prep_schedule=prep_schedule)
 # Validate local schedule independently, including native RX/MX one-step groups.
 busy={}
 for t,ss in by.items():
  for s in ss:
   if s.startswith('h '):continue
   qs=list(map(int,QRE.findall(s)))
   if s.startswith('cx'):assert qs[1] in nb(qs[0]),s
   for q in qs:assert (t,q) not in busy,(t,q,s,busy.get((t,q)));busy[t,q]=s
 return text,meta
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('route');p.add_argument('out');p.add_argument('--o',required=True);p.add_argument('--b');p.add_argument('--c');p.add_argument('--bc');a=p.parse_args()
 r=json.loads(Path(a.route).read_text());preps={k:json.loads(Path(getattr(a,k)).read_text()) for k in (('o','bc') if a.bc else ('o','b','c'))}
 text,meta=build(r,preps);meta['source']=vars(a)
 Path(a.out+'.json').write_text(json.dumps(meta,indent=2)+'\n');Path(a.out+'.qasm').write_text(text)
 print(json.dumps({k:v for k,v in meta.items() if k!='prep_schedule'}),flush=True)
