import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/tools')]
import frame_tools as ft
from qtools.evaluator import frontend as f
ft.f=f
for name in ('original','frame','coherent'):
 stem=H/name;r=ft.singles(stem);stem.with_suffix('.singles.json').write_text(json.dumps(r,indent=2)+'\n')
 print(name,json.dumps({'loss':r['first_order_loss'],'count':r['harmful_count'],'top':[{'weight':x['weight'],'label':x['label'],'record_flips':x['record_flips']}for x in r['harmful'][:5]]}),flush=True)
