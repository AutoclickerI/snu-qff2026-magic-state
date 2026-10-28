# Derived from work Copyright IBM 2025, Apache License 2.0.
# Modified for this task: native d=3 extraction and T seed; see REPORT.md.
"""d=3 unitary initializer from IBM ColorCode.unitary_prep, with magic seed T/Tdg.
Reference: IBM/gauging_clifford_measurement color_code.py at 3a5bb25eddcce5945f43b8f6ca462b0a48d2b25b, Apache-2.0.
Original prep uses S_DAG seed for +i; here S_DAG is replaced by T or T_DAG.
This independent transcription uses nonpipelined resets and layers; the subsequent stabilizer round is not yet included.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
import frame_tools as ft,frontend_axis as f,record_contract
from qtools.evaluator import sparse_walsh as sw
ft.f=f;record_contract.fa=f;sw.fa=f;sw.parse_current=f.parse_current;ft.OUT=H
D=[0,11,9,26,12,21,14];f.DATA=D
rst=[9,6,7,8,10,14,13,15,16,21,19,20,25]; plus=[9,6,7,10,14,13,16,21,19,25];extra=[0,12,11,26]
rounds=[[(9,8),(14,15),(21,20)],[(9,15),(14,20)],[(14,8),(21,15)],[(7,8),(16,15),(19,20)],[(20,19),(15,16),(8,7)],[(10,16),(13,19)],[(16,10),(13,7)],[(19,13)],[(7,13)]]
late=[[(7,13)],[(19,13)],[(6,7),(25,19)],[(19,25),(7,6)],[(6,0),(13,12),(10,11),(25,26)],[(26,25),(11,10),(12,13),(0,6)]]

def build(phase):
 ops=[f.Op('RX' if q in plus else 'R',(q,),0)for q in rst+extra]
 for t,edges in enumerate(rounds,1):ops.extend(f.Op('CX',e,t)for e in edges)
 ops.append(f.Op(phase,(13,),10))
 for t,edges in enumerate(late,11):ops.extend(f.Op('CX',e,t)for e in edges)
 meas=[6,13,10,25]
 ops.extend(f.Op('M',(q,),17,i)for i,q in enumerate(meas));dets=[{i}for i in range(4)]
 ops.sort(key=lambda x:x.time)
 stem=ft.emit('seed_'+phase.lower(),ops,dets,D,metadata={'source':'IBM/color_code.py 3a5bb25eddcce5945f43b8f6ca462b0a48d2b25b; adapted S_DAG seed to T/Tdg','scope':'physical native initializer, no verification round'})
 raw=ft.raw_check(stem.with_suffix('.qasm').read_text(),D)
 print('RAW',phase,json.dumps(raw),flush=True)
 if raw['ok']:
  ss=ft.singles(stem);print('SINGLES',json.dumps({'first_order_loss':ss['first_order_loss'],'harmful_count':ss['harmful_count']}),flush=True)
  print('PRICE',json.dumps(ft.price(stem)),flush=True)
if __name__=='__main__':
 for phase in ('T','TDG'):build(phase)
