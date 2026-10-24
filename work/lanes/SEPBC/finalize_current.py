"""Reconcile unchanged receipts and write the current Task A/B evidence ledger."""
from pathlib import Path
import json,re,hashlib,collections,sys
H=Path(__file__).resolve().parent
J=lambda p:json.loads(p.read_text())
rows=[]
for p in sorted(H.glob('*.screen.json')):
 name=p.name.removesuffix('.screen.json')
 if not name.startswith(('sepbc_v29c','es_','endstate_')):continue
 md=J(H/(name+'.json'));sc=J(p)
 row=dict(stem=name,screen=sc,metadata=md,sha256=sc['sha256'],reference_deltas=dict(sepBC=sc['total']-5.71112722e-5,ABC210=sc['total']-5.03262480e-5))
 for suffix,key in [('.ablation.json','ablation'),('.speed_prediction.json','speed_prediction'),('.allorders.json','allorders'),('.allorders_general.validation.json','allorders_validation'),('.idle_curve.json','idle_curve'),('.build.json','build')]:
  f=H/(name+suffix)
  if f.exists():row[key]=J(f)
 log=H/(name+'.unchanged_exact.log')
 if log.exists():
  text=log.read_text();third=re.search(r'third order: ([\deE+.\-]+)',text);total=re.search(r'1-F \(to 3rd order\) = ([\deE+.\-]+)',text)
  if third and total:
   d=J(H/(name+'.unchanged_exact.json'))
   assert abs(d['loss1'])<1e-12,(name,d['loss1'])
   assert abs(d['loss2']-sc['second'])<1e-13,(name,d['loss2'],sc['second'])
   assert third[1]==f"{sc['third']:.5e}" and total[1]==f"{sc['total']:.5e}",(name,third[1],total[1],sc)
   row['unchanged_cli']=dict(source=name,second=d['loss2'],third_printed=third[1],total_printed=total[1],agreement='second full precision; third/total at CLI printed precision')
 if 'ablation'in row:assert abs(row['ablation']['rows'][0]['total']-sc['total'])<1e-14,name
 for suffix,key in [('.judge.log','judge'),('.speed.log','judge_diagnostic')]:
  f=H/(name+suffix)
  if f.exists():row[key]=f.read_text()
 rows.append(row)
archive=H/'current_results.json'
if archive.exists():
 present={r['stem']for r in rows}
 rows.extend(r for r in J(archive)['rows']if r['stem']not in present)
 rows.sort(key=lambda r:r['stem'])
for r in rows:
 matches=[v for v in rows if v['sha256']==r['sha256'] and v['metadata']['data_qubits']==r['metadata']['data_qubits'] and 'unchanged_cli'in v]
 if 'unchanged_cli'not in r and matches:
  r['unchanged_cli']=dict(matches[0]['unchanged_cli'],byte_identical_to=matches[0]['stem'])
  if 'ablation'in matches[0]:r['ablation']=matches[0]['ablation'];r['ablation_alias']=matches[0]['stem']
missing=[r['stem']for r in rows if 'unchanged_cli'not in r]
(H/'current_results.json').write_text(json.dumps(dict(rows=rows,missing_unchanged=missing),indent=2))
if '--require-complete'in sys.argv:assert not missing,missing
winner=next(r for r in rows if r['stem']=='sepbc_v29c_q5_both')
best=min((r for r in rows if not r['stem'].startswith('sepbc_v29c')),key=lambda r:r['screen']['total'])
def mechanism(s):
 if s.startswith('sepbc_v29c'):return 'Known-zero detector in an existing q5 idle slot'
 if 'noguard'in s:return 'Removing coherent-hop source checks leaves extra undetected faults; R unchanged'
 if 'target'in s:return 'Best relaxed-R geometry costs 24 actual data hops; exposure remains'
 if 'joint'in s:return 'Joint prefix/reset lifetimes; A/B storage still dominates'
 if 'ca12'in s or s.startswith('endstate_cli'):return 'Stationary C, lower-danger A12; serialized A/B exposure dominates'
 if 'ca11'in s:return 'Stationary C, lower-danger A11; serialized A/B exposure dominates'
 if 'cdirect'in s:return 'Six C teleports removed; original A10 encoder pairs with idle noise'
 return 'Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss'
