import json
from pathlib import Path
H=Path(__file__).resolve().parent;report=H/'REPORT.md';s=report.read_text();body='\n'.join(z for z in s.splitlines()if not z.startswith('**New gated finalist')).lstrip();rows=[]
for p in (H/'pop35b').glob('*/*.gate.json'):
 g=json.loads(p.read_text())
 if not g.get('gated'):continue
 rel=str(Path(g['stem']).relative_to(H));mc=f"mean {g['MC3_mean']:.9e}"if'MC3_mean'in g else'pending'
 line=f"**New gated finalist `{rel}`: all-orders {g['loss']:.12e}, acceptance {g['allorders_acceptance']:.9f}; judge PASS, acceptance {g['judge_acceptance']:.6f}, {g['judge_seconds']:.3f}s/1e6; XTIM FAST {g['speed']['median_seconds_per_1e6']:.3f}s/1e6; MC3 {mc}.**"
 rows.append((g['loss'],line))
rows.sort();report.write_text('\n\n'.join(line for _,line in rows)+'\n\n'+body+'\n');print('Finalists',len(rows),'best',rows[0][0])
