# COMBO2 — LAYOUT2 clean B+C preparation

This lane tested BC2's `clean` B+C fault rule with LAYOUT2's actual block ordering
`B=[6,24,18,10,9,11,2]`, `C=[0,30,12,4,3,5,1]`. The first attempt reused a BC2 prep
without changing its hard-coded B/C arrays; `tprep.check` correctly rejected those circuits
for wrong output state, so they are retained only as a negative mismatch receipt. The copied
SAT/FT model in `sat6.py`/`ft.py` was then patched to these LAYOUT2 arrays.

All scheduling work used the CP release-aware merger in `merge_cp.py`, which includes the parity
cat preparation and constrains cat controls through `R+1`. Measurement rewrites were generated
with `MAIN/minit.py`. No submission was made.

## Candidate table

Values are at p=1e-3. Exact columns are through third order when `|c1|<1e-12`.
MC is omitted for candidates rejected by a judge gate or outside the requested exact screen.

| Candidate | Prep rule/depth/CX | R | wait steps | c1 | 2nd | 3rd term | exact total | exp(-A1) | MC seeds 0/1000/2000, mean | seed-0 acceptance | status | files |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---|
| LAYOUT2 old prep (comparison) | old parity rule / 14 / 68 | 54 | 15 | — | — | — | — | — | — | 0.511507 (1e6 check) | PASS | `test_cp_old.qasm` |
| clean d16 k100, A filtered | clean / 16 / 86 | 57 | 18 | 4.9565e-19 | 1.00563e-4 | 4.90793e-5 | 1.49642e-4 | 0.49134 | — | 0.492859 (1e6) | FAIL acceptance | `r23_1_3_A_filtered_clean16b_cp.qasm/.json`, `clean_d16_k100_0.receipt.json` |
| clean d16 k100 + all first-use measure | clean / 16 / 86 | 57 | 18 | — | — | — | — | — | — | 0.4781 (1e6) | FAIL acceptance | `r23_1_3_A_filtered_clean16b_cp_mall.qasm/.json` |
| clean d16 k100, A=c11 | clean / 16 / 86 | 57 | 18 | 4.9565e-19 | 1.00565e-4 | 5.00219e-5 | 1.50587e-4 | 0.49062 | — | 0.490658 (1e6) | FAIL acceptance | `c11_A_clean16b_cp.qasm/.json`, `c11_A_clean16b_cp.metrics.json` |
| clean d16 k100, A=c12 | clean / 16 / 86 | 57 | 18 | 4.9565e-19 | 1.00563e-4 | 5.03066e-5 | 1.50870e-4 | 0.48942 | — | 0.489518 (1e6) | FAIL acceptance | `c12_A_clean16b_cp.qasm/.json`, `c12_A_clean16b_cp.metrics.json` |
| clean d14 k100 + data-overlap helpers | clean / 14 / 87 | 55 | 16 | — | — | — | — | — | — | — | FAIL correctness (non-deterministic A detectors) | `helper_strict.qasm/.json`, `r23_1_3_A_filtered_cleanh4_cp.qasm/.json`, `helpers_d14_k100_1.receipt.json` |
| BC2 clean prep embedded without B/C remap | clean / 14 / 82 | 58–63 | — | — | — | — | — | — | — | — | FAIL correctness (wrong output data) | `clean14_earlycp.qasm/.json` (and the corresponding correctness receipt) |

The d16 exact values above come from `r23_1_3_A_filtered_clean16_cp.metrics.json`; the
`clean16b` schedule is byte-identical. The old-prep row is a comparison only and is not a finalist.

## Solver receipts and measured negatives

- LAYOUT2-specific clean search with no helpers: depth 14, caps 68 and 73 timed out; depth 14
  cap 68/73 and helper windows also timed out. Fixed-pivot depth-14 searches at caps 68, 78,
  82 and 100 were UNSAT for all four old pivot orders (`fixed_clean_*.receipt.json`).
- No-helper depth-15 cap 82 (two seeds) timed out after 300 s each (`clean_d15_k82_*.receipt.json`).
- No-helper depth-16 cap 100 seed 18000 reached SAT after 271.38 s with 86 CX; seed 18001
  timed out after 613.02 s (`clean_d16_k100_*.receipt.json`). Its merged circuit starts at
  R=57 and fails acceptance, so it was not priced by MC.
- A depth-14 cap-100 witness with helpers `[17,19,25,31]` reached SAT at 87 CX
  (`helpers_d14_k100_1.receipt.json`) but those helpers overlap final data cells. Both strict and
  CP release merges fail noiseless detector determinism; this is a state-validity negative, not a
  candidate.
- A search restricted to non-output free helpers `[31]`, `[31,32]`, and `[31,32,33,34,35]`
  completed with TIMEOUT receipts after the host load returned below its 64-core limit; no clean
  witness was found (`helpers_free_retry_*.receipt.json`).

## Comparison

The supplied incumbent `v16_bc2m` is exact `8.41984e-5`, with three-seed mean below the BC2
clean baseline `8.46431e-5`. None of the judge-valid COMBO2 circuits above reaches that screen:
the only complete clean witness found so far has R=57 and fails acceptance. The lane therefore
has no MC finalist yet; all eligible work and solver receipts remain under this directory.

The final free-helper run also completed without a witness: `[31]` timed out at 600.05 s after
five CEGAR iterations, `[31,32]` timed out at 600.29 s after three iterations, and all five
free cells timed out at 600.53 s after three iterations (`helpers_free_retry_{0,1,2}.receipt.json`).
