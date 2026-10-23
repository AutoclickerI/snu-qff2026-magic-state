import sys,json,math,shutil,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent
# Consolidate exact screens and all-order receipts, keeping the largest shot count.
rows={}
for line in (B/'subset_screen.jsonl').read_text().splitlines():
 j=json.loads(line);rows.setdefault(j['name'],{}).update(first=j['first'],second=j.get('second'))
for p in B.glob('*_score.json'):
 j=json.loads(p.read_text());name=p.name.removesuffix('_score.json')
 for suffix in ['_both','_mc','_exact']:name=name.removesuffix(suffix)
 if name in ['rm_circuit','rm_optimized']:continue
 r=rows.setdefault(name,{})
 if 'exact2' in j:r.update(first=j['exact2']['loss1'],second=j['exact2']['loss2'])
 mc=j.get('mc',[])
 if mc and (not r.get('mc') or mc[0]['shots']>=r['mc'][0]['shots']):
  r['mc']=mc;r['mean']=sum(x['loss'] for x in mc)/len(mc);r['sem_mean']=math.sqrt(sum(x['sem']**2 for x in mc))/len(mc);r['acceptance']=sum(x['acceptance'] for x in mc)/len(mc)
for name,r in rows.items():
 p=B/(name+'.json')
 if p.exists():
  j=json.loads(p.read_text());r.update(cx=j.get('cx'),depth=j.get('depth'),data_qubits=j.get('data_qubits'))
