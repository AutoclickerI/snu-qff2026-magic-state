"""Consolidate required evidence; no pending field is represented as a pass."""
from pathlib import Path
import json,re,hashlib,sys,collections
V=Path(__file__).resolve().parent;H=V.parent;BASE=5.8937742042181006e-5
J=lambda p:json.loads(p.read_text())
rows=[]
for f in sorted(V.glob('*.screen.json')):
 s=f.name.removesuffix('.screen.json');md=J(V/(s+'.json'));r=dict(stem=s,screen=J(f),metadata=md)
 for ext,key in [('.build.json','build'),('.exact.json','exact'),('.allorders.json','allorders'),('.ablation.json','ablation'),('.speed_prediction.json','speed'),('.detorder.validation.json','detorder')]:
  p=V/(s+ext)
  if p.exists():r[key]=J(p)
 for ext,key in [('.judge.log','judge'),('.mc.log','mc'),('.exact.log','exact_log')]:
  p=V/(s+ext)
  if p.exists():r[key]=p.read_text()
 if 'exact_log'in r:
  t=re.search(r'1-F \(to 3rd order\) = ([\deE+.-]+)',r['exact_log']);r['exact_complete']=bool(t)
  if t:assert abs(float(t[1])-r['screen']['total'])<=1e-10,(s,t[1],r['screen']['total'])
 if 'ablation'in r:
  ab=next(x for x in r['ablation']['rows']if x['label']=='all');assert abs(ab['total']-r['screen']['total'])<1e-13
 if 'mc'in r:
  m=re.search(r' mean ([\deE+.-]+)',r['mc']);r['mc_mean']=float(m[1])if m else None
  r['mc_seeds']=[dict(seed=int(a),loss=float(b),acceptance=float(c))for a,b,c in re.findall(r' (0|1000|2000) ([\deE+.-]+) ± [\deE+.-]+ acc ([\d.]+)',r['mc'])]
 p=V/(s+'.qasm');assert hashlib.sha256(p.read_bytes()).hexdigest()==r['screen']['sha256']
 rows.append(r)
archive=V/'results.json'
if archive.exists():
 present={r['stem']for r in rows};rows.extend(r for r in J(archive)['rows']if r['stem']not in present);rows.sort(key=lambda r:r['stem'])
pending=[]
for r in rows:
 missing=[]
 if not r.get('exact_complete'):missing.append('unchanged exact2')
 if 'allorders'not in r:missing.append('all orders')
 if 'ablation'not in r:missing.append('loss split')
 if 'judge'not in r:missing.append('judge')
 if 'speed'not in r:missing.append('speed')
 if r.get('allorders',{}).get('loss',1)<BASE and r.get('mc_mean')is None:missing.append('MC3')
 if missing:pending.append(dict(stem=r['stem'],missing=missing))
