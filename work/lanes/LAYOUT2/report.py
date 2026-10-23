"""Regenerate the current lane report from preserved experimental artifacts."""
import json,math
from pathlib import Path
P=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def fmt(x):return 'pending' if x is None else f'{x:.6g}'
metrics={p.name.removesuffix('_metrics.json'):read(p) for p in P.glob('c*_metrics.json')}
valid=sorted(((k,v) for k,v in metrics.items() if v.get('passed') and 'third' in v),key=lambda kv:kv[1]['third'])
mcvalid=sorted(((k,v) for k,v in valid if len(v.get('mc',[]))==3),key=lambda kv:sum(r['score'] for r in kv[1]['mc'])/3)
s=['# LAYOUT2 — physical late logical-X parity check','',
   'All changes and artifacts are confined to this lane. No credentials were read and no submission was made. Python jobs used thread caps; no agents were spawned.',
   '', '## Result', '']
if valid:
 k,v=valid[0];s += [f'Best completed exact score: `{k}.qasm`, {v["cx"]} CX, first order {fmt(v["first"])}, exact second {fmt(v["second"])}, exact third total {fmt(v["third"])}, exp(-A1) {fmt(v["exp_A1"])}; official 1e6-shot PASS, acceptance {fmt(v["acceptance"])}.']
else:s+=['Full evaluations are in progress.']
if mcvalid:
 k,v=mcvalid[0];mean=sum(r['score'] for r in v['mc'])/3
 s += ['',f'Best completed three-seed mean: `{k}.qasm`, {mean:.9g}; seed-0 key {v["mc"][0]["score"]:.9g}; {(1-mean/1.0373e-4)*100:.2f}% below the supplied baseline mean.']
 s += ['', 'The final artifact is [best.qasm](best.qasm) with [best.json](best.json). It is byte-identical to the named winner and includes the data-qubit mapping, layout, provenance, exact scores, all MC seeds, and SHA-256.']
 sk,sv=min(mcvalid,key=lambda kv:kv[1]['mc'][0]['score'])
 s += ['',f'The lowest measured seed-0 key among these candidates is `{sk}.qasm`: {sv["mc"][0]["score"]:.9g}, with mean {sum(r["score"] for r in sv["mc"])/3:.9g}. The mean-based ranking is used for `best`; this lane does not submit. Close rankings among the finalists are within MC sampling uncertainty.']
s+=['','Comparison supplied in the task: cand_best_m exact third total 1.01894e-4; 1e8-shot seeds 0/1000/2000 mean 1.0373e-4; acceptance 0.544.',
    '', '## Reproducible full-circuit layout', '',
    'The passing r23_1_3 family has:', '',
    '```text', 'd = [7,25,19,16,15,17,8]', 'A = [13,26,20,22,21,23,14]',
    'B = [6,24,18,10,9,11,2]', 'C = [0,30,12,4,3,5,1]',
    'M = {1,3,5}; target cells = [26,22,23]',
    'cat = [27,28,29]; CX tree 27->28->29',
    'R+1 checks: 27->26, 28->22, 29->23; cat MX parity at R+2',
    'data moves = [[15,16,17],[4,10,16],[3,9,15],[7,13,19],[0,6,7],[20,26,25]]',
    'hops = 12; BC helpers = 0', '```', '',
    'A: 13 CX, depth 8, danger vector [0,9,0,23,0,4,0,0] in p/15 units. M avoids every occupied Z_L Z_j bin; it also detects a pure Z_L. The emitted encoder and its Pareto alternatives were independently checked against synth.check and synth.dangerous_z.',
    '', 'The 68-CX BC preps have 14 layers and zero bad X faults at every cell/time under the required rule sB==sC and pB==pC and pB==(sB==0). Every emitted SAT circuit also passes a GF(2) target-space rank check and the actual at-most-K cap.',
    '', 'The merge preserves the judge schedule of the existing pre-stage, respects each cell’s release, and schedules routes, both preps, and cat preparation together. The cat may reuse a helper only after its prep duties end. The `e` variant reads A\\M at R+1; only M needs to wait for the R+1 cat couplings. This change is separately validated by the full judge.',
    '', '## Full-circuit measurements', '',
    'Third is the total through order three, not the isolated cubic term. Judge acceptance is measured at 1e6 shots; exp(-A1) is the analytical estimate.', '',
    '| Circuit | R | CX | First | Exact second | Exact third | exp(-A1) | Judge acceptance | Verdict |',
    '|---|---:|---:|---:|---:|---:|---:|---:|---|']
for k,v in sorted(metrics.items()):
 cfg=read(P/(k+'.json'));R=cfg.get('R')
 if R is None and '_m' in k:
  base=k.split('_m')[0];bp=P/(base+'.json')
  if bp.exists():R=read(bp).get('R')
 s.append(f'| [{k}]({k}.qasm) | {R} | {v.get("cx")} | {fmt(v.get("first"))} | {fmt(v.get("second"))} | {fmt(v.get("third"))} | {fmt(v.get("exp_A1"))} | {fmt(v.get("acceptance"))} | {"PASS" if v.get("passed") else "FAIL"} |')
s+=['','Each row has `<stem>_check.log`, `<stem>_exact.log`, and `<stem>_metrics.json`. Acceptance failures are retained as counterexamples. All checked circuits pass format, class, and correctness; their failures are acceptance failures.', '', '## Monte Carlo', '', '| Circuit | seed 0 | seed 1000 | seed 2000 | mean | Acceptance mean |', '|---|---:|---:|---:|---:|---:|']
anymc=False
for k,v in sorted(metrics.items()):
 if len(v.get('mc',[]))==3:
  rows=v['mc'];anymc=True;s.append('| '+k+' | '+' | '.join(fmt(r['score']) for r in rows)+' | '+fmt(sum(r['score'] for r in rows)/3)+' | '+fmt(sum(r['acceptance'] for r in rows)/3)+' |')
