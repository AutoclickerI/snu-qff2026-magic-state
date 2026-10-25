import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,sys,subprocess
from grid_new import H,build
choices=json.loads((H/'choices.json').read_text());manifest=json.loads((H/'grid_manifest.json').read_text());out=[]
for label,m in manifest.items():
    for row in m['builds'][:2]:
        seed=int(row['name'].rsplit('s',1)[1]);r=build(choices[label],label,m['roles'],seed,jit=True);out.append(r)
        p=subprocess.run([sys.executable,str(H/'price.py'),r['name'],'1'],capture_output=True,text=True)
        (H/'logs'/f'{r["name"]}.process.log').write_text(p.stdout+p.stderr)
        print(p.stdout if not p.returncode else p.stderr,flush=True)
(H/'grid_jit_manifest.json').write_text(json.dumps(out,indent=2)+'\n')