(V/'results.json').write_text(json.dumps(dict(rows=rows,pending=pending),indent=2))
if '--complete'in sys.argv:assert not pending,pending
ranked=sorted([r for r in rows if 'allorders'in r],key=lambda r:r['allorders']['loss']);best=ranked[0]if ranked else min(rows,key=lambda r:r['screen']['total'])
s=best['screen'];name=best['stem'];ao=best.get('allorders',{});mc=best.get('mc_mean');status='COMPLETE'if not pending else 'RUNNING'
lines=[f'Status: {status} — v30f critical-tail redesign; original R48 shortened to R45.','',
'Previous accepted deliveries: [REPORT_v29c.md](REPORT_v29c.md), [REPORT_v28s.md](REPORT_v28s.md). No submissions, commits, pushes, credential access, or other-lane writes.','',
'## Result','',
f"Best currently ranked circuit: [v30/{name}.qasm](v30/{name}.qasm) / [metadata](v30/{name}.json). R={best['metadata']['R']}, {best['metadata']['cx']} CX, depth={best['metadata']['native_depth']}; exact parts {s['second']:.12e} + {s['third']:.12e} = **{s['total']:.12e}**; c1={s['c1']:.3e}; exp(-A1)={s['exp_minus_A1']:.10f}.",'',
(f"All orders **{ao['loss']:.12e}**, acceptance **{ao['acceptance']:.10f}**, **{100*(BASE-ao['loss'])/BASE:.4f}%** below v30f's inherited all-orders {BASE:.12e}."if ao else 'All-orders result pending.'),
(f"MC3 mean **{mc:.9e}**; individual seeds: "+'; '.join(f"{r['seed']}: {r['loss']:.9e} (acceptance {r['acceptance']:.5f})"for r in best['mc_seeds'])+'.'if mc else 'MC3 pending.'),
'Judge: '+best.get('judge','pending').strip().splitlines()[-1],
'Speed: '+(f"{best['speed']['classification']}, XTIM prediction {best['speed']['median_seconds_per_1e6']:.3f} s/1e6."if 'speed'in best else 'pending'),'',
'The grid remains data `[0,20,7,10,3,22,21]`, A `[1,14,8,9,2,16,15]`, B `[6,26,13,11,4,23,27]`, C `[12,25,19,17,5,29,28]`. The original data-transfer paths and fused q4/q10 boundary remain. The winning tail variant retains every native operation and detector; timing and commuting order change. The sensitivity variant preserves that R45 order and uses existing timing slack. Initialization times and resource operations in the delivered metadata are rebuilt from the actual native plan; inherited R48 timing fields are replaced.','',
'The bare-tail MC mean5.579558e-5 is slightly below the sensitivity mean5.584138e-5; that difference is far below sampling resolution. Applicable all-orders loss ranks the sensitivity circuit first.','',
'## What actually forces R48','',
'Full operation/edge/slack evidence: [v30/CRITICAL_PATH.md](v30/CRITICAL_PATH.md), [original DAG](v30/critical.json), and [R45 witness DAG](v30/commute_tail.critical.json). Original fixed native order has a zero-slack chain through the blue-check tail, the q8→q9→q15→q21 data transfer, MZ15 at40, RX15 at41, and A encoder gates42–47. The round starts48. The resource is not the binding component.','',
'| Original chain | Earliest ready | Slack to R48 |','|---|---:|---:|','| B/C resource, including actual prefix releases | 36 | 12 |','| A preparation | 48 | 0 |','| Tail coherent transfers/source checks | 41 | 7 |','| Prefix/blue-check operations outside classified transfers | 36 | 12 |','| Terminal T† gates alone | 28 | 20 |','',
'These component slack numbers share dependencies and are not independently shiftable. The critical source-zero measurement/reset before A15 belongs to the transfer/A boundary. Every cell release, native ES/LS and operation slack is tabulated in CRITICAL_PATH.md. Final-round offsets remain D→A/B→C atR, B→D/readout processing atR+1, final readouts atR+2. Readout offsets set total depthR+3 but do not force the original R48 start.','',
'Legal CX reordering moves CX2→8 before CX2→3 in the blue tail, pipelines forward data propagation before coherent source uncomputation, and reorders A\'s commuting target-8 gates. The resulting actual schedule reaches MZ15 at38, RX15 at39, A gates40–44, and R45. CP-SAT proves R45 optimal for the modeled fixed gate/reset/measurement program even when all CX/CX and valid diagonal-phase/CX-control commutations are allowed. This is not a global architecture bound.','',
'The R48→45 gain in the bare tail variant splits into4.94880e-7 at second order and2.25882e-6 at third order; all-orders gain is2.96245e-6. Its actual gain per removed round step differs from the grid-free sweep because the circuit has different gate/noise structure and the schedule reorders interacting operations.','',
'## Built variants','',
'All losses are conditional 1−F at STANDARD p=1e-3. The screen is a full categorical cubic contraction using unchanged EVAL\'s model; independent CLI receipts are required separately. All-orders uses the unmodified MAIN/sparse arithmetic (72 canonical), copied locally so outputs stay in SEPBC. MAIN added independent per-key parallel dispatch during this run; all mathematical kernel functions are AST-identical, and the winner is replayed against the current implementation row for row. The software hashes and dispatch diff are retained. Barriers cover every used qubit; no FRAME/POSTSELECT lines. The 64-detector COMP29 composition uses its proven invertible detector-row rewrite only for the unchanged exact2 reference, with complete gate/noise/decoder equivalence checks.','',
'| Stem | R | CX | Second | Third | All orders | Proxy | 1e6 gate | FAST | MC3 mean |','|---|---:|---:|---:|---:|---:|---:|---|---|---:|']
for r in sorted(rows,key=lambda r:r.get('allorders',{}).get('loss',r['screen']['total'])):
 z=r['screen'];a=r.get('allorders');gate='PASS'if 'passed=True'in r.get('judge','')else('FAIL'if'passed=False'in r.get('judge','')else'pending');speed=r.get('speed',{}).get('classification','pending');mc=r.get('mc_mean')
 lines.append(f"| `{r['stem']}` | {r['metadata']['R']} | {r['metadata']['cx']} | {z['second']:.9e} | {z['third']:.9e} | {format(a['loss'],'.10e')if a else 'pending'} | {z['exp_minus_A1']:.7f} | {gate} | {speed} | {format(mc,'.7e')if mc else ('not triggered'if a and a['loss']>=BASE else 'pending')} |")
