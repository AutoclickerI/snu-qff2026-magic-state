import json,sys
from pathlib import Path
import layout_model as L
H=Path(__file__).resolve().parent
L.CROSS=True;L.KEEP_A=sys.argv[1]=='both';L.KEEP_R3=True
near=dict(A=[1,14,8,9,2,16,15],B=[6,26,13,11,4,23,27],C=[12,25,19,17,5,29,28])
for R,helpers in [(44,1),(45,2),(46,2)]:
    r=L.solve(A_LEN=4,fixR=R,helper=helpers,near=near,MAXH=3)
    name=f'carry_{sys.argv[1]}_R{R}_h{helpers}'
    (H/'layouts'/f'{name}.json').write_text(json.dumps(r,indent=2)+'\n')
    print(name,json.dumps(r),flush=True)
