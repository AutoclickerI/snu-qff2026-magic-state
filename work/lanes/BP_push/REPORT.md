# BP_push: Bell-pair final round (final 2026-10-23 23:00 KST)

## Result
The only gain found is a cycle-level one that L5 also found by hand: **delay the tile-0 Bell CX to layer 2** (tile-0 members have no
gate at layer 1), annealed jointly with the schedule and then re-ALAP'd (commuting ALAP, priority seeds 1..N). Cycle proxy
1.0980e-4 -> 1.0805e-4 (-1.6%). Full circuits: 115 CX, same tails [3,1,1,2,1,1,1] as v11, passes `fast_check` and the sequential judge.

| candidate (`cands/`) | seed 0 | seed 1000 | seed 2000 | 3-seed mean | unbiased mean (30 re-draws, sem 2.2e-7) |
|---|---|---|---|---|---|
| v11 (reference) | 1.1940e-4 | 1.2241e-4 | 1.1880e-4 | 1.2020e-4 | 1.2189e-4 (100 re-draws) |
| BP_A_bell0_s41 (lowest seed-0 key among well-tested) | 1.18484e-4 | 1.1838e-4 | 1.1944e-4 | 1.1877e-4 | 1.1944e-4 |
| BP_B_bell0_s1 (best unbiased mean) | 1.1972e-4 | 1.1805e-4 | 1.1911e-4 | 1.1896e-4 | 1.1932e-4 |
| BP_C_bell0_s44 | 1.1791e-4 | 1.2090e-4 | 1.1725e-4 | 1.1869e-4 | 1.1966e-4 |
| BP_D_bell0_s461 (lowest seed-0 key; selection-biased, `seqcheck` PASS, c1 0) | 1.17084e-4 | 1.1926e-4 | 1.1987e-4 | 1.1874e-4 | 1.2004e-4 |
| 01e17f2e7b (out_b, not packaged) | 1.1961e-4 | 1.1936e-4 | 1.1916e-4 | 1.1938e-4 | 1.1936e-4 |

True gain over v11: about -2.1% (1.2189e-4 -> ~1.193e-4). Seed-0 selection from ~150 ALAP seeds is worth nothing by itself: the
population mean of seed-0 scores is 1.2085e-4 (~480 ALAP seeds screened, top ~75 re-drawn 6x, top 8 re-drawn 30x); the best seed-0 key regressed from 1.171e-4 to a true 1.200e-4, and the real spread between ALAP seeds is ~1%, so rank by re-draw means.
Files: `cands/BP_*.qasm|json` (json: data_qubits, score, n_2q, source, other seeds). BP_A and BP_B: `seqcheck.py` PASS, sequential
score bit-identical to fast_check (BP_A 1.18484e-4; c1 3.7e-17 = roundoff). Not in `work/submissions/` (lane write scope).

L5 results are better (combined_lns_0012 3-seed 1.1327e-4: tile-0 delay + retained X readouts + boundary timing + LNS on official MC). My
candidates are the cycle-level baseline of that family, not a replacement. No cycle I found beats the cycle L5 already uses.

## What each lever bought
- **Tile-0 Bell delay (anneal2.py, gmodel2.py `bell_layer`)**: proxy -1.6%, real -2.1%. Delaying tiles 1 or 2 is invalid (their members are used at layer 2).
- **Global optimum of the A1 round**: 100+ chains (lmax 8, 9, 10; T0 up to 3e-5; moves on hop CNOTs allowed; Bell layers 1..5; orientation) all end at
  1.0980e-4 (1.0805e-4 with the delay). The plateau within +3% has 16 distinct schedules (`plateau.py`); the full-circuit score follows the proxy
  monotonically (all 16 states x 6 ALAP seeds, `out_p`): the best proxy state is the best circuit. Tile-2 orientation flips give identical circuits.
- **Chain extra (3,3) under (2,3) for d5 (variant A4)**: proxy 3.9e-4 (hook), closed. Variant v6 with the delay: 1.122e-4 (worse than A1).
- **Naive text-level retention of the Bell a-members' MX states** (`retain.py`, all 7 masks on BP_C): 1.184e-4 to 1.246e-4 vs 1.179e-4 unretained,
  all worse or equal; L5's gain needs boundary re-timing around the retained qubit, not a text edit.

## What limits further gains
Loss sensitivity of the cycle proxy (remove one noise location, `sens.py`): d0 tail (3 idle steps) 2.57e-5 of 1.098e-4, d3 tail (2 steps) 1.58e-5, five
one-step data tails ~0.9e-5 each, Bell/extra preparation errors (Z after RX on tile-2 `a` 7.6e-6, X after R on extra (4,2) 5.7e-6) ~1.7e-5 together.
Each extra tail step costs ~0.86e-5. Tail excess comes from capacity: after the unbell a member accepts only one check type, so a member with
two data (d0 and d2 on (1,0)) can end only one of them at the last layer; tile 0's members have no free neighbour (all four neighbours of (1,0) and (2,0) are
data or the pair), so no X-only extra can relieve them, and d6 touches 6 CNOTs and saturates layers 2..7. Trading d0's tail for d2's costs the same. The floor with
tails of 1 for all is 5.86e-5; the rest of the gap (~4e-5) is these tails plus prep errors that only retention-type changes (L5) or a different readout
(L3 direct) can remove.
