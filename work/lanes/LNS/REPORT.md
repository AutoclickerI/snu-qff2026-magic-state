# LNS

**Status: running. A fully MC-ranked delivery exists; the complete move-set certificate is still open.**

Delivery alias: `best.qasm/.json` = **bc_port_229898d242**. Ranking uses completed 1e8-shot means at seeds 0/1000/2000; acceptance is a gate.

Delivery exact: **5.16277975475e-05 + 1.59530374643e-05 = 6.75808350118e-05**; exp(-A1) **0.53902294**; R **44**, **204 CX**. Exact delta from v22h_c2c9: **-3.72512177e-06 (-5.224%)**.

Best completed MC mean: **6.79427e-05**, `bc_port_229898d242`; seed-0 acceptance **0.53909**.

Best exact screen: **bc43_cone_r5**, **6.62426382943e-05**, delta from v22h_c2c9 **-5.06331849e-06 (-7.101%)**.
Second 5.1581979095e-05; cubic 1.46606591993e-05; exp(-A1) 0.54476479; c1 p 2.92e-19; R [43, 43], 204 CX.
This exact screen is not promoted by predicted acceptance or score alone. Its MC status is shown below.

| Finalist | Seed 0 | Seed 1000 | Seed 2000 | Mean | Seed-0 acc | Check |
|---|---:|---:|---:|---:|---:|---|
| bc_port_229898d242 | 6.863403e-05 | 6.750823e-05 | 6.768585e-05 | 6.79427e-05 | 0.53909 | PASS |
| round43_pair_39303eb2d8 | 6.93125e-05 | 6.987742e-05 | 6.761043e-05 | 6.893345e-05 | 0.53886 | PASS |
| bc_port_ed4839a8a8 | 6.852339e-05 | 6.904925e-05 | 6.929668e-05 | 6.895644e-05 | 0.53259 | PASS |
| bc_follow1_25345cb641 | 6.953067e-05 | 7.028041e-05 | 6.90633e-05 | 6.962479e-05 | 0.53926 | PASS |
| iter3_0cc1febf8e | 7.026273e-05 | 6.997225e-05 | 7.035348e-05 | 7.019615e-05 | 0.53577 | PASS |
| bc_w_fast | 7.007544e-05 | 7.156851e-05 | 7.130104e-05 | 7.098166e-05 | 0.53421 | PASS |
| fast_compound2_774000b526 | 7.023561e-05 | 6.95945e-05 | 7.347679e-05 | 7.11023e-05 | 0.52559 | PASS |
| fast_follow2_36fc263c49 | 6.945745e-05 | 7.067343e-05 | 7.318427e-05 | 7.110505e-05 | 0.52017 | PASS |
| fast_compounds_d2fa7dd5be | 7.05832e-05 | 7.300042e-05 | 7.092891e-05 | 7.150418e-05 | 0.52888 | PASS |
| reset_h | 7.168144e-05 | 7.18449e-05 | 7.161891e-05 | 7.171509e-05 | 0.53222 | PASS |
| reset_w | 7.146481e-05 | 7.206699e-05 | 7.362855e-05 | 7.238678e-05 | 0.53397 | PASS |
| choices_6123b801f1 | pending | pending | pending | pending | pending | PASS |
| bc_finish1_2a4a2be789 | pending | pending | pending | pending | pending | PASS |

| Move family | Evaluations | Invalid screens | Better than parent | Best exact delta vs starting bar |
|---|---:|---:|---:|---:|
| timing | 6934 | 0 | 227 | -5.05388747e-06 |
| commute | 1024 | 0 | 72 | -4.53791198e-06 |
| init | 1640 | 404 | 262 | -4.57850342e-06 |
| phase | 127 | 18 | 14 | -4.53310861e-06 |
| readout | 6053 | 705 | 39 | -4.52792518e-06 |
| hop | 344 | 52 | 34 | -3.73239161e-06 |
| triple | 171 | 0 | 144 | -5.06331849e-06 |