(B/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
finalists={name:r for name,r in rows.items() if r.get('mc') and len(r['mc'])==3 and r['mc'][0]['shots']==100000000 and r['acceptance']>=.5}
name,best=min(finalists.items(),key=lambda nr:nr[1]['mean'])
assert name=='va_ta0_PA','Review region decomposition for new best before finalizing'
for ext in ['qasm','stim','json']:shutil.copy2(B/(name+'.'+ext),B/('rm_optimized.'+ext))
meta=json.loads((B/'rm_optimized.json').read_text());meta.update(source_variant=name,score=best,status='noiseless verified; STANDARD grid-free measured; adjacency NOT satisfied')
(B/'rm_optimized.json').write_text(json.dumps(meta,indent=2)+'\n')
# Keep canonical scores attached to the canonical circuit, never the superseded 12-CX frame.
for suffix in ['_score.json','_both_score.json','.log']:
 src=B/('rm7_serial_asap'+suffix)
 if src.exists():shutil.copy2(src,B/('rm_circuit'+suffix))
limits=json.loads((B/'judge_limits.json').read_text());lim=limits[name]
regions=json.loads((B/(name+'_regions.json')).read_text());assert regions['shots']==100000000
full2=best['second'];tail2=regions['tail_exact2']['loss2'];rest2=regions['rest_exact2']['loss2'];cross2=full2-tail2-rest2
crossmc=best['mean']-regions['tail']['loss']-regions['rest']['loss']
paper=json.loads((B/'paper_high.json').read_text());orders=json.loads((B/'paper_orders.json').read_text())
selected=['rm_frame12','rm7_serial_barriers','rm7_serial_asap','rm7_serial_alap','rm7_parallel_asap','rm7_parallel_alap','rm7_serial_dummy_alap','rm7_parallel_dummy_alap','rm7_lateverify','rm7_lateverify_alap','rm7_parallel_asap_steane','rm7_parallel_steane_alap','va_TA_TB_PA_PB','va_TA_TB','va_PA','va_TA_PA','va_TA_PB','va_ta02_PA','va_ta0_PA']
table='| Variant | CX | Mean 1−F | Acceptance | Shots/seed |\n|---|---:|---:|---:|---:|\n'
for n in selected:
 r=rows.get(n,{})
 if 'mean' in r:table+=f"| `{n}` | {r.get('cx','—')} | {r['mean']:.8g} | {r['acceptance']:.6f} | {r['mc'][0]['shots']:,} |\n"
seedtable='| Seed | 1−F | SEM | Acceptance |\n|---:|---:|---:|---:|\n'+''.join(f"| {r['seed']} | {r['loss']:.11g} | {r['sem']:.3g} | {r['acceptance']:.8f} |\n" for r in best['mc'])
report=f'''# RM_PROTO — reproduced paper and retained-output evaluation

Completed grid-free study. **Best tested retained-output variant: mean 1−F = {best['mean']:.11g} ± {best['sem_mean']:.3g} SEM, acceptance {best['acceptance']:.8f}** under the judge's STANDARD noise at p=1e-3. It has 119 CX, 35 active qubits, and zero first-order loss. This remains above the leader's quoted 6.29e-5 even before routing; it is not a grid submission.

## 1. Circuit summary and artifacts

- **`rm_circuit.{{qasm,stim,json}}`**: canonical paper adaptation for RM_GRID, 89 CX, 19 active qubits, depth 59, serial reused flag ancillas. All four paper source groups are retained. Its measured mean is 1.2609125e-2, acceptance 0.5030749 (three 10-million-shot seeds). Data qubits in judge Steane order are **[4,2,3,0,5,1,6]**, corresponding to paper labels [5,3,4,1,6,2,7].
- **`paper_raw.*`**: original 82-CX physical circuit, with its physical software gauge frame documented below. It intentionally fails the judge's fixed-codespace check without that frame; it is a reproduction artifact, not a candidate.
- **`rm_optimized.*`**: best tested variant, exact copy of `{name}.*`; the JSON records the provenance and scores.
- `rm_frame12.*`: superseded 94-CX coherent-frame prototype, retained as negative evidence. Its scores are distinct from the canonical 89-CX files.
- Stim files use the judge/xtim extended Stim syntax, including T and T_DAG.

Sources: supplied [arXiv:2609.12698](https://arxiv.org/abs/2609.12698), especially Appendices A–C; the exact 25-CX encoder is transcribed from [Daguerre–Kim, arXiv:2410.07327v3, Fig. 5](https://arxiv.org/pdf/2410.07327). The downloaded reference PDF and rendered encoder figure are in `paper/`. `build.py` contains every encoder and flag-gadget CX in execution order.

The encoder starts paper qubits 7,9,11,13,14 in |+⟩ and the other ten in |0⟩. A |+⟩ verifier controls seven CX onto **even labels 2,4,6,8,10,12,14** and is measured in X. Four reusable ancillas implement TA=(p14,p16,p17), TB=(p1,p2,p3), PA=(p8,p12), PB=(p10,p11), using the exact Table III geometry and Appendix B right-to-left gate order. These use 30+20 CX. The verifier, ten source syndromes and four flags give 15 deterministic source detectors. Odd paper labels receive T, even labels T†. Bulk qubits 8–15 are measured in X; their total parity is detector 16.

**Gauge-frame incompatibility:** the paper applies the physical software frame Z47^s1 Z45^s2 Z27^s3, with s1=u8⊕u9⊕u13⊕u14, s2=u9⊕u10⊕u11⊕u14, s3=u11⊕u12⊕u13⊕u14. The judge's FRAME declarations support only logical Paulis. Without physical gauge correction, 7/8 of noiseless branches lie outside its fixed +1 Steane codespace (exact infidelity 0.875). Postselecting all three random signs would give ideal acceptance 1/8 and cannot meet 0.5.

The canonical adaptation adds **CX(i→i+7), i=1…7**, before bulk readout. This coherently applies the required physical frame up to a Steane stabilizer and a logical Z. Declare FRAME_X=0 and **FRAME_Z=u8⊕…⊕u14**. On accepted even-bulk branches the latter also equals u15. These seven CX are real noisy gates under our judge; they are not hidden software corrections.

## 2. Reproduction against the paper

The paper model has exactly **150 independent noisy locations**: 30 preparations, 82 CX, 15 T/T†, 23 live measurements. It has no idle noise and ideal destructive output tomography. The software frame is represented by noiseless coherent gates, with bulk measurement flips placed before those gates so recorded-bit errors induce the correct physical frame. This placement matters.

`paper_eval.py` enumerates distinct faulty locations through weight three, including every Pauli component, using the exact rotation state. It separately postselects the three X-type or three Y-type destructive syndrome parities and combines their accepted weights and logical expectations **before** normalization; it does not substitute the judge's six-syndrome decoder.

| Quantity | Reproduced result | Paper |
|---|---:|---:|
| First-/second-order loss coefficients | 0 within 1e-12 roundoff | 0 |
| Cubic coefficient | {orders['coefficient_cubic']:.12f} | 2837363/13500 = 210.175037037037 |
| Acceptance from fault weights ≤3 | {orders['acceptance_through_fault3']:.12f} | 0.8689553 lower endpoint |
| Acceptance including adversarial higher-order mass | [0.8689553296, 0.8689733607] | [0.8689553, 0.8689734] |
| Conditional loss retaining weights ≤3 | {orders['loss_through_fault3']:.11g} | same low-order calculation |
| Finite-p upper bound, 99.9% joint confidence | **{paper['upper_infidelity']:.11g}** | ≤2.19e-7, rounded ≤2.2e-7 |
| Estimated finite-p infidelity | {paper['estimated_infidelity']:.11g} | not the certificate |

For the independent finite-p certificate, `paper_high.py` sampled **1,000,000 fault-location subsets at each weight 4,5,6**, seed 20261024; positive-loss counts were 277,187,96. One-sided Clopper–Pearson bounds with Bonferroni allocation cover the three strata; all weight≥7 events receive unit loss (mass 2.59537e-10); the denominator floor is (1−p)^150. Evidence: `paper_orders.json`, `paper_high.json`. The headline result is reproduced, not merely quoted or obtained by substituting p into a fitted cubic.

## 3. Our-judge grid-free score and loss split

The canonical 89-CX adaptation's three 10-million-shot scores are {', '.join(f"{r['loss']:.10g}" for r in rows['rm7_serial_asap']['mc'])}, mean **{rows['rm7_serial_asap']['mean']:.10g}**, acceptance **{rows['rm7_serial_asap']['acceptance']:.7f}**. Its first-order loss is zero; second-order expansion is **0.01367511908**. Terminal last-output-gate plus idle-only loss is 0.001123901486, remaining-only 0.008424130787, mixed term 0.004127086808 at second order. Canonical output terminal idle counts in judge data order are **[10,21,13,20,1,1,4]**. This explains why the destructive paper result does not survive unchanged as a live-output score. Evidence: `rm_circuit_breakdown.json` and `rm7_serial_asap_both_score.json`.

The optimized variant uses a reduced source check set (one flagged TA check Z8Z9Z10Z15 plus PA's two checks), the original encoder and logical-X verifier, all 15 T/T† gates, the seven-CX coherent frame, and a final Steane round. Blocks A=|+L⟩ and B=|0L⟩ detect output X and Z errors; independent D=|+L⟩ verifies A's Z errors and C=|0L⟩ verifies B's X errors. The bulk/source cells are reset and reused. Ancilla preparation is scheduled as late as dependencies permit.

**Best circuit — 100 million shots per seed, exact xtim engine, unchanged STANDARD noise and decoder:**

{seedtable}

Mean **{best['mean']:.11g} ± {best['sem_mean']:.3g} SEM**; seed-0 three-significant-figure key **{best['mc'][0]['loss']:.3g}**. Acceptance mean **{best['acceptance']:.8f}**. Exact single-fault loss is zero (numerical residue {best['first']:.2g}); second-order conditional expansion **{full2:.11g}**. The Monte Carlo includes all fault orders; the difference from the expansion is material.

For the following split, **tail** includes the full noisy channels on the last two output-check CX gates and all data idle noise beginning there. It includes the partners' Pauli components; it is not just a hand-selected data marginal. **Rest** includes every other channel.

| Noise enabled | Second-order conditional expansion | All-order MC 1−F | MC acceptance |
|---|---:|---:|---:|
| Tail only | {tail2:.11g} | {regions['tail']['loss']:.11g} ± {regions['tail']['sem']:.3g} | {regions['tail']['acceptance']:.8f} |
| Rest only | {rest2:.11g} | {regions['rest']['loss']:.11g} ± {regions['rest']['sem']:.3g} | {regions['rest']['acceptance']:.8f} |
| Mixed / ablation residual | {cross2:.11g} | {crossmc:.11g} | — |
| All | {full2:.11g} | {best['mean']:.11g} | {best['acceptance']:.8f} |

Tail/rest MC each uses 100 million shots, seed 0. The second-order split is additive. The all-order residual is full mean minus the two ablations and includes interactions and conditional-normalization effects; it is not a uniquely assigned causal contribution. Evidence: `{name}_regions.json`. The tail's **2.5666667e-5 second-order loss matches the direct-readout floor in work/bounds.py**. Every output has consecutive final checks and exactly one terminal idle step.

## 4. Tail-optimised variants and decisions

All Monte Carlo means below use seeds 0/1000/2000; shot counts are explicit. First-order loss is zero except for `va_TA_TB` (1.6666667e-5 at p=1e-3). `results.json` also records exact screens, including source-check subsets with nonzero first order.

{table}

- Replaced the initial 12-CX coherent gauge frame by seven transversal CX; retained the 12-CX version as negative evidence.
- Tested serial barriers, ASAP and late scheduling; independent flag gadgets reduce source depth from 59 to 31. Late scheduling alone can improve acceptance while worsening loss.
- Tested explicit checked dummy partners in the final step. Serial late-scheduled result is score-neutral within noise; parallel reuse adds three steps and worsens loss. The idealized dummy floor does not account for this preparation/reuse cost.
- Tested moving and flagging the logical-X verifier at the end of source checks. It lengthens exposure and is worse in these schedules.
- Added a verified Steane round with direct one-step final readout. Verifying both ancilla blocks removes substantial source×round cross terms.
- Screened all 15 proper subsets of the four source groups and six reduced-TA variants. Dropping both pair groups gives first-order loss 1.6666667e-5 at p=1e-3. These candidates were also ranked by total loss, since zero first order is not a judge requirement; their best screened variant was Monte Carlo checked. The winning reduced source keeps PA and one flagged TA check. This changes the paper recipe and is explicitly an optimization, not part of the reproduction.
- Gauge readout timing follows the tested ASAP and late schedules; all eight bulk qubits are measured before their cells are reset and reused for output-round ancillas. Their timing, final check order, and output waiting steps are included in the actual STANDARD schedule.

No global-optimality or routing-feasibility claim is made. The surviving gap is mostly earlier faults and their interactions with the final round, not an avoidable multi-step terminal readout.

## 5. Judge-limit and correctness checks

`verify_limits.py` runs the judge's format, xtim class, exact correctness, and noiseless cross-engine checks with **only the adjacency predicate bypassed in process**. No judge source was edited.

| Check | Canonical rm_circuit | Optimized rm_optimized | Limit |
|---|---:|---:|---:|
| Active qubits | 19 | {lim['active_qubits']} | 36 |
| CX count | 89 | {lim['CX_count']} | no separate CX cap |
| T/T† count | 15 | {lim['T_count']} | exact-engine processability |
| Rotation rank | 5 | {lim['rotation_rank']} | 22 |
| Measure + reset | 53 | {lim['measure_reset']} | 1000 |
| Statements | 184 | {lim['statements']} | 5000 |
| Bytes | 3236 | {lim['bytes']} | 200000 |
| Noiseless fidelity | 1 | 1 | 1 |
| Deterministic detectors | 16/16 | 21/21 | all |
| STANDARD acceptance | 0.503075 | {best['acceptance']:.6f} | ≥0.5 |

Both pass the non-grid format/class/correctness checks. **Chip adjacency is not satisfied and routing is unverified**, as requested for this lane. No submission or credentials access occurred. Evidence: `judge_limits.json`; canonical SHA-256 `{limits['rm_circuit']['qasm_sha256']}`; optimized SHA-256 `{lim['qasm_sha256']}`.

## Reproduction and provenance

Run from this directory with `/home/jihoon/competitions/quantumn/.venv/bin/python`, `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`:

1. `build.py` reconstructs the paper and canonical circuit; `paper_eval.py` and `paper_high.py` reproduce the paper metric.
2. `variants.py`, `alap.py`, `dummy.py`, `late_verify.py`, `subsets.py`, `verified_a.py`, `reduced_ta.py` generate the evaluated variants.
3. `score.py va_ta0_PA --mode mc --procs 4 --shots 100000000` reproduces the three-seed judge metric; `regions.py va_ta0_PA 100000000 6` reproduces the noise split.
4. `verify_limits.py rm_circuit va_ta0_PA va_ta02_PA va_TA_PA` reproduces limits and noiseless checks.

Only OS processes were used; no subagents or collaboration tools. Jerry jobs used capped threads and bounded worker pools; local compute stayed at at most two processes. When Jerry's observed load approached 75% of 64 cores, subsequent MC jobs were reduced to four workers; independent six-worker region scoring started only after load fell below 26.

**Cache containment correction:** local xtim checks initially created reference-cache files in repository-root `.xtim_cache`, outside the requested lane. The local run was stopped by exact PID; cache paths now point explicitly under RM_PROTO. `cache_audit.py` identified exact circuit keys and removed 30 lane-specific root cache entries, preserving unrelated entries. `cache_audit.json` records this correction. No source file outside this lane was changed. Generated caches are ignored by this lane's `.gitignore`.
'''
(B/'REPORT.md').write_text(report)
for ext in ['qasm','stim','json']:
 p=B/('_schedule_input.'+ext)
 if p.exists():p.unlink()
print(name,best['mean'],best['acceptance'],crossmc)
