import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,subprocess,sys
from build_candidates import H,suffix
choices=json.loads((H/'choices.json').read_text())
for label,t in choices.items():
    name=suffix(t,'suffix_'+label+'_jit',jit=True)
    r=subprocess.run([sys.executable,str(H/'price.py'),name,'1'],capture_output=True,text=True)
    (H/'logs'/f'{name}.process.log').write_text(r.stdout+r.stderr)
    print(r.stdout if not r.returncode else r.stderr,flush=True)