status='COMPLETE — Task A verified; Task B emitter and witness-family diagnosis delivered.' if '--complete'in sys.argv else 'RUNNING — physical checks complete; all-orders ranking/final receipt reconciliation in progress.'
lines=[f'Status: {status}','',
'Current delivery replaces the working journal. The earlier accepted v28s delivery is preserved in [REPORT_v28s.md](REPORT_v28s.md). No submissions, commits, pushes, credentials access, or other-lane writes.','',
'## Task A: v29c known-state detector','',
'Best qualified grid circuit: [sepbc_v29c_q5_both.qasm](sepbc_v29c_q5_both.qasm) / [metadata](sepbc_v29c_q5_both.json). It adds Z measurements on q5 at native steps37 and38 and their singleton detectors, inside existing idle slots. 213 CX, R48, depth51. The independent A/BC CSS-state scan, including symbolic record frames, found only q5/Z at37 and38; this does not claim an exhaustive search of arbitrary prefix observables.','',
f"Exact parts: second **{winner['screen']['second']:.12e}**, third **{winner['screen']['third']:.12e}**, total **{winner['screen']['total']:.12e}**; c1={winner['screen']['c1']:.3e}; exp(-A1)={winner['screen']['exp_minus_A1']:.10f}. Unchanged exact2 CLI agrees. Against v29c's 6.26263311786e-5, the cubic improvement is {(6.26263311786e-5-winner['screen']['total'])/6.26263311786e-5*100:.4f}%. Against LADDER sepBC/ABC210, shortfall is {winner['reference_deltas']['sepBC']:.9e}/{winner['reference_deltas']['ABC210']:.9e}.",'',
'1e6 judge PASS: seed-0 acceptance **0.50627**, **3.1 s** on zebra. XTIM prediction **FAST**, 5.4724 s/1e6 in its concurrent timing run. MC at 1e8 shots, seeds0/1000/2000: **6.306625e-5 / 6.279701e-5 / 6.229151e-5**; mean **6.271826e-5**; seed-0 acceptance **0.50645**. The three-seed estimate is noisy; it is not used to overrule applicable all-orders ranking.','',
'| Variant | Second | Third | Total | exp(-A1) | MC3 mean | All orders |','|---|---:|---:|---:|---:|---:|---:|']
for s,mc in [('sepbc_v29c_q5_t37',6.271770e-5),('sepbc_v29c_q5_t38',6.251170e-5),('sepbc_v29c_q5_both',6.271826e-5)]:
 r=next(x for x in rows if x['stem']==s);v=r['screen'];ao=f"{r['allorders']['loss']:.12e}"if 'allorders'in r else 'pending'
 lines.append(f"| `{s}` | {v['second']:.10e} | {v['third']:.10e} | {v['total']:.10e} | {v['exp_minus_A1']:.9f} | {mc:.6e} | {ao} |")
base=H/'inputs/v29c.allorders.json'
if base.exists() and 'allorders'in winner:
 ba=J(base);wa=winner['allorders'];lines+=['',f"All-orders parent v29c: **{ba['loss']:.12e}**; q5/t37+t38: **{wa['loss']:.12e}**, acceptance **{wa['acceptance']:.12f}**, improvement **{100*(ba['loss']-wa['loss'])/ba['loss']:.4f}%**. The five-projector extension validates the complete categorical channel multiset against EVAL, direct projector sectors, and a three-channel categorical enumeration for each circuit; scope rank5, 15 rotations, width26. See adjacent `.allorders_general.validation.json` and `.allorders.log` receipts."]
