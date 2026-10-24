import os,sys,json,re,hashlib
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from pathlib import Path
H=Path(__file__).resolve().parent
S={x['file'][:-5]:x for x in json.loads((H/'schedule_summary.json').read_text())}
E={};checks={};MC={}
for name in S:
 p=H/(name+'.exact.log');txt=p.read_text();get=lambda pat:float(re.search(pat,txt).group(1))
 E[name]=dict(c1=get(r'c1 p = ([\deE.+-]+)'),second=get(r'second order: ([\deE.+-]+)'),third=get(r'third order: ([\deE.+-]+)'),total=get(r'1-F \(to 3rd order\) = ([\deE.+-]+)'),acc=get(r'exp\(-A1\) = ([\deE.+-]+)'))
 checks[name]=json.loads((H/(name+'.check.json')).read_text())['check']
 p=H/(name+'.mc.json')
 if p.exists():
  d=json.loads(p.read_text());assert len(d['seeds'])==3;MC[name]=d
rank=sorted(MC,key=lambda n:MC[n]['mean']);winner=rank[0];assert winner=='reuse10' and MC[winner]['mean']<8.3e-5 and checks[winner]['passed']
f=lambda x:f'{x:.6e}'
lines=[f'''# EARLYBC report

The completion gate is met by **[reuse10.qasm](reuse10.qasm)** and [reuse10.json](reuse10.json): three-seed 100,000,000-shot mean **{f(MC[winner]['mean'])}**, seed-0 acceptance **{MC[winner]['seeds'][0]['acceptance']:.8f}**, and PASS at 1,000,000 shots. This is a measured **{100*(1-MC[winner]['mean']/8.347295e-5):.2f}%** reduction from v17a's published three-seed mean 8.347295e-5 ([reference receipt](../MAIN/spec/mc3_v17.log)).

The winner starts the round at **R=49**, one actual judge step earlier than v17a. It retains the exact 82-CX B+C encoder, the 11-CX A encoder present in the source circuit, both readout re-encoding edges **17→16 and 19→25**, and all existing measurement-initialization records. It has the same 209 CX and six data hops. No block teleports were added. The target **R≤40 remains unachieved**; this report satisfies the first completion condition, not a universal infeasibility claim.

## What changed

The pre-stage's native X measurement on cell 10 leaves a known |+⟩ on accepted branches because c[8] is already postselected to zero. `reuse10` preserves that native MX with `h; measure; h`, removes the following reset, and implements the data-4 transfer with **CX 10→4; CX 4→10**. A two-CX transfer into |+⟩ uses this reverse order. The source cell is subsequently reset for the B encoder, as before. The judge's correctness check verifies the actual full circuit and detector conventions.

The hop runs at steps **33–34**, replacing **34–35**. Cell 4 is reset for B at 35 instead of 36; the B+C critical path and final round then move one step earlier. All other prefix operations retain their measured timing. `simplify.py` also commutes compatible CNOTs and reaches R=48 (`reuse10_commute`), but its measured three-seed mean ranks behind `reuse10`, despite a slightly lower third-order screen.

The unchanged per-qubit-order schedule has the exact critical chain recorded in [fixed_critical_path.json](fixed_critical_path.json): reset 10 at 33 → the two data-hop CXs → reset 4 at 36 → the B+C chain through its last CX at 49. Its earliest possible round is 50. Thus moving unrelated preparation gates earlier cannot shorten that chain.

## Source roles and geometry

In code order 0…6:

- Pre-stage data: `[0,20,7,4,3,15,8]`; round/output data: `[0,20,7,10,3,22,21]`.
- A: `[1,14,8,9,2,16,15]`; B: `[6,26,13,11,4,23,27]`; C: `[12,25,19,17,5,29,28]`.
- Data routes: `4→10`, `15→16→22`, `8→9→15→21`; the other four data qubits stay in place.
- B+C interaction path: `6–12–13–19–25–26–27–28–29–23–17–11–5–4`.
- A interaction tree: `1–2–8–14–15–16`, with the extra branch `8–9`.

At step 33, the available partners of the original data cells are: `0:{1,6}`, `20:{14,19,21,26}`, `7:{1,6,13}`, `4:{5,10}`, `3:{2,9}`, `15:{9,14,16,21}`, `8:{2,9,14}`. Their union has 12 cells, so 14 simultaneous A/B partners require movement. B+C also conflicts with data cell 4, not only cell 6; cells 13 and 19 become available at 20 and 16.

Two source-metadata corrections were verified from the actual model text: q3's `T_DAG` is at **31**, the other six are at **32**; and the A encoder contains **11 CX** after its final initializations, although old metadata says 13. These do not change the baseline R=50 diagnosis. [v17a_source.check.json](v17a_source.check.json) records a fresh 1e6-shot source check.

## Schedules

Every step below comes from `tprep.noise.schedule(Model(...).text)`, independently of the builders; see [audit_schedule.py](audit_schedule.py), [schedule_summary.json](schedule_summary.json), and each `*.judge_schedule.json`. Preparation intervals include initialization. `c1 p` is exact2's printed first-order contribution at p=0.001, not the unscaled coefficient. All are numerically zero, so the third-order screen applies. “Exact total” means the exact expansion **through order three**, an estimate of the full noisy score; `exp(-A1)` is an acceptance estimate. Every row has a matching JSON containing `data_qubits` and a fresh `*.check.json` at 1e6 shots.

| Circuit | R | B+C prep | A prep | Moves (data/block) | CX | c1 p | 2nd | 3rd increment | Exact total through 3rd | exp(-A1) | 1e6 judge |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|''']
order=['fixed_alap','reuse10','reuse10_commute','reuse9_10','reuse9_10_15','reuse9_10_15_6','commute','cancel_alap','cancel_commute','mx_init','partial24','partial15']
for name in order:
 s=S[name];e=E[name];c=checks[name];interval=lambda k:'–'.join(map(str,s[k]))
 lines.append(f"| [{name}]({name}.qasm) / [JSON]({name}.json) | {s['R']} | {interval('BC_prep')} | {interval('A_prep')} | 6 / 0 | {s['cx']} | {e['c1']:.3e} | {f(e['second'])} | {f(e['third'])} | {f(e['total'])} | {e['acc']:.5f} | {'PASS' if c['passed'] else 'FAIL acceptance'} ({c['acceptance']:.6f}) |")
