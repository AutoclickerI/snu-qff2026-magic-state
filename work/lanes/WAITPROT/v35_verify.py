"""Verify source-bound receipts, exported artifacts, menu patches and report links."""
from v35_build import *
from v35_publish import circuit

manifests=['initial','extra','live','combo','follow','mechanism','consecutive','final','early','close','terminal']
expected={}
for label in manifests:
 for j in json.loads((V/(label+'_jobs.json')).read_text()):
  if j['stem']in expected:assert expected[j['stem']]['sha256']==j['sha256']
  expected[j['stem']]=j
receipts=[]
for name,j in expected.items():
 p=V/name;r=json.loads(p.with_suffix('.score.json').read_text());sha=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest()
 assert sha==j['sha256']==r['sha256']==json.loads(p.with_suffix('.json').read_text())['qasm_sha256'],name
 if r['ok']:
  assert r['noiseless_correct'] and r['loss']>0 and 0<r['acceptance']<1,name
  assert r['omission_bound']<1e-11,name
 else:assert 'error'in r and 'traceback'in r,name
 receipts.append(dict(stem=name,sha256=sha,ok=r['ok'],loss=r.get('loss'),acceptance=r.get('acceptance'),error=r.get('error')))

finalists=[]
for p in sorted(V.glob('*.gates.json')):
 if p.name.endswith('.owl_gates.json'):continue
 g=json.loads(p.read_text());name=g['stem'];score=json.loads((V/(name+'.score.json')).read_text())
 if name=='canonical_base'or not g['passed']or g['speed']['classification']!='FAST'or score['loss']>=L0 or score['acceptance']<.5005:continue
 mc=json.loads((V/(name+'.mc.json')).read_text());audit=json.loads((V/(name+'.audit.json')).read_text())
 sha=hashlib.sha256((V/(name+'.qasm')).read_bytes()).hexdigest()
 assert sha==g['sha256']==score['sha256']==mc['sha256']==audit['sha256'],name
 assert mc['returncode']==0 and [s['seed']for s in mc['seeds']]==[0,1000,2000],name
 assert all(s['acceptance']>=.5 for s in mc['seeds']),name
 assert abs(mc['mean']-sum(s['score']for s in mc['seeds'])/3)<1e-15
 assert audit['all_channels_faults_rotations_projectors_and_observables_match']and audit['native_ticks_match'],name
 finalists.append(dict(stem=name,sha256=sha,loss=score['loss'],acceptance=score['acceptance'],MC3=mc['mean'],seed0=mc['seeds'][0]['score'],passed=True,FAST=True))

menu=json.loads((H/'menu_v35a.json').read_text())
assert menu['base_sha256']==BASE_SHA
patches=0
def ops_key(o):return(o['t'],tuple(lines(o)))
for row in menu['entries']:
 if not row['ok']:continue
 p=ROOT/row['stem'];assert hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest()==row['sha256'],row['stem']
 patch=row['lines'];baseops={ops_key(o)for o in BASE['ops']}
 for r in patch['remove']:baseops.remove((r['t'],tuple(r['lines'])))
 for r in patch['add']:baseops.add((r['t'],tuple(r['lines'])))
 c=circuit(p);assert baseops=={ops_key(o)for o in c['ops']},row['stem']
 base_dets={'// DETECTOR '+' '.join(f'c[{b}]'for b in rr)for rr in BASE['dets']}
 base_dets-=set(patch['detector_remove']);base_dets|=set(patch['detector_add'])
 assert base_dets=={'// DETECTOR '+' '.join(f'c[{b}]'for b in rr)for rr in c['dets']},row['stem']
 assert abs(row['loss_gain']-(L0-row['loss']))<1e-15
 assert abs(row['acceptance_cost']-(A0-row['acceptance']))<1e-15
 patches+=1

aliases=[]
for alias in ['v35_best','v35_seed0_best']:
 m=json.loads((H/(alias+'.metrics.json')).read_text());p=H/m['source_stem']
 for ext in ['.qasm','.json']:assert(H/(alias+ext)).read_bytes()==p.with_suffix(ext).read_bytes()
 assert m['gate']['passed']and m['mc']['returncode']==0
 aliases.append(dict(alias=alias,source=m['source_stem'],byte_identical=True))
report=(H/'REPORT.md').read_text();assert 'pending'not in report.lower()
for target in re.findall(r'\]\(([^)]+)\)',report):assert(H/target).exists(),target
width=None
for line in report.splitlines():
 if not line.startswith('|'):width=None;continue
 n=len(line.split('|'))
 if width is None:width=n
 assert width==n,line
out=dict(status='COMPLETE',unique_priced_circuits=len(receipts),numerical=sum(r['ok']for r in receipts),noiseless_rejections=sum(not r['ok']for r in receipts),menu_patches_reconstructed=patches,finalists=finalists,aliases=aliases,receipts=receipts)
(V/'completion_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k not in('receipts','finalists','aliases')}))
