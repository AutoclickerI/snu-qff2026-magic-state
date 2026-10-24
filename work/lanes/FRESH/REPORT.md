# FRESH

## Standalone speed screen for every lane

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -B work/lanes/FRESH/general_atoms.py work/lanes/MAIN/v36b
```

Add `--details` for each offending X/Z atom and its first failing normalized gate. Output is one JSON record: `prediction` (FAST/SLOW/REJECTED), `general_atoms`, source hash, elapsed seconds, and offending gates. No shot sampling or installed-engine changes. The C++ helper builds once in FRESH; all subsequent work is read-only. A zero-shot installed-engine compile distinguishes PPR retry from outright class rejection. Typical warm runtime on the eight fixtures: **0.075–0.273s**. Source: `general_atoms.py`, `general_atoms.cpp`; machine receipts: `r37/predictor_validation.json`.

Validation: v35b0 atoms/5.97s, SX212/176.60s, v24 1/113.09s, q8 reuse127/129.38s, ENDSTATE full reuse103/117.45s, safe ENDSTATE0/4.965s, direct v35b q8 port118/218.53s, v36b0/measured FAST. All eight predictions match. These are measured reference timings on the same circuits; classification detects the exact dispatch path, not a universal proof of <=20s for arbitrary large circuits. Finalists still receive the XTIM timing gate.

Current work tests whether the later cultivation record can replace the first flag, and whether moving the measured reuse across the last relevant T can eliminate the non-Pauli residual without sacrificing ideal correctness or single-fault protection. Every proposed instrument change retains those tests.

Status: ACTIVE — P72 on v36b; standalone general-atoms predictor delivered; acceptance floor0.5002.

<!-- r35 verified start -->
## Verified improvements (ranked by all-orders)

| Circuit | All-orders loss | Acceptance | Judge seconds / XTIM | MC0 / 1000 / 2000; mean |
|---|---:|---:|---|---|
| [r35/sepbc_reset_40_41](r35/sepbc_reset_40_41.qasm) | 4.1293260532646e-05 | 0.500603698545 | PASS 2.91s / FAST 5.24s | 4.041815e-05 / 4.19884e-05 / 4.100048e-05; **4.1135677e-05** |
| [r35/sepbc_reset_40_41_42](r35/sepbc_reset_40_41_42.qasm) | 4.1293260852693e-05 | 0.501438639169 | PASS 2.78s / FAST 4.01s | 4.07112e-05 / 4.186887e-05 / 4.04464e-05; **4.1008823e-05** |
| [r35/sepbc_reset_39_40_41_42](r35/sepbc_reset_39_40_41_42.qasm) | 4.1293323277639e-05 | 0.502275276528 | PASS 2.65s / FAST 4.45s | 4.266645e-05 / 4.055366e-05 / 4.169966e-05; **4.1639923e-05** |
| [r35/finish_long](r35/finish_long.qasm) | 4.3775984368318e-05 | 0.500670701215 | PASS 2.46s / FAST 3.44s | 4.520524e-05 / 4.243429e-05 / 4.360624e-05; **4.374859e-05** |
| [r35/echo_combo_15_20](r35/echo_combo_15_20.qasm) | 4.3794244281304e-05 | 0.502169741553 | PASS 2.42s / FAST 3.53s | 4.435724e-05 / 4.431438e-05 / 4.472478e-05; **4.4465467e-05** |
| [r35/echo_combo_10_15](r35/echo_combo_10_15.qasm) | 4.379866179064e-05 | 0.503517231406 | PASS 3.16s / FAST 5.25s | 4.388779e-05 / 4.509719e-05 / 4.448315e-05; **4.4489377e-05** |
| [r35/feedback_i128_t30](r35/feedback_i128_t30.qasm) | 4.3932872229262e-05 | 0.509298490873 | PASS 2.82s / FAST 4.60s | 4.468389e-05 / 4.506063e-05 / 4.407154e-05; **4.4605353e-05** |

All rows passed exact ideal acceptance1/loss0, detector determinism, no harmful single fault, unchanged judge1e6, XTIM FAST and three seeds of100M shots. Ranking is all-orders; MC values remain separate.
<!-- r35 verified end -->








## Verified inherited decoder finalists

| Stem | All-orders loss | Acceptance | CX / R / native depth | Judge 1e6 | MC3 |
|---|---:|---:|---|---|---|
| guard5_timing_0_a_decode | 4.393449361722461e-5 | .5008999079248619 | 206 / 44 / 47 | PASS, acceptance .500306, 3.5 s | 4.456018 / 4.328335 / 4.349371 e-5; mean 4.377908e-5 |
| guard5_timing_1_a_decode (MAIN/v35a) | 4.393527676042078e-5 | .5012369386242203 | 206 / 44 / 47 | PASS, acceptance .501503, 3.2 s | MAIN re-draw campaign in progress; no FRESH MC3 receipt yet |

These use reviewer 6's A partial decoder rebuilt on SEPBC's actual R44 schedule: CX9->15 at44, CX8->9 at45, A8 MX and A9/A15 M at46, conjugated detector rows and the deterministic flag. The terminal q15 instrument is preserved. ST2 independently obtained identical all-orders values with a circuit-native rebuild. Earlier wording calling ST2's method a textual merge was incorrect. Native ticks run0–46, hence depth47; the handoff used48.

The first port accidentally delayed A15 to47, adding a complete output-data idle tick: all-orders loss9.287e-5. Restoring A15 to46 avoids that exposure. Its CX14->15 at45 commutes with the decoder gates.

Earlier claims that echo additions were ruled out by acceptance were inference without pricing, not a closure. The relevant remaining budget is all-orders acceptance minus .5005: .000399908 for _0 and .000736939 for _1. The prior guard_joint_2 decoder price4.490225e-5/acceptance.510896 was imported from ST2, not a FRESH build.

## Current experiments and scope

`round35.py` rebuilds native operations and writes clean metadata, exact ideal/single-fault certificates, all-orders receipts and XTIM probes in `r35/`. It uses MAIN's unchanged sparse contraction with reviewer6's SX-capable frontend; each physical SX/SXdg retains its native depolarizing channel. A baseline reproduction checks the frontend substitution.

- Full SX/SXdg layer on all seven data qubits: ideal acceptance1, loss0, six output stabilizers+1, no harmful single fault (c1=3.09e-19). All-orders **4.29707586343367e-5**, acceptance **.5012579553842883**, but **SLOW:191.1 s per1e6** in the standard XTIM predictor. The gain is2.20% on v35a. Baseline with the SX-capable frontend reproduces v35a's loss and acceptance exactly.
- All128 fixed-A SX subset masks were checked exactly. Only masks0 and127 preserve deterministic detectors and ideal acceptance1/loss0; every proper nonempty subset fails. Certificate: `r35/sx_subset_certificate.json`. This is a closure for fixed A checks and paired physical SX/SXdg on a subset, not for re-encoded A resources.
- All32 code-preserving SX sign/early-output variants remain SLOW. Seven nonempty subsets of the three reused resource MX pivots converted to RX also remain SLOW (all-three147.5 s/1e6). These probes use5000 shots twice; full-layer confirmation uses50000 twice. This rules out those rewrites, not all SX representations.
- Alternate flag on A9 (CX9->15 then CX9->8, exchanging final A8/A9 measurement bases and detector bit labels): exactly the same all-orders physics as v35a, FAST4.44 s/1e6. Combining it with SX has the same4.29707586343367e-5 loss and remains SLOW196.3 s/1e6.
- COMP29's terminal CX28->29 needs the same tick as two of v35a's C readout copies. Rebuilding with those two copies removed gives **4.40382889022135e-5**, acceptance **.503649603857789**, FAST5.47 s/1e6, ideal/single-fault PASS. It loses1.03e-7 but frees.002412665 acceptance; retain as a possible acceptance trade, not a finalist.
- BCFB encoders00000/00002 require q15 one tick before its current known-zero readout. Reusing the q15 zero state without that readout fits, but loses badly: **5.62183411406548e-5**, acceptance **.502955314246236**, FAST; removing three new prep checks gives5.63371797167250e-5/.505142622272356. No harmful single faults. Subsequent evidence corrected the initial q15 diagnosis: the q9 known-zero boundary flag had also been removed. Restoring that one flag in the newer BCFB encoder13 changes5.55789e-5 to **4.40217102326814e-5**, acceptance.501404518847142. This identifies q9 boundary rejection as the dominant lost protection. The repaired port remains worse than v35a.
- In progress: all-orders timing feedback over every operation's per-wire slack; latest external encoder integration. The timing runner uses the exact Laurent degree bound in idle survival (degree<=2 for CX, <=1 for a one-qubit instrument), evaluates enough contraction nodes, and directly re-evaluates any selected unsampled optimum. Local unitary timing is noise-identical by depolarization covariance. It logs all direct prices and interpolation coverage; it is a coordinate search, not a global schedule optimum certificate.

Prior architecture experiments, prices and mechanisms are in [REPORT_prior_architecture.md](REPORT_prior_architecture.md). The current target is a fully gated improvement over v35a, not the obsolete below5e-5 threshold, which these decoder ports already meet.

## Completed timing and integration campaign

The full single-coordinate sweep completed with158 direct all-orders evaluations. Final timing-only `r35/feedback_best`: **4.393213150459585e-5**, acceptance **.5130332404367713**, 206CX/R44/depth47. Retained moves: M21 t32->36, M22 t28->34, R13 t25->33, M16 t24->30, R19 t13->17, M19 t12->10, M20 t2->7. Each direct candidate passed ideal checks; final all-single-fault checks accompany promoted descendants. These changes remove idle exposure of known prepared states. The loss gain is small; restored acceptance is the main benefit. One pass is not a coordinate optimum after all subsequent changes.

Echo tests on that result (all-orders):

| Added checks | Loss | Acceptance | Decision |
|---|---:|---:|---|
| q15/q21 X20–29 | 4.38010810233578e-5 | .507150895990 | improving |
| q20/q26 Z20–31 | 4.39252213188724e-5 | .507994310490 | improving |
| q10/q16 X20–28 | 4.39295322215377e-5 | .509357429641 | improving |
| q15/q21 + q20/q26 | 4.37942442813041e-5 | .502169741553 | fully gated above |
| q10/q16 + q15/q21 | 4.37986617906404e-5 | .503517231406 | fully gated above |
| all three | 4.37918244409386e-5 | .498571766236 | acceptance fail |
| longer q15/q21 X19–29 + q20/q26 Z18–31 | 4.37759843683178e-5 | .500670701215 | fully gated: MC4.374859e-5 |

Here a window includes helper reset at its start, two CXs at start+1/end-1 and measurement at its end; actual edge times are in the candidate recipe. Helpers are released cells and are measured before resource reuse. These are the ST2 echo construction rebuilt on the feedback schedule. Adding another A1 or q6 same-basis prep check changes loss by less than floating roundoff while lowering acceptance below.5005; those checks are rejected.

Six echoed-CX pairs borrowing live A9 in q10's late idle were ideal-correct but worse (best4.40212380859009e-5). Borrowing a prepared code-block qubit without a dedicated helper does not provide the same clean parity monitor.

Further SX controls: H–S–H decomposition on all7, the early2, or late5 inputs all remain SLOW (about198–209s/1e6), despite preserving the ideal/single-fault contract. No FAST implementation of the4.29708e-5 SX gain has been demonstrated.

External-lane check: COMP29's latest `g_ro_00010` is CX14->15, already present in v35a at t45, so adding it again would cancel the existing check. The CX28->29 trade was rebuilt and priced above. SEPBC's R43 measured-q2 reuse witness is reported SLOW169s/1e6 and worse than v35a in all-orders; it is not promoted. ENDSTATE has not reported a newly gated improvement yet.

Independent exact2 --third initially failed because72 detector bits overflow its int64 batch array. The original failure log is preserved. A lane-local wrapper widens only the detector-mask storage to Python integers; it leaves projection arithmetic and the exact2 evaluator unchanged. The widened-storage rerun completed: c1=3.0901e-19, second3.813456124749e-5, third5.40184e-6, total4.35364e-5 (third/total printed precision), exp(-A1)=.50086. The wide batch was independently compared with scalar evaluation on six signatures including detector bits65/70/71; maximum discrepancy1.12e-16. All-orders ranking and official gates are unaffected by that representation repair.

## Best complete circuit and reproducibility

Delivery: [best.qasm](best.qasm), [best.json](best.json), byte-identical QASM to `r35/finish_long`. **210CX, R44, native depth47,72 detectors**. All-orders loss **4.3775984368317795e-5**, acceptance **.5006707012148813**, sparse cutoff omission bound1.198e-14 (does not bound floating roundoff). Gain over v35a: **0.36256%**.

Judge1e6 seed0: **PASS**, loss4.095617689072667e-5, acceptance.500535,2.4563s on zebra. XTIM: **FAST3.4405s/1e6**. Three100M-shot seeds0/1000/2000: **4.520524e-5 / 4.243429e-5 / 4.360624e-5**, mean **4.374859e-5**; acceptances.50072/.50066/.50062. Ideal acceptance1/loss0, all72 detectors deterministic, all six output stabilizers+1, native schedule match, nearest-neighbor CX and no harmful single fault verified.

Exact composition: v35a + the seven timing moves listed above + q15/q21 X echo (reset21@19, CX15->21@20 and28, M21@29, singleton flag) + q20/q26 Z echo (RX26@18, CX26->20@19 and30, MX26@31, singleton flag). The subsequent measured initializations of these helpers are retained. No source detector was removed. Geometry and logical prefix action are unchanged except the certified timing feedback.

Verified scope: finite SX family exclusions, native ideal/single-fault certificates, all-orders prices, official judge and measured local runtime/MC. Not proved: a global timing optimum, a global impossibility of FAST SX, or any server timing guarantee. Remaining leverage: a different SX-compatible A instrument/resource or an earlier round architecture; the tested fixed-A partial SX masks fail exact determinism.

Exact-third receipt: `r35/finish_long.exact_wide.log` and `.json`; second-order loss 3.813456124748494e-05, exp(-A1) 0.5008567011544917. The leading pair remains q10 Z idle at t35–41 × A encoder CX at t41/42 (1.549e-7 per listed pair); final data idle pairs contribute1.111e-7 each. The remaining loss is dominated by round/readout and late data exposure.

## Current r36 engine diagnosis (installed judge unchanged)

The user handoff attributed `restore_181_182_188` to FRESH; repository evidence identifies it as ST2's `v35/tightened/restore_181_182_188`, now MAIN/v35b. It is the new baseline,210CX/R44/depth47. All-orders SX port on v35b: **4.26691144433378e-5**, acceptance **.5017063522710992**, ideal and single-fault PASS, but SLOW176.8s/1e6. The older v35a SX result was4.29707586343367e-5.

**Measured exact-engine rule:** the circuit-wide `has_general` flag is set when any propagated noise X/Z atom needs the PPR retry (leaves the intermediate diagonal-plus-Pauli representation). `process_shot_` sends **every nonzero-event shot** to `process_shot_general_`, before the pattern memo branch. That path clones the bare state and sequentially measures conjugated observables. It is not a distinct-plan-per-shot problem. Installed binary disassembly checks byte at offset0x4e8 AND `nev>0`; GDB counts on the unmodified installed .so confirm it.

| Circuit | Static failed standard atoms | Exact shots traced | General-path shots | Pattern builds / replays | Exact s/1e6 (10k probe) |
|---|---:|---:|---:|---|---:|
| v35b |0|1000|0|43 /170|5.97|
| v35a SX |212|1000|552|0 /0|176.60|
| v24 |1|1000|569|0 /0|113.09|
| q8 reuse v25k |127|1000|531|0 /0|129.38|

The Python `CompiledDetectorSampler._program` has only `sample`, `ok`, `errors`, `ref_error`; `_run` returns scalar status and record arrays, **no plan counters**. `plans/plan_hits/plan_misses/ppr_plans/fallback_shots/exact_shots` belong to the separate `TwirlSampler.channel_report()`. On10000 shots: v35b123 plans/123 misses/0 PPR; SX1 diagonal plan/1 miss/128 PPR plans; v24125 plans/125 misses/0 PPR. All have twirl fallback_shots=exact_shots=0. Therefore those counters cannot predict the production exact runtime. Twirl sample_barrier refuses SX's non-diagonal state-retention case; q8 reuse's twirl diagnostic hits a conjugated-generator Hermiticity exception, while the official exact sampler runs. These diagnostic failures are preserved, not used as circuit gate failures.

Diagnostic env timing (s/1e6,10000 shots): v35b default5.97 / memo-off12.81 / force-full807.79; SX176.60 /187.31 /586.20; v24113.09 /141.29 /414.47. These are diagnostic switches only; no official gate uses them.

Source confirmation: upstream tagv3.1.3 commit89c550ffe5aef69548a78ca42d819c3326cd5f5c was fetched read-only into `xtim_source/`. `cpp/src/framed_sampler.cpp` around1766–1778 contains the branch and1274 onward the clone path. The installed disassembly matches that branch. The requested docs exist in this checkout, not in the installed wheel's RECORD; branch_frames/frame_cosets describe the separate retained-state/twirl API. `r36_trace.py` reads installed-engine function entries; `r36_static.py` uses the installed normalized/deferred signature and a standalone class-propagation diagnostic (all phase signs irrelevant to class membership). It matches all four traced flags; it is not substituted for physics evaluation.

Mechanism-guided experiments: diagonal S/Sdg transversal gauges have0 failed atoms and are FAST, but all-orders5.062507125771568e-5 loses. H/SX/SXdg on data expose about210 residual atoms and are SLOW. An equivalent Y-check can instead prepare A in|0_L>, use A->D with diagonal Sdg/S on data, and dualize the terminal A decoder. To preserve the original depth its A couplings must occur at43, phase restoration44, B coupling45. The fixed-release523-encoder library had no fit; moving the actual known-zero q16 source read earlier is the first model relaxation. No global architecture closure is claimed.

## r36 resource and scheduling follow-up

The fixed seven-cell A0 model (arbitrary matching CX layers, all35 input-pivot choices, endpoint checked up to GL(3,2), source flags retained) is infeasible for A coupling at43 with the original releases. Allowing the q16 known-zero read at37 did not change that scoped verdict. Dropping the five zero-source flags, while resetting the two reused X sources for FAST, is also infeasible by43. These are fixed-layout/reset/release models, not circuit lower bounds.

A global commuting-prefix schedule was then optimized with CP-SAT while freezing B/C resource gates. It preserves every detector and exact operator commutation, including CX with a common control/target and Z phases through CX controls. It releases A cells at {1:35,14:27,8:35,9:37,2:35,16:31,15:39}, versus their old late releases. The check-resource synthesis still requires44 with safe reuse of known-zero sources, or45 with fresh resets on all seven A cells. The45 fresh-reset witness uses11CX; complete models/statuses are in `r36/dual_sat_*.json` and logs. The positive45 witness checks that the endpoint model is not simply inconsistent.

Measurement-based alternative: an encoded identity teleport from old data to A0 fits the retimed sources atR44 and uses only a logical Z frame from the old data's seven MX outcomes. Its ideal state/detectors pass, but the full single-fault audit fails: unverified A0 encoder X hooks produce accepted multi-qubit output errors. Several prior-prefix X faults also become harmful. This architecture needs a verified teleport resource; the former B check acts on the old data and does not verify those output A faults. No score/gate improvement is claimed for that circuit.

The commuting-prefix witness is also being priced with the **original A+ resource and A decoder restored**, so the usable timing work is not discarded with the failed teleport architecture.

## r36 completed FAST rewrite and better composition

`r35/dualY_delayed` is a complete fault-tolerant Y-check realization with A0, A->D at44, diagonal Sdg/S on data at43/45, B->D at46 and a dual A decoder. It is **FAST12.64s/1e6** in the10k predictor, zero standard-propagation failures, ideal acceptance1/loss0, no harmful single fault. Its cost is fatal: **all-orders7.158724524641037e-5, acceptance.4948539353907606**, depth48. This proves the Y-check can avoid the general engine path; it does not preserve the original SX circuit's noise price. One added schedule tick, changed A resource/flag errors and prefix retiming are all included; they have not been isolated into additive costs.

The standalone encoded teleport likewise has0 propagation failures (FAST class), but its first-order loss is nonzero because its A0 resource is unverified. `r36/teleport_single_faults.json` preserves every harmful single and its weight. It is not a contender.

ENDSTATE diagnostic transfer: `region2_d11_reuseA` has103 standard-propagation failures and458/1000 exact general-path shots; its safe `region2_k56_A2_safe_dest` counterpart has0 failures. Thus the same rule explains that source-reuse slowdown. Their geometry/output placement differs from v35b, so these are engine diagnoses, not claims of a direct circuit port.

A new SEPBC finalist appeared during this work: `v34/checked16_timing_0`, all-orders4.146051958326e-5, with its twelve-CX A encoder and source checks retained. Rebuilding FRESH's seven timing changes and the two ST2 echoed checks on it gives4.129309724486993e-5 but acceptance.498936936809. Applying the v35b initial-MZ-to-reset acceptance trade makes it feasible:

| MZ source bits replaced by reset | All-orders loss | Acceptance | Judge1e6 / FAST |
|---|---:|---:|---|
|40,41|**4.129326053264635e-5**|**.5006036985453153**|PASS acc.500648,2.91s; FAST|
|40,41,42|4.129326085269341e-5|.5014386391688026|PASS acc.501428,2.78s; FAST|
|39,40,41,42|4.129332327763941e-5|.5022752765284105|PASS acc.502347,2.65s; FAST|

All three are211CX/R44/depth47, ideal/single-fault PASS and use the unchanged MAIN sparse contraction. The numerical difference between the first two is only3.20e-13; it is reported rather than treated as a meaningful Monte Carlo separation. Their acceptance budgets differ materially. The first two three-seed100M MC runs completed and are promoted above; the wider-margin four-reset comparator also completed (MC mean4.1639923e-5). These FAST candidates beat the SLOW v35b SX target4.26691144433378e-5 through a different resource/composition improvement. The original coherent data-SX layer itself has not been made FAST.

## Current best delivery (r36)

`best.qasm/json` = `r35/sepbc_reset_40_41`: **4.129326053264635e-5**, all-orders acceptance **.5006036985453153**, **211CX/R44/depth47**, judge1e6 PASS (acceptance.500648,2.910s), XTIM FAST5.24s/1e6. MC100M seeds0/1000/2000: **4.041815e-5 /4.198840e-5 /4.100048e-5**, mean **4.1135677e-5**. This is **5.64% below v35b** and **3.23% below its SLOW SX port**. The improvement comes from the SEPBC A encoder plus the measured timing/protection composition, not from making the original SX layer fast.

`best_margin.qasm/json` keeps extra acceptance by also resetting initial q20 instead of measuring it: all-orders4.129326085269341e-5, acceptance.5014386391688026, MC mean4.1008823e-5, PASS/FAST. It costs only3.20e-13 in the computed loss, a negligible practical separation; both complete results are provided.

Best QASM SHA256 and full local recipe/verification are embedded in the accompanying JSON. Frozen bases and installed-code hashes are in `r36/inputs/` and `r36/installed_manifest.json`. No installed xtim/judge file was changed; all GDB and static diagnostics are read-only with outputs confined to FRESH.

Independent exact-third result for `best`: c1=3.090120751873293e-19, second=3.500154419292439e-05, third≈6.02727e-6, total≈4.10288e-5; exp(-A1)=0.500771209742264. The third/total values use the CLI printed precision. All-orders remains the ranking value. Exact pair contributions are still dominated by the final correction/readout round and its output-data idle; the new A encoder removes the earlier leading A×data-wait component.

Run disposition: all spawned compute processes exited, including local exact-third and remote MC. `best` and `best_margin` have complete circuit, provenance, ideal/single-fault, all-orders, judge, speed and MC receipts. No submission, credentials, commit/push, installed-engine modification or sub-agent was used.

The remaining SX-specific gap is explicit: the installed engine's general-path trigger is established with exact function-call counts; a complete FAST Y-check representation was built, but its measured7.1587e-5/.49485 price fails performance/acceptance. An equally fast, equally low-exposure implementation of the original4.2669e-5 data-SX circuit was not found. The delivered4.1293e-5 FAST circuit surpasses that score via the newly available encoder and protection composition. No global impossibility claim is made for SX, source reuse or another layout.

Final direct source-reuse port: `r35/v35b_reuse8` removes RX8 after the deterministic MX8 flag. Removing that otherwise-empty native tick compresses R44->43 and depth47->46; the emitter was normalized to the actual judge schedule and checked again. Ideal/single-fault PASS, c1=3.09e-19; **all-orders4.3647551161123466e-5**, acceptance **.5109363669146295**, but **SLOW218.53s/1e6** (two10k samples). Static diagnostic finds118 offending atoms at the reused measurement cone. Thus the q8 edit does port physically to v35b and improves its mean slightly, but the same circuit-wide general-path trigger defeats runtime. No million-shot or MC finalist run was launched for this SLOW port. All FRESH jobs have now exited.

P72 direct price `r37/drop_mx8`: all-orders 4.46385857262654e-05, acceptance 0.511239580939. Ideal acceptance1/loss0, c1<1e-12, static0 general atoms. Detector deletion is an actual acceptance trade, not claimed noise-channel equivalence.

P72 direct price `r37/drop_mx2`: all-orders 4.18543390665247e-05, acceptance 0.503926829486. Ideal acceptance1/loss0, c1<1e-12, static0 general atoms. Detector deletion is an actual acceptance trade, not claimed noise-channel equivalence.

P72 direct price `r37/drop_mx8_mx2`: all-orders 8.74725978439898e-05, acceptance 0.514517729091. Ideal acceptance1/loss0, c1<1e-12, static0 general atoms. Detector deletion is an actual acceptance trade, not claimed noise-channel equivalence.

P72 QND flag copy `r37/remote_flag13`: replace live MX8/reset8 by an X-parity read on terminal helper13 through dirty bus14, using CX13->14, CX14->8, CX13->14, CX14->8. The dirty bus is restored, preserving the desired projection. The q7/helper13 storage guard conflicts and is removed. Result: ideal/single-fault PASS,0 general atoms, measured FAST4.55s/1e6; all-orders5.040580927919172e-5, acceptance.493423907142875, depth48. Failure scope: this four-CX remote realization and its one added schedule tick, not terminal-helper readouts generally.

A three-CX postselected version is now tested: U V U = V CX13->8, where U=CX13->14 and V=CX14->8. On accepted X8=+1, the extra V acts trivially, so the cleanup CX can be omitted. This permits the original inverse-cat CXs to begin at22, one tick earlier than v36b, while helper13 is measured terminally. Full noise pricing is required because a flipped readout and the rejected branch do not share the same noisy channel.