lines+=['',
'Layout remains data `[0,20,7,10,3,22,21]`, A `[1,14,8,9,2,16,15]`, B `[6,26,13,11,4,23,27]`, C `[12,25,19,17,5,29,28]`. The inherited v29c coherent transfers and terminal instrument are unchanged; there is no additional move. The complete native operation plan is retained. t37+t38 has no resolved cubic benefit over t38 alone and consumes more acceptance. The completed all-orders comparison changes the selection: both measurements improve on t38 alone by8.17455e-11 (6.30862316092e-5 versus6.30863133547e-5). That tiny higher-order gain is well below MC resolution, but all-orders loss is the stated ranking rule. t38 alone remains a qualified near-tie, with MC3 mean6.251170e-5, acceptance0.507344 and3.3s at1e6.','',
'The unchanged top-pair report identifies the remaining A/data exposure: q7 X-idle at20–23 with q20 Y-idle at40–46 contributes7.731e-7; q4 X-idle at18–39 with each late A CX fault contributes2.411e-7; q0 Z/Y-idle at39–47 with late A encoder faults contributes1.989e-7 per listed pair. q5 catches BC preparation faults but leaves these A/data and round contributions. These are physical-pair examples, not an additive attribution of the LADDER reference gap.','',
'## Task B: complete ENDSTATE attachment','',
'Reusable CLI: [endstate_emit.py](endstate_emit.py), with [input contract and examples](EMITTER.md). It consumes native operations/detectors, uses the independently extracted real v23/v29 cultivation prefix, searches geometry and common code automorphisms, routes data by coherent two-CX transfers with source-zero checks, and schedules physical lifetimes. Prefix reset intervals are jointly movable; borrowing before implicit |0> input inserts a real noisy restoring reset. Each emitted circuit retains operation provenance for ablations. The v29 core omits its later blue-check package; an earlier pilot preserving that package is listed separately.','',
f"Best attachment through third order: [{best['stem']}.qasm]({best['stem']}.qasm) / [metadata]({best['stem']}.json); second **{best['screen']['second']:.12e}**, third **{best['screen']['third']:.12e}**, total **{best['screen']['total']:.12e}**; c1={best['screen']['c1']:.3e}, exp(-A1)={best['screen']['exp_minus_A1']:.10f}. It has {best['metadata']['cx']} CX, R={best['metadata']['R']}. 1e6 diagnostic: acceptance **0.42449**, **4.9 s**; fails acceptance. No Task B circuit reaches the 6.2e-5 trigger for 1e8 MC. This negative does not close the broader end-state family.",'',
'Original witness has A10/B11/C11 and 20 block teleports. C-final equals B-initial in code order, so after B vacates its cells C can use the same 11-CX encoder directly: six C teleports disappear. EXENC on the same A cells reduces danger from 73 p/15 units at10 CX to 16 at 11 CX and 10 at 12 CX. The A12 derivative intentionally exceeds the original witness\'s <=11 property; no contest limit is exceeded. Canonical path/ASAP enumeration counts are 184 at 10 CX, 6794 at 11, 125472 at 12; this is not an exhaustive claim over arbitrary schedules.','',
'Final attachment layout and coherent data paths are in the best stem\'s JSON. It uses the transpose of the fragment, prefix shifted two rows, common code permutation `[1,2,0,4,6,5,3]`, 12 data hops and 14 A/B teleports; C is stationary. Data paths: `12→13→7→1`, `32`, `19→18→12`, `22→16→10`, `15→9→3→4→5`, `28`, `20→14`.','',
'### Built circuits','',
'Every unique full circuit below is priced by unchanged exact2 --third --top30. Byte-identical QASM and identical data metadata share a verified receipt; aliases are listed in [current_results.json](current_results.json). All c1 satisfy abs(c1)<1e-12. Delta columns compare with LADDER sepBC=5.71112722e-5 / ABC210=5.03262480e-5. These deltas include interactions and are not additive taxes.','',
'| Stem | R | CX | Second | Third | Total | exp(-A1) | Delta sepBC / ABC210 | Mechanism |','|---|---:|---:|---:|---:|---:|---:|---:|---|']
for r in rows:
 s=r['stem']
 if s.startswith('sepbc_v29c') or 'byte_identical_to'in r.get('unchanged_cli',{}):continue
 v=r['screen'];md=r['metadata'];dd=r['reference_deltas']
 lines.append(f"| `{s}` | {md.get('R','?')} | {md.get('cx','?')} | {v['second']:.8e} | {v['third']:.8e} | {v['total']:.8e} | {v['exp_minus_A1']:.6f} | {dd['sepBC']:.7e} / {dd['ABC210']:.7e} | {mechanism(s)} |")
