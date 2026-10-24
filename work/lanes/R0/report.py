import os,sys,json,re,hashlib
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent
load=lambda name:json.loads((H/name).read_text())
F=lambda x:'—' if x is None else f'{x:.9g}'
rows=[]
for name in ['v16_bc2m','abc_ideal','abc_base','alap_ideal','alap_base']:
 s=load(name+'.score.json');d=load(name+'.json');base=name=='v16_bc2m';good=abs(s.get('c1',1))<1e-12;mc={x['seed']:x for x in s.get('mc',[])}
 r='50 / 50 / 51' if base else f"{d['R']} / {d['Rmax']} / {d['last_cx']}"
 wait='17 each' if base else ','.join(map(str,d['wait_steps']))
 cx=(H/(name+'.qasm')).read_text().count('cx ')
 vals=[f'[{name}]({name}.qasm)',r,wait,str(6 if base else d['data_moves']),str(0 if base else d['block_moves']),'no' if base else 'yes',str(cx),F(s.get('c1')),F(s.get('second')) if good else 'invalid: c1 ≠ 0',F(s.get('third')) if good else '—',F(s.get('total')) if good else '—',F(s.get('exp_A1')),*[F(mc.get(seed,{}).get('score')) for seed in [0,1000,2000]],F(s.get('mean')),F(mc.get(0,{}).get('acceptance')),F(s.get('acceptance_1e6')),f'[{"PASS" if s["judge_passed"] else "FAIL acceptance"}]({name}.check.log)',f'[JSON]({name}.json), [scores]({name}.score.json)']
 rows.append('| '+' | '.join(vals)+' |')
sol=[]
for name in ['bound38_00','bound38_01','bound38_10','bound38_11','bound38_20','bound38_21','good10','good20','compact10','compact20','abc_long','abc_alap']:
 d=load(name+'.json');sol.append('| '+ ' | '.join([f'[{name}]({name}.json)',d['status'],F(d['wall']),d['args']['transform'],str(d.get('R','—')),str(d.get('Rmax','—')),str(d.get('last_cx','—')),str(d.get('data_moves','—')),str(d.get('block_moves','—'))])+' |')
report='''# R0 report

**No improved judge-valid circuit was found.** The success condition is not met. No submission was made.

The v16 reference was rerun on owl through the same evaluation pipeline: **8.55379233064e-5** mean over 100,000,000 shots at each of seeds 0, 1000, 2000; seed-0 acceptance **0.53313237**. Its exact total through third order is **8.41984e-5**.

The smallest physically audited routing objective with preparation connectivity is a **last round CX of 39** (`good10`); A couplings span **33–38**. This is a routing witness, not a synthesized full circuit. The smallest completed full circuit has A couplings **33–42**, last round CX **43**, and passes format/class/correctness at 1e6 shots, but fails acceptance. ALAP scheduling changes the A range to **34–42**, with the same last CX. There is no new fully judge-valid R to report.

## Full-circuit measurements

R is reported as **first A CX / last A CX / last round CX**, to avoid calling a highly staggered round “R=33” while it finishes at 43. Wait entries are each data qubit's first A coupling minus 33, in code-index order; they include intervals overlapped by moves. Move counts are two-CX transfers, excluding resets. `c1` is the contribution at p=0.001, as printed by exact2. The second/third columns are used only for |c1| < 1e-12. `exp(-A1)` is an analytical **estimate**, not an acceptance measurement. MC entries are each 1e8 shots.

| Candidate | R first / last A / last CX | Wait steps | Data moves | Block moves | Staggered | CX | c1 | 2nd | 3rd increment | Exact total | exp(-A1), estimate | MC 0 | MC 1000 | MC 2000 | Mean | Seed-0 acceptance, 1e8 | Acceptance, 1e6 | Judge, 1e6 | Files |
|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
'''+ '\n'.join(rows)+'''

`abc_ideal` and `alap_ideal` are state-correct joint B+C encoders with nonzero first-order loss. They were **not** excluded on c1: both received all three full MC seeds. They fail the judge's acceptance gate as well as having much higher 1-F. Their printed second-order diagnostic is deliberately not treated as a valid screen.

`abc_base` and `alap_base` use the independently checked base FT rule, not the stronger clean rule. Their exact totals are far outside the mandatory MC threshold 8.6724352e-5, and their measured 1e6 acceptance fails. No threshold-eligible candidate is awaiting MC. No new circuit has measured 1e8 acceptance above 0.5. First-use measurement variants were not expanded after these acceptance failures: that rewrite spends acceptance, so it cannot rescue these circuits.

## Binding constraints and solver receipts

The phase model prepares/checks B+C in the never-used region, consumes C, and prepares A in that region without touching the already-prepared B. It reserves both cells of each transfer, separately reserves destination initialization, permits data moves between A and B couplings, and requires each data A CX before its B CX. It allows two data moves and three block moves in the step-38 feasibility tests; more sequential two-CX transfers cannot fit before the required coupling in that time window. A may use all seven spare cells as preparation helpers. C partners are distinct, adjacent to their B qubits, and in the never-used region.

With CP-SAT presolve **disabled**, all six translation representatives are **INFEASIBLE for last round CX <= 38**. Their receipts below include solver response statistics and complete arguments. The other seven orientations are grid isometries of these six translations, so this covers the symmetry/translation placements for this model. This is a conditional model result, **not** an impossibility proof for every permitted circuit architecture.

| Search | Status | Wall seconds | Transform | First A | Last A | Last CX | Data moves | Block moves |
|---|---|---:|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(sol)+'''

