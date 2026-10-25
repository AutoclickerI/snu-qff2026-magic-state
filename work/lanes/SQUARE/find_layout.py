import json,os,sys
from pathlib import Path
import layout_model as L
H=Path(__file__).resolve().parent
info=json.loads((H/'prefix.json').read_text())
L.START=dict(enumerate(info['data_qubits']))
L.READY={i:44 for i in range(7)}
L.REL={int(q):v for q,v in info['release'].items()}
for q in L.START.values():L.REL[q]=99
L.CROSS=False
os.environ['WORKERS']=os.environ.get('SQUARE_WORKERS','2')
joint='joint' in sys.argv
L.SEPARATE_CONNECTED=not joint
L.A_CONNECTED='acon' in sys.argv
L.COMPACT='compact' in sys.argv
r=L.solve(A_LEN=1 if joint else 5,BC_LEN=1 if joint else 9,BC_LATE=1 if joint else 5,NLATE=7,MAXH=3 if L.COMPACT else 2,flag=False)
(H/('layout_compact.json' if L.COMPACT else 'layout_acon.json' if L.A_CONNECTED else 'layout_joint.json' if joint else 'layout_square.json')).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r),flush=True)
