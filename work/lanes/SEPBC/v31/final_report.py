"""Rebuild the final report from receipts, including archived comparators."""
from pathlib import Path
import json,re
V=Path(__file__).resolve().parent;H=V.parent
old={r['stem']:r for r in json.loads((V/'results.json').read_text())};rows=[]
for p in V.glob('*.screen.json'):
 n=p.name.removesuffix('.screen.json');mf=V/(n+'.json');md=json.loads(mf.read_text())if mf.exists()else old[n]['metadata'];r=dict(stem=n,screen=json.loads(p.read_text()),R=md['R'],metadata=md)
 for ext,key in [('.allorders.json','allorders'),('.speed_prediction.json','speed')]:
  f=V/(n+ext)
  if f.exists():r[key]=json.loads(f.read_text())
 for ext,key in [('.judge.log','judge'),('.mc.log','mc')]:
  f=V/(n+ext)
  if f.exists():r[key]=f.read_text()
 m=re.search(r' mean ([\deE+.-]+)',r.get('mc',''));r['mc_mean']=float(m[1])if m else None
 m=re.search(r'acc=([\d.]+)',r.get('judge',''));r['judge_acceptance']=float(m[1])if m else None
 m=re.search(r'\(([\d.]+)s, 1 procs\)',r.get('judge',''));r['judge_seconds']=float(m[1])if m else None
 r['qualified']=(r['allorders']['acceptance']>=.5 and r['screen']['exp_minus_A1']>=.5002 and 'passed=True'in r.get('judge','')and r.get('speed',{}).get('classification')=='FAST'and r['judge_seconds']<=20 and r['judge_acceptance']>=.5)
 rows.append(r)
rows.sort(key=lambda r:r['allorders']['loss']);by={r['stem']:r for r in rows};(V/'results.json').write_text(json.dumps(rows,indent=2))
finals=['guard5_timing_0','guard5_timing_1','guard_joint_2'];best=by[finals[0]];parent=5.557789120876857e-5
assert all(by[n]['qualified']and by[n]['mc_mean']is not None for n in finals)
L=['Status: COMPLETE — R44 finalist below 5e-5. Previous delivery: [REPORT_v31s.md](REPORT_v31s.md).','','## Verified finalists','','| Stem | R / CX | All orders | Acceptance | exp(-A1) | 1e6 judge on zebra | MC3 mean |','|---|---:|---:|---:|---:|---|---:|']
for n in finals:
 r=by[n];a=r['allorders'];z=r['screen'];L.append(f'| [v31/{n}](v31/{n}.qasm) | {r["R"]} / {r["metadata"]["cx"]} | {a["loss"]:.12e} | {a["acceptance"]:.9f} | {z["exp_minus_A1"]:.9f} | {r["judge_seconds"]:.1f}s, PASS, FAST | {r["mc_mean"]:.7e} |')
