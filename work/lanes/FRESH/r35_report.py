from pathlib import Path
import json
H=Path(__file__).resolve().parent;D=H/'r35';p=H/'REPORT.md'
rows=[]
for file in D.glob('*.verified.json'):
 r=json.loads(file.read_text());a=r['allorders']
 if a['loss']>=4.393527676042078e-5 or a['acceptance']<.5005:continue
 rows.append((a['loss'],file.name.removesuffix('.verified.json'),r))
rows.sort()
block=['<!-- r35 verified start -->','## Verified v35a improvements','','| Circuit | All-orders loss | Acceptance | Judge seconds / XTIM | MC0 / 1000 / 2000; mean |','|---|---:|---:|---|---|']
for loss,name,r in rows:
 block.append(f'| [r35/{name}](r35/{name}.qasm) | {loss:.14g} | {r["allorders"]["acceptance"]:.12f} | PASS {r["judge"]["seconds"]:.2f}s / FAST {r["speed"]["median_seconds_per_1e6"]:.2f}s | '+ ' / '.join(f'{v:.8g}' for v in r['seeds'])+f'; **{r["mean"]:.8g}** |')
block+=['','All rows passed exact ideal acceptance1/loss0, detector determinism, no harmful single fault, unchanged judge1e6, XTIM FAST and three seeds of100M shots. Ranking is all-orders; MC values remain separate.','<!-- r35 verified end -->','']
s=p.read_text()
if '<!-- r35 verified start -->' in s:
 a=s.index('<!-- r35 verified start -->');b=s.index('<!-- r35 verified end -->')+len('<!-- r35 verified end -->');s=s[:a]+ '\n'.join(block)+s[b:]
else:s=s.replace('# FRESH\n','# FRESH\n\n'+'\n'.join(block),1)
s=s.replace('No new v35a improvement has completed all gates yet.','Verified results are ranked above; echo integrations continue.')
p.write_text(s)
