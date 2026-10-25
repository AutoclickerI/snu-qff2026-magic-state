# INTEG2: re-integration of gadgets on v36f (PLAN P75)

Result: **`integ2_h2` = MAIN/v36g, all-orders 3.836054467100275e-5 (−1.55e-8, −0.040% vs v36f), acceptance 0.50151,
320 CX**, judge 1e6 PASS (acceptance 0.501167), FAST (2.59 s/1e6 single process; `speed_predict` 3.3 s), 81 deterministic
detectors. Fallback `integ2_g1` (same without the six timing shifts) 3.8369001604011376e-5 (−7.06e-9), PASS, FAST.
Verdict: the gadget space on v36f is used up: no v36f element hurts, the best new single gains 1.7e-9.

## Changes vs v36f (removal cost from the joint; positive = it pays)
| Element | Price | Δacc if removed |
|---|---:|---:|
| echoX q11, helper h17, ticks 20–27 | +1.99e-9 | +0.00315 |
| guard h12→q13, 8–10 | +1.51e-9 | +0.00090 |
| pair 6→7 at 8 | +1.22e-9 | −0.00100 |
| pair 5→11 (run 20–26) | +7.0e-10 | −0.00100 |
| guard h28→q22, 22–29 | +6.3e-10 | +0.00074 |
| guard h18→q19, 6–7 | +6.2e-10 | +0.00094 |
| pair 20→26 at 29; echoX q12 h18 20–23; guard h5→q4 8–9; pair 16→17 at 24 | +1.8 to +2.8e-10 each | |
| MX→reset on init checks c187, c183, c186, c188 (together) | +1.8e-10 | −0.00337 |
| CX 3→4 tick 20 → 19 | −7.4e-9 (gain) | |
| CX 20→21 27→28, M q13 32→33, CX 5→11 23→21 and 24→26, CX 16→17 24→22 | −1.0e-9 together | |
The trades and shifts were priced alone and in the whole circuit, not removed one at a time from the final joint.

## Leave-one-out of v36f's 49 elements (removal cost)
q6 unread guard 5.8e-7 (its q7 ticks 3.9e-7, q0 ticks 2.0e-7); q13 guard 2.1e-7; BFLAG pair 4→5 at 38 1.5e-7; late
guards g32 1.4e-7, g33 9.5e-8, g24 9.0e-8, g18 7.3e-8; q14/q21 echo ends 1.4e-7; pair 20→14 at 40 1.2e-7; INTEG echoes
h21 on q15 6.9e-8, pguard16 6.4e-8, h12 on q13 3.1e-8, h26 on q20 2.7e-8, Z-echo on q6 2.3e-8; INTEG pairs 1.0–2.6e-8
each. Nearly worthless now: echo h25 on q19 6.2e-9 (+0.0060 acceptance if removed), echo h22 on q21 5.6e-9 (+0.0051),
echo h6 on q0 4.9e-9, pairs 20→21 1.3e-9 each, extension 10→16 1.3e-10 (`loo_i2_v36f.json`).

## Closures (each closes only the recipe tested)
- 115 new singles with legality re-derived on v36f's schedule: best −1.72e-9; late pairs with A/B partners still lose
  8e-7 to 1.2e-6 (`singles_i2_v36f.json`).
- 186 acceptance trades (drop the detector, omit the measurement, or reset instead, on each of 62 single-bit checks): all
  cost loss (`trades_table.txt`).
- 184 remove-one-add-another swaps on the freed helper: best −1.6e-9.
- Missing detectors: only two deterministic record parities lie outside the detector span (c281, c295); adding them
  changes loss < 3e-16 and costs 0.003–0.006 acceptance (`detgap_*`).
- q6 guard target pattern at 37–41: all 31 alternatives lose ≥ 1.7e-8; pguard16_22 instead of pguard16_10 +1.0e-8.
- Timing shifts ±3 ticks on v36f (197): one gain; on the joint ±3 at most −3e-10, ±12 nothing.
- Acceptance has no buyer: ≈ 0.018 is available for < 2e-8 total loss (MX→reset on c181–c188 +0.0068 for 4.2e-9;
  removing or guard-replacing echoes h22, h25), but no gadget on v36f is worth buying with it.

## Open
Bundling ≈ 27 trades at once broke additivity (+1.43e-6) although each priced fine alone; not diagnosed (nothing needed
the acceptance).

## Evaluator
`MAIN/sparse` used reviewer 9's v36c basis only, so v36f fell back to the plain basis (≈ 130 s at 16 processes). `ev2.py`
searches a basis per circuit from a warm start (`warm_v36f.json`, from `mkwarm.py`): 5.5 s on v36f, matching `MAIN/sparse`
within 2.2e-16 on four circuits. The main session ported this into `MAIN/sparse` (`compile_best`, `basis_warm.json`,
`fastfill.py`).

## Verified vs inferred
Verified: v36f reproduced; rebuilding v36f from the plan gives bit-identical text; both finalists confirmed with
`MAIN/sparse`; judge 1e6, speed and detector determinism on both. Main session re-ran `integ2_h2` with `MAIN/sparse`
(3.836054467100275e-5, 0.5015149656) and judge 1e6 (PASS, 0.501167). Not run: 1e8, 3-seed means; one-at-a-time removal
of the trades and shifts in the final joint; multi-change combinations beyond the swaps. Inferred: that the menu is
exhausted beyond singles, the greedy chain and swaps.

## Files
Finalists `integ2_h2.*`, `integ2_g1.*`, `finalists.json`; builders `lib.py`, `gadgets.py`, `joint.py`, `guards_pc.py`,
`elements.py`, `loo_build.py`, `singles.py`, `swap.py`, `shift.py`, `greedy.py`, `knap.py`, `detgap.py`, `moves.py`,
`tab.py`, `dump.py`; evaluator `ev2.py`, `mkwarm.py`, `warm_v36f.json`; data `loo_i2_v36f.*`, `singles_i2_v36f.*`,
`trades_table.txt`, `detgap_i2_v36f_*.json`, `*.list`, `i2sh*.json`; `logs/`. Candidates `c/` and results `res/` were
rebuildable and are deleted.