The physical transfer model allows an initial no-reset B move into a prefix MX cell at step 33: `CX destination->source; CX source->destination`. The measurement's known Z offset stays on B and is XORed into B's readout detectors. A can similarly reuse the one Z-measured prefix cell. Other destinations are initialized; initialization may overlap earlier work on the source. Later reuse of known source/measurement states is not exhaustively modeled, so this is another explicit limit of the bound.

Two geometric facts explain the gap:

1. The two-row shifts leave a two-cell disconnected component in the never-used region (`[24,30]` for transform 0,2,0). A seven-qubit block cannot be prepared across this disconnected component and the main component before step 33. The first relaxed step-37 routing witnesses placed B there and are **not preparation-feasible**. `bc20.receipt.json` independently returned UNSAT before adding any fault constraints. `good20` excludes these initial cells.
2. Exhaustive connected-region enumeration (`packing.py`, `packing.json`) finds only **15, 11, 2, 1, 0, 0** concurrent A+BC packings for translations (0,0), (0,1), (1,0), (1,1), (2,0), (2,1). Here A occupies seven connected cells, BC the other fourteen connected cells, and BC admits seven distinct adjacent B–C pairs. The two one-row/left packings put A along the bottom boundary, forcing substantial A transfers to upper data. This closes only the stated concurrent connected-region recipe.

The relaxed all-two-step models `relax2_*.json` reached last CX 37, zero data moves. They omit reset-basis costs and preparation constraints and are preserved only as lower-bound diagnostics. They are not full circuit candidates.

## Encoders and verified construction

The complete circuits use `abc_long`'s concurrent layout, A `[24,32,18,27,31,33,30]`, B `[0,34,2,4,17,23,29]`, C `[1,35,3,5,11,22,28]`, with the v16 prefix translated down one row. Exact A enumeration found a 13-CX, depth-7 encoder with danger **0.002** (`abc_long_A.json`, statistics adjacent), versus the supplied v16 A danger 0.0006666667. The encoder was independently checked by EXENC's state/topology/danger checks.

The joint B+C state-correct 24-layer encoder has 98 CX (`abc_ideal24.prep.json`). The 28-layer base-FT encoder has 145 CX and zero base-rule violations after 92 CEGAR constraints (`abc_base28.prep.json`, receipt adjacent). Clean-rule searches at depth 24 and 30 with free basis, and depth 28 with fixed canonical basis, timed out. Those are **timeouts, not infeasibility proofs**.

`build.py` merges native prefix steps, encoders, transfers, staggered couplings and deterministic detectors. Its current implementation schedules preparation and BC verification per cell ALAP; `abc_ideal`/`abc_base` preserve the earlier common-deadline experiment, and `alap_*` are its improved scheduling result. `route.py --alap --fixed-paths ...` fixes positions and C's labeling while maximizing coupling times at the same final CX. `audit_route.py` independently checks adjacency, resource conflicts, live-token occupancy and output mapping.

