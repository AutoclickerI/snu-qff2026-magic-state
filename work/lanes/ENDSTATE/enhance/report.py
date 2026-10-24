from pathlib import Path
import json,re,sys,shutil
H=Path(__file__).resolve().parent;P=H.parent;BAR=4.66293348171918e-5;FLOOR=.5005
J=lambda p:json.loads(p.read_text())
def read(name,suffix):
 f=H/(name+suffix);return J(f)if f.exists()else{}
def mc(name):
 f=H/(name+'.mc3.log')
 if not f.exists():return {}
 text=f.read_text();seeds={int(s):dict(loss=float(v),sem=float(e),acceptance=float(a))for s,v,e,a in re.findall(r' (0|1000|2000) ([\deE.+-]+) ± ([\deE.+-]+) acc ([\deE.+-]+)',text)};means=re.findall(r' mean ([\deE.+-]+)',text);exit=read(name,'.mc3.exit.json')
 return dict(seeds=seeds,mean=float(means[-1])if means and len(seeds)==3 and exit.get('exit_code')==0 else None)
rows=[]
for f in H.glob('*.price.json'):
 r=J(f)
 if not r.get('ok'):continue
 name=r['stem'];m=read(name,'.json');sp=read(name,'.speed.json');ch=read(name,'.check.json');mcr=mc(name);gated=sp.get('classification')=='FAST'and ch.get('passed')and mcr.get('mean')is not None and r['acceptance']>=FLOOR
 rows.append(dict(name=name,loss=r['loss'],acceptance=r['acceptance'],meta=m,speed=sp,check=ch,mc=mcr,gated=bool(gated)))
rows.sort(key=lambda r:r['loss']);valid=[r for r in rows if r['acceptance']>=FLOOR];gated=[r for r in valid if r['gated']];wins=[r for r in gated if r['loss']<BAR];best=gated[0]if gated else None
status='COMPLETE within the reported finite models; no lane jobs remain.'if '--complete'in sys.argv else'RUNNING: full-circuit refinement and validation are active.'
L=['# ENDSTATE — acceptance-budget optimization','',f'**Status: {status}**','']
if wins:
 L+=['**Finalists beating v34m (all gates complete):**','']
 for r in wins:L.append(f"- [{r['name']}]({H.name}/{r['name']}.qasm): all-orders **{r['loss']:.12g}**, acceptance **{r['acceptance']:.9f}**, MC3 **{r['mc']['mean']:.9g}**, FAST **{r['speed']['median_seconds_per_1e6']:.2f}s/1e6**, judge PASS.")
else:L+=['**No fully gated ENDSTATE finalist beats v34m’s4.66293348171918e-5.**','']
if best:
 L += [f"Best fully gated ENDSTATE result: [{best['name']}](enhance/{best['name']}.qasm), all-orders **{best['loss']:.12g}**, acceptance **{best['acceptance']:.9f}**, MC3 mean **{best['mc']['mean']:.9g}**, FAST **{best['speed']['median_seconds_per_1e6']:.2f}s/1e6**. Canonical lane copy: [BEST_ENDSTATE.qasm](BEST_ENDSTATE.qasm), [metadata](BEST_ENDSTATE.json).",'']
 shutil.copyfile(H/(best['name']+'.qasm'),P/'BEST_ENDSTATE.qasm');meta=dict(best['meta'],source_stem=best['name'],allorders_loss=best['loss'],allorders_acceptance=best['acceptance'],MC3=best['mc'],speed=best['speed'],judge=best['check']);(P/'BEST_ENDSTATE.json').write_text(json.dumps(meta,indent=2))
