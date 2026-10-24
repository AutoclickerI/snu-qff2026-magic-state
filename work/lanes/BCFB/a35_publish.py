import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;D=H/'a35';rows=[]
for p in (D/'candidates').glob('*.verification.json'):
 v=json.loads(p.read_text());stem=Path(str(p).replace('.verification.json',''));a=json.loads(Path(str(stem)+'.allorders.json').read_text())
 if v['passed'] and a['acceptance']>=.5005:rows.append((a['loss'],stem,a,v))
rows.sort();loss,stem,a,v=rows[0];md=json.loads(stem.with_suffix('.json').read_text());text=stem.with_suffix('.qasm').read_text();sha=hashlib.sha256(text.encode()).hexdigest();md.update(selection_source=str(stem.relative_to(H)),qasm_sha256=sha,allorders={k:a[k] for k in ['loss','acceptance','conditional_loss_kernel_omission_bound']},verification=v)
(H/'best.qasm').write_text(text);(H/'best.json').write_text(json.dumps(md,indent=2));(H/'BEST.json').write_text(json.dumps(dict(stem=str(stem.relative_to(H)),qasm='best.qasm',metadata='best.json',sha256=sha,allorders=md['allorders'],verification=v),indent=2))
(H/'STATUS.md').write_text(f'# BCFB current status\n\nCurrent base: v35b. Best verified: {stem.relative_to(H)}.\nAll-orders {loss:.16g}, acceptance {a["acceptance"]:.12f}; official judge PASS, XTIM FAST, MC3 complete.\nActive search details and finalist table: REPORT.md.\nNo submissions, credentials, commits, pushes or subagents.\n')
print('PUBLISHED',stem.name,loss,a['acceptance'],sha,flush=True)
