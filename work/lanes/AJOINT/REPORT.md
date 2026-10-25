# AJOINT

Verdict: PASS — verified finalist; scoped completeness contract met; no further gain in completed growth campaigns.
Target: L < 3.751821654835085e-05, A >= 0.5002; tau=3.761821654835085e-05; rank feasible J_tau=A(L-tau).
Current v37a prices: 4471; preserved v36k prices: 2322 (distinct QASM hashes).
Best v37a: `cand/ajoint_dd374d5610e8.qasm`; L=3.73848905325705e-05, A=0.5004499980669088, J_tau=-1.16768004146e-07, SHA=dd374d5610e861e58bb91609a1626aca7bbc48e8f2dbb87b71229524b0a795b1.

## Decisions and verification
Reproduced v37a exactly at 3.761821654835085e-5 / 0.5007854638217537; QASM and factor-boundary round trips agree. Ordered D=[6,20,19,10,2,22,16].
Rebased all role/depth assumptions to 49 ticks. Full quantum ports, reset environments, records and T axes are retained; every replacement rebuilds exterior propagation and all native noise.
Coherent binary constraints propose witnesses; independent exact ideal-state/output-stabilizer and single-fault tests verify them before complete all-orders pricing. No A-only v36c table is reused.
B/C resource gates/preparations are fixed; A–resource cross edges may vary. GLOBAL owns B/C synthesis and late X checks; POLISH owns generic greedy edits. New A preparation/guard/decoder templates are this lane’s scope.
Reused GLOBAL’s additional detector-basis warm start only after the MAIN-basis v37a reproduction; code is identical and the new basis is checked against the same saved control.
No submissions, commits, pushes, GPUs or subagents. Lane allocations are capped at hippo <=24, zebra <=4; all computational threads capped at 1.
The cancelled v36k local synthesis was interrupted; its surviving remote polish tree was stopped by numeric PID and exit observed. Completed prices remain; interrupted searches are not claimed complete.

## v37a result and measured costs
The joint q9 guard/check reorder alone gives L=3.753954116903901e-5, A=0.5006495346329741. Move M9/c321 from 37 to 39 and CX9→10 from 39 to 37; keep CX9→10 at 38 and A9 preparation at 40.
The initial witness also delayed M14 and advanced M15; that readout swap costs 6.820385158e-8 by itself. Removing it exposed the larger 7.867537931e-8 guard gain.
First integration reused POLISH 9d10b31c7505: L=3.742419456453801e-5, A=0.5019760324440733, judge gates_ok=True. The final integration reuses POLISH ecc75052febf (replayed L=3.740490924864062e-5, A=0.5009507268136882); replacing its conflicting CX16→10@37 adds a measured 2.001871607e-8 gain. No independent greedy pass was run on v37a.
Finalist cand/ajoint_dd374d5610e8: 396 CX, 49 ticks; A encoder remains the incumbent 11 CX. Exact L=3.73848905325705e-5, A=0.5004499980669088, J=-1.1676800414623413e-7; target margin 1.333260158e-7, acceptance headroom 0.0002499980669. Judge gates_ok=True, passed=True at 1e6; independent MAIN-basis replay differs by 1.11e-16 in L.
The fixed-release A grammar has 11,811 rank-four states and five matching layers 41–45 with <=13 CX. Initial 15 pivot choices yielded 657 schedules / 1,314 full prices on POLISH 9d. Expanded search covers all 35 four-pivot choices, including RX15@40 replacing M15/c322: 1,268 schedules / 2,536 prices on POLISH ecc. All passed the full ideal/single-fault checks; incumbent encoder plus joint guard remains best.
Correction: the first analytic Z screen ignored B syndrome rejection and incorrectly called four schedules necessary-FT survivors. That screen was withdrawn; it excluded NONE of either completed enumeration. All initial saved prices remain valid measurements.
Swapping A7/A8 preparation roles, their first CX and q8–D2 guard directions costs about 6.4e-7. Making ONLY the two q8–D2 CX channels at 39/40 perfect makes both circuits exactly L=3.7516367485605454e-5, A=0.50171927468887: the excess depends on those guard channels.
Encoded C4 guards: all 68 four-wire A9/D10/C4/q16 configurations were priced on each of v37a and the two shared POLISH exteriors, with full ideal/single-fault checks and fixed B/C preparation. Best latest: L=3.742956875018693e-5, A=0.5014446836806705, J=-9.459643547736124e-8; the flag buys 0.0009946856138 acceptance but adds 4.467821762e-8 loss versus the finalist. Old v37a best: L=3.758031050333089e-5, A=0.5016445763907961.
A latest-batch launch raced its script sync and repeated 15 old-context cases. Those receipts were retained as history; the corrected ordered sync/launch priced all 68 latest cases. audit37.json checks every expected case, source hash, ordered output map and unchanged B/C preparation.
Expanded CP windows reach 19 wires and ticks 28–48, including arbitrary X/Z data-probe labels, alternative A readout roots and CEGAR exclusions of exact invalid assignments. UNKNOWN is not an impossibility proof; coverage.json and per-solve logs record each finite scope.
Final-exterior growth: accepted-process window FEASIBLE (16 full prices, 49 invalid assignments excluded); X/Z-probe window FEASIBLE (24 prices, one excluded); earlier 28–48 window UNKNOWN (zero witnesses, 360 s). Of 40 prices only three meet A>=0.5002; best ties the finalist exactly. Earlier-finalist growth also found no resolved gain in 31 prices. All campaign processes exited successfully.
On v37a the dense full-signature A/N tables require 2 MiB (pilot 6 wires), 1 GiB (12), 64 GiB (16), 128 GiB (18); the latter exceeds hippo RAM. The final 19-wire, ticks 28–48 window has measured rank 43 / 128 TiB. Both its factorized rejoin and the final pilot round trip reproduce L within 2.22e-16. This is a dense-representation limit, not a lower bound on every compression.
The latest encoded flag has an explicit trace certificate: Z10 between CX4→10 at ticks 39/40 leaves Z4 after the echo; c334 reads that trace through deterministic parities {330,332,334,336} and {333,334,335,336}. Verified rotation, detector, output and record signatures agree exactly.
Full report: REPORT.full.md and results.json (local, not in git).
