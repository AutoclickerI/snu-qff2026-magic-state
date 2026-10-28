import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
import frame_tools as ft,frontend_axis as f,record_contract
ft.f=f;record_contract.fa=f;ft.OUT=H/'native_teleport'
p=ft.OUT/'fixed_source';text=p.with_suffix('.qasm').read_text();ops,_=f.parse_current(text);frames=ft.parse_frames(text);B=[12,26,25,11,3,28,17];f.DATA=B
comp=record_contract.complete(f.make_model(ops,[]),[]);assert not any(x['reference']for x in comp['missing'])
dets=[set(x['bits'])for x in comp['missing']];stem=ft.emit('fixed_complete',ops,dets,B,frames,{'parent':str(p),'contract':'all noiseless deterministic affine rows'})
raw=ft.raw_check(stem.with_suffix('.qasm').read_text(),B);print(json.dumps({'rows':len(dets),'raw':raw},indent=2));(H/'native_teleport_contract.json').write_text(json.dumps({'rows':len(dets),'raw':raw,'completion':comp},indent=2)+'\n')
