# Derived from work Copyright IBM 2025, Apache License 2.0.
# Modified for this task: native d=3 extraction and T seed; see REPORT.md.
"""IBM flagged superdense d=3 syndrome round, literal nonpipelined layer extraction.
Derived from color_code.py at IBM/gauging_clifford_measurement commit
3a5bb25eddcce5945f43b8f6ca462b0a48d2b25b, Apache-2.0.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
import frontend_axis as f,frame_tools as ft,record_contract
from qtools.evaluator import sparse_walsh as sw
ft.f=f;record_contract.fa=f;sw.fa=f;sw.parse_current=f.parse_current;ft.OUT=H
D=[0,11,9,26,12,21,14];f.DATA=D;g=json.loads((H/'geometry.json').read_text());Q={tuple(c)for c in g['code_data']};pc=lambda p:(p[0]+1)*6+p[1]-1
layers=[[]for _ in range(10)];first=[];second=[];flags=[]
for p in g['plaquettes']:
 r,c=p['flag'];flag=(r,c);a=(r,c-1);b=(r,c+1);flags.append(pc(flag));early=c%6==2
 if early:
  first.append(pc(b));second.append(pc(a))
  for i,e in [(0,(flag,b)),(1,(flag,a)),(2,(a,flag)),(9,(flag,a)),(8,(flag,b)),(7,(b,flag))]:layers[i].append(tuple(map(pc,e)))
 else:
  first.append(pc(a));second.append(pc(b))
  for i,e in [(0,(flag,a)),(1,(flag,b)),(2,(b,flag)),(9,(flag,b)),(8,(flag,a)),(7,(a,flag))]:layers[i].append(tuple(map(pc,e)))
 side1=[(r+1,c-1),(r,c-2),(r-1,c-1)];side2=[(r+1,c+1),(r,c+2),(r-1,c+1)]
 for j,q in enumerate(side1):
  if q in Q:
   layers[(3 if early else 1)+j].append((pc(a),pc(q)))
   layers[(6 if early else 4)+j].append((pc(q),pc(a)))
 for j,q in enumerate(side2):
  if q in Q:
   layers[(1 if early else 3)+j].append((pc(b),pc(q)))
   layers[(4 if early else 6)+j].append((pc(q),pc(b)))
for t,layer in enumerate(layers):
 used=[q for edge in layer for q in edge]
 assert len(used)==len(set(used)),(t,layer)
 assert all(abs(a//6-b//6)+abs(a%6-b%6)==1 for a,b in layer),(t,layer)

def append_stab(ops,dets,clock,bit):
 ops += [f.Op('R',(q,),clock)for q in first+second]
 ops += [f.Op('RX',(q,),clock)for q in flags]
 for i,layer in enumerate(layers,1):ops.extend(f.Op('CX',edge,clock+i)for edge in layer)
 for i,q in enumerate(first):ops.append(f.Op('M',(q,),clock+11,bit+i));dets.append({bit+i})
 # Individual label and order don't matter; each row is deterministic on clean |T_L>.
 for i,q in enumerate(second):ops.append(f.Op('M',(q,),clock+12,bit+3+i));dets.append({bit+3+i})
 for i,q in enumerate(flags):ops.append(f.Op('MX',(q,),clock+12,bit+6+i));dets.append({bit+6+i})
 ops.sort(key=lambda o:o.time)
 return ops,dets,clock+13,bit+9
if __name__=='__main__':
 base=H/'seed_t';ops,dets=f.parse_current(base.with_suffix('.qasm').read_text());ops,dets,_,_=append_stab(ops,dets,18,4)
 stem=ft.emit('seed_stab',ops,dets,D,metadata={'scope':'native unpipelined IBM seed and flagged syndrome','layers':layers,'first':first,'second':second,'flags':flags})
 raw=ft.raw_check(stem.with_suffix('.qasm').read_text(),D);print('RAW',json.dumps(raw),flush=True)
 if raw['ok']:
  ss=ft.singles(stem);print('SINGLES',json.dumps({'loss':ss['first_order_loss'],'n':ss['harmful_count']}),flush=True);print('PRICE',json.dumps(ft.price(stem)),flush=True)