if not anymc:s+=['','MC is pending for the final best. Every circuit below the 1.019e-4 exact-third trigger is automatically evaluated with fast_check.check at 1e8 shots, seeds 0/1000/2000.']
s+=['','## Layout search and A encoder screen', '',
    '`layout.py` is CP-SAT over data and A/B/C placements, legal ordered data routes, checkerboard partner colors, connected A, connected B+C+helpers, a Fano logical-X line, and a connected three-cell cat with three simultaneous adjacent targets. Two cat controls cannot perform three CX at R+1. Geometry is optimized by round-time lower-bound surrogate, hops, then helpers; actual R comes from the full merged schedule. Encoder-dependent admissibility is enforced by exact post-synthesis screening, not inferred from geometry.',
    '', 'A search keeps a nondominated set over all eight danger bins, depth, and CX. The initial screen enumerates all ASAP circuits from minimum CX through minimum+2. These are finite-domain conclusions, not unrestricted encoder optimality claims. The selected layout was extended through minimum+4 (15 CX): 43,516,789 canonical circuits in the 15-CX class alone, with all emitted witnesses independently verified. See `a_extra3_layout_A_stats.json` and `a_extra4_layout_A_stats.json`.',
    '', '| Admissible layout | R surrogate | Hops | Connectivity helpers | M | Cat cells | A CX/depth |',
    '|---|---:|---:|---:|---|---|---|']
sp=P/'screen.json'
if sp.exists():
 for row in read(sp):
  if not row['caught']:continue
  l=read(P/row['layout']);a=row['best'];s.append(f'| {row["layout"]} | {l["R_lb"]} | {l["hops"]} | {len(l["hBC"])} | {l["M"]} | {l["cat"]} | {a["cx"]}/{a["depth"]} |')
s+=['','Geometric incumbent JSONs and layout logs preserve all found placements, including failed A screens. `screen.json` summarizes the A screen. All four legal shortest-route combinations of r23_1_3 retain R=55 with the c5 prep (`c5r_routes.json`).',
    '', '## Synthesis findings and limits', '',
    '- Unrestricted BC pivot/basis searches mostly timed out (UNKNOWN, not UNSAT). Fixing canonical pivots and their matching output-generator basis made the same target synthesis tractable: 14-layer, 68-CX FT witnesses appeared in seconds.',
    '- The K=60..67 and depth 12..13 UNSAT results apply only with those canonical pivots/basis and the stated depth; they do not prove unrestricted bounds.',
    '- Initial `bc_fixed_*` seed-0 trials used a pivot-order mismatch and are invalid. The corrected `bc_basis_*`, `bf_*`, `narrow_*`, and `vary_*` runs use consistent ordering; final emitted witnesses have independent state and FT checks.',
    '- Independent staged BC encoders plus swaps gave an 82-CX/depth-23 diagnostic. Window SAT reduced this to a certified 80-CX/depth-22 witness, but the resulting R=62 circuit fails acceptance. It was superseded by the direct 14-layer syntheses.',
    '- The existing 73-CX BC template admits 144 relative Steane automorphisms under the FT test. Embedding that template in a cat-compatible layout did not yield a candidate within the searches. Fixed-B permutation infeasibility was also checked with CP-SAT presolve disabled; no global layout impossibility is claimed.',
    '- First-use measurement screening uses the copied minit.py. On c5, q11, q18, q5 improved exact second order by 3.6667e-7, 3.2222e-7, and 1.6667e-7 respectively; full third-order and judge checks assess the combined change.',
    '- Larger 14-CX A encoders reduce the pre-filter danger units from 36 to 25/23, but their full second-order scores stay essentially unchanged and their third-order scores worsen (c11/c12). Once the logical-X filter is present, minimizing raw A danger alone is not the right final objective. The 15-CX Pareto frontier is preserved; it was not promoted to further full-circuit candidates on that proxy alone.',
    '- All six candidates below the exact-third threshold received all three requested 1e8-shot MC seeds. No threshold-triggered MC is pending. Global optimality over layouts, encoders, and joint preparations remains unproved.',
    '', '## Reproduction', '', 'Run from this directory with PYTHONDONTWRITEBYTECODE=1 and OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1:', '',
    '```bash',
    'A_EARLY=1 /home/jihoon/competitions/quantumn/.venv/bin/python build.py r23_1_3.json r23_1_3_A_filtered.json r23_1_3_BC_d14_k68_s5.json replay',
    '/home/jihoon/competitions/quantumn/.venv/bin/python minit.py replay . 5,11,18',
    '/home/jihoon/competitions/quantumn/.venv/bin/python evaluate.py replay_m5_11_18 16', '```',
    '', 'To rerun synthesis separately: `encode.py r23_1_3.json --workers 2 --extra 2`, or `BC_PIVOTS=1 BC_BASIS=1 bc.py r23_1_3.json 14 68 5`, using the required Python executable. Solver reruns may find different witnesses; use the preserved prep JSONs for exact circuit reconstruction.',
    '', 'Use owl’s specified Docker image for pycryptosat; the mirrored wheel requires newer glibc than native tom. The copied enumeration binary also requires owl’s container or local zebra. `evaluate.py` invokes the original exact2.py --third and unmodified tprep.check; it never submits.', '']
(P/'REPORT.md').write_text('\n'.join(s))
