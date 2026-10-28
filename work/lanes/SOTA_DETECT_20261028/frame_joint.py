import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path[:0]=[str(H),str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/tools')]
import acceptance_search as ac,frame_tools as ft,frontend_axis as f
from qtools.evaluator import sparse_walsh as sw
ft.f=f;sw.fa=f;sw.parse_current=f.parse_current;ft.OUT=H/'frame_cand'
p=R/'work/lanes/EXPAND2_20261027/release_phase/native_incumbent_phase_late'
ops,rows,data,m,e,groups=ac.prepare(p)
v0=296881791826164449280;v1=1180596138885567741952
selector=next(r for r in ac.null_rows([v0],len(rows)) if (r&v1).bit_count()%2)
dets=[ac.xor_rows(rows,r) for r in ac.null_rows([v0,v1],len(rows))]
frame={'X':(0,set(ac.xor_rows(rows,selector))),'Z':(0,set())}
s=ft.emit('joint0',ops,dets,data,frame,{'unframed_direction':v0,'x_framed_direction':v1,'selector':selector})
print(json.dumps(ft.price(s)),flush=True)