lines+=['','Mechanisms: `commute_tail` is the constructive R48→45 improvement. Moving commuting choices into the earlier prefix (`commute_mid`, `commute_all`, phase variants) gives no further R gain and changes harmful pair/triple exposure. Removing A initialization checks (`release_drop9`, `release_drop129`) does not shorten R; it exposes preparation faults. The imported q15 instrument also does not shorten R. EXENC\'s five-layer A encoder remains R45 after real cell releases and increases its dangerous-Z tally from10 to25 units of p/15; its full circuit loses. Retiming COMP29\'s composition toR45 does not preserve all of its original local gains; full scoring determines the result. `sensitivity_tail` spends existing R45 timing slack using the exact pair/triple derivative and reprices all channels.','',
'## Loss split','',
'Noise-removal rows are counterfactual diagnostics; differences interact and cannot be added as independent taxes. A preparation includes its source-zero initialization checks, B/C preparation includes its native resource checks, and idle noise is classified by whether its interval ends beforeR. The complete provenance is in each retained plan and the consolidated numerical ledger.','',
'| Circuit / diagnostic | Full cubic | No pre-round idle | No A noise | No B/C noise | Only round noise |','|---|---:|---:|---:|---:|---:|']
base=V/'baseline.ablation.json'
abl=[('v30f (unchanged input)',J(base))]if base.exists()else[]
abl += [(r['stem'],r['ablation'])for r in rows if 'ablation'in r]
for nm,a in abl:
 zz={r['label']:r['total']for r in a['rows']};lines.append('| '+nm+' | '+' | '.join(f'{zz[k]:.9e}'for k in ['all','no_pre_round_idle','no_A_noise','no_resource_noise','only_round_noise'])+' |')
if 'ablation'in best:
 lines+=['','Largest physical second-order pair classes in the selected circuit:','','| Pair class | Contribution |','|---|---:|']
 for k,v in sorted(best['ablation']['pair_classes'].items(),key=lambda x:-x[1])[:8]:lines.append(f'| {k} | {v:.10e} |')
lines+=['','## Verified versus inferred','','Verified: original dependency/slack certificate; legal nearest-neighbour R45 schedules; upstream noiseless correctness and abs(c1)<1e-12 for all emitted variants; actual 1e6 judge and XTIM speed receipts; unchanged exact2 and sparse all-orders results when marked complete; all improved all-orders candidates receive MC3. Source SHA, full numerical receipts and failures remain in [v30/results.json](v30/results.json). Nonfinal complete-circuit artifacts are archived in v30/nonfinal_plans.json.gz and removed as loose files; the bare R45 and sensitivity finalists remain. Initialization metadata is derived from the final native operations. One COMP29 preparation-reset attribution was corrected and its ablation rerun; gate/noise physics and scores did not change. No job is left running at final delivery.','','Inference and scope: a shallower B/C resource, including helper-assisted preparation or pipelined B→h→C verification, cannot remove this particular A/data release chain by itself. The eight spare cells are not direct neighbours of the binding A15/9 inputs. Dirty-bus UVUV is a valid identity but needs a new binding interaction/placement to help here; no new helper resource is claimed as built or ruled out. Going belowR45 needs a different measured boundary/data route/A synthesis or prefix program, beyond the proven fixed-operation commutation model. Those broader families remain open.','']
if pending:lines+=['Pending required evidence: '+json.dumps(pending),'']
(H/'REPORT.md').write_text('\n'.join(lines));print(json.dumps(dict(circuits=len(rows),pending=pending,best=name)))
