import os,sys,json,re,hashlib,shutil,subprocess
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','PYTHONDONTWRITEBYTECODE'):os.environ[k]='1'
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(OUT/'report.py')],check=True)
r=json.loads((OUT/'results.json').read_text());winner=r['finalists'][0];name=winner['name'];assert winner['mean']<7.282e-5
for f in r['finalists']:
 if f['name']=='tdg_0':continue
 ref=json.loads((OUT/(f['name']+'.reference.json')).read_text());fast=json.loads((OUT/(f['name']+'.result.json')).read_text());assert abs(ref['total']-fast['total'])<1e-10,(f['name'],ref,fast)
 assert ref['sha256']==hashlib.sha256((OUT/(f['name']+'.qasm')).read_bytes()).hexdigest()
for suffix in ['.qasm','.json','.check.json','.reference.log','.reference.json','.mc.log']:
 shutil.copyfile(OUT/(name+suffix),OUT/('best'+suffix))
check=json.loads((OUT/'best.check.json').read_text());assert check['passed']
# Verify all saved candidates have metadata and record evidence by content hash.
manifest=[]
for q in sorted(OUT.glob('*.qasm')):
 meta=json.loads(q.with_suffix('.json').read_text());assert len(meta['data_qubits'])==7
 sha=hashlib.sha256(q.read_bytes()).hexdigest();evidence=q.with_suffix('.check.json')
 if not evidence.exists():
  # watch_1 is a generated alias of m15, confirmed byte-for-byte.
  aliases=[x for x in OUT.glob('*.qasm')if x!=q and x.read_bytes()==q.read_bytes()and x.with_suffix('.check.json').exists()]
  assert aliases,q;evidence=aliases[0].with_suffix('.check.json')
 c=json.loads(evidence.read_text());assert c['passed'],(q,c)
 manifest.append(dict(file=q.name,sha256=sha,data_qubits=meta['data_qubits'],R_native=meta['R'],CX=meta['CX'],check_file=evidence.name,check_passed=True))
(OUT/'manifest.json').write_text(json.dumps(dict(winner=name,mean=winner['mean'],seed0_acceptance=winner['seeds']['0'][1],candidates=manifest),indent=2)+'\n')
p=OUT/'REPORT.md';t=p.read_text();old=t.splitlines()[2]
gain=100*(7.282e-5-winner['mean'])/7.282e-5
new=f"**Complete. Delivery: [best.qasm](best.qasm) and [best.json](best.json), identical to `{name}`.** Its three-seed 1e8-shot MC mean is **{winner['mean']:.6e}**, {gain:.2f}% below the supplied 7.282e-5 bar; seed-0 acceptance is **{winner['seeds']['0'][1]:.5f}**. It passes the actual 1e6-shot judge and the unmodified `exact2.py --third` confirmation."
t=t.replace(old,new,1)
t+='\n## Verification and remaining limits\n\nThe four new MC finalists have unmodified exact2 reference receipts; their printed third-order totals agree with the accelerated exploration to all printed digits. [manifest.json](manifest.json) records QASM hashes, data metadata, native R/CX, and passing 1e6-shot check evidence for every saved circuit, including the delivery alias. The copied MC runner in `inputs/mc3.py` is byte-identical to `MAIN/spec/mc3.py`; the local copy was required because that path was missing on jerry. The native-schedule comparison and actual judge gates, rather than builder layer labels, verify the deliverable.\n\nThe improvement is the observed three-seed mean required by the task; the difference is small relative to per-seed Monte Carlo uncertainty and does not establish statistical superiority of the true mean. No physical implementation or official submission was attempted. General block relocation, other encoder footprints, and routes inside the pre-stage with later CX partners following remain open. All lane-launched computation was collected on process exit; no HOPS worker is intentionally left running.\n'
p.write_text(t)
print(json.dumps(dict(winner=winner,check=check['passed'],candidates=len(manifest)),indent=2),flush=True)