z=best['screen'];L +=['',f'Choose **guard5_timing_0** by all-orders loss: {(1-best["allorders"]["loss"]/parent)*100:.3f}% below v31s. Cubic parts: second={z["second"]:.12e}, third={z["third"]:.12e}, total={z["total"]:.12e}, c1={z["c1"]:.3e}. Seed-0 acceptance is {best["judge_acceptance"]:.6f} at 1e6 and 0.50064 at 1e8. MC seeds 0/1000/2000 give 4.970669e-5 / 4.782393e-5 / 4.951755e-5. Timing_1 has slightly higher acceptance and an all-orders loss 9.25e-10 higher.',
'', 'The first fast composition, full_timing_0, completed MC at 22:54 KST, before the 23:05 target: all-orders 5.47613043144e-5, MC mean 5.520342e-5. The first R44 finalist A44_timing_10 completed MC around 23:07: all-orders 5.34509514949e-5, MC mean 5.341976e-5. The final five-guard result completed after the first deadline. MAIN decides the submission slot. No submissions, commits, pushes or credentials were used. All lane compute jobs have exited.',
'','## Construction and acceptance budget','',
'Data cells remain [0,20,7,10,3,22,21]; A=[1,14,8,9,2,16,15], B=[6,26,13,11,4,23,27], C=[12,25,19,17,5,29,28]. The prefix retains coherent 2-CX data hops. There are no separate-block measured teleports. The 57-CX correlated B/C resource is retained. A still uses 11 CX, but its X-input pivots change from [1,2,9,15] to [1,2,8,14]; q9/q15 reuse their source-zero measurements. The final circuit has 204 CX, 69 detectors, 86 measurements and 47 native steps.',
'', 'The v30g port includes its q15 terminal instrument, four readout copies, final A14→15 readout edge, measured-Z initialization on q11/q5/q12, and exact-loss timing feedback. R48 timestamps were not copied. The instrument port completes the other commuting q9 fanout before replacing the terminal instrument. Ideal correctness and physical noise were checked on each emitted circuit.',
'', 'The remaining acceptance budget is spent on five WAITPROT storage guards, repriced in actual R44 idle slots. X guards use R(h), CX(data→h), wait, CX(data→h), MZ(h). The Z guard uses RX(h), CX(h→data), wait, CX(h→data), MX(h). Each measurement is a new zero detector. Final native timings are:',
'','| Data / helper | Axis | Reset | First / second CX | Measurement |','|---|---|---:|---|---:|',
'| 0 / 6 | Z | 34 | 35 / 39 | 40 |','| 20 / 19 | X | 15 | 18 / 31 | 32 |','| 7 / 13 | X | 19 | 20 / 23 | 24 |','| 10 / 11 | X | 18 | 19 / 28 | 29 |','| 4 / 5 | X | 17 | 18 / 32 | 33 |',
'', 'All guard CX, reset, measurement and idle noise is included. The sixth proposed guard (data10/helper4, Z) has no native idle slot within the tested window.',
'','| Single guard on A44_feedback_0 | Cubic saved | A1 spent | Saved / A1 spent |','|---|---:|---:|---:|']
for r in sorted(json.loads((V/'waitport_singles.json').read_text()),key=lambda r:r['gain']/r['cost_A1'],reverse=True):L.append(f'| {r["stem"]}: {r["recipe"]} | {r["gain"]:.7e} | {r["cost_A1"]:.7f} | {r["gain"]/r["cost_A1"]:.7e} |')
L +=['', 'Every subset of the five feasible guards was jointly screened. Untimed all-five guards fail acceptance: proxy 0.49812577, all-orders 0.49800612. Timing feedback improves loss and restores proxy acceptance to 0.50081163. Replacing the later q5/q11 initialization by the guard readout worsens loss; q19/q13 reuse gives no useful gain. Eight tested idle-slot repeats of known measured states have zero cubic gain and spend acceptance. The extra q19 measured-zero initialization saves only about 1.7e-9 all-orders on the R45 composition while spending about 0.0085 acceptance; it is not in the final circuit.',
'','## Critical path and round pricing','',
'See [v31/CRITICAL_PATH.md](v31/CRITICAL_PATH.md) for node-level ES/LS and conditional CP certificates. In v31s, a zero-slack suffix runs through the blue-check release and data transfer to q9 source MZ at37, RX9 at38, MX9 at39, A gates40–44 and D→A at45. Reorienting A removes that late q9 X-preparation dependency and yields R44.',
'', 'The final binding suffix is MX1 at27 → R1 at28 → CX2→1 at29 → CX3→2 at30 → CX8→2 at31 → CX2→8 at32 → CX8→9 at33 → CX9→8 at34 → MZ8 at35 → RX8 at36 → MX8 at37 → A encoder38–43 → D→A at44. Final ready slack: A=0, data hops=4, B/C=5, prefix=8. The v31s emitted-order B/C slack was7; the old R48 figure of12 is not the current slack. The guards use some B/C cells earlier without delaying the round. Readout offsets remain R, R+1 and R+2.',
'', 'CP-SAT proves R43 infeasible for the fixed R44 operation set under both tested tail CX-commutation and diagonal-control-phase extensions. This is not a lower bound on all architectures. Removing source checks c54/c56 reaches R43 but worsens all-orders to 5.46174068815e-5; removing c57 is much worse (~6.7e-5). A six-cell rank-three factor plus late q9 fanout needs10+2 CX in the enumerated state graph; four selected R44 witnesses score 5.55661–5.84459e-5. The 20 chosen initializations/shortest witnesses do not exhaust alternative encoders.',
'', 'R45→R44 from the ported design improves all-orders from5.47613043144e-5 to5.34509514949e-5 (−1.31035e-6), including the A change. Controlled delayed-round variants below keep the gate multiset and other timings, placing one terminal resource CX in each added native layer. They measure realizable later-round exposure, not an optimized later-R architecture. Empty global layers are compressed by the native emitter; the initial empty-layer recipe was rejected as an invalid timing experiment.',
'','| Schedule | R | All orders | Acceptance |','|---|---:|---:|---:|']
for n in ['guard5_timing_0','round_delay_45','round_delay_46']:
 r=by[n];L.append(f'| {n} | {r["R"]} | {r["allorders"]["loss"]:.12e} | {r["allorders"]["acceptance"]:.9f} |')
