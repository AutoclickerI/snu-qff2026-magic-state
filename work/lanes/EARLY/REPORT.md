# EARLY: earlier round and suffix placement on v36c (PLAN P76)

Verdict: **closed, no finalist.** v36c's R44 is locally optimal; the global floor of the layout model is R42; an earlier
round is worth ≈ 0.5e-6 at best before the cost of rebuilding the suffix, and no placement frees neighbours of the
late-idling data at an acceptable cost. Controls: v36c 4.1151559437773416e-5 (0.50273); ENDSTATE's best
4.985991832508814e-5 (0.51414).

## Layout model (`layout.py`, CP-SAT; `calib.py`, `pinsplit.py`, `r43.py`, `layouts.json`)
- Calibration: v36c's end state pinned gives R44, matching the circuit. The binding cell is A6 at q15 (the chain `crit.py`
  finds: D6 hops 8→9→15→21, M15 at 39, A encoder, D→A at 43/44).
- v36c is locally optimal: pinning only v36c's B/C cells gives R44 (OPTIMAL), with or without the flag; pinning only A
  gives R44. B6 at 27 forces D6 to 21, every route from 8 to 21 passes 15, and 15 is the only cell that can hold A6; it is
  released at 40, so the round cannot start before 44. Re-placing A alone or B/C alone cannot help.
- Global floor R42 (OPTIMAL, R41 infeasible), also with two hop paths reusing a cell at different times: R43 needs 6 hops
  (as v36c), R42 needs 8; both need new A, B and C positions. The floor held across parameter variations and prefix
  translations.
- Worth of an earlier round (all orders): waiting data cost 4.48e-6 in total (data idle 33–42 noiseless: 3.6673e-5),
  ≈ 0.56e-6 and +0.004 acceptance per tick removed (inferred by scaling noise, not removing ticks). A hop costs 0.1–1.0e-6
  (D3 4→10 1.01e-6, D6 15→21 0.53e-6, D5 16→22 0.09e-6). Net before the rebuild: ≈ −0.55e-6 for R43, −0.9 to +0.9e-6
  for R42; a rebuild redoes the A encoder, the 57-CX B/C resource and the guards (ENDSTATE's last port lost 8.7e-6).

## Why ENDSTATE's R38 layout lost
- It has no blue check: v36c without the blue check gives 4.67394e-5, so the check is worth 5.6e-6, and keeping it
  forces R ≥ 42. Dropping it to start earlier: v36c without blue, waiting-data noise from tick 29 scaled to 0.5 / 0.6,
  gives 4.1877e-5 / 4.2725e-5; break-even needs the wait cut to ≈ 40% (≈ R34), at v36c's A quality.
- A's preparation costs 8.0e-6 in ENDSTATE's best vs 2.0e-6 in v36c. The flag's own price is ≈ 2.8e-6 (two flag data
  idling at R); it pays only when it catches more A danger than that (that ENDSTATE's A danger is mostly flag-blind is
  inferred, not decomposed).

## Protecting the wait
- Late weight-4 plaquette checks on spare cells cannot be placed: with A and B∪C each connected, no spare cell (or
  adjacent spare pair) touches 4 data, and at most 3 data have any spare neighbour. As phantoms (off-grid ancillas) a
  two-ancilla XZ check gives −2.72e-6 (3.8434e-5), a one-ancilla X-type −1.35e-6 (3.9801e-5); one-ancilla Z-type checks
  hurt (4.14–4.15e-5). Not covered: checks borrowing A/B/C cells before they are prepared (as the blue check does).
- X echoes on waiting data: ≈ −0.38e-6 per −0.0034 acceptance; every variant fell below 0.5002 on v36c (e_all 3.9160e-5
  at 0.4873). Losers: removing the q21 guard (4.11766e-5); extending the q6 echo to q7 (4.36–4.47e-5: one helper X fault
  puts X on D0 and D2, which with one A-side fault aliases to logical X); moving T† (no change).

## Freeing neighbours of late-idling data (`freed.py`, `runfreed.sh`, `runR.sh`, `logs/freed*.log`)
Spare cell = no A/B/C/data role and free from R−W on (prefix releases and hop paths counted); objective weights each
data label by its residual late-idle cost.
| Round, window | Data that get a spare neighbour | Cost of the layout |
|---|---|---|
| R44, cell free from 38 (or 41) | D0 (q0, 0.42e-6) via its vacated start cell 0 (hop 0→6) | 8 roles moved, 10 hops (v36c 6) |
| R44 | D0 and D4 (1.47e-6) via vacated cells 0 and 3 | everything one row down: 21 roles moved, 13 hops |
| R45 | the same 1.47e-6 | the same row shift |
| R46 | D0, D3, D4 (2.37e-6) | 15 hops, round 2 ticks later (≈ +1.1e-6 waiting); FEASIBLE, not proved optimal |
D1 q20 (1.24e-6), D2 q7 (1.07e-6), D3 q10 (0.9e-6), D5 q22 (0.67e-6), D6 q21 (0.44e-6) cannot get a spare neighbour at
R44 even for the last 3 ticks (proved). Every freed cell is the data's own start cell emptied by a hop, and each hop
costs more than a gadget can recover. The R43/R42 layouts free no data neighbour.

## Open
A prefix change that releases a cultivation guard/helper cell next to q7, q3 or q20 by ≈ tick 33, without touching
A or B/C, for a gadget at round time (the phantom one-ancilla X-type check, −1.35e-6, bounds what one cell can do only
loosely: a single cell touches fewer than 4 data).

## Verified vs inferred
Verified: every loss and acceptance above; model calibration (v36c pinned → R44); OPTIMAL results for R42 and both pinned
halves; geometry infeasibilities. Inferred: per-tick value of a shorter wait (noise scaled); net value of R43/R42
rebuilds; why ENDSTATE's flag failed; that the model's timing transfers to new placements.

## Files
`layout.py` (placement/timing model), `freed.py`, `calib.py`, `pinsplit.py`, `r43.py`, `crit.py`, `geomcheck.py`,
`layouts.json`, `logs/`, `cf/` (counterfactual specs for `MAIN/sparse/region.py`), `noblue.py`, `screen*.py`,
`whatif*.py`, `qedit.py`, `addops.py`, `rmgadget.py`, `tmove.py`, `embed.py`, `timeline.py`, `tl2.py`, `rev.sh`.