`check_prefix.py` confirms that all **137 native prefix operations** have exactly the same qubits (under the translation), gates and steps 0–32 as v16. In particular, native MX folding is preserved when a measured prefix cell is reused. This is recorded in the adjacent `.prefix.json` receipts. All four candidate QASMs have adjacent JSON data-qubit mappings and passed full `tprep.check` format/class/correctness, including detector determinism, at 1e6 shots.

## Loss attribution

ALAP scheduling lowers the base-FT exact total from **7.6460e-4 to 6.1365e-4**, but leaves it over seven times v16. The corresponding measured 1e6 acceptance is **0.440789**.

`pairs.py` calls MAIN/ablate.py's unchanged pair/triple evaluation engine with labels derived from the actual moving-token schedule. A single round-start cutoff would classify almost every post-prefix transfer as “round” for these staggered circuits. The receipt is `alap_base.pairs.log`.

The largest exact pair contributions are B idle × B idle **8.120e-5**, BC prep × B idle **7.060e-5**, and BC prep × BC prep **5.415e-5**. B idle × final data tail adds **3.916e-5**, B idle × data wait **3.820e-5**, and B idle × B move **3.159e-5**. Early C consumption releases routing space but leaves B waiting/moving after its verification. That added exposure dominates the data-wait savings in these measured constructions. The four leading pair terms alone exceed v16's entire loss.

## Scope, remaining uncertainty, and reproduction

All R0 compute jobs completed; no R0 background jobs remain. No successful full R35–37 construction was found. The bounded phase model closes last-CX <=38 for the stated preparation/transfer restrictions; unrestricted dynamic reuse of known states, more general preparation interleavings, and additional late B verification remain open. A routing witness is not an encoder or a judge result. The connected-region counts do not prove that arbitrary space-time Clifford preparation is impossible.

The requested MAIN/REPORT.md does not exist; MAIN/minit.py, MAIN/ablate.py and its v16 receipts were read. The other requested reports/tools were read. LAYOUT3 was read only. All generated files and caches are under R0. No credentials were accessed, no submission was attempted, and no agents were spawned. Dragon's expected repo path was absent; compute ran locally and on owl under the requested thread/CPU caps, with capacity checks before launches.

Reproduce from the repository root, with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`:

```sh
.venv/bin/python work/lanes/R0/proof_batch.py
.venv/bin/python work/lanes/R0/packing.py
.venv/bin/python work/lanes/R0/build.py work/lanes/R0/abc_alap.json work/lanes/R0/abc_long_A.json work/lanes/R0/abc_base28.prep.json work/lanes/R0/alap_base
.venv/bin/python work/lanes/R0/check_prefix.py work/lanes/R0/alap_base
.venv/bin/python work/lanes/R0/evaluate.py alap_base 12
```

The evaluate script changes its working directory to R0. On owl, use the specified fnc-build:22.04 Docker wrapper and check capacity first. `manifest.json` records candidate hashes and confirms the mandatory MC audit.
'''
(H/'REPORT.md').write_text(report)
manifest={}
for name in ['v16_bc2m','abc_ideal','abc_base','alap_ideal','alap_base']:
 s=load(name+'.score.json');txt=(H/(name+'.qasm')).read_bytes();eligible=abs(s.get('c1',1))>=1e-12 or s.get('total',1)<=8.41984e-5*1.03
 manifest[name]=dict(sha256=hashlib.sha256(txt).hexdigest(),score_sha_matches=hashlib.sha256(txt).hexdigest()==s['sha256'],has_data_qubits='data_qubits' in load(name+'.json'),mc_required=eligible,mc_seeds=[m['seed'] for m in s.get('mc',[])],mc_complete=not eligible or {m['seed'] for m in s.get('mc',[])}=={0,1000,2000})
assert all(d['score_sha_matches'] and d['has_data_qubits'] and d['mc_complete'] for d in manifest.values())
(H/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('report and manifest written')
