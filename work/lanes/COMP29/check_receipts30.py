"""Audit completed reference receipts against full-circuit screens and hashes."""
import json,math,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
rows=json.loads((H/'v30_manifest.json').read_text());done=[];pending=[];bad=[]
for row in rows:
    n=row['stem'];p=H/n;ef=p.with_suffix('.exact.json');sf=p.with_suffix('.screen.json')
    if n=='f_base':
        assert hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest()==row['sha256']
        done.append(dict(stem=n,inherited_reference=True));continue
    if not ef.exists():ef=p.with_suffix('.exact_equivalent.json')
    if not ef.exists():pending.append(n);continue
    e=json.loads(ef.read_text())
    if 'total' not in e:pending.append(n);continue
    s=json.loads(sf.read_text());err=abs(e['total']-s['total']);tol=5*10**(math.floor(math.log10(abs(e['total'])))-6)+1e-14
    sha=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest();check=dict(stem=n,delta=err,printed_rounding_tolerance=tol,sha256=sha,reference_kind='direct CLI' if e.get('unchanged_cli') else 'proved conditional equivalent')
    if err>tol or (e.get('source_sha256') and e['source_sha256']!=sha):bad.append(check)
    else:done.append(check)
out=dict(named_combinations=len(rows),reference_complete=len(done),reference_pending=len(pending),disagreements=bad,pending_stems=pending)
(H/'v30_reference_status.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='pending_stems'}))
if bad:raise SystemExit(1)
