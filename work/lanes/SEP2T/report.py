"""Write the lane report from persisted judge, solver, and ablation receipts."""
import os,sys,json,re,math,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
HERE=Path(__file__).resolve().parent
def read(name):
 p=HERE/name
 return json.loads(p.read_text()) if p.exists() else {}
def number(x):return '—' if x is None else f'{x:.7g}'
def mc(name,s):
 if len(s.get('seeds',[]))==3:return s['seeds'],s.get('mean',sum(x['score'] for x in s['seeds'])/3)
 p=HERE/(name+'.mc3.log')
 if not p.exists():return [],None
 rows=[dict(seed=int(seed),score=float(score),acceptance=float(acc)) for seed,score,acc in re.findall(r' (0|1000|2000) ([\deE.+-]+) ± [^\n]+? acc ([\d.]+)',p.read_text())]
 mean=re.search(r' mean ([\deE.+-]+)',p.read_text())
 return rows,float(mean.group(1)) if len(rows)==3 and mean else None

candidates=['l2_alap','route_l5','routed_auto_pruned','routed56','abstract_built','abstract_cleanA','reuseA_alap','reuseA_refined','pipeline_alap','abstract_trim','general51','abstract_final','general_final']
full=[]
for name in candidates:
 s=read(name+'.score.json');m=read(name+'.json')
 if not s:continue
 assert (HERE/(name+'.check.log')).exists(),name
 seeds,mean=mc(name,s);full.append((name,s,m,seeds,mean))
ranked=sorted([r for r in full if r[4] is not None],key=lambda r:r[4]);best=ranked[0] if ranked else None
bestname=best[0] if best else 'abstract_trim'
models=[
 ('connected_h1.receipt.json','Arbitrary connected seven-cell graphs; one-hop moves into initial holes','240 s / 2 workers','none'),
 ('geom_l3_h1.json','10-CX LAYOUT3 encoder graphs; one-hop placement relaxation','120 s cap / 1 worker','placement only; no timing claim'),
 ('l3_h1_time.receipt.json','10-CX graphs; complete lifetimes, early A, one block hop, ≤2 data hops, R≤80','240 s cap / 2 workers','none'),
 ('connected_chain_h1.receipt.json','Arbitrary connected graphs; one-hop relocation chains','600 s / 8 workers','none'),
 ('long_h2_r0c0.receipt.json','Original FREELAY L5 two-teleport model, r0c0, fixed labels, no early A, ≤2 data hops, R≤60','3600 s cap / 6 workers; proof in 2618.1 s','none; bounded-model infeasibility proof'),
 ('long_l3_h2.receipt.json','10-CX graphs, two block hops, early A, ≤3 data hops, R≤80','3600 s planned / 16 workers; interrupted at 1177 s','no incumbent'),
 ('routed_auto.receipt.json','Fixed L5 endpoints; exact vacancy routing, first solution','600 s cap / 6 workers; first solution 1.36 s','122 teleports; pruned build 72, native R73'),
 ('routed_auto_opt.receipt.json','Same routing, optimization with complete feasible hint','600 s / 6 workers','54 teleports, lower bound 46; checked native R63'),
 ('free_l3_auto.receipt.json','Free final positions, in-place A, separately staged B/C, code automorphisms','180 s / 2 workers','proxy65: 7 data + 30 block Manhattan distance'),
 ('routed_free.receipt.json','Route that placement with stationary final data','600 s cap / 4 workers','16 batches and ≤60 moves: infeasible in this bound'),
 ('abstract_h2.receipt.json','Connected-cell timing model, six-step placeholder encoders, two block hops','1200 s planned / 6 workers; stopped at 511 s to build','21 block + 12 data moves; exact encoders rebuilt at native R56'),
 ('pipeline_l3_h2.receipt.json','10-CX graphs; block CX chains may overlap preceding source measurement','1800 s + ≤30 s tie-break / 4 workers','checked reconstruction: native R56, 24 block + 13 data moves'),
 ('reuseA_l3_h2.receipt.json','Allow measured A endpoints to be reused by B/C; first solution','1800 s cap + ≤30 s tie-break / 16 workers','checked native A50 / BC74; 39 block moves'),
 ('reuseA_opt.receipt.json','Optimize A-cell reuse with complete witness hint','1200 s planned / 16 workers; interrupted at 493 s','checked native A45 / BC58; 29 block moves'),
 ('general_exact_h2.receipt.json','Real EXENC A15/B15/C12 graphs, complete timing/routing, two block hops','1200 s + ≤30 s tie-break / 16 workers','checked general_final native R51, 27 block + 16 data moves'),
]
lines=['# SEP2T — separate blocks built and priced','']
if best:
 name,s,m,seeds,mean=best
 lines += [f'Best measured three-seed circuit: **[{name}]({name}.qasm)**, mean **{mean:.6e}** at 1e8 shots per seed; seed-0 acceptance **{seeds[0]["acceptance"]:.5f}**. It **fails the 0.5 acceptance gate** and does not beat v19’s supplied mean 7.537e-5. No eligible improvement was found. The broad separate-block question remains open; the completed work satisfies the build/price/breakdown branch, not a global impossibility proof.','']
