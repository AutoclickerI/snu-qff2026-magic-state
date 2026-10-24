import sys,json,re
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
for mode in ['echo','flag35','echo35']:
 p=HERE/'grid_flag_m.qasm';ls=p.read_text().splitlines();j=json.loads(p.with_suffix('.json').read_text());head=[];by={};dets=[];t=0
 for s in ls:
  if s.startswith('barrier'):t+=1
  elif s.startswith(('OPENQASM','include','qreg','creg')):head.append(s)
  elif s.startswith('// DETECTOR'):dets.append(s)
  elif s.strip():by.setdefault(t,[]).append(s)
 if mode.startswith('echo'):
  for b,f,start in [(28,34,42)]:
   meas=next(s for s in by[45] if s.startswith(f'measure q[{f}]'))
   by[45].remove(meas);by[47].append(meas)
   cx=next(s for s in by[46] if s.startswith(f'cx q[{b}],'))
   by[46].remove(cx);by[45].append(cx)
   by[start].append(f'cx q[{b}],q[{f}];');by[46].append(f'cx q[{b}],q[{f}];')
 if mode.endswith('35'):
  n=int(re.search(r'creg c\[(\d+)\]',p.read_text())[1]);head=[f'creg c[{n+1}];' if s.startswith('creg') else s for s in head]
  by[28].append('reset q[35];');by[29].append('cx q[29],q[35];');by[45].append('cx q[29],q[35];');by[46].append(f'measure q[35] -> c[{n}];');dets.append(f'// DETECTOR c[{n}]')
 out=head;bar='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
 for t in range(48):
  busy=set()
  for s in by[t]:
   if s.startswith('h'):continue
   qs=set(map(int,re.findall(r'q\[(\d+)\]',s)));assert not(qs&busy),(mode,t,s,qs&busy);busy|=qs
  out+=by[t]+[bar]
 txt='\n'.join(out[:-1]+dets)+'\n';j.update(cx=txt.count('\ncx '),late_checks=mode)
 p=HERE/('grid_'+mode);p.with_suffix('.qasm').write_text(txt);p.with_suffix('.json').write_text(json.dumps(j,indent=2)+'\n');print(p.name,j['cx'])