Counts are completed evaluations, including earlier controls/repeated recipes; build failures and interrupted work are not certificates. Full descriptions, hashes, objective parts and errors are in the lane JSONL logs. Physical-equivalence qualifications are below.

## Delivery and provenance

The MC table and `best.qasm/.json` alias are authoritative. Promotion requires a passing judge check and all three 1e8-shot seeds. The observed mean defines the requested rank; differences near a per-seed SEM of 1e-6 remain statistically unresolved.

Fully sampled normal-speed finalist **bc_port_ed4839a8a8**: exact **5.20467e-5 + 1.64852e-5 = 6.853195009309e-5**, exp(-A1) **0.53247581**, R45, 204 CX. Its MC mean is **6.895644e-5** and seed-0 acceptance **0.53259**. The unmodified `exact2.py --third` receipt is `bc_port_ed4839a8a8.reference.log`; full precision is in its `.exact.json`.

Relative to v22h_c2c9, this normal-speed finalist uses BCSYN2's fb_s401_0035 preparation (via MAIN/v23h_c2c9), LNS pre-stage watches and RX checks, commuting pre-stage swaps, q10 measured initialization, and readout 14→8. It retains the pre-stage q8 reset. BCSYN2 receives credit for its prep; this lane ports and combines the remaining moves. `delivery_diff.json` lists the emitted operation and detector changes. Both original h/w families were explored; the sampled new-BC w sibling has mean 7.098166e-5.

The main reset-free finalist **bc_port_229898d242** also removes the pre-stage q8 reset: **5.162779754751e-5 + 1.595303746430e-5 = 6.758083501181e-5**, exp(-A1) **0.53902294**, R44, 204 CX. Its MC status is in the table. It is promoted only by its completed observed mean.

## Measured mechanisms

- Removing the q8 RX after its X measurement deletes the sole operation in that layer, reducing the native round from 45 to 44. Exact pair and cubic contributions fall. The removed reset also makes the exact sampler much slower.
- MX initialization of the six B+C pivots carries random Z-frame records through the Clifford suffix into detector parities. The new BCSYN2 prep already uses the appropriate six pivots; its q19 pivot must not receive the old q19 Z-measured-init edit.
- Commuting pre-stage CX swaps include 9→10 / 9→15, 1→0 / 1→7, and 9→3 / 9→15. They alter fault propagation and exposure; each retained combined result has an exact receipt.
- Watches before early resets and MX checks after selected RX preparations reject additional faults. Their gains depend on the full circuit; the old BUDGET negative does not close these combined recipes.
- Readout 14→8 joins 17→16 and 19→25. All 1,953 directed matchings on the ten enumerated grid edges were checked on reset_h and on bc_follow1_25345cb641; these same three edges win both scans. `bc44_matchings.certificate.json` states the precise one-layer scope.
- The alternative data-15 route 15→21→22 finishes before data 8 enters 21. On the old-BC normal-speed branch it improves exact loss by 1.03227e-8 (`fast_follow2_36fc263c49`). Its completed MC mean, 7.110505e-5, does not beat its parent's 7.110230e-5 observed mean.
- CP-SAT finds R44 while retaining both q8 resets and the same native-operation multiset (`bc_follow1_25345cb641`, `bc44_operations_identity.json`). Exact is 6.768568336265e-5; MC mean 6.962479e-5. The reset-retaining R43 random and pair-gradient searches each tested 48 valid proposals. Their best exact is 6.785252303261e-5 (`round43_pair_39303eb2d8`), MC mean 6.893345e-5. A later combined q8-reuse/commuting-order R43 circuit, **bc_finish1_2a4a2be789**, is independently verified at **6.677235988444e-5**, exp(-A1) **0.54582403**, 204 CX. Its MC is pending; the earlier R43 negative closes only the reset-retaining recipes.

## Third order

