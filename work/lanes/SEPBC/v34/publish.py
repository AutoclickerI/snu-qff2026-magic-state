"""Publish verified results and the scope of the unsuccessful R43 search."""
from pathlib import Path
import json,re
V=Path(__file__).resolve().parent;H=V.parent
old={r['stem']:r for r in json.loads((V/'results.json').read_text())}if(V/'results.json').exists()else{}
rows=[]
for p in V.glob('*.screen.json'):
 n=p.name.removesuffix('.screen.json');mdfile=V/(n+'.json');md=json.loads(mdfile.read_text())if mdfile.exists()else old[n]['metadata'];r=dict(stem=n,metadata=md,screen=json.loads(p.read_text()),allorders=json.loads((V/(n+'.allorders.json')).read_text()))
 for ext,key in [('.judge.log','judge'),('.mc.log','mc')]:
  q=V/(n+ext)
  if q.exists():r[key]=q.read_text()
 q=V/(n+'.speed_prediction.json')
 if q.exists():r['speed']=json.loads(q.read_text())
 m=re.search(r' mean ([\deE+.-]+)',r.get('mc',''));r['mc_mean']=float(m[1])if m else None
 m=re.search(r'\(([\d.]+)s, 1 procs\)',r.get('judge',''));r['judge_seconds']=float(m[1])if m else None
 m=re.search(r'acc=([\d.]+)',r.get('judge',''));r['judge_acceptance']=float(m[1])if m else None
 r['qualified']=('passed=True'in r.get('judge','')and r.get('speed',{}).get('classification')=='FAST'and r['judge_seconds']<=20 and r['judge_acceptance']>=.5 and r['allorders']['acceptance']>=.5005)
 rows.append(r)
rows.sort(key=lambda r:r['allorders']['loss']);by={r['stem']:r for r in rows};(V/'results.json').write_text(json.dumps(rows,indent=2))
finals=['checked16_timing_0','layer26_timing_0','layer_26_R44_m2'];assert all(by[n]['qualified']and by[n]['mc_mean']is not None for n in finals)
base=json.loads((V/'baseline_v34m_allorders.json').read_text());best=by[finals[0]];b=best['screen'];fresh=by['decoder0']
L=['Status: **R43 target not achieved. Verified R44 improvement delivered; all jobs exited.** Prior result: [REPORT_guard5_R44.md](REPORT_guard5_R44.md).','','## Verified finalists','','| Stem | R / CX | All-orders 1−F | All-orders acceptance | exp(-A1) | Judge 1e6 on zebra | MC3 mean |','|---|---:|---:|---:|---:|---|---:|']
for n in finals:
 r=by[n];a=r['allorders'];z=r['screen'];L.append(f'| [v34/{n}](v34/{n}.qasm) | {r["metadata"]["R"]} / {r["metadata"]["cx"]} | {a["loss"]:.12e} | {a["acceptance"]:.9f} | {z["exp_minus_A1"]:.9f} | PASS, {r["judge_seconds"]:.1f}s, FAST | {r["mc_mean"]:.7e} |')
