import os,sys,json,hashlib,math
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent
names=['tp_v16','tp_v16_omove','tp_v16_reuse','tp_joint52','tp_joint52_m11_21_22','tp_joint52_alap']
base=H.parent/'R0/v16_bc2m.score.json'
b=json.loads(base.read_text());assert b['sha256']==hashlib.sha256((H.parents[1]/'candidates/v16_bc2m.qasm').read_bytes()).hexdigest()
(H/'baseline_receipt.json').write_text(json.dumps(b,indent=2)+'\n')
meta=json.loads((H/'tp_joint52.json').read_text());ms=json.loads((H/'tp_joint52_m11_21_22.json').read_text());ms={**meta,**ms,'measure_init':[11,21,22]};(H/'tp_joint52_m11_21_22.json').write_text(json.dumps(ms,indent=2)+'\n')
f=lambda x:'—' if x is None else f'{x:.9g}'
rows=[];geo=[];manifest=[]
for n in names:
 q=H/(n+'.qasm');d=json.loads(q.with_suffix('.json').read_text());s=json.loads((H/(n+'.score.json')).read_text());mc=json.loads((H/(n+'.mc.json')).read_text()) if (H/(n+'.mc.json')).exists() else s
 sha=hashlib.sha256(q.read_bytes()).hexdigest();assert sha==s['sha256']
 if mc.get('mc'):assert mc['sha256']==sha
 vals=mc.get('mc',[]);m={x['seed']:x for x in vals};eligible=abs(s['c1'])>=1e-12 or s.get('total',1)<8.6e-5
 assert not eligible or len(vals)==3,(n,'MC missing')
 rows.append('| '+ ' | '.join([f'[{n}]({n}.qasm)',f"{d['R']} / {d['Rmax']} / {d['last_step']-1}",str(d['cx']),f(s['c1']),f(s['second']),f(s.get('third')),f(s.get('total')),f(s['exp_A1']),f(m.get(0,{}).get('score')),f(m.get(1000,{}).get('score')),f(m.get(2000,{}).get('score')),f(mc.get('mean')),f(m.get(0,{}).get('acceptance')),f(s['acceptance_1e6']),'PASS' if s['judge_passed'] else 'FAIL acceptance',f'[{n}.json]({n}.json) · [receipt]({n}.score.json)'])+' |')
 geo.append('| '+ ' | '.join([n,str(d['O']),str(d['B']),str(d['C']),str(d['data_qubits']),str(d['moves'])])+' |')
 manifest.append(dict(candidate=n,sha256=sha,c1=s['c1'],exact_total=s.get('total'),mandatory_mc=eligible,mc_seeds=list(m),prefix=json.loads((H/(n+'.prefix.json')).read_text())))
solver_names=['bound40','best41','fast_bound40','fast41','joint52','joint52_alap','full52','full56table','full56first','full48relax','fixed60']
sol=[]
for n in solver_names:
 r=json.loads((H/(n+'.json')).read_text());sol.append(f"| [{n}]({n}.json) | {r.get('alap_status',r['status'])} | {f(r.get('alap_wall',r['wall']))} | {r.get('R','—')} | {r.get('Rmax','—')} | {r.get('last_cx','—')} | {r.get('moves','—')} |")
