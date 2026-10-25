"""Recompute actual Taylor coefficients, not finite-p idle-channel pair sums."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,hashlib,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
if len(sys.argv)==1:
    passed=[]
    for p in sorted((H/'logs').glob('*.receipt.json')):
        r=json.loads(p.read_text())
        if 'exact_second_order_p2' not in r:continue
        x=subprocess.run([sys.executable,__file__,str(p)],capture_output=True,text=True)
        if x.returncode:print(x.stdout+x.stderr,flush=True);raise SystemExit(x.returncode)
        passed.append(json.loads(x.stdout))
    (H/'coefficient_audit.json').write_text(json.dumps(passed,indent=2)+'\n')
    print(json.dumps(dict(checked=len(passed),max_model_error=max(abs(x['model_difference']) for x in passed if x['model_difference'] is not None))),flush=True)
    raise SystemExit
p=Path(sys.argv[1]);r=json.loads(p.read_text());meta=r['metadata'];stem=H/r['stem'];text=stem.with_suffix('.qasm').read_text()
sys.path.insert(0,str(H/('sparseframe' if '// FRAME' in text else 'sparse')))
import frontend as fa
if '// FRAME' in text:
    import re
    fa.FRAME_X=[];fa.FRAME_Z=[]
    for line in text.splitlines():
        if line.startswith('// FRAME_X'):fa.FRAME_X+=list(map(int,re.findall(r'c\[(\d+)\]',line)))
        if line.startswith('// FRAME_Z'):fa.FRAME_Z+=list(map(int,re.findall(r'c\[(\d+)\]',line)))
import numpy as np
from collections import defaultdict
from dataclasses import replace
from judge_subset.noise import STANDARD
base=fa.noise_blocks;start=meta['noise_start']
def selected(text,p,first_order=True):
    prog,blocks=base(text,p,noise=replace(STANDARD,idle=0),first_order=True)
    _,steps,gaps=fa.schedule(text)
    for i,ins in enumerate(prog):
        if steps[i][0][1]<start:blocks[i]=[ins.text]
    for i,q,t,n in gaps:
        count=sum(j>=start for j in range(t,t+n))
        if count:blocks[i].append(f'DEPOLARIZE1({count*p}) {q}')
    return prog,blocks
fa.noise_blocks=selected;fa.DATA=meta['data_qubits'];ops,dets=fa.parse_current(text);m=fa.make_model(ops,dets);e=fa.Engine(m);by=defaultdict(list)
for f in m.faults:
    if f['p']:assert f['s']==0;by[f['d']].append(f)
_,kernel=e.ntable(0,0);c2=0.
for d,fs in by.items():
    a,_=e.ntable(0,d);assert abs(a-(d==0))<1e-10
    es=np.array([f['e'] for f in fs]);ps=np.array([f['p'] for f in fs]);cs=np.array([f['chan'] for f in fs])
    c2+=float(np.sum(np.triu(np.outer(ps,ps)*kernel[es[:,None]^es[None,:]]*(cs[:,None]!=cs[None,:]),1)))
c2/=1e-6;expected=meta['template']['second_order_p2'];diff=None if expected is None else c2-expected
assert diff is None or abs(diff)<1e-7,(stem,c2,expected)
old=r['exact_second_order_p2'];r['exact_second_order_p2']=c2;r['coefficient_audit']=dict(method='true first derivatives of every aggregated idle channel',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(stem=r['stem'],coefficient=c2,previous_finite_p_pair_sum=old,model_difference=diff)))
