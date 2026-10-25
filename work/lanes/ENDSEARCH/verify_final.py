import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,hashlib,shutil,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'sparse'))
import frontend as fa

# Price the least-depth realizable resource synthesis in each new geometry.
manifest=json.loads((H/'grid_manifest.json').read_text())
for label,m in manifest.items():
    for row in m['builds'][:2]:
        name=row['name']
        if (H/'logs'/f'{name}.receipt.json').exists():continue
        p=subprocess.run([sys.executable,str(H/'price.py'),name,'1'],capture_output=True,text=True)
        (H/'logs'/f'{name}.process.log').write_text(p.stdout+p.stderr)
        print(p.stdout if not p.returncode else p.stderr,flush=True)
# The incumbent is checked by the same copied evaluator.
for ext in ('qasm','json'):shutil.copyfile(H/f'inputs/v37b.{ext}',H/f'builds/incumbent_v37b.{ext}')
if not (H/'logs/incumbent_v37b.receipt.json').exists():
    p=subprocess.run([sys.executable,str(H/'price.py'),'incumbent_v37b','1'],capture_output=True,text=True)
    (H/'logs/incumbent_v37b.process.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr

receipts=[json.loads(p.read_text()) for p in (H/'logs').glob('*.receipt.json')]
checked={};failed=[]
for r in receipts:
    stem=H/r['stem'];src=stem.with_suffix('.qasm').read_text();sha=hashlib.sha256(src.encode()).hexdigest();assert sha==r['sha256']
    if sha in checked:continue
    ops,dets=fa.parse_current(src);native,_=fa.native_text(ops);_,steps,_=fa.schedule(native)
    assert all(len(ss)==1 and ss[0][1]==o.time for ss,o in zip(steps,ops)),stem
    assert all(set(d)<={o.bit for o in ops if o.bit is not None} for d in dets)
    grid=all(abs(a//6-b//6)+abs(a%6-b%6)==1 for o in ops if o.kind=='CX' for a,b in [o.qs])
    checked[sha]=dict(stem=r['stem'],grid_edges=grid,native_ticks=max(o.time for o in ops)+1)
    if r['metadata'].get('grid_free') is False:assert grid,stem

import xtim
xtim.cache_dir=str(H/'.xtim_cache')
import fast_check
judges=[]
prior={j['sha256']:j for j in json.loads((H/'verification.json').read_text())['judge']} if (H/'verification.json').exists() else {}
for label in ('grid_square_v37b',)+tuple(min((r for r in receipts if r['stem'].split('/')[-1].startswith('grid_'+x+'_')),key=lambda r:r['loss'])['stem'].split('/')[-1] for x in ('tree','square_leaf')):
    p=H/'builds'/label;md=json.loads(p.with_suffix('.json').read_text())
    sha=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest()
    if sha in prior:
        judges.append(dict(prior[sha],stem=label));continue
    rep=fast_check.check(p.with_suffix('.qasm').read_text(),md['data_qubits'],shots=10**6,procs=1)
    j=dict(stem=label,sha256=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest(),shots=10**6,
      format_ok=rep.format_ok,class_ok=rep.class_ok,correctness_ok=rep.correct_ok,acceptance=rep.acceptance,
      loss=rep.score,sem=rep.sem,cx=rep.n_2q,passed=rep.passed)
    judges.append(j);print(json.dumps(j),flush=True)
for r in receipts:
    name=r['stem'].split('/')[-1]
    if name.startswith('suffix_') or name in [j['stem'] for j in judges]:
        for ext in ('qasm','json'):shutil.copyfile(H/(r['stem']+'.'+ext),H/'cand'/(name+'.'+ext))
out=dict(checked=checked,judge=judges)
(H/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(checked=len(checked),official_grids=len(judges))),flush=True)
