# ENDSEARCH — closed: measured P114 obstacles
Verdict: STOP under the main session’s continuation gate. All four C4/dual full prices and four completed CP-SAT retimes lose; every outer-check-on diagnostic exceeds 3.4e-5. No P114 finalist and no new grid build.
Baseline: v37h exact L=3.611954991494179e-5, A=0.5015489333258328; finalist threshold L<3.601954991494179e-5 at A>=0.5002. The full-circuit 2.8e-5 target remains unmet.
Path closure: compiled example L=5.327964809001302e-5, A=0.5019189441179466; A preparation noiseless gives 5.165114701859771e-5; data waits noiseless gives 3.1612989451564574e-5. Later best sampled native build reached 5.04792166198866e-5, A=0.5063572844528017. Waiting dominates this family; joint layout searches were UNKNOWN/interrupted, not a general infeasibility certificate. Details: tree37/PATH_REPORT.md.
Original terminal frontier is preserved in results.json and the archived path report: square 25.667 p^2, trees >=27.207 p^2, unmeasured-partner templates >=28.747 p^2 within the enumerated grammar. These are not universal floors.

Every full build retains v37h’s real prefix/resource preparation and records. Serial builds grow outputs before both outer checks and lift data contacts to inner logical supports; retimes interleave commuting growth and check operations. The extra check measures XXXX for C4, ZZZZ for its X/Z dual. Complete circuits use phantom cells; they are architecture tests, not 36-cell submissions.
Optimistic diagnostic: disable every gate/read/reset/idle noise channel strictly before the first final encoded B contact; retain every channel at and after that native tick. This also removes growth and earlier-check noise when they precede the cut. Retimed schedules may interleave residual preparation after the cut. Cuts are counterfactual prices, not additive costs or certified lower bounds.

| Variant / schedule | Full L | Full A | Cut tick | Outer-check-on L | Outer-check-on A |
|---|---:|---:|---:|---:|---:|
| C4 | 0.000136976004841 | 0.382682870819 | 50 | 9.96759372014e-05 | 0.898813148552 |
| C4 + XXXX | 0.000153695638659 | 0.327211311823 | 50 | 0.000125532430255 | 0.788637782314 |
| Dual | 0.00018834678184 | 0.386237730728 | 50 | 9.08973026348e-05 | 0.900899639775 |
| Dual + ZZZZ | 0.000122177111482 | 0.327213386184 | 50 | 8.23404417602e-05 | 0.78863851821 |
| C4 / retimed | 0.000149631299447 | 0.464928577225 | 46 | 0.000104826194861 | 0.911896057208 |
| C4 + XXXX / retimed | 0.000154680893665 | 0.436675251482 | 46 | 0.000106155392751 | 0.872400104097 |
| Dual / retimed | 0.000122078140801 | 0.459753067206 | 46 | 9.11297714928e-05 | 0.900906137179 |
| Dual + ZZZZ / retimed | 0.000108401108361 | 0.43075094095 | 45 | 8.35054631104e-05 | 0.834276111444 |

Best complete new ending: dual + ZZZZ, retime_4, L=1.0840110836108175e-4, A=0.4307509409503924, 52 native ticks; SHA256 cbaab4979cbae74becb5a9e9a2e491ced1108c2e7899a1a8fe530044cff8fc1b. It misses both loss and acceptance. Best diagnostic among all eight: dual + ZZZZ serial schedule, L=8.234044176023708e-5, A=0.7886385182095561.
(b) C4 obstacle: even perfect history before encoded B leaves >=9.967593720144728e-5 in the two unflagged schedules, and >=1.0615539275052061e-4 with XXXX verification. The implemented check/wait/contraction sequence itself is already too expensive.
(c) Dual obstacle: the corresponding minima are 9.089730263483849e-5 without ZZZZ and 8.234044176023708e-5 with it. Dual checking improves some full prices but cannot meet the continuation gate in these schedules.
CP-SAT retimes completed OPTIMAL: 51 ticks without the extra check, 52 with it. This certifies the objective only for each fixed native gate list, pairwise commutation constraints, fixed prefix before tick 28, and last-two-layer handoff. It does not certify optimal Clifford synthesis or grid preparation.
A precursor-synthesis sweep saved exact six/seven-wire ideal-instrument solutions; two precursor layers were infeasible in the six-wire normal grammar, while three/four layers produced witnesses. Those witnesses were not full noisy circuits. Rep2-XX builds passed raw ideal checks but were not priced. Neither search is resumed under the owner’s stop gate; they remain open, not negative results.

Verified here: incumbent replay matches L and A exactly; C4 perfect-input tail reproduced L=2.192096391856255e-5, A=0.9787606162143896. All 18 completed prices pass six raw output stabilizers +1 and organizer exact raw correctness before ranking. No harmful first-order event found; computed single-fault contributions are <1e-18. Largest recorded kernel omission bound is <5.7e-14, excluding floating-point roundoff.
Validation failure retained: the old path prefix cut was not raw-correct on v37h and was never priced. These full builds preserve the complete incumbent instrument. CONTRACT independently localized the reused M1@28 boundary and repaired it; no fresh-resource boundary repair was assumed here.
CONTRACT REPORT.md, AUDIT.md and all 61 result records were read, not modified: its case audit supports floor 2.1892512824770078e-5; its independent early-storage outer-tail cost is 5.15580332542e-5, and compact helper alternative is 4.36799568012e-5 full / 3.61082230277e-5 with perfect resource preparation. These are CONTRACT measurements, not ENDSEARCH reruns.
Geometry remains open for prepared circuits: CONTRACT found movable D admits a connected bus with non-square K-D-H-L paths. No static-square packing assumption is used to close this lane. Missing XXXX measurement means C4 distance alone does not guarantee protection from waiting errors.
Unverified: arbitrary larger/direct verified inner-code preparation, new precursor synthesis, grid placement of those alternatives, and universal preparation no-go claims. No P114 circuit qualified for judge speed/gates testing or promotion; cand/ retains only historical search prototypes, not a current finalist.
Execution: old path containers and queued launchers were stopped by verified IDs/PIDs. C4 jobs and the final diagnostic container exited; no owned endsearch-* container remains. Other lanes’ containers were not touched. No Tom, subagents, submissions, commits/pushes, credential reads, or writes outside this lane.
Files: c4/{lift.py,retime.py,diagnose.py,price.py,raw.py,collect.py,summary.json}; c4/builds/ saved QASM+ordered outputs; c4/logs/*.receipt.json exact prices and evaluator hashes; c4/owl/diagnostic_results.json and solver logs. results.json has all 18 P114 prices merged into the SHA256-keyed ledger, with separate scopes for full noise and cuts.
