# IDEAS: fresh-eyes review of v36c (PLAN P79)

Verdict: **no finalist.** Every idea with an optimistic bound above 0.5% is owned by a lane or blocked on this grid.
Bounds are all-orders losses on v36c (4.11516e-5, acceptance 0.50273) with the named noise made perfect; the
gadget's own cost is not charged. Specs: `bounds1.py`, `bounds2.py`, `bounds3.py` (results `b*_v36c.json`), tool
`abl.py` (whole channels or single Pauli components perfect; imports `MAIN/sparse`).

## Ranked ideas
| # | Assumption broken → idea | Mechanism | Bound | Δacc | Result |
|---|---|---|---|---|---|
| 1 | B/C's Z errors only cost acceptance | third-order masking: two same-type waiting-data errors plus one checker flip on the third qubit of their line cancel the syndrome and the judge miscorrects to a logical; Z-side flips: any Z on B, Z on C before B→C (copied to B), B readout flips | 9.04% (`mask_Zsyn`; B Z 5.71%, C Z 3.63%, B readout flips 1.74%) | +0.030 | open: one distance-3 round cannot tell a flip on checker k from a data error on k; a synthesis objective for the B/C resource (BFLAG) |
| 2 | A's X errors only cost acceptance | the same masking on the X side | 4.03% (A encoder 2.40%) | +0.017 | open: objective for A-encoder synthesis (P59) |
| 3 | C's check sees all of B's X errors | correlated X on a B/C pair escapes; some single faults are caught by one detector bit (top: B4 reset t36 × C17 idle t42) | 8.95% (`BX_res32_43`) | +0.023 | open: needs a B-only Z parity before t44 (BFLAG); free cells 18/24 reach C12/C19/C25, busy at nearly every tick 34–44 |
| 4 | the decoder's early coupling (D10/D21 idle at t44) can be avoided | X leak 10/15 p instead of 4/15 p | 6.59% (`d1021_idle44`) | +0.0007 | closed by geometry (below); EARLY owns freeing a neighbour cell |
| 5 | data waits are cheap | waits cost exactly 0 at second order, only at third | 11.04% (Z 8.75%, X 5.11%) | +0.032 | owned (INTEG, EARLY); Z waits cost 1.7× X waits: protect Z first |
| 6 | prefix acceptance is the price of the T-check | injection (t ≤ 12): +0.067 acceptance for 1.19% loss; t13–30: +0.129 for 5.42% | 1.19% / 5.42% | +0.067 / +0.129 | owned (T14 closed the 14-T route); the injection spends 5× more acceptance per unit loss than the T-check |
| 7 | the decoder is an add-on | drop it to free D10/D21 | — | — | closed: `v36c_nodec` 8.41815e-5 (×2.05); the A encoder is built around the flag |
| 8 | terminal extras are cheap | edges 14→15, 17→16 0.83%; flag masking 0.32%; C copies 0.29% (+0.0057); decoder CX 0.14% | ≤ 0.83% | small | below threshold or owned (INTEG) |
| 9 | accept weight-1 round syndromes (the judge corrects weight 1) | gains acceptance | — | + | closed by arithmetic: ≈ 2e-2 loss per unit acceptance vs the market's 3e-5 to 1e-4 |
| 10 | FRAME corrections instead of rejection | accept a syndrome, apply a logical frame | — | + | closed: at p = 1e-3 every syndrome is dominated by harmless single faults |
| 11 | H frame during the wait; moving T/T† | change error meaning or timing | 0 | 0 | closed: depolarizing noise commutes with every unitary |
| 12 | a second X check after B (C on its spare tick) | C as a late X-syndrome block | — | — | closed: C's Z errors would land on the data after B's check |

Round items belong to TERM (no template below the Steane round): final data idle 63.7%, D→A unflagged X 6.97%, B→C
unflagged X 8.48%.

## Findings
- 15% of the loss is third order and above: exact second order 3.50015e-5, so 6.15e-6 is higher order. The waits on
  q7, q3, q10, q22, q21, q0 appear only there; idea 1's checker flips complete them.
- The A decoder carries the circuit: without it, Z faults on A's X-pivot qubits (A14 init and idle, A9 init) pair with
  data Z waits (top pair 3.3e-6).
- The decoder always costs two data-idle ticks: {8,9,15} is the only connected weight-3 X_L on A's cells; each decoder
  CX's control must be coupled before it, its target is busy then, and every data qubit is busy with B→D at 45, so both
  qubits of the first decoder CX are coupled by t43. Moving the first decoder CX into A's encoder accepts X7X10; an echo
  on A9 makes detector rows using r9 non-deterministic; re-pairing data with A by a code symmetry is forced to the
  identity; no neighbour of cells 10 or 21 is free at t44. Both idle ticks on D10 instead: ≤ 0.4%, needs A9 free at t42.

## Verification
- The evaluator reproduces v36c exactly; `v36c_nodec` has deterministic detectors and no first-order loss (exact2).
- The ledger agrees with TERM's and T14's region maps. The main session re-ran `bounds2.py` through `MAIN/sparse`:
  `mask_Zsyn` 3.743162e-5 (+9.04%), `BX_res32_43` 3.746926e-5 (+8.95%).
- Not done: exact2's third-order mode overflows at 72 detectors, so the third-order split comes from all-orders
  counterfactuals, not a triple enumeration.

## Files
`abl.py`, `chan.py`, `bounds{1,2,3}.py` + `b{1,2,3}_v36c.json`, `excess.py`, `triples.py`, `accrank.py`,
`show_adj.py`, `ticks.py`, `timeline.py`, `v36c_exact2.txt`, `v36c_sens.json`, `v36c_timeline.txt`,
`v36c_triples.txt`, `adj_v36c.log`, `v36c_nodec.{qasm,json}` + `build_nodec.py` (negative control).
