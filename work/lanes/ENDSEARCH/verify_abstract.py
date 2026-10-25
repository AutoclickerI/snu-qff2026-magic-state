"""Organizer's exact raw-state correctness check for grid-free circuits.
This calls the exact verifier directly; adjacency is intentionally outside
this abstract experiment and no format-validity claim is made.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,re,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'sparse'))
import frontend as fa
from tprep.exact import verify
out=[]
for name in [p.stem for p in sorted((H/'builds').glob('suffix_*.qasm'))]+['hop_unmeasured']:
    stem=H/'builds'/name;src=stem.with_suffix('.qasm').read_text();md=json.loads(stem.with_suffix('.json').read_text())
    ops,ds=fa.parse_current(src);text,_=fa.native_text(ops);measure=[o for o in ops if o.bit is not None];rec={o.bit:i for i,o in enumerate(measure)}
    for d in ds:text+='\nDETECTOR '+' '.join(f'rec[{rec[b]-len(measure)}]' for b in sorted(d))
    frame={'X':(0,[]),'Z':(0,[])}
    for l in src.splitlines():
        if l.startswith('// FRAME'):
            kind=l[9];const=int(re.search(r'\(([01])\)',l).group(1));frame[kind]=(const,[rec[int(b)] for b in re.findall(r'c\[(\d+)\]',l)])
    r=verify(text,md['data_qubits'],frame=frame);assert not r['errors'],(name,r)
    out.append(dict(stem=name,sha256=hashlib.sha256(src.encode()).hexdigest(),method='organizer tprep.exact.verify, raw codespace and target; grid format not checked',result=r))
(H/'abstract_verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps([{k:v for k,v in x.items() if k!='result'}|{'infidelity':x['result']['infidelity']} for x in out]),flush=True)