prices=json.loads((H/'tp_joint52.price.json').read_text()) if (H/'tp_joint52.price.json').exists() else []
price_rows='\n'.join(f"| {r['no_region']} | {f(r['second'])} | {f(r['third'])} | {f(r['total'])} | {f(r['exp_A1'])} |" for r in prices)
text=f'''# TP2 report

**No candidate met the required improvement. The success condition was not met.** No submission was made.

The smallest full circuit built has teleport couplings at **33–47**, last round CX **48**, and final measurement **49**. It passes format, class and correctness, but fails acceptance and is much noisier than v16. The smallest fully judge-valid new circuit starts at **50**. The best new candidate measured at 1e8 shots on all three seeds is `tp_v16_reuse`: mean **1.74393709220e-4**, seed-0 acceptance **0.50536187**, versus v16's **8.55379233064e-5** and **0.53313237**.

The relaxed CP-SAT routing minimum is **last CX 41**, with teleport couplings **33–40**, 17 two-CX transfers, and final measurement 42. Last CX <=40 is INFEASIBLE with presolve disabled, even with preparation connectivity and C omitted and immediate reuse of measured prefix cells allowed. This is a conditional bound for the model described below, not a general circuit impossibility result.

## Candidate measurements

All exact values use EVAL/exact2.py `--third`, and every c1 is below 1e-12. c1 is its contribution at p=0.001. Third means the incremental third-order term. `exp(-A1)` is an analytical **estimate**. R is **first teleport CX / last teleport CX / last round CX**, not a claim that the complete round ran at its first coupling. Every QASM has adjacent JSON listing the final physical cells of logical O in code order. All six candidates passed format/class/correctness at 1e6 shots. MC columns are 100,000,000 shots each; dashes mean not run. None had exact total <8.6e-5, so no mandatory MC is outstanding. Only measured MC means establish ranking.

| Candidate | R first / last / last CX | CX | c1 p | 2nd | 3rd increment | Exact total | exp(-A1), estimate | MC 0 | MC 1000 | MC 2000 | MC mean | Seed-0 acceptance, 1e8 | Acceptance, 1e6 | Judge, 1e6 | Files |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
{chr(10).join(rows)}
| [v16 reference](../../candidates/v16_bc2m.qasm) | 50 / 50 / 51 (star) | 207 | {f(b['c1'])} | {f(b['second'])} | {f(b['third'])} | {f(b['total'])} | {f(b['exp_A1'])} | {f(b['mc'][0]['score'])} | {f(b['mc'][1]['score'])} | {f(b['mc'][2]['score'])} | {f(b['mean'])} | {f(b['mc'][0]['acceptance'])} | {f(b['acceptance_1e6'])} | PASS | [cached same-text receipt](baseline_receipt.json) |

The baseline numbers are R0's completed same-seed run, reused after verifying its QASM SHA-256 matches `work/candidates/v16_bc2m.qasm`; TP2 did not claim a second independent baseline run. Reuse's full MC receipt is [tp_v16_reuse.mc.json](tp_v16_reuse.mc.json).

## Geometry and construction

O/B/C columns give cells at preparation completion. `Output O` gives cells after all transfers, and equals the JSON `data_qubits`. A move is one two-CX transfer; v16-derived rows include its six data moves plus seven additional transfers. The joint family leaves the original data unmoved and transfers O/B 34 times.

| Candidate | O prep cells | B prep cells | C prep cells | Output O | Moves |
|---|---|---|---|---|---:|
{chr(10).join(geo)}

`tp_joint52` uses EXENC's exhaustive 7-cell O encoder: **12 CX, depth 8, danger 0.0008**. The minimum-CX proof is 11 and minimum depth is 6; the selected 12-CX circuit has the lower enumerated danger. Receipts: [joint52_O.json](joint52_O.json), [stats](joint52_O_stats.json). Separate B/C connected regions with direct initial pairings cannot be packed alongside O; the constructed alternative is a **104-CX, 22-layer joint B+C** encoder. BC2's independent fault checker finds **0 base-rule violations**, **64 clean-rule violations**, and **62 robust-rule violations**. Full exact c1 also confirms first-order safety. The depth-16 clean search timed out after adding 82 fault constraints: [receipt](joint52_BC16clean.receipt.json). This is not an UNSAT result.

C checks B at step 30 and is measured at 31, releasing routing space. The round then transfers O to data neighbours, measures data in place, transfers O where necessary, and applies B->O. The builder schedules actual per-cell prep gates ALAP, rather than initializing all blocks at time zero. `alap.py` also optimizes fixed-route gate times to shorten O's post-teleport exposure; it preserves the minimum final CX 48. `tp_joint52_m11_21_22` uses MAIN/minit.py on O's three nonpivot first-use Z resets. Its exact total is slightly lower than the base, with lower acceptance; it cannot rescue the acceptance failure. The original v16 prefix is preserved even in this variant.

`check_prefix.py` independently converts every full candidate with the judge and verifies all **137 native prefix operations** have identical gates, cells and times 0–32 to v16. Each candidate's `.prefix.json` is a receipt. `audit_route.py` checks routing cell occupancy, move/reset conflicts, adjacency, and logical operation ordering. It does not certify a missing encoder.

## A validated exception to the output-offset warning

`tp_v16_reuse` removes the reset between measuring D and transferring O into those same D cells. Its two-CX transfer leaves an X^m offset on the transferred block. The three declared D parity checks ensure accepted m is a Hamming codeword; X^m is therefore an X stabilizer times X_L raised to parity(m). This cancels the teleport X_L frame. The candidate declares an empty X frame, and **the judge confirms correctness**, c1 is negligible, and acceptance passes at 1e8 shots. This is a validated codeword/frame cancellation, not permission to leave an arbitrary untracked offset on output. No project rule/document was changed. It saves one step against the reset-based O transfer but remains above v16.

## Solver domain, receipts and binding constraint

`route.py` reserves both cells for every two-CX move, explicitly reserves destination reset, releases each data cell only after its actual Z measurement, permits O moves after teleportation, and requires B->O after the final O move. The initial O/B sites are in the 21 never-used cells. Prefix cells remain occupied through step 32. `--fast-prefix` allows a first transfer at 33 into a released, measured prefix cell without reset; MX destinations use the dual transfer. Bounds allow four transfers per token, more than fit before last CX 40 at two steps per transfer. C and encoder connectivity are omitted in the relaxed bound. Later reuse of moved-from known states without reset, routing before 33, arbitrary interleaved encoders and changes to the unchanged prefix are outside that bound.

| Receipt | Status | Wall seconds | First O->D | Last O->D | Last round CX | Moves |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(sol)}

The binding geometric issue is access to the upper-left data while keeping O and B live: releasing D helps, but O must sometimes retreat after its first coupling to admit B. The relaxed optimum has 17 transfers before adding any C preparation/routing. Exhaustive connected-region enumeration finds 677 seven-cell regions in the unused footprint and 168 ordered three-region partitions, but **zero** partitions admitting all seven direct B–C pairings. It also finds zero sequential separate B/C connected preparations with O's reserved region under the tested staging assumptions. Receipts: [packing.json](packing.json), [staged_packing.json](staged_packing.json), [helper_packing.json](helper_packing.json), [three_partitions.json](three_partitions.json).

`fullroute.py` explicitly retains C, reserves its moves and measurements, and limits the B–C-to-B–O gap. Runs with last-CX horizons 51/55 and gap 3/4/6 timed out without a solution; a fully fixed initial placement at horizon 59 and gap 8 also timed out. UNKNOWN is not evidence of impossibility. `joint52` is the completed alternative with C consumed before routing. It exposes B for 13–18 steps after its check and some O qubits for many steps after teleportation. That exposure and transfers dominate the saved pre-round data wait.

## Exact loss attribution

[price.py](price.py) uses MAIN/ablate.py's exact scoring engine with moving-token labels and splits each aggregated idle gap at label boundaries. Static `--a` and final-output data labels would misclassify these circuits, since O moves and preparation overlaps steps 0–32. Each row removes the named region's noise; changes are not additive.

| Region made noiseless | 2nd | 3rd | Total | exp(-A1), estimate |
|---|---:|---:|---:|---:|
{price_rows}

Making O’s exposed region noiseless lowers the exact total from 1.94468e-3 to 7.84703441e-4; making B’s exposed region noiseless lowers it to 6.35113904e-4. Removing preparation noise alone leaves 1.31240939e-3. These measurements identify post-check exposure as the principal failure of this construction. Full receipt: [tp_joint52.price.json](tp_joint52.price.json). `O_exposed` includes O's teleport coupling, subsequent movement, B coupling and tail; `B_exposed` includes B after its early C check through readout; `prep` is unused-footprint preparation and C check/readout outside those categories. The original-prefix region is independently identified by cells and times.

## Reproduction and scope

Run from the repository root with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`. Check host capacity before each launch. All files/caches generated here stay in TP2; R0/LAYOUT3 were read only. MAIN/REPORT.md does not exist; the requested MAIN tools and measurement receipts were read. No credentials were accessed, no agents were spawned, and nothing was submitted.

```sh
.venv/bin/python work/lanes/TP2/route.py --horizon 41 --hops 4 --connect none --postmove --no-presolve --fast-prefix --workers 2 --out work/lanes/TP2/recheck_bound40.json
.venv/bin/python work/lanes/TP2/build.py work/lanes/TP2/joint52.json work/lanes/TP2/rebuilt --o work/lanes/TP2/joint52_O.json --bc work/lanes/TP2/joint52_BC22.prep.json
.venv/bin/python work/lanes/TP2/evaluate.py rebuilt --procs 5
.venv/bin/python work/lanes/TP2/teleport_v16.py reuse
.venv/bin/python work/lanes/TP2/mc.py tp_v16_reuse 8
```

`evaluate.py` runs the 1e6 judge first, exact third-order screen next, and automatically runs three MC seeds for every exact total below 8.6e-5 or nonzero c1. `manifest.json` verifies this gate for every generated candidate. The six candidates above are the complete generated-QASM set. The remaining opening is an encoder/routing schedule that keeps C verification late and avoids O's prolonged exposure after teleportation; the present bounded searches do not close it.
'''
(H/'REPORT.md').write_text(text)
(H/'manifest.json').write_text(json.dumps(dict(candidates=manifest,baseline_sha256=b['sha256'],mandatory_mc_complete=True),indent=2)+'\n')
print('report written',len(names),'candidates',len(prices),'ablation rows')
