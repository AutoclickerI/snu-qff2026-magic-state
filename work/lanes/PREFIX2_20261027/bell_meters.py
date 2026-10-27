"""Native two-qubit parity checks using Bell pairs on grid plaquettes.

These differ from one-helper two-contact meters: adjacent data cannot share a
single neighbor on a bipartite grid. A parallel Bell pair measures ZZ or XX
without moving the data and detects the dangerous creation faults of copied rows.
"""
import os,sys,json,itertools,math
from pathlib import Path
import numpy as np
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path.insert(0,str(H.parent/'PREFIX20261027'));sys.path.insert(0,str(H.parent/'T14'))
from qcirc import parse,emit,adjacent
from qtools import price,write_stem
from qtools.validity import raw_check
from search_phase import singles
CELLS=[1,2,3,7,8,9,14,15,16]

def specs(text):
 units,dets=parse(text);stop=min(u['t'] for u in units if u['b']==500)
 busy={(u['t'],q) for u in units for q in u['q']}
 first={q:min([u['t'] for u in units if q in u['q']]+[999]) for q in range(36)}
 qi={q:i for i,q in enumerate(CELLS)};ix=np.arange(1<<len(CELLS),dtype=np.uint32);v=np.zeros(len(ix),complex);v[0]=1
 bits={q:(ix>>i)&1 for q,i in qi.items()};out=[]
 for t in range(stop):
  if t>=2:
   for a,b in itertools.combinations(CELLS,2):
    if not adjacent(a,b) or (t,a) in busy or (t,b) in busy:continue
    zz=float(np.sum(abs(v)**2*(1-2*((bits[a]^bits[b]).astype(float)))))
    xx=float(np.vdot(v,v[ix^(1<<qi[a])^(1<<qi[b])]).real)
    for basis,ev in [('Z',zz),('X',xx)]:
     if ev<1-1e-10:continue
     for h1 in range(36):
      if h1 in [a,b] or not adjacent(a,h1):continue
      for h2 in range(36):
       if h2 in [a,b,h1] or not adjacent(b,h2) or not adjacent(h1,h2):continue
       if first[h1]<=t+1 or first[h2]<=t+1:continue
       if any((s,q) in busy for s in range(t-2,t+2) for q in [h1,h2]):continue
       out.append(dict(t=t,a=a,b=b,h1=h1,h2=h2,basis=basis))
  for u in [u for u in units if u['t']==t and set(u['q'])<=set(CELLS)]:
   k=u['k'];qs=u['q']
   if k in ['R','RX']:
    assert np.max(abs(v[bits[qs[0]]==1]))<1e-10
    if k=='RX':v=(v+v[ix^(1<<qi[qs[0]])])/np.sqrt(2)
   elif k=='CX':v=v[ix^((bits[qs[0]])<<qi[qs[1]])]
   elif k in ['T','TDG']:v*=np.exp((1j if k=='T' else -1j)*np.pi/4*bits[qs[0]])
   else:raise ValueError(u)
 return units,dets,out

def build(stem,sp,name):
 st=Path(stem);units,dets=parse(st.with_suffix('.qasm').read_text());data=json.loads(st.with_suffix('.json').read_text())['data_qubits'];bit=max(u['b'] for u in units if u['b'] is not None)+1
 t,a,b,h1,h2,ba=[sp[k] for k in ['t','a','b','h1','h2','basis']]
 extra=[dict(k='RX',q=(h1,),t=t-2,b=None),dict(k='R',q=(h2,),t=t-2,b=None),dict(k='CX',q=(h1,h2),t=t-1,b=None)]
 extra += [dict(k='CX',q=(x,y) if ba=='Z' else (y,x),t=t,b=None) for x,y in [(a,h1),(b,h2)]]
 extra += [dict(k='M' if ba=='Z' else 'MX',q=(q,),t=t+1,b=bit+j) for j,q in enumerate([h1,h2])]
 text=emit(units+extra,dets+[[bit,bit+1]])
 return write_stem(text,data,H/'cand',name)

def run(base):
 current=Path(base);best=price(current,1);results=[]
 for round in range(3):
  u,d,ss=specs(current.with_suffix('.qasm').read_text());print('round',round,'specs',ss,flush=True);winner=None
  for i,sp in enumerate(ss):
   st=build(current,sp,f'bell_r{round}_{i}');raw=raw_check(st.with_suffix('.qasm').read_text(),json.loads(st.with_suffix('.json').read_text())['data_qubits'])
   if not raw['ok']:print('INVALID',sp,raw,flush=True);continue
   c1,n=singles(st);ans=dict(stem=str(st),parent=str(current),spec=sp,c1=c1,harmful=n)
   if c1<1e-5:
    p=price(st,1);ans.update(loss=p['loss'],acceptance=p['acceptance'])
    if p['acceptance']>=.5002 and p['loss']<best['loss']:
     if winner is None or p['loss']<winner[1]['loss']:winner=(st,p)
   print(json.dumps(ans),flush=True);results.append(ans);(H/'bell_results.json').write_text(json.dumps(results,indent=2))
  if winner is None:break
  current,best=winner;(H/'bell_best.json').write_text(json.dumps(dict(stem=str(current),**best),indent=2))
if __name__=='__main__':run(sys.argv[1])
