# PRECELL: guards for late-idling data and B/C qubits (PLAN P82)

Result: **`precell_eg` = MAIN/v36f, all-orders 3.837606198613569e-5 (−2.19% vs v36e), acceptance 0.50439, 293 CX**,
judge 1e6 PASS (acceptance 0.504456), FAST (≈ 4–5 s/1e6); official seed-0 1e8 on hippo 3.814798435873977e-5 ± 7.4e-7,
acceptance 0.50435168. Intermediate: `precell_e` (v36e + ported edits) 3.879041e-5 (−1.13%), 1e8 seed 0 3.825498e-5;
`precell_nom7` (on v36d) 3.9884193e-5 (−1.00% vs v36d), 1e8 seed 0 3.850306e-5.

## Bounds on v36d (all orders; idle runs made perfect = ceiling)
| Idle runs perfect | 1-F | Δ vs v36d |
|---|---:|---:|
| q20 late (36–39, 42) | 3.9465696e-5 | −8.20e-7 |
| q7 late (34, 37–43) | 3.9314151e-5 | −9.72e-7 |
| q3 late (34–43) | 3.9332008e-5 | −9.54e-7 |
| q10 late (35–38, 40–41) | 3.9592273e-5 | −6.94e-7 |
| q10 late plus its tick-44 idle | 3.8207440e-5 | −2.08e-6 |
| q20 + q7 + q3 / all four | 3.7800855e-5 / 3.7329137e-5 | −2.49e-6 / −2.96e-6 |
| q0, q22, q21 late | | −4.07e-7, −5.89e-7, −3.94e-7 |
Phantom single-cell gadgets (an off-grid ancilla touching only those data): the best is a continuous guard (fresh helper,
CX with the data on every idle tick, measured at the end), which leaves ≈ 40% of the idle error undetected (≈ 60% of
each bound). Helper free for the whole late window (no real cell is): q7 −5.81e-7, q3 −5.72e-7, q20 −4.91e-7, q10
−4.16e-7. X-echoes come out below guards; Z-echoes lose on q3, q10 (+1.1e-7, +5.7e-8: the helper's Z errors reach the
data undetected). Realistic windows (ending when the neighbour's A/B/C role starts): q7 at 37–40 via q6 −2.92e-7; q3 at
34 plus q10 at 35–37 via q9 −2.45e-7; q3 at 34–35 −1.15e-7; q20 at 36 −9.8e-8. Every neighbour of q20, q7, q3, q10 is an
A, B or C cell whose role starts at 32–41, so a release at ≈ 33 buys at most a couple of ticks; q6 (B from 42) is the
exception.

## Edits (v36d → precell_nom7 → ported to v36e as precell_e)
1. q6: its X-echo on q0 (32–40) becomes one continuous guard: reset to \|0⟩ at 31, CX 6→7 at 32 and 34–41 (6→0 at 33),
   then straight into its B role at 42 with no readout; a guard X fault stays on q6, is copied to C at 44 and flagged
   there. Under BFLAG's r3, q6 keeps MX 40, reset 41, CX 12→6 at 42, so the unread guard is legal (readout dropping worth
   5.7e-8).
2. q1's CX pair at 35–36 moved from q7 to q0 (dropped on v36e).
3. q14's X-echo on q20 ends at 36 instead of 35; its MX at 37 replaces A's reset as the \|+⟩ init.
4. q21's Z-echo on q20 ends at 35 instead of 34.
5. On v36e only: r3 starts q13's B role later (measure-init at 37), so q13 sits as known \|0⟩ at 33–36 next to q7; it
   guards q7 at 34–36 and its measurement at 37 reads the guard; q6 then takes q0 at 33–36.
Leave-one-out on v36e (removal cost): q6 guard 2.15e-7, q13 guard 2.13e-7, q14 echo end ≈ 1.3e-7, q21 echo end 1.5e-8.

## Guard menu on precell_e (51 guard singles, 25 INTEG-style late singles, combinations priced whole)
Only guards on B/C resource qubits idling at 40–42 pay; their neighbours include never-used cells (q24, q32, q33) and q18
(free until its reset at 44). Kept (removal cost): q32 → B q26 at 40–41 (1.44e-7), q33 → B q27 at 42 (9.5e-8), q24 → C
q25 at 41 (9.0e-8), q18 → C q12 at 41 (7.3e-8), q22 → q21 at 15–16 (1.2e-8). Inferred mechanism: those idle Z errors would
show up as false data Z syndromes at B's readout; a guard cuts them from 2p/3 to 4p/15 per tick.

## Closures (each closes only the recipe tested)
- Freeing q9 by routing D6 through q14 (8→14→15): the reroute costs +6.28e-7; best version +3.57e-7.
- Skipping the guard readout on q11 or q13 (v36d): loses (their X faults enter the B/C encoder as unflagged seed errors).
- Echo ends merged into the next init: q19 (v36d +1.1e-8; v36e into its C init +5.6e-7); q13 −3.2e-8 alone but competes
  with q6 for tick 32; q2 valid but sends xtim to the slow path (216 s/1e6).
- q6's early role (13–30) as a guard: invalid (its CX 7→6 at 18, 25 are cultivation logic; five non-deterministic
  detectors).
- Prefix guards on helper qubits, helper echoes in ticks 15–31: within ±2e-9. Late CX pairs with A partners (q0–q1,
  q1–q2, q1–q7, q2–q3, q16–q22): +0.8 to +1.2e-6. Pair q26–q32 at 40 −4.8e-8, beaten by the guard on the same ticks.
- The guard menu is used up on the current schedule.

## Verification
Every number from the all-orders evaluator (`MAIN/sparse`), results tied to qasm hashes; every built circuit passed the
judge gates; finalists judge 1e6 PASS, FAST, 1e8 seed 0 as above. Main session re-verified `precell_eg`
(3.837606198613569e-5, 0.5043917, judge PASS, FAST). Not run: 3-seed means, re-draws. Speed timings vary with host load.

## Next
Make guardability part of the B/C resource objective: count idles on cells next to free cells (q12, q19, q25, q26, q27,
q28, q29) as guardable so the resource schedule puts its idles where a guard reaches them (sent to BFLAG).

## Files
Finalists `precell_eg`, `precell_e`, `precell_nom7`, `precell_z_a` (.qasm, .json); builders `build_*.py`, `guards.py`,
`joint_g.py`, `integ_menu.py`; tools `phantom.py`, `redit.py`, `scan_merge.py`, `gaps.py`, `rg.py`, `ev.py` (prices
through `MAIN/sparse`, caches in `res/`); data `bounds.txt`, `results.tsv` (174 priced stems), `cf/`, `logs/`.