The new-BC reset-free finalist has cubic increment **1.595303746431e-5**: positive weight-three **2.127121197761e-5** plus normalization **−5.318174513305e-6**. Its largest positive triple is Z idle on q10 at steps 30–43, q3 at 28–42 and q0 at 29–42 (**1.060265014055e-7**). The largest pair is X idle on q7 at 22–25 with Y idle on q20 at 36–42 (**7.731256006325e-7**). Details: `bc_port_229898d242.attribution.json`.

`choices_6123b801f1.attribution.json` contains thresholded positive triples and pair region sums after q8 reuse. Its largest positive triple is Z-idle on data cells 10, 3 and 0 (1.13019773e-7), followed by A9 Z idle with data 3/0 (4.06067654e-8). Positive weight-three sums exclude the negative pair-times-other-channel normalization and are not the complete cubic increment. `analyze.py` reconstructs prefix labels from HOPS operation identities; new operations may have incomplete region labels. Labeling does not affect the exact objective.

The compiled cubic LNS evaluated 2,997 unique proposals on the slow branch and changed 32 operation times, including advancing 16→22 by seven steps (`cubic_lns_best`). Its independently checked exact is 6.894852306313e-5, exp(-A1) 0.51611202. Coordinate cleanup restored estimated acceptance to 0.54108559 at exact 6.892883722419e-5 (`cleaned_best`, `cleaned.certificate.json`). A separate 3,033-proposal normal-speed timing search found no gain. These old-BC screens are superseded by the new-BC finalists; their MC is unrun.

## Verification and limits

- BCSYN2's exact Fourier contraction is a fast algebraic evaluation of the pair/cubic objective. `moments_validation.json` matches the pruned evaluator on both supplied bases within 3.9e-18. Every retained improvement receives an independent TREP2-pruned exact2 check; correctness requires |c1| < 1e-12.
- Unmodified exact2 receipts also verify the sampled iter3_0cc1febf8e, fast_compounds_d2fa7dd5be and current delivery. The fixed-order compiled cubic models each validate five emitted schedules before search and independently recheck their winners.
- LP fixed-order retiming agrees with five CP-SAT integer-optimum references (`retime_lp_vs_cpsat.json`). CP-SAT handles commuting orders and synchronized rounds. Solver timeouts and sampled CP solutions do not prove optimality.
- A pure T/Tdag move inside an unchanged single-wire idle interval is exactly channel-equivalent under isotropic depolarization. `phase_idle_identity.json` checks 992 splits with maximum error 4.45e-16. Earlier ~2.7e-10 surrogate differences are truncation/resummed-idle grouping effects, not physical improvements. New single-unit scans skip these shifts; HOPS masks crossing CXs remain included. Historical table counts include these qualified screens.
- `iter1` through `iter7` coverage receipts and the readout/coordinate certificates close only their stated finite neighborhoods. General routes, footprints, arbitrary check networks and all CP solutions remain open. The new-BC best-exact neighborhood scan is in progress, including inverse MX/RX choices and idle parity watches. A separate causal-cone search scores the full cubic objective; the old-base cone run was stopped when the stronger R43 screen superseded it, and its provisional trace is not a closure certificate.
- Runtime is measured; server timeout risk is inferred. The reset-free family took about 83 s for the first 1e6-shot check on zebra and 132 CPU-s for a later check on Jerry. Sequential 1e8-shot server evaluation may exceed one hour; no server runtime verdict is claimed. Adding retained detector c7 to X/Z/XZ frames passed 10k-shot checks but showed no useful speedup (`frame_runtime.json`).
- All MC uses a byte-identical copy of MAIN/spec/mc3.py with the required check and seeds 0/1000/2000. The lane wrapper confines xtim cache writes to LNS.
- Early bit-allocation/native-folding bugs failed before scoring, were fixed, and affected proposals were regenerated. Capacity-related interruptions and incomplete MC are explicit in receipts. No submission, commit, push, credentials access, sub-agent or other-lane modification was performed.

