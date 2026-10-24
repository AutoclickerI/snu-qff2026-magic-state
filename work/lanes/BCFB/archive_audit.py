import json,tarfile,hashlib,csv
from pathlib import Path
H=Path(__file__).resolve().parent
expected=sum(g['stored'] for g in json.loads((H/'RUN_SUMMARY.json').read_text())['groups'])+2
prior={f'witnesses/prior_BCSYN2_s{r["seed"]}.json':r['sha256'] for r in json.loads((H/'prior_feedback_audit.json').read_text())}
nw=nr=ne=0;names=set();evidence=[]
with tarfile.open(H/'witnesses.tar.xz','r|xz') as tar:
 for m in tar:
  assert m.name not in names,m.name;names.add(m.name)
  if m.name.startswith('witnesses/'):nw+=1
  elif m.name.startswith('receipts/'):nr+=1
  elif m.name.startswith('evidence/'):ne+=1;evidence.append(m.name)
  else:raise AssertionError(m.name)
  if m.name in prior:
   w=json.loads(tar.extractfile(m).read());assert hashlib.sha256(w['raw_log'].encode()).hexdigest()==prior[m.name]
assert nw==nr==expected,(nw,nr,expected)
with (H/'search.csv').open() as f:assert sum(1 for _ in csv.DictReader(f))==expected
p=H/'witnesses.tar.xz';out=dict(status='PASS',witnesses=nw,receipts=nr,evidence_files=ne,sha256=hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),bytes=p.stat().st_size,archived_evidence=evidence)
(H/'ARCHIVE_AUDIT.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='archived_evidence'}))
