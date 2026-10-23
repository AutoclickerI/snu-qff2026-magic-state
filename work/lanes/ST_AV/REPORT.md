# ST_AV: D verifier block for A

## 1. Grid-free exact proxy (stav.py; poc.proxy, round only; first-order term 0 in every row)
A encoder / D | input noise 0 | 5e-3 | 1e-2 | 2e-2 | qubits | CX
--- | --- | --- | --- | --- | --- | ---
std, no D | 3.232e-5 | 3.343e-5 | 3.455e-5 | 3.679e-5 | 28 | 48
s7307, no D | 3.539e-5 | 3.716e-5 | 3.894e-5 | 4.252e-5 | 28 | 50
exact (prepA_L5_exact), no D | 3.545e-5 | 3.700e-5 | 3.856e-5 | 4.169e-5 | 28 | 51
any A (std, s7307, exact) with D (std or exact encoder) | 2.8986e-5 | 2.8986e-5 | 2.8986e-5 | 2.8986e-5 | 35 | 64-70

With D the proxy is independent of the A encoder, of D's encoder, of input noise and of the D->A time (gap 0, 2, 6 tested):
all of A's Z faults are caught, so A needs no good encoder. Remaining excess over the 2.567e-5 floor: 3.3e-6.
Gain: 0.6e-5 (s7307, no input noise) to 1.35e-5 (input noise 2e-2) of round loss. Round loss only; order 2.

## 2. Grid layout (layout.py, layout_seq.py, layout_re.py; CP-SAT, 6x6, all with d_i~a_i, d_i~b_i, b_i~c_i, a_i~dd_i)
- 35 cells, no helpers: each of A, D, B+C connected alone: INFEASIBLE. A, D, B, C each connected alone: INFEASIBLE.
  Only B+C connected jointly (A, D free) or A+D / B+C joint are feasible, but a joint B+C prep breaks C's independence (FINDINGS, ST_BC).
- Sequential preps with helper cells from not-yet-prepared blocks (24 orders, 3 workers x 400 s): feasible, 49-64 helper-weighted objective, many helpers.
- D on the cells of C (D measured before C is prepared; 28 cells + 8 free, `layout_re.py c bc|cb`): feasible; D on B cells: INFEASIBLE.
  Best found (not proven optimal, bound 55 vs 97-109): `re4_cbc.json`, `re4_ccb.json`; data moves up to 6 hops, 8-11 helper cells per block.

## 3. Full circuit (build_all.py: SAT encoders with helpers; merge_av.py; exact2.py --third)
Pre-stage busy until 33; merged round starts at R = 78-79 (the helper chains and 5-6 hop data moves serialize preps).
Block encoders 20-46 CX, depth 7-10. Files: tcbc_c.qasm, tccb_c.qasm (+ .json).
| candidate | R | first order | 2nd order | 3rd order total | exp(-A1) |
--- | --- | --- | --- | --- | ---
tcbc_c (re4_cbc) | 79 | 3e-19 | 4.61e-5 | 3.58e-4 | 0.304 (fails >= 0.55) |
tccb_c (re4_ccb) | 78 | 3e-19 | 5.81e-5 | 3.93e-4 | 0.287 |
(first test layout re_cbc: 2nd order 5.34e-5, exp(-A1) 0.33)
Fault tolerance holds (first order 0) but 3rd order is 3x the v12 target 1.13e-4 and acceptance fails; no 3-seed MC run (not competitive).
No D-free circuit on the same layout was built, so the D-vs-no-D third-order comparison on the grid is not measured.

## Verdict
D removes A's encoder cross term on paper (order 2, grid-free: 3.5e-5 -> 2.9e-5) but the 35th..28th cell budget makes it unbuildable on 6x6 without
serial helper-routed preps; the delay/extra CX cost far exceeds the 1e-5 gain. Not pursued further.