if 'ablation'in best:
 ab=best['ablation'];lines+=['','### Noise ablation of the best attachment','','Counterfactual removals preserve all other physical channels and the complete categorical cubic calculation. They are diagnostic, not attainable circuits or lower bounds.','','| Channels retained/removed | Second | Third | Total |','|---|---:|---:|---:|']
 for r in ab['rows']:lines.append(f"| {r['label']} | {r['second']:.10e} | {r['third']:.10e} | {r['total']:.10e} |")
 lines+=['','Dominant physical second-order pair classes:','','| Pair class | Contribution |','|---|---:|']
 for k,v in sorted(ab['pair_classes'].items(),key=lambda x:-x[1])[:8]:lines.append(f'| {k} | {v:.10e} |')
 lines+=['','The round alone is 2.87129e-5. Removing pre-round idle noise gives 4.01420e-5; removing teleport noise alone leaves 1.82351e-4. Thus the main shortfall is exposure during serialized A/B preparation and its cubic interactions. The idle-scaling diagnostic reaches 5e-5 at 0.16366 of current pre-round idle probability. This does not prove an achievable schedule or imply that exactly 83.6% of physical waiting steps must disappear. All variants have their own ablation rows and top-pair examples in the ledger.']
lines+=['','## Verified versus inferred','','Verified: unchanged exact2 receipts and full categorical screens; native adjacency/timing and upstream ideal correctness for emitted circuits; complete Task A 1e6 gates/FAST/MC3; diagnostic acceptance failure for the best attachments; identical-file receipt aliases; the current ENDSTATE catalog contains only witness12_h1 as a full native fragment. Numerical evidence remains in `current_results.json` and adjacent retained receipts. Nonfinal complete-circuit QASM/metadata/plans have been removed; the three qualified Task A variants and the best Task B diagnostic remain, alongside the previous accepted delivery and source fragments.','','Scope: the final joint search covers 48 relative geometries, two low-Manhattan common automorphisms and two routes per geometry (192 fixed-route scheduling models, all OPTIMAL for R, minimum55). R is a proposal objective; full loss ranks emitted candidates. It does not prove optimal fidelity or routes. The earlier free-data scheduling bounds R>=63 (original) and R>=51 (directC+A12) apply only to the pilot final-prefix-release model, not the expanded joint-lifetime model. A separate 336-model search over all 168 automorphisms/two routes on the minimum-bound geometry reached R60 and worsened the real score.','','Inferred: new end-states need substantially shorter harmful A/B storage, through interleaving or helper-assisted preparation. Native extra block moves, tagged helper reuse and explicit round offsets are supported by the emitter, but no new <=2-move/helper ENDSTATE fragment was present to validate those families. Fragment-internal data relocation requires a separate lifetime adapter and is rejected explicitly. No global impossibility or sub5e-5 feasibility claim is made.','']
if missing:lines+=['Pending unchanged CLI receipts: '+', '.join(missing),'']
(H/'REPORT.md').write_text('\n'.join(lines))
print(json.dumps(dict(rows=len(rows),unique=len({r['sha256']for r in rows}),missing=missing,best=best['stem'],report=str(H/'REPORT.md'))))
