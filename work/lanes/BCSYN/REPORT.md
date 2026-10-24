# BCSYN — reverse endpoint plus BC2 clean/FT synthesis

The fixed v18 target is

`B = [6,26,13,11,4,23,27]`, `C = [12,25,19,17,5,29,28]`, with the six
four-body rows in `ft.py`.  The reverse model propagates those rows backwards
through a 14-layer nearest-neighbour CNOT network and requires at most six
nonzero input rows.  The input is therefore six `|+>` pivots and `|0>` on the
other footprint cells.  The forward model uses the same layer matching and
adds the BC2 CEGAR constraints from `ft.py`.

`ft.sig` includes the logical parity bit for **both** B and C.  The full-circuit
detectors retain C's declared logical parity (`c[21] c[22] c[24] c[25] c[26] c[27]`).
The clean/FT witnesses below were checked with Stim at zero noise and with the
`clean` CEGAR predicate.  Endpoint-only rows were checked only against the
noiseless target; they are synthesis bounds and were not inserted into a
submission.

## Prep synthesis

Times are wall seconds. `TIMEOUT` is a solver timeout, never an UNSAT claim.
The exact prices in the last column are the full v18 replacement screens; a
dash means that the prep did not pass the clean predicate or had no witness.

| Formulation | CX cap | depth | init / helpers | clean/FT | status | time | witness CX | in-situ exact total / exp(-A1) |
|---|---:|---:|---|---|---|---:|---:|---|
| reverse endpoint CP-SAT (no fault constraints) | 82 | 14 | six `|+>` pivots / none | endpoint only | SAT | 18.61 | 78 | — |
| reverse endpoint CP-SAT (no fault constraints) | 78 | 14 | six `|+>` pivots / none | endpoint only | SAT | 7.41 | 72 | — |
| reverse endpoint CP-SAT (no fault constraints) | 74 | 14 | six `|+>` pivots / none | endpoint only | SAT | 31.32 | 71 | — |
| reverse endpoint CP-SAT (no fault constraints) | 70 | 14 | six `|+>` pivots / none | endpoint only | SAT | 2.96 | 67 | — |
| reverse endpoint CP-SAT (no fault constraints) | 68 | 14 | six `|+>` pivots / none | endpoint only | SAT | 43.53 | 67 | — |
| reverse endpoint CP-SAT (no fault constraints) | 66 | 14 | six `|+>` pivots / none | endpoint only | SAT | 55.02 | 66 | — |
| reverse endpoint CP-SAT (no fault constraints) | 64 | 14 | six `|+>` pivots / none | endpoint only | SAT | 12.06 | 64 | — |
| reverse endpoint CP-SAT (no fault constraints) | 62 | 14 | six `|+>` pivots / none | endpoint only | SAT | 90.76 | 62 | — |
| reverse endpoint CP-SAT (no fault constraints) | 60 | 14 | six `|+>` pivots / none | endpoint only | TIMEOUT | 301.27 | — | — |
| reverse endpoint CP-SAT (no fault constraints) | 58 | 14 | six `|+>` pivots / none | endpoint only | TIMEOUT | 300.67 | — | — |
| reverse + BC2 clean CEGAR (hinted SAT witness) | 82 | 14 | six `|+>` pivots / none | Stim PASS; clean PASS | SAT | 0.47 | 82 | **8.15335e-5 / 0.51766** (all first-use measures) |
| reverse + BC2 clean CEGAR (unhinted seed 9) | 82 | 14 | six `|+>` pivots / none | — | TIMEOUT | 900.18 | — | — |
| reverse + BC2 clean CEGAR | 78 | 14 | six `|+>` pivots / none | — | TIMEOUT | 900.17 | — | — |
| reverse + BC2 clean CEGAR | 74 | 14 | six `|+>` pivots / none | — | TIMEOUT | 900.11 | — | — |
| reverse + BC2 clean CEGAR | 70 | 14 | six `|+>` pivots / none | — | TIMEOUT | 900.14 | — | — |
| reverse + BC2 clean CEGAR | 66 | 14 | six `|+>` pivots / none | — | TIMEOUT | 900.05 | — | — |
| reverse + BC2 clean CEGAR | 82 | 13 | six `|+>` pivots / none | — | TIMEOUT | 900.49 | — | — |
| reverse + BC2 clean CEGAR | 78 | 13 | six `|+>` pivots / none | — | TIMEOUT | 900.50 | — | — |
| reverse + BC2 clean CEGAR | 82 | 14 | six `|+>` pivots / helpers `18,24,30,31,32,33,34,35` | — | TIMEOUT | 60.38 | — | — |
| BC2 forward clean CEGAR (reference) | 82 | 14 | six `|+>` pivots / fixed footprint | Stim PASS; clean PASS | SAT | 211.22 | 8.15335e-5 / 0.51766 (same replacement) |

