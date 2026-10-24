"""Audit completed receipts, preserve a best-circuit alias, prune rebuildable intermediates."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ap=argparse.ArgumentParser();ap.add_argument('--prune',action='store_true');a=ap.parse_args()
assert Path.cwd().name=='BC2'
pending=[];scored=[]
for p in sorted(Path('.').glob('*.score.json')):
    if p.name=='best.score.json':continue
    stem=p.name[:-11];r=json.loads(p.read_text())
    assert Path(stem+'.qasm').exists() and Path(stem+'.json').exists(),stem
    if r.get('check_1e6',{}).get('passed'):
        x=r.get('exact')
        if x is None: pending.append((stem,'exact third-order screen'));continue
        need=(x['total'] is not None and x['total']<=1.03*1.01894e-4) or 1e-12<=abs(x['c1'])<=1.0382e-4
        if need and (set(r.get('MC',{}))!={'0','1000','2000'} or 'mean' not in r):
            pending.append((stem,'three MC seeds'));continue
        if 'mean' in r:
            assert all(v['shots']==10**8 for v in r['MC'].values()),stem
            assert abs(r['mean']-sum(v['score'] for v in r['MC'].values())/3)<1e-16,stem
            if r['MC']['0']['passed']:scored.append((r['mean'],stem,r))
for p in Path('.').glob('*.receipt.json'):
    r=json.loads(p.read_text())
    if r.get('status')=='SAT' and p.name.startswith(('compact_','primed_','combined_','window_')):
        stem=p.name[:-13]+'_m27_29'
        if not Path(stem+'.score.json').exists():pending.append((stem,'synthesized prep has not been scored'))
Path('completion_audit.json').write_text(json.dumps(dict(pending=pending,ranked=[(v,s) for v,s,_ in sorted(scored)]),indent=2))
print('PENDING',pending,flush=True)
if pending:sys.exit(2)
mean,stem,r=min(scored)
baseline=json.loads(Path('v14_bcm.score.json').read_text())['mean']
for ext in ('.qasm','.json','.score.json'):shutil.copyfile(stem+ext,'best'+ext)
best=dict(stem=stem,mean=mean,baseline_mean=baseline,relative_reduction=1-mean/baseline,
          seed0_acceptance=r['MC']['0']['acceptance'],seeds={k:v['score'] for k,v in r['MC'].items()},exact=r['exact'])
Path('BEST.json').write_text(json.dumps(best,indent=2))
removed=[]
if a.prune:
    for p in Path('.').glob('*.qasm'):
        if not p.with_suffix('.score.json').exists():
            removed.extend([str(p),str(p.with_suffix('.json'))])
            p.unlink();p.with_suffix('.json').unlink()
    for d in Path('.').glob('*_init_scan'):
        if not d.is_dir():continue
        for p in d.glob('*.qasm'):
            removed.extend([str(p),str(p.with_suffix('.json'))])
            p.unlink();p.with_suffix('.json').unlink()
    Path('pruned_intermediates.json').write_text(json.dumps(removed,indent=2))
    Path('pruned_intermediates.txt').write_text('\n'.join(removed)+'\n')
subprocess.run([sys.executable,'report.py'],check=True)
manifest=[]
for p in sorted(Path('.').glob('*.qasm')):
    if not p.with_suffix('.score.json').exists():continue
    for q in (p,p.with_suffix('.json'),p.with_suffix('.score.json')):
        manifest.append(hashlib.sha256(q.read_bytes()).hexdigest()+'  '+str(q))
Path('ARTIFACTS.sha256').write_text('\n'.join(manifest)+'\n')
counts=collections.Counter(json.loads(p.read_text()).get('status') for p in Path('.').glob('*.receipt.json'))
print('BEST',best,'SOLVERS',dict(counts),'CANDIDATES',len(list(Path('.').glob('*.score.json'))),flush=True)
