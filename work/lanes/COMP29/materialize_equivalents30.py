"""Fill only certified equivalent prices after an actual reference is available."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
cert=json.loads((H/'q19_equivalence.json').read_text());complete=0;pending=0
for p in cert['cases']:
    with_check=H/p['stem'];without_check=H/p['representative']
    if with_check.with_suffix('.exact.json').exists() and without_check.with_suffix('.exact.json').exists():continue
    if without_check.with_suffix('.exact.json').exists():
        stem,rep=with_check,without_check;target_hash,ref_hash=p['sha256'],p['representative_sha256'];ratio=cert['alpha_at_p001']
    elif with_check.with_suffix('.exact.json').exists():
        stem,rep=without_check,with_check;target_hash,ref_hash=p['representative_sha256'],p['sha256'];ratio=1/cert['alpha_at_p001']
    else:pending+=1;continue
    rf=rep.with_suffix('.exact.json')
    r=json.loads(rf.read_text())
    assert r.get('unchanged_cli')
    assert hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest()==target_hash
    assert hashlib.sha256(rep.with_suffix('.qasm').read_bytes()).hexdigest()==ref_hash
    if r.get('source_sha256'):assert r['source_sha256']==ref_hash
    s=json.loads(stem.with_suffix('.screen.json').read_text())
    out=dict(kind='proved conditional equivalence',representative=rep.name,certificate='q19_equivalence.json',source_sha256=target_hash,representative_sha256=ref_hash,exp_minus_A1=s['exp_minus_A1'],c1=s['c1'],acceptance_ratio_target_over_reference=ratio,pending_representative=False,reference_unchanged_cli=True,total=r['total'],loss2=r['loss2'],loss3=r['loss3'],reference_receipt=rf.name)
    stem.with_suffix('.exact_equivalent.json').write_text(json.dumps(out,indent=2)+'\n');complete+=1
print(dict(equivalent_prices=complete,waiting_for_representative=pending))