if valid:L += [f"Lowest acceptance-valid analytic candidate currently priced: [{valid[0]['name']}](enhance/{valid[0]['name']}.qasm), **{valid[0]['loss']:.12g}**, acceptance **{valid[0]['acceptance']:.9f}**. Gating status is shown below; an analytic screen alone is not a promotion.",'']
L += ['## Controls and corrected geometry','',
'Unchanged all-orders controls reproduce MAIN/v34m **4.6629334817191845e-5**, acceptance **0.5012004436526478**, and R38 **5.613750017530951e-5**, acceptance **0.5941345160159276**. Required floor is **0.5005**; actual R38 headroom is0.09363. The R38 base previously passed the judge/FAST and MC3 mean5.601091e-5.','',
'The actual R38 A label order is **[14,20,13,21,9,27,15]**, with D=[8,26,19,22,10,28,16]. The A cells in the retarget prompt belong to row89. All new R38 builds use the actual R38 metadata. The geometry/preparation catalog and separate-block closure remain in [REPORT_joint_geometry.md](REPORT_joint_geometry.md) and [REPORT_separate.md](REPORT_separate.md).','',
'## A partial decoder: model and results','',
'Native logical-X triples are labels{0,1,2} (cells14,20,13) and{1,3,5} (cells20,21,27). Back-propagating an X readout through each candidate CX decoder verifies its membership in the A X-stabilizer group; X on a transversal-CX target commutes with D→A. All original Z-syndrome detector rows are conjugated, never discarded. A terminal X flag is then added.','',
'The <=3-CX catalog has118 distinct ideal linear-map/readout-root representatives;57 meet the selected <=1-extra-terminal-step fixed-wire timing model. Distinct noisy decompositions of the same ideal map are not exhaustively covered. Both logical-X and stabilizer-X flags are tested. All scheduled base decoder candidates pass noiseless verification.','',
'Three scheduling policies were priced: original round times (`a_dec_*`), B→D/B readout at the final layers (`a_late_*`), and both syndrome couplings as late as decoder dependencies permit (`a_ports_*`). None improves R38. The additional unchecked data time outweighs the flag gain in these models. This is not a universal impossibility theorem for joint preparation/decoder synthesis.','',
'Removing coherent-hop zero-source guard measurements feeding A zero inputs was separately tested (27;15+27;14+15+27). The complete original correctness checks remain; the entire measurement/intervention is removed, not merely an inconvenient detector.21 base/decoder variants were verified and priced, with no winning decoder. Two decoder bundles additionally protect the early data ports by fresh/deferred-readout X guards; best6.42867e-5, also worse than R38.','',
'## Guards, initializations and nonlinear knapsack','',
'Actions include fresh echoed X/Z checks in idle slots, echoes spanning only commuting data gates, reuse of measured helpers with record parity, known-zero checks, and measured-Z replacements for resets. Helpers are reserved by actual lifetimes. Every emitted candidate is adjacency/nonoverlap checked, then verified by the unchanged noiseless judge before any noisy price. Invalid candidates retain explicit failure receipts.','',
'The initial151-action catalog has72 positive measured marginals. Linear knapsack proposals use measured gain and log-acceptance cost with physical compatibility constraints. Whole-circuit repricing is mandatory: denser packages can worsen loss or fail acceptance. The best initial package was5.100818050478785e-5 at acceptance0.5261592629298845; its first nonlinear refinement gave5.050853252303778e-5 at0.5369310010890898.','',
'**Proposal metadata bug fixed:** some prefix `qs` arrays were unordered occupancy pairs, not CX directions. The proposer now parses control/target from the literal QASM CX line. All22 noncommuting windows proposed by the old direction logic were caught by the unchanged noiseless gate and were not priced. Valid QASM and its measured prices were unchanged. The corrected union catalog contains200 actions,125 byte-identical verified cache hits and75 new prices;131 have positive single-action gain. Cache reuse requires identical QASM bytes, identical data-label order and a successful noiseless receipt.','',
'Corrected knapsack packages reached4.985991832508814e-5 at acceptance0.5141424130038148. Full-circuit removal/replacement refinement uses single removals, single insertions replacing at most two conflicting actions, and group removals. The finite catalogs and neighborhood scopes are saved; no global optimum over arbitrary checks is claimed.','',
'R37, selectively transported-T R37, and R39 ports were repriced rather than assuming transferred gains. An invalid R37-selective echo spanned the actual CX14→13 at step24; this was the direction bug above. Its entire intervention was reverted and the original operation restored. Repaired ports pass noiseless checks. The first ported package family did not beat R38.','',
'## Ranked complete circuits and screens','',
'Ranking uses unchanged MAIN sparse72/canonical arithmetic. Full barriers cover all used qubits; no FRAME/POSTSELECT directives are introduced. Independent noise-model snapshots and exact source hashes are retained. All acceptance and loss values below are measured calculations, not R/CX extrapolations.','',
'| Circuit | All-orders loss | Acceptance | CX | Native depth / round range | FAST gate | Judge1e6 | MC3 mean |','|---|---:|---:|---:|---|---|---|---:|']
chosen=[]
for r in valid:
 if r['gated']or '_pack'in r['name']or r['name'].startswith('refine'):
  chosen.append(r)
 if len(chosen)>=18:break
for r in chosen:
 m=r['meta'];nat=m.get('actual_native',{});times=f"{nat.get('depth',m.get('native_depth','?'))} / {nat.get('round_range',m.get('round_start_range',m.get('R','?')))}";speed=r['speed'].get('classification','pending');judge='PASS'if r['check'].get('passed')else('FAIL'if r['check']else'pending');mean=r['mc'].get('mean');L.append(f"| [{r['name']}](enhance/{r['name']}.qasm) | {r['loss']:.12g} | {r['acceptance']:.9f} | {m.get('cx','?')} | {times} | {speed} | {judge} | {mean if mean is not None else 'pending'} |")
L += ['','[Complete priced catalog](enhance/catalog_priced.json) includes all successful candidates and their gate status; individual `.price.json` files include noiseless failures. Each QASM has metadata and an operation plan, including exact guard cells/times, preparation changes, decoder rows and provenance.','',
'## Verification, scope and retained diagnostics','',
'- Verified: positive controls; all promoted circuit geometry and ideal target/detector checks; actual all-orders prices and acceptance; physical native schedules where reported; FAST, judge1e6 and three-seed100M results only where completed. All original hard limits remain.','- Inferred/proposal-only: additive marginal knapsack gains/costs and explanatory fault mechanisms. Actual combined prices supersede them. No universal bound over all geometries, arbitrary helper schedules or different architectures is claimed.','- The old SLOW full-source-reuse diagnostic completed: seeds0/1000/2000 =6.923248e-5 /6.910766e-5 /6.988363e-5, mean6.940792e-5. Its analytic5.799916e-5 forecast disagrees; QASM/metadata hashes match across hosts. Cause remains unresolved. It fails FAST and is excluded from promotion. This is separate from the proposer-direction bug. FAST retained candidates have MC cross-checks.','- Computation stayed within this lane, with thread variables1; hippo allocation expanded only after00:20. No credentials, submissions, commits, pushes, messages to other lanes or agents were used.','']
(P/'REPORT.md').write_text('\n'.join(L));(H/'catalog_priced.json').write_text(json.dumps(rows,indent=1));print('priced',len(rows),'fully gated',len(gated),'wins',len(wins),'best',best['name']if best else None)
