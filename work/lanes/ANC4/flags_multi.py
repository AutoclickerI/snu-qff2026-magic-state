import os,sys,json,re,itertools
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'upstream/snu-qff2026-problem'));sys.path.insert(0,str(HERE/'inputs/EVAL'))
from exact2 import Eval
QRE=re.compile(r'q\[(\d+)\]')
p=HERE/'grid_cp20.qasm';raw=p.read_text().splitlines();j=json.loads(p.with_suffix('.json').read_text());by={};t=0;head=[];dets=[]
for s in raw:
 if s.startswith('barrier'):t+=1
 elif s.startswith(('OPENQASM','include','qreg','creg')):head.append(s)
 elif s.startswith('// DETECTOR'):dets.append(s)
 elif s.strip():by.setdefault(t,[]).append(s)
B=j['layout']['b'];F=j['layout']['f'];vals={q:0 for q in B+F};iv=0;columns={};busy={}
for t in range(45):
 columns[t]=vals.copy();busy[t]=set()
 for s in by.get(t,[]):
  qs=list(map(int,QRE.findall(s)));busy[t]|=set(qs)
  if not qs or not set(qs)<=set(B+F):continue
  if s.startswith('reset'):vals[qs[0]]=0
  elif s.startswith('h'):vals[qs[0]]=1<<iv;iv+=1
  elif s.startswith('cx'):vals[qs[1]]^=vals[qs[0]]
columns[45]=vals.copy();busy[45]=set()
outdir=HERE/'flags_multi';outdir.mkdir(exist_ok=True);out=[]
b,f=13,12
opts=[t for t in range(20,40) if b not in busy[t] and columns[t].get(b)]
windows=[]
for num in [2,3]:
 for times in itertools.combinations(opts,num):
  v=columns[45][b]
  for t in times:v^=columns[t][b]
  if v==0:windows.append(times)
windows.sort(key=lambda t:(len(t),45-t[0],t))
seen=set()
for times in windows:
  # Evaluate one latest tuple per sequence of symbolic B values.
  key=tuple(columns[t][b] for t in times)
  if key in seen:continue
  seen.add(key);start=times[0];end=45
  groups={t:s.copy() for t,s in by.items()}
  # Keep A/F readouts at 45. Move all B-data CXs to 46, B MXs to 47.
  groups[47]=groups.pop(46);cxs=[s for s in groups[45] if s.startswith('cx')];groups[45]=[s for s in groups[45] if not s.startswith('cx')];groups[46]=cxs
  groups.setdefault(start-1,[]).append(f'reset q[{f}];');
  for t in times:groups[t].append(f'cx q[{b}],q[{f}];')
  groups[45].append(f'cx q[{b}],q[{f}];');groups[46].append(f'measure q[{f}] -> c[65];')
  lines=[s for s in head if not s.startswith('creg')]+['creg c[66];'];bar='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
  for t in range(48):lines+=groups.get(t,[])+[bar]
  lines=lines[:-1]+dets+['// DETECTOR c[65]'];txt='\n'.join(lines)+'\n';name='f12_t'+'_'.join(map(str,times));stem=outdir/name
  stem.with_suffix('.qasm').write_text(txt);meta=j.copy();meta.update(flag=[b,f,*times,45],cx=j['cx']+len(times)+1);stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
  try:
   ev=Eval(txt,j['data_qubits']);c1=float((ev.fp*ev.n_single).sum());a1=float((ev.fp*(1-ev.a_single)).sum());out.append(dict(name=name,c1=c1,A1=a1));print(out[-1],flush=True)
  except Exception as e:print(name,str(e),flush=True)
(HERE/'flags_multi_singles.json').write_text(json.dumps(out,indent=2)+'\n')
