"""Merge the v16 prefix, ALAP staged A/BC encoders, and a route.py witness."""
import os,sys,json,re,argparse
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE));from route import transform,P0
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
QR=re.compile(r'q\[(\d+)\]');CR=re.compile(r'c\[(\d+)\]')
def make(lay,A,BC):
 physical=lay['args'].get('physical',False)
 assert physical or (lay['args']['reset_a'] and not lay['args']['fast_b'])
 raw=(ROOT/'work/candidates/v16_bc2m.qasm').read_text().splitlines();by={};t=0;measured=set();dets=[]
 k,tr,tc=map(int,lay['args']['transform'].split(','))
 # Extend transform from the footprint to exactly its prefix qubits.
 def tf(q):
  r,c=divmod(q,6);return [(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
 r0=min(tf(q)[0] for q in P0);c0=min(tf(q)[1] for q in P0)
 def mp(q):r,c=tf(q);return (r-r0+tr)*6+c-c0+tc
 for line in raw:
  if line.startswith('// DETECTOR'):
   ds=set(map(int,CR.findall(line)))
   if ds<=measured:dets.append(ds)
  if t>=33:continue
  if line.startswith('barrier'):t+=1;continue
  if not line or line.startswith(('OPENQASM','qreg','creg','include','//')):continue
  assert set(map(int,QR.findall(line)))<=P0,line
  by.setdefault(t,[]).append(QR.sub(lambda m:f'q[{mp(int(m.group(1)))}]',line))
  if line.startswith('measure'):measured.update(map(int,CR.findall(line)))
 n=max(measured)+1
 bits={}
 def emit(t,lines):by.setdefault(t,[]).extend(lines)
 # Per-cell reverse critical-path scheduling, ALAP to hard native deadlines.
 def prep(p,cells,deadline):
  jobs=[];init=set(cells)|{q for L in p['ops'] for e in L for q in e}
  for q in sorted(init):jobs.append(([q],[f'reset q[{q}];']+([f'h q[{q}];'] if q in p['pivots'] else [])))
  for L in p['ops']:
   for u,v in L:jobs.append(([u,v],[f'cx q[{u}],q[{v}];']))
  free={q:(deadline[q] if isinstance(deadline,dict) else deadline) for q in init}
  for qs,ls in reversed(jobs):
   st=min(free[q] for q in qs)-1;assert st>=0,(st,qs)
   emit(st,ls)
   for q in qs:free[q]=st
 # Prepare and verify each BC pair as late as its first move/coupling and
 # the C cell's reuse permit. Pair checks commute with later prep gates
 # on disjoint cells, so preserving per-cell order is sufficient.
 for i,q in enumerate(lay['c']):bits['c',i]=n;n+=1
 frames={}
 for key,tok in lay['tokens'].items():
  frames[key]=set()
  for j,(u,v,t,e) in enumerate(zip(tok['pos'],tok['pos'][1:],tok['times'],tok['ends'])):
   if u==v:continue
   if physical:
    assert e==t+2
    if tok['fast'][j]:
     bit=None
     for line in by[32]:
      if line.startswith(f'measure q[{v}]'):bit=int(CR.findall(line)[0]);break
     assert bit is not None,(key,v)
     frames[key].symmetric_difference_update({bit})
     if key[0]=='b':
      at=next(ii for ii,l in enumerate(by[32]) if l.startswith(f'measure q[{v}]'))
      by[32].insert(at+1,f'h q[{v}];')
    else:emit(tok['target_start'][j],[f'reset q[{v}];']+([f'h q[{v}];'] if key[0]=='b' else []))
    a,b=(v,u) if key[0]=='b' else (u,v)
    emit(t,[f'cx q[{a}],q[{b}];']);emit(t+1,[f'cx q[{b}],q[{a}];'])
   else:
    assert e==t+3
    emit(t,[f'reset q[{v}];']);emit(t+1,[f'cx q[{u}],q[{v}];']);emit(t+2,[f'cx q[{v}],q[{u}];'])
 for i in range(7):
  d=lay['tokens'][f'd{i}']['pos'][-1]
  for k in 'ab':
   tok=lay['tokens'][f'{k}{i}'];q=tok['pos'][-1];t=tok['coupling'];u,v=(lay.get('data_at_A',[lay['tokens'][f'd{j}']['pos'][-1] for j in range(7)])[i],q) if k=='a' else (q,d)
   emit(t,[f'cx q[{u}],q[{v}];']);bits[k,i]=n
   emit(t+1,([f'h q[{q}];'] if k=='b' else [])+[f'measure q[{q}] -> c[{n}];']);n+=1
 ad={};bcd={}
 for i in range(7):
  aa=lay['tokens'][f'a{i}'];bb=lay['tokens'][f'b{i}'];cq=lay['c'][i]
  def first_transfer(tok):
   for u,v,t in zip(tok['pos'],tok['pos'][1:],tok['times']):
    if u!=v:return t if physical else t+1
   return tok['coupling']
  ad[lay['a'][i]]=first_transfer(aa)
  touch=min([t for t,ls in by.items() if t>=32 and any(cq in map(int,QR.findall(l)) for l in ls)]+[1000])
  ct=min(first_transfer(bb)-1,touch-2)
  bcd[lay['b'][i]]=bcd[cq]=ct
  emit(ct,[f'cx q[{lay["b"][i]}],q[{cq}];'])
  emit(ct+1,[f'measure q[{cq}] -> c[{bits["c",i]}];'])
 prep(BC,lay['b']+lay['c'],bcd)
 prep(A,lay['a'],ad)
 for k in 'abc':
  for S in GENS:
   par={bits[k,i] for i in S}
   for i in S:par.symmetric_difference_update(frames.get(f'{k}{i}',set()))
   dets.append(par)
 dets.append({bits['c',i] for i in range(7)})
 out=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{n}];']
 bar='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
 for t in range(max(by)+1):
  ls=by.get(t,[]);qs=[int(q) for l in ls for q in QR.findall(l)]
  # RX/MX h pairs intentionally share a cell at the same native step.
  out += [f'// step {t}']+ls+[bar]
 out=out[:-1]+['// DETECTOR '+' '.join(f'c[{c}]' for c in sorted(d)) for d in dets]
 return '\n'.join(out)+'\n'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('layout');p.add_argument('a');p.add_argument('bc');p.add_argument('out');z=p.parse_args()
 d=json.loads(Path(z.layout).read_text());txt=make(d,json.loads(Path(z.a).read_text()),json.loads(Path(z.bc).read_text()))
 Path(z.out+'.qasm').write_text(txt);meta=dict(data_qubits=[d['tokens'][f'd{i}']['pos'][-1] for i in range(7)],R=d['R'],Rmax=d['Rmax'],last_cx=d['last_cx'],wait_steps=[d['tokens'][f'a{i}']['coupling']-33 for i in range(7)],data_moves=d['data_moves'],block_moves=d['block_moves'],staggered=len({d['tokens'][f'a{i}']['coupling'] for i in range(7)})>1 or len({d['tokens'][f'b{i}']['coupling'] for i in range(7)})>1,cx=txt.count('cx '),source=vars(z));Path(z.out+'.json').write_text(json.dumps(meta,indent=2)+'\n');print(meta)