L +=['','## Loss mechanisms','', 'These counterfactual channel removals are nonadditive and are not attainable circuits. Values are cubic loss ×10⁶. No measured block-teleport noise exists. Idle gaps crossing R are grouped with round; operation provenance is retained in each plan.',
'','| Circuit | Full | No pre-round idle | No B/C noise | No A noise | No data-hop noise | Round only |','|---|---:|---:|---:|---:|---:|---:|']
for n in ['full_timing_0','A44_feedback_0','release_54_56','guard5_timing_0']:
 d=json.loads((V/(n+'.ablation.json')).read_text());rs={r['label']:r['total']*1e6 for r in d['rows']};L.append('| '+n+' | '+' | '.join(f'{rs[k]:.6f}'for k in ['all','no_pre_round_idle','no_BC_encoder','no_A_encoder','no_data_hops','only_round'])+' |')
L+=['','Unchanged exact2 second-order physical-pair sums agree with the moment contraction to <1e-15. Dominant final pair classes:','','| Pair class | Loss ×10⁶ |','|---|---:|']
pd=json.loads((V/'guard5_timing_0.pairs.json').read_text())
for k,value in list(pd['pair_classes'].items())[:8]:L.append(f'| {k} | {value*1e6:.6f} |')
L +=['', 'Compared with A44_feedback_0, guards/timing reduce A × pre-round-idle pairs from5.763664e-6 to4.077003e-6, and idle × idle from0.774158e-6 to0.111037e-6. Removing the guards’ own physical noise would save about0.53e-6 cubic. R43 source-check removal mainly admits prefix × idle pairs (0.376757e-6→1.394842e-6) and data-hop × idle pairs (+0.398345e-6); its shorter round does not compensate.',
'','## Built-variant ledger','',
'All emitted physical variants have all-orders prices. Non-emitted subset screens are in guard_subsets.json and four_guards.json. Nonfinal plans are archived in v31/nonfinal_plans.json.gz; numeric receipts remain individual files. Gate/MC absent means not run on that comparator; only the selected finalists require all delivery gates. Δ is all-orders loss minus parent v31s, ×10⁶.',
'','| Variant | R | Cubic | exp(-A1) | All orders | Δ ×10⁶ | Gate / MC |','|---|---:|---:|---:|---:|---:|---|']
for r in rows:
 a=r['allorders'];z=r['screen'];check='PASS/FAST'if r['qualified']else'acceptance fails'if a['acceptance']<.5 or z['exp_minus_A1']<.5002 else'not run';check+=(' / '+format(r['mc_mean'],'.7e')if r['mc_mean']is not None else' / not selected');L.append(f'| {r["stem"]} | {r["R"]} | {z["total"]:.10e} | {z["exp_minus_A1"]:.8f} | {a["loss"]:.12e} | {(a["loss"]-parent)*1e6:+.6f} | {check} |')
L +=['','## Verified versus inferred','',
'Verified: ideal detector/output contract and |c1|<1e-12 for every screened circuit; nearest-neighbor gates and exact emitted schedules; complete all-orders evaluation within its full-barrier, zero-FRAME/no-POSTSELECT scope; final million-shot judge checks, FAST classifications and 3×10⁸-shot MC; conditional R43 CP infeasibility; selected physical-pair sums and noise-removal ablations.',
'', 'Cubic method: unchanged EVAL Model/Engine and exact categorical moment contraction. At69 detectors an active projector reaches bit64 and the engine’s signed-int64 batch input overflows. Lane-local wide_moments.py checks every identity-projector rejection bit as a Python integer and batches the unchanged active-projector engine. No detector constraint or noise channel is removed. It agrees with original lane moments where supported and with256 unmodified scalar Engine.table cases on each of two circuits (max difference <1e-31); see wide_validation.json. No unchanged exact2 --third CLI receipt is claimed for these >64-detector circuits. Independent all-orders and full judge/MC validate the finalists.',
'', 'Not established: a global R43 impossibility, all possible helper/encoder designs, an official submission score or leaderboard result. Neighboring MC differences are statistical; all-orders ranks the candidates. Judge speed is measured on zebra. All-orders omission bounds exclude floating-point roundoff and remain in the result JSON.',
'', 'Reusable tools: build.py, earlier_A.py, near_A.py, feedback.py, waitport.py, guard_subsets.py, four_guards.py, critical_analysis.py and restore_variant.py. Metadata is derived from actual plans, not inherited v30f times. The previous reusable ENDSTATE emitter and mechanism closure remain documented in REPORT_v29c.md.', '']
(H/'REPORT.md').write_text('\n'.join(L));print('Published',len(rows),'priced variants and',len(finals),'verified finalists')