lines += ['All reported circuits use the real 6×6 grid, separate A/B/C preparation, correct teleport-frame detectors, and native ALAP timing. Every reported circuit received the full 1e6-shot judge. No submission, commit, push, credential access, sub-agent, or write to another lane was performed.','',
 '## Models and searches','',
 '“INFEASIBLE” applies only to the stated formulation and bounds. TIMEOUT is never called UNSAT. Interrupted searches are identified explicitly. A placement proxy or abstract preparation duration is not a native circuit measurement.','',
 '| Method | Budget | Status | Best schedule found |',
 '|---|---|---|---|']
for filename,method,budget,schedule in models:
 r=read(filename);status=r.get('result',r.get('status','RUNNING / receipt not collected'))
 if filename=='geom_l3_h1.json' and status=='OPTIMAL':status='FEASIBLE placement relaxation'
 if r.get('secondary_status')=='UNKNOWN':status+='; ALAP tie-break TIMEOUT'
 lines.append(f'| {method} | {budget} | [{status}]({filename}) | {schedule} |')
lines += ['| Constructive vacancy clearing, independent 11-CX blocks | 3000 trials | FEASIBLE | 87 teleports, native R100; `route_l5` |',
 '| EXENC on the actual A graph, pure-logical danger prioritized before correlated danger | all 6,303,146 canonical paths at 12–15 CX; 3 workers | EXHAUSTIVE for these path classes / ASAP schedules | A15, depth7, danger vector `[0,7,0,0,7,0,0,0]`; no class skipped |','',
 'The prior FREELAY one-hop infeasibility results remain limited to its fixed encoder families and final-cell assumptions. Its two-hop timeouts were not proofs. This lane found actual two-hop placement witnesses using different encoder graphs. It also identified two restrictive timing assumptions: successive block teleports can overlap the prior source measurement, and early-measured A endpoints can be reused. The latter is governed by lifetime occupancy, rather than a global final-cell distinctness constraint.','',
 'The first abstract timing witness used a six-step preparation allowance. Actual EXENC preparations were inserted in expanded ticks and the complete circuit was rescheduled and checked. Its model R is never substituted for native R. An old pipelining formulation also allowed a skipped terminal move to relax a coupling deadline; this was corrected to depend on the last actual move. Older witnesses were reconstructed with explicit physical dependencies before reporting.','',
 '## Full circuits','',
 'R is **A coupling / B→C check**, read from the judge’s native schedule; B→data follows B→C by one step. Moves are data hops / one-CX block teleports. c1 is the first-order contribution at p=0.001; 2nd and 3rd are increments. “Exact total” is through order three, and is omitted when |c1|≥1e-12. exp(-A1) is an acceptance **estimate**. MC seeds are 0/1000/2000, each at 1e8 shots. Acceptance-failing results are diagnostics, not eligible ranked submissions.','',
 '| Circuit | R native A/BC | CX | Moves D/block | c1 | 2nd | 3rd | Exact total | exp(-A1), estimate | MC seeds → mean | Seed-0 acceptance | Files |',
 '|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|']
for name,s,m,seeds,mean in sorted(full,key=lambda r:(r[4] is None,r[4] or r[1].get('total',1))):
 c1=s.get('c1');second=s.get('second');log=HERE/(name+'.exact.log')
 if log.exists():
  z=re.search(r'^second order: ([\deE.+-]+)',log.read_text(),re.M)
  if z:second=float(z.group(1))
 valid=c1 is not None and abs(c1)<1e-12;mcstr=' / '.join(number(x['score']) for x in seeds)+(' → **'+number(mean)+'**' if mean is not None else '') if seeds else '—'
 acc=(number(seeds[0]['acceptance'])+' (1e8)') if seeds else (number(s.get('acceptance_1e6'))+' (1e6)')
 ra=m.get('R_A_native',m.get('R_native'));r=m.get('R_native');files=f'[QASM]({name}.qasm), [JSON]({name}.json), [check]({name}.check.log), [exact]({name}.exact.log)'
 lines.append(f'| {name} | {ra}/{r} | {m.get("cx")} | {m.get("data_hops")}/{m.get("block_moves")} | {number(c1)} | {number(second)} | {number(s.get("third")) if valid else "—"} | {number(s.get("total")) if valid else "—"} | {number(s.get("exp_A1"))} | {mcstr} | {acc}; FAIL | {files} |')