L +=['',f'Choose **checked16_timing_0** by all-orders expectation: {(1-best["allorders"]["loss"]/base["loss"])*100:.3f}% below v34m ({base["loss"]:.12e}) and {(1-best["allorders"]["loss"]/fresh["allorders"]["loss"])*100:.3f}% below FRESH’s decoder port. Its cubic parts are second={b["second"]:.12e}, third={b["third"]:.12e}, total={b["total"]:.12e}; c1={b["c1"]:.3e}. Native depth47, 207 CX, 68 detectors, 84 measurements. The acceptance floor0.5005 is met.',
'', 'Best MC seeds0/1000/2000: 4.057677e-5 / 4.262330e-5 / 4.210989e-5; acceptances0.50090 / 0.50078 / 0.50083. The million-shot gate acceptance is0.501715. The variant without the added q16 check has a lower sampled MC mean, but the all-orders expectation ranks the checked circuit first; the 6.37e-8 expectation difference is much smaller than MC uncertainty.',
'', 'FRESH’s guard5_timing_0_a_decode is the rebase, credited to FRESH/reviewer6: all-orders4.39344936172e-5, acceptance0.500899908, MC mean4.377908e-5. The local decoder0 copy is byte-identical; native noisy blocks and the million-shot seed-0 result agree. Its MC receipt is reused with provenance in fresh_rebase_proof.json. The three finalists above have their own new judge/speed/MC runs.',
'','## What changed','',
'Data and final roles are unchanged: D=[0,20,7,10,3,22,21], A=[1,14,8,9,2,16,15], B=[6,26,13,11,4,23,27], C=[12,25,19,17,5,29,28]. The guard5 prefix, its five waiting-data guards, coherent data-hop plan and correlated 57-CX B/C resource are retained. The successful new encoder uses12 CX and X pivots[14,8,9,16]. It prepares the same |+L> state; it was synthesized with the actual cell releases, not ported from a free-space schedule.',
'', 'All data-source checks are retained, including c54/c55/c56/c57 and the blue outputs c64/c67. Old A-input X verifications on q1/q2/q8 are not source checks: q1/q2 become Z inputs in the new encoder, and the whole new preparation is independently priced. The best adds a native known-X check on q16 in its idle slot at40, after RX16 at39 and before CX16→15 at41. q16’s source-zero MZ c55 remains at38.',
'','| Native step | A encoder CX |','|---:|---|','| 37 | 8→2 |','| 38 | 14→8, 2→1 |','| 39 | 1→2, 9→8 |','| 40 | 8→2, 9→15 |','| 41 | 8→9, 16→15 |','| 42 | 9→8, 15→14 |','| 43 | 14→8 |',
'', 'Decoder compatibility is explicit: D10→A9 and D21→A15 run at43, CX9→15 at44, CX8→9 at45, then MX8 and MZ9/MZ15 at46. The other five D→A couplings and all B→C checks run at44. The decoder adds no native step relative to the guard5 readout tail. Every new pivot is reset into its preparation basis; the successful variants do not reuse the troublesome pre-blue random X state.',
'','## R43 work and closure scope','',
'The detailed node/edge timing certificate is [v34/CRITICAL_PATH.md](v34/CRITICAL_PATH.md). On the initial R44 decoder port, q8’s source check at35, RX at36, input verification at37, and the A encoder38–43 bind the round. On the new encoder, parallel critical branches meet at CX8→2 at37: q8 is released/checked at35 and initialized at36; the blue q2 output is measured at35 and reset in Z at36. The encoder then occupies the central cells through43, forcing the remaining data couplings at44. Final component ready slack: A0, data-hop completion4, B/C5, prefix8. Terminal T/T† operations are ready by31 in the emitted-order earliest schedule (13 steps of ready slack).',
'', 'A correct R43 construction exists by removing the reset before the blue q2 check and reusing its earlier X measurement. That shifts Bell preparation29→28 and the q8 release35→34. It fails the speed requirement. With the original A encoder, XTIM predicts169.05s/1e6; retiming gives174.83s/1e6. With the new12-CX encoder and q2 later reset in Z, it still predicts146.31s/1e6. No million-shot gate or MC was wasted on these SLOW recipes.',
'','| Tested family | Measured or proved result | Exact scope |','|---|---|---|',
'| Fixed-operation retiming | R43 INFEASIBLE with the ordinary reset; R43 constructible with pre-blue X reuse | Tested global CX/control-phase commutations; no gate resynthesis |',
'| Unitary A preparation | No R42/R43 witness;120 R44 algebraic witnesses replayed | 11811 rank-four subspaces,35 input coordinate sets,95 matching layers including empty, no CX-count cap; two routes and five initialization modes at recorded release bounds |',
'| Route through q14 instead of q9 | Full R44 circuits built/priced; no R43 state-prep witness | Corrected prefix-release order, same final geometry |',
'| One UVUV dirty bus | No R43 witness in132 recipes | One macro through data3/7/10, specified directions/start times; endpoints reserved during the macro |',
'| Measurement-assisted prep | No R43 witness;41 R44 calibration branches replayed | Rank5→4 by one Z measurement, or rank4→3 then one X preparation; no external helpers or multiple measurements |',
'| Earlier D→A during A encoding | No R43 assignment | 168 invertible syndrome maps HM=NH on the selected fresh-input R44 witnesses, not every possible gate path |',
'| Four staggered branch schedules | Schedule-infeasible | Only the four exact branch recipes tested |',
'| Permuting the four blue-q2 data gates | Schedule-infeasible or ideal detectors become random | All24 permutations with the existing detector contract; no detector removed to pass |',
'', 'These negatives do not prove a global R43 lower bound. More general Clifford encoders, multiple measured helpers, different endpoint layouts and a larger prefix-instrument redesign remain outside the search. Measurement calibration verifies the algebraic zero-outcome CSS update, not a complete emitted judge circuit. A q14 route ordering bug was corrected before final witnesses and full-circuit prices were generated; final search_validation.json checks their release times, disjoint layers and target subspace independently.',
'','## Price of the decoder and the R step','',
'All values below are full all-orders expectations. The no-decoder ablations keep the early data couplings and restore the original A-Z detector basis; they are matched controls, not separately optimized no-decoder designs.',
'','| Variant | R / depth | With decoder | Without decoder | Runtime status |','|---|---|---:|---:|---|']
for n,nd in [('decoder0','decoder0_no_decoder'),('reuseblue_0_R43','reuseblue_0_R43_no_decoder'),('checked16_timing_0','checked16_timing_0_no_decoder'),('layer_26_R44_m2_reuse_R43','layer_26_R44_m2_reuse_R43_no_decoder')]:
 r=by[n];L.append(f'| {n} | {r["metadata"]["R"]} / {r["metadata"]["native_depth"]} | {r["allorders"]["loss"]:.12e} | {by[nd]["allorders"]["loss"]:.12e} | {r.get("speed",{}).get("classification","not timed")} |')
