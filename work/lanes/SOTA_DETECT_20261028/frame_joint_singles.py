import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/tools')]
import frame_tools as ft,frontend_axis as f
ft.f=f
r=ft.singles(H/'frame_cand/joint0')
(H/'frame_joint_singles.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['first_order_loss'],r['harmful_count'])