The endpoint-only sweep reaches 67 CX at cap 70, but those witnesses are not
clean: the reverse endpoint is necessary but not sufficient for fault tolerance.
The only clean reverse witness found in the allotted runs is the 82-CX circuit;
the lower caps and depth-13 instances remained unresolved at timeout.

The helper run was deliberately included to test cells released by the v18
prefix. It did not produce a witness. First-use `measure`/`MX` variants were
then generated for the clean 82-CX witness and checked in situ; all three pass
the judge gates.

## Full circuits

All rows below pass `tprep.check` at 1,000,000 shots. `c1` is below the exact2
threshold, so the third-order screen is valid. The three MC values are each
100,000,000 shots at seeds 0, 1000 and 2000.

| circuit | R (native) | CX | c1 | 2nd | 3rd increment | exact total | exp(-A1) | MC 0 / 1000 / 2000 | MC mean | seed-0 acceptance | files |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| **v18 encoder19_alap** | **46** | 203 | 2.9236e-19 | 5.62262e-5 | 1.98379e-5 | **7.60640e-5** | 0.52776 | 7.742218e-5 / 7.508943e-5 / 7.657090e-5 | **7.636083e-5** | 0.52782 | [MAIN/v18.qasm](../MAIN/v18.qasm), [MAIN/v18.json](../MAIN/v18.json) |
| reverse clean 82-CX, first-use `m10` | 47 | 203 | 2.9236e-19 | 5.76410e-5 | 2.38936e-5 | 8.15346e-5 | 0.51852 | 8.513398e-5 / 8.281887e-5 / 8.259343e-5 | 8.351543e-5 | 0.51871 | [QASM](rev82_minit/rev82_m10.qasm), [JSON](rev82_minit/rev82_m10.json) |
| reverse clean 82-CX, first-use `m14` | 47 | 203 | 2.9236e-19 | 5.76632e-5 | 2.39264e-5 | 8.15896e-5 | 0.51852 | 8.321646e-5 / 7.992562e-5 / 8.284773e-5 | 8.199660e-5 | 0.51859 | [QASM](rev82_minit/rev82_m14.qasm), [JSON](rev82_minit/rev82_m14.json) |
| reverse clean 82-CX, all first-use measures | 47 | 203 | 2.9236e-19 | 5.76410e-5 | 2.38925e-5 | 8.15335e-5 | 0.51766 | 8.380484e-5 / 8.433573e-5 / 8.206603e-5 | 8.340220e-5 | 0.51775 | [QASM](rev82_minit/rev82_mall.qasm), [JSON](rev82_minit/rev82_mall.json) |
| EARLYBC MX-init extension | 50 | 209 | 3.183e-19 | 5.68772e-5 | 2.49984e-5 | 8.18756e-5 | 0.54359 | 8.280201e-5 / 8.518379e-5 / 8.418470e-5 | 8.405683e-5 | 0.54377 | [QASM](../EARLYBC/mx_init.qasm), [JSON](../EARLYBC/mx_init.json) |

The reverse clean replacement is 0.55e-5 above v18 in the exact screen and
0.70e-5 above it in the three-seed MC, so v18 remains the ranked circuit.  No
candidate from this lane beats the completion bar; the synthesis and in-situ
price tables provide the requested cap/depth results and the clean witness.

## Verification receipts and commands

- Prep checks: `verify_prep.py` (Stim target plus `ft.py` clean CEGAR).
- Replacement/scheduling: `screen_prep.py` (v18 prefix, fixed round spacing,
  ALAP B+C insertion), followed by `BC2/minit.py`.
- Judge checks: `judge_check.py` and `work/lanes/MAIN/spec/mc3.py`.
- Exact prices: `work/lanes/EVAL/exact2.py --third` with eight processes.

All artifacts written by this lane are under `work/lanes/BCSYN/`; no submission,
commit, push, credential access, or writes to ANC4, BUDGET, TREP2, or other
lanes were made.