lines += ['''
## Finalists ranked only by 1-F

Each MC column is 1e8 shots with STANDARD noise and the actual grid. Runs use `fast_check.check`, the repository's judge-equivalent chunked sampler, after `tprep.check(..., shots=10**6)` in [mc_rank.py](mc_rank.py). Acceptance above 0.5 does not enter the ranking. Source records and standard errors are retained in each `*.mc.json`.

| Circuit | Seed 0 | Seed 1000 | Seed 2000 | Mean | Seed-0 acceptance | Files |
|---|---:|---:|---:|---:|---:|---|''']
for name in rank:
 d=MC[name];v=d['seeds'];lines.append(f"| {'**'+name+'**' if name==winner else name} | {f(v[0]['score'])} | {f(v[1]['score'])} | {f(v[2]['score'])} | {f(d['mean'])} | {v[0]['acceptance']:.8f} | [QASM]({name}.qasm), [JSON]({name}.json), [MC]({name}.mc.json), [check]({name}.check.json) |")
base=S['fixed_alap'];best=S[winner]
lines += [f'''
## Wait, idle, and movement trade-off

`reuse10` saves one step of pre-round data exposure, adds **zero** CX and **zero** moves, and removes one reset. B+C idle exposure after its initializations and before the round is **{base['BC_idle_steps']} → {best['BC_idle_steps']} qubit-steps**; A idle exposure is **{base['A_idle_steps']} → {best['A_idle_steps']}**. These counts come from the judge's idle gaps, not wall-clock scheduling. The second-order contribution falls from 5.70772e-5 to 5.67240e-5, and the third-order increment from 2.53769e-5 to 2.35070e-5. The measured total third-order-screen gain is 2.2230e-6. This jointly prices the earlier round and reset replacement; it is not an isolated noiseless-wait ablation.

The partial-overlap tests move every available B+C operation ASAP from a lower bound of 24 or 15 while respecting released cells and the fixed gate order. They actually overlap the pre-stage but still finish at 48 and reach R=49 because cell 4 remains on the critical path. Their B+C idle exposures rise to **{S['partial24']['BC_idle_steps']}** and **{S['partial15']['BC_idle_steps']} qubit-steps** respectively, versus **{best['BC_idle_steps']}** in the winner. Both fail the official acceptance gate: **0.485778** and **0.443306** at 1e6 shots. Their exact screens are {f(E['partial24']['total'])} and {f(E['partial15']['total'])}. These two tested partial-overlap schedules are worse; other branch timings and relocation remain open.

Reusing cell 9 as well gives no further R reduction and a worse mean. Reusing cell 15 after an earlier data transfer raises the measured second-order contribution. Propagation of residual transfer errors into the next data token is the mechanism inferred from the CX directions; this variant is rejected by score. Removing the two cancellable CX pairs also fails to improve the measured ranking. X-basis measurement initialization of all six B+C pivots is correctness-valid with propagated record frames (`mx_init`), but its three-seed mean is worse than the winner.

## Placement and teleport-routing search coverage

The search retained the original encoder interaction graphs and both re-encoding adjacencies. CP-SAT presolve was disabled throughout, following the documented OR-Tools failure mode. Static Manhattan objectives are placement proxies, not score or schedule measurements.

- **Stationary block embedding:** [place_released_0.json](place_released_0.json) is INFEASIBLE for B+C in the 21 never-used cells plus released cells 13/19, A with its unchanged tree, data at Manhattan distance ≤4 from its pre-stage positions, and both readout edges. The never-used-only domain is a subset. This proof is limited to that fixed-label, no-block-move model.
- **All A/B/C staged early:** [stage_0.receipt.json](stage_0.receipt.json) / [stage_0_60.json](stage_0_60.json) achieve the static optimum 60 for `sum(block Manhattan distances) + 3*sum(data Manhattan distances)`. Preparation fits the free cells, but the routing model reserves each source through its measurement and each destination from initialization. For this placement, [route0.receipt.json](route0.receipt.json) is INFEASIBLE at R≤43 with ≤3 block hops and ≤2 data hops per token. [route1.receipt.json](route1.receipt.json) remains INFEASIBLE at R≤45 with ≤4/3 hops. With ≤6/4 hops and R≤50, [route3.receipt.json](route3.receipt.json) is UNKNOWN; its objective bound implies R≥48 **for that model and starting placement**, with no feasible routing witness found.
- **A allowed in released pre-stage ancilla cells:** static optimum 52 in [stage_2_52.json](stage_2_52.json); its A preparation is only ready at 40 on several wires. [route2.receipt.json](route2.receipt.json) is INFEASIBLE at R≤46 with ≤4 block / 3 data hops per token.
- **Code-coordinate automorphisms:** [autostage.py](autostage.py) allows the 168 Steane coordinate automorphisms for A and B/C independently. The placement search found cost 46 with lower bound 26, not an optimum ([receipt](autostage_0.receipt.json)). Routing the earlier cost-50 incumbent failed at R≤44 in [autoroute0.receipt.json](autoroute0.receipt.json). Later placements have not been routed. This remains an open route to R≤40.

No time-expanded teleport schedule was found, so no full teleport circuit or MC performance is claimed. [route.py](route.py) and the route-assembly branch of [build.py](build.py) remain experimental. The completion condition is satisfied by the measured winner; the global relocation family is not proved exhausted.

## Reproduction and verification

From the repository root, use `.venv/bin/python` with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`:

- `work/lanes/EARLYBC/reuse.py` builds the winner and the other reuse variants from v17a.
- `work/lanes/EARLYBC/evaluate.py 8 reuse10` runs the 1e6-shot judge and `EVAL/exact2.py --third`.
- `work/lanes/EARLYBC/mc_rank.py 8 reuse10` runs the required three 1e8-shot seeds.
- `work/lanes/EARLYBC/audit_schedule.py` independently extracts steps from every candidate's exact model text.

All circuit artifacts, solver receipts, scripts, checks, and MC results are in this lane. No submission, commit, push, credential access, or sub-agent action was performed. Zebra and hippo worker limits were respected; all launched jobs were collected on process completion. [manifest.json](manifest.json) records the delivered QASM/JSON hashes and check status.
''']
(H/'REPORT.md').write_text('\n'.join(lines))
manifest={name:dict(qasm_sha256=hashlib.sha256((H/(name+'.qasm')).read_bytes()).hexdigest(),json_sha256=hashlib.sha256((H/(name+'.json')).read_bytes()).hexdigest(),check=checks[name],mc=MC.get(name),schedule=S[name]) for name in S}
(H/'manifest.json').write_text(json.dumps(manifest,indent=2));print('winner',winner,MC[winner]['mean'],'candidates',len(S),'finalists',len(MC))
