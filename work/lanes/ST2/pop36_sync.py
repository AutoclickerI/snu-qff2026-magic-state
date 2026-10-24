"""Keep lane-local handoff sorted by exact expectation while jobs finish."""
import json,re
from pathlib import Path
H=Path(__file__).resolve().parent;OUT=H/'pop36b'
rows=[]
for p in OUT.glob('*/*.gate.json'):
 g=json.loads(p.read_text())
 if not g.get('gated'):continue
 rel=str(Path(g['stem']).relative_to(H));mc=f"mean {g['MC3_mean']:.9e}"if'MC3_mean'in g else'pending'
 line=f"**New gated finalist `{rel}`: all-orders {g['loss']:.12e}, acceptance {g['allorders_acceptance']:.9f}; judge PASS, acceptance {g['judge_acceptance']:.6f}, {g['judge_seconds']:.3f}s/1e6; XTIM FAST {g['speed']['median_seconds_per_1e6']:.3f}s/1e6; MC3 {mc}.**"
 rows.append((g['loss'],line))
p=H/'REPORT.md';body='\n'.join(z for z in p.read_text().splitlines()if not z.startswith('**New gated finalist')).lstrip();rows.sort();p.write_text('\n\n'.join(s for _,s in rows)+'\n\n'+body+'\n');print('CURRENT_GATES',len(rows),rows[0][0]if rows else None)
