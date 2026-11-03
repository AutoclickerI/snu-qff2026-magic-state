import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/tools')]
import frame_tools as ft,frontend_axis as f
from qtools.evaluator import sparse_walsh as sw
ft.f=f;sw.fa=f;sw.parse_current=f.parse_current;ft.OUT=H/'frame_cand'
p=R/'work/lanes/EXPAND2_20261027/release_phase/native_incumbent_phase_late'
ops,dets,md=ft.load(p)
s=ft.emit('control',ops,dets,md['data_qubits'],{'X':(0,set()),'Z':(0,set())})
print(json.dumps(ft.price(s)),flush=True)
