import sys,json,math,lzma
from pathlib import Path
H=Path(__file__).resolve().parent;K=H/'knapsack';BASE=5.1443198493581796e-5
rows=[]
for p in K.glob('*/**/*.score.json'):
 try:rows.append(json.loads(p.read_text()))
 except ValueError:pass
uniq={r['stem']:r for r in rows};rows=list(uniq.values());priced=[r for r in rows if '/prices/'in r['stem']or'/additional/'in r['stem']];good=sorted([r for r in rows if r.get('ok')and r.get('acceptance',0)>=.5005],key=lambda r:r['loss']);gated=[]
for p in K.glob('*/**/*.gate.json'):
 r=json.loads(p.read_text())
 if r.get('gated')and r['loss']<BASE-1e-13:gated.append(r)
gated.sort(key=lambda r:r['loss']);lines=['# ST2 — acceptance knapsack and protection composition','', '**Status: RUNNING. Base MAIN/v32p; all-orders 5.144319849358e-5, acceptance0.500961772549. Required candidate acceptance floor0.5005.**','']
if gated:
 lines+=['## Gated improvements','','| Stem | All-orders loss | Acceptance | Judge 1e6 acceptance / seconds | XTIM | MC3 |','|---|---:|---:|---|---|---|']
 for r in gated:lines.append(f"| `{Path(r['stem']).relative_to(H)}` | {r['loss']:.12e} | {r['allorders_acceptance']:.9f} | {r['judge_acceptance']:.6f} / {r['judge_seconds']:.3f} | {r['speed']['classification']} | {r.get('MC3','pending')} |")
 lines.append('')
lines+=['## Acceptance prices','',f'{len(priced)} completed prices are locally collected; {sum(r.get("ok",False)for r in priced)} have all-orders values. Unfinished remote prices are not counted. Every detector row, eight complete echo gadgets, the q16 watch, known-zero measurements, measured initialization forms, physical blue branches, and A/B/C detector subsets are being priced.','', 'Selected completed marginal prices below are complete-circuit all-orders differences relative to v32p. Positive acceptance is recovered by removing/replacing the element. They are not additive physical attributions.','', '| Removed/replaced element | Loss increase | Acceptance recovered | Verified status |','|---|---:|---:|---|']
for r in sorted([r for r in priced if r.get('ok')and r.get('acceptance_recovered',0)>1e-6 and r.get('delta_loss',1)<5e-7],key=lambda r:r['delta_loss']/r['acceptance_recovered'])[:20]:lines.append(f"| `{r['stem']}` | {r['delta_loss']:+.9e} | {r['acceptance_recovered']:+.9f} | all-orders |")
lines+=['','## Search and repair','', 'Marginal log-acceptance knapsacks use conflict constraints between alternative edits, followed by full all-orders repricing of every composition. Other operators include shortened/split echo intervals, sequential use of measured helpers with parity transport, checked-Z preparations, zero-width-aware cubic-gradient timing proposals, and protection subsets on SEPBC R44/R45 seeds. BCFB’s new A witness is ported with full-prefix timing repair at fixed R45. Acceptance is a hard gate; it is not a ranking reward.','', 'The previous timing surrogate missed newly created idle gaps. This pass uses SEPBC’s explicit zero-probability gap channels before differentiating; the on-disk judge/noise model remains unchanged. The proposed circuits still receive full all-orders evaluation.','', 'Sparse factor-cache experiment reproduced the baseline exactly but obtained zero cache hits before its memory cap; it is not used for search ranking.','', '## Verification and resources','', 'All-orders sparse evaluation supports these Python-integer detector masks. Cubic diagnostics above the raw64-bit limit use ST2’s proven reference-only ordering. Candidates that lose deterministic noiseless detectors are rejected. Finalists require the original judge1e6, actual zebra runtime≤20s, XTIM FAST, and three1e8-shot seeds.','', 'The initial zebra pool was paused by owned PID when host load rose; its remaining work was moved to owl after MAIN redraws exited at23:25. All completed prices were preserved. No submissions, commits, pushes, credentials, or subagents. Active jobs will be collected before completion.','', 'Prior verified v30g loss ledger, v32p delivery, and442-evaluation search are preserved in `report_v32p.md.xz`.','']
(H/'REPORT.md').write_text('\n'.join(lines))
print('report',len(rows),'evaluations',len(gated),'gated improvements')
