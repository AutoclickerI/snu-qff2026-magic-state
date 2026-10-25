import json,os,sys
from pathlib import Path
import layout_model as L
H=Path(__file__).resolve().parent
L.CROSS=True
near=dict(A=[1,14,8,9,2,16,15],B=[6,26,13,11,4,23,27],C=[12,25,19,17,5,29,28])
mode=sys.argv[1]
if mode=='cat':
    # The same two-cell footprint as the original XZ model; an X-cat check uses a shorter window.
    src=Path(L.__file__).read_text().replace('R - 8','R - 6').replace('R - 6 >= arr','R - 4 >= arr')
    namespace={'__name__':'cat_layout'};exec(compile(src,L.__file__,'exec'),namespace);namespace['CROSS']=True
    solve=namespace['solve']
else:solve=L.solve
for R,helpers in [(44,0),(44,1),(45,2),(46,2)]:
    kw=dict(A_LEN=4,fixR=R,helper=helpers,near=near,MAXH=3)
    kw['check' if mode=='cat' else 'xcheck']=1
    result=solve(**kw)
    name=f'{mode}_R{R}_h{helpers}'
    (H/'layouts'/f'{name}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(name,json.dumps(result),flush=True)