L +=['', 'The new encoder is poor without the logical-X flag:8.68097e-5 versus4.14605e-5 with it. This is why judging encoders only by their old unflagged danger score misses the improvement. The actual R43 reuse constructions also alter prefix noise and timing, so the earlier free-space estimate of1.4e-6 saved per tick cannot be applied to them. The tested R43 recipe loses fidelity to its R44 parent as well as failing speed.',
'','## Loss split','', 'Values are cubic loss ×10⁶. Channel-removal ablations are nonadditive counterfactuals, not attainable circuits. There are no measured block teleports. Idle gaps crossing R are grouped with round.',
'','| Circuit | Full | No pre-round idle | No B/C noise | No A noise | No data-hop noise | Round only |','|---|---:|---:|---:|---:|---:|---:|']
for n in ['decoder0','checked16_timing_0','layer_26_R44_m2_reuse_R43']:
 d=json.loads((V/(n+'.ablation.json')).read_text());z={x['label']:x['total']*1e6 for x in d['rows']};L.append('| '+n+' | '+' | '.join(f'{z[k]:.6f}'for k in['all','no_pre_round_idle','no_BC_encoder','no_A_encoder','no_data_hops','only_round'])+' |')
L +=['', 'The unchanged exact2 second-order pair contraction agrees with the lane moment contraction to<1e-15. The decoder-matched new encoder eliminates A×pre-round-idle (1.550352e-6), A×round (0.728889e-6) and A×B/C (0.337778e-6) contributions to evaluator precision. A×prefix falls0.504444e-6→0.006667e-6. Second order improves3.813456e-5→3.500154e-5, while third order increases5.543862e-6→6.177157e-6. All-orders confirms the net gain.',
'', 'The final round×round pair component is3.054444e-5, about87.27% of the remaining second-order loss. This is a component of this round instrument, not a universal lower bound. Remaining B/C self pairs contribute2.18e-6. The full physical-pair classes and examples are in checked16_timing_0.pairs.json.',
'','## Complete priced ledger','',
'Every ideal-valid emitted circuit has an all-orders price. Failed ideal/schedule recipes are in the search/build JSON files. Nonfinal plans are archived in v34/nonfinal_plans.json.gz; numeric receipts remain separate. Gate/MC “not selected” means it was a comparator, not a delivered finalist.',
'','| Variant | R | Cubic 1−F | All orders | Acceptance | Gate / MC |','|---|---:|---:|---:|---:|---|']
for r in rows:
 n=r['stem'];z=r['screen'];a=r['allorders'];status='PASS/FAST'if r['qualified']else'SLOW'if r.get('speed',{}).get('classification')=='SLOW'else'acceptance<0.5005'if a['acceptance']<.5005 else'not selected';status+=(' / '+format(r['mc_mean'],'.7e')if r['mc_mean']is not None else' / no MC');L.append(f'| {n} | {r["metadata"]["R"]} | {z["total"]:.10e} | {a["loss"]:.12e} | {a["acceptance"]:.9f} | {status} |')
L +=['','## Verified versus inferred','',
'Verified: full ideal correctness and |c1|<1e-12 for each priced circuit; grid adjacency and emitted native timing; all-orders acceptance≥0.5005 for each finalist; unchanged million-shot judge PASS, ≤20s/1e6 on zebra, XTIM FAST and3×1e8-shot MC. Source checks and decoder timing are audited in the final metadata. Independent search replay and conditional CP certificates are in the lane. No submissions, commits, pushes, credentials, subagents or writes to other lanes were used.',
'', 'Cubic values use the previously validated lane moment contraction on unchanged EVAL Model/Engine, with exact wide-integer identity-projector rejection before active-projector batching. They are not claimed as unchanged exact2 --third CLI receipts beyond its integer-width scope. Ranking uses the byte-copied current MAIN/sparse evaluator, within its full-barrier/no-FRAME/no-POSTSELECT scope. Independent judge/MC checks validate the finalists. Sparse omission bounds do not include floating-point roundoff.',
'', 'Unverified/open: a fast R43 construction, a global architecture lower bound, multi-helper/general-Clifford synthesis, and any official submission outcome. All jobs exited. Reproduction uses the saved requests, C++ finite-state engines, assemble_layers.py, feedback.py, input_checks.py, audit.py and restore_variant.py. The previous ENDSTATE emitter remains available; this task did not reopen its old exposure-limited recipes.', '']
(H/'REPORT.md').write_text('\n'.join(L));print('Published',len(rows),'priced circuits; R43 remains unresolved; three verified R44 finalists')
