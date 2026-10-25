# MERGE

Verdict: VERIFIED FINALIST; completion contract met.
Best judge-verified candidate: [merge_final](cand/merge_final.qasm); L=3.69040347155986e-05, A=0.505719164710953, J_tau=-2.62559217838343e-07.
SHA256 `42df45423212ae031fb8c7f1975c3aa30effe9c08231c2f7b7c5f3eab2d59172`. Threshold: L < 3.737321460072e-05; A >= .5002; tau=3.742321460072e-05 (v37b).

Native diff audit against v37a:

| Lane | Removed / added native units | Qubit/tick cells | Classical bits touched | Detector rows removed / added |
|---|---:|---:|---:|---:|
| POLISH | 9 / 10 | 26 | 4 | 0 / 0 |
| GLOBAL | 16 / 26 | 42 | 18 | 5 / 7 |
| COMPLETE | 191 / 179 | 378 | 35 | 0 / 0 |
POLISH/GLOBAL: zero quantum-cell overlap; records323/325/329 are shared because POLISH retimes their reads and GLOBAL extends their detector parities.
POLISH/COMPLETE: nine shared cells (q7/q13/q15/q21 at47–48 and q16@37), four shared records. GLOBAL/COMPLETE:23 shared cells,12 shared records. Full locations and operation/record changes: res/diffs_initial.json.
No source has OBSERVABLE, FRAME or POSTSELECT declarations. The unchanged detector text in COMPLETE retains record meanings while Bell readout ports and native timing change.

Measured contributions (conditional comparisons, not additive independent fault budgets):

| Change | Before L | After L | Delta L | After A |
|---|---:|---:|---:|---:|
| COMPLETE full R45 completion | 3.76182165482e-05 | 3.74407047481e-05 | -1.775118e-07 | 0.500225852495 |
| Compatible POLISH prefix + regenerated early readouts | 3.74407047481e-05 | 3.73023911737e-05 | -1.38313574e-07 | 0.5025503869 |
| GLOBAL B/C core on R45 | 3.73023911737e-05 | 3.71496068203e-05 | -1.52784353e-07 | 0.503047541621 |
| COMPLETE, matched POLISH/GLOBAL recipe | 3.73193019354e-05 | 3.71496068203e-05 | -1.69695115e-07 | 0.503047541621 |
| GLOBAL full diff added directly to v37b | 3.74232146008e-05 | 3.72411721146e-05 | -1.82042486e-07 | 0.502898511957 |
| Repair of three-way merge | 3.71496068203e-05 | 3.69040347156e-05 | -2.45572105e-07 | 0.505719164711 |

Final source refresh: POLISH advanced to a616ec8433e4 (reproduced L=3.740287049942354e-5, A=.5010835093559184); GLOBAL cand/ contains no improvement over the stronger supplied build; COMPLETE winner unchanged. Re-diffed POLISH against v37a and v37b; transported its remaining edits/competing row5 network; priced37 combinations plus2 direct menu edits; final regenerated greedy repair follows.

Repair coverage:1549 distinct regenerated proposals (1006 numerical,543 rejected); full extension pass over all174 useful/buyer recipes; seven source-guard combinations; positive joint repair;39 refreshed POLISH transports; final regenerated pass of90 saved proposals and sequential full-price greedy composition. Final pass accepted11 extensions. This is finite-menu coverage, not a convergence/global-optimality claim.
Runtime repair: the numerically best final circuit exceeded90s in its1e6 judge run (terminated by exact PID); short exact-sampler probes gave≈340s/1e6. Bisection identified pair1→7 at37–38. Removing only that pair costs8.4443e-10 L and retains the other improvements. The recommended candidate passes the complete1e6 judge check within the documented20s limit. Slower numerical witnesses remain recorded, explicitly ineligible for promotion.
Reporting correction: a NumPy boolean prevented the first outcome-JSON write; converted it to builtin bool and rebuilt the summary from saved receipts, without changing circuits or measurements.

Merge decisions: retain COMPLETE’s R45 schedule; shift GLOBAL’s B/C orientations/preparations one tick earlier; retain COMPLETE’s measured-q7 source instead of GLOBAL’s competing q7 initialization. Reapply POLISH through the lane-local regenerated menu.
POLISH CX16→10 cannot be transplanted to39/40/41/43/44: all20 saved variants fail deterministic detectors. Restoring its old slot collides with q15’s source read. Restoring GLOBAL’s pair16→17 slot collides with q15’s earlier prefix operation. These failures close the tested local transports only.
Acceptance purchases and deletions are priced as complete circuits. Exact A, not the sampled acceptance, enforces the0.5002 floor. Rank is J_tau=A*(L-tau).
Evaluator: copied MAIN all-orders contraction and POLISH adapter; all73 Fourier moments. A frozen trained detector basis changes contraction coordinates only; the merged control reproduces bit-for-bit. Cache receipts bind QASM hash, ordered data and evaluator/adapter/basis hashes.
Verified: v37a/v37b reproduced within1.2e-16; all listed prices come from saved QASM; every cand artifact has a1e6-shot judge receipt. Structural/ideal failures remain errors. Numerical omission bounds are retained in results.json.
Inference limits: finite menu and transported-schedule coverage; no global optimality claim. Source-lane advertised numbers are not used as newly measured MERGE prices.
Full report with every price: REPORT.full.md and results.json (local, not in git).