lines += ['',
 '`general_alap` was independently checked at 1e6 shots and then proved equivalent to `abstract_cleanA` by identical native operations/times, detector declarations, and data ordering. Only simultaneous written operation order differs; its redundant exact run was stopped, and no separate score is claimed ([receipt](general_alap.equivalence.json)).','',
 '## Measured loss breakdown','']
abl=read(bestname+'.ablation.json')
if not abl:
 lines.append(f'Best-circuit ablation pending for `{bestname}`. The completed nearby-circuit decompositions are retained; no result is substituted silently.')
else:
 rows=abl['rows'];base=rows[0]['total'];lines += [f'For **{bestname}**, the exact-through-third total is **{base:.9e}**. With one region noiseless:','']
 for row in rows[1:]:lines.append(f'- **{row["noiseless"]}**: {row["total"]:.9e}; reduction {base-row["total"]:.9e} ({100*(base-row["total"])/base:.2f}%).')
 lines += ['', 'These marginal reductions overlap and must not be added: faults in different regions interact. Idle is every pre-round idle channel; round includes the final data idle. Preparation/teleport/prefix operation noise is assigned by operation provenance, not a time cut. B and C remain independently prepared even when their encoder cells are reused at different times.',f'[Full ablation]({bestname}.ablation.json), [log]({bestname}.ablation.log), [second-order region pairs]({bestname}.pairs.json).']
lines += ['',
 'The native schedules show long live-state exposure while cells are released and blocks move; its cost is measured above. On `abstract_cleanA`, making pre-round idle noiseless lowers the third-order total from 1.705697e-4 to 4.683673e-5. That is an ablation, not a realizable score. Native R alone is insufficient: `general51` starts earlier while adding data hops and teleports, and its measured screen is worse.','',
 '## Verification, decisions, and limits','',
 '- B→C immediately precedes B→data in every build. Teleport measurement records are XORed into A’s Z checks or B’s X checks; C’s Z teleport frame is propagated through B→C into B’s readout. Full judge correctness checks these frames.',
 '- A-only encoder selection was corrected to distinguish pure logical Z faults from faults requiring a second data error. The original A13 produces nonzero c1 and was evaluated by three-seed MC, not ranked by invalid third order. The extended exact search finds A15 with zero pure-logical danger.',
 '- Full ALAP was refined so terminal/reset-followed measurements run ASAP, and teleport source measurements may overlap the round when their cells are distinct. `abstract_trim` advances seven measurements and removes 72 idle qubit-steps; its exact screen improves but its acceptance still fails.',
 '- MC uses the unchanged `MAIN/spec/mc3.py`; sunfish runs its byte-identical lane-local copy because that mirror lacked the original script. `abstract_built` uses the same check and fast_check seed implementation through evaluate.py because c1 is nonzero. MC receipts retain the precision emitted by the driver; evaluate.py also saves full-precision seed values.',
 '- Best-circuit fast ablations use TREP2’s exact detector-dependency pruning, with the baseline checked against the unchanged exact2 --third result to its printed precision. Earlier complete ablations also use unmodified exact2. No test or judge gate was weakened.',
 '- Untested space remains: other connected encoder graphs, more general encoder/move interleaving, data relocation during the prefix, A coupling before final T_DAG, and longer searches. The fixed-template and bounded routing negatives do not rule these out.',
 '',
 'Reproduction uses the project `.venv/bin/python` and `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`. `co_design.py`, `build_abstract.py`, `rebuild_solver.py`, `reschedule.py`, `trim_measurements.py`, `evaluate.py`, and `ablate.py` retain the model and build paths. Each QASM has sibling metadata with `data_qubits`.',
 '', '[audit.json](audit.json) independently verifies the native timing and reported CX counts for all 13 reported circuits. [manifest.json](manifest.json) verifies all 26 QASM/JSON pairs and identifies which have direct judge receipts. All SEP2T compute jobs have finished or were explicitly interrupted and recorded; none is left running.','']
(HERE/'REPORT.md').write_text('\n'.join(lines));print('report',bestname,number(best[4]) if best else 'pending')
