# FASTR43: FAST realizations of SLOW-but-better edits on v36f (PLAN P72)

Verdict: **closed, no finalist.** Neither edit pays on v36f, and both are SLOW by a mechanism of xtim's exact engine
that no FAST gate choice avoids in the places these edits need.

## Prices on v36f (all orders, `MAIN/sparse`; lane copy with the SX-capable frontend reproduces v36f and FRESH's v35b SX)
| Circuit | 1-F | Acceptance | Δ vs v36f | Engine | s/1e6 (1 proc) | Judge 1e5 |
|---|---:|---:|---:|---|---:|---|
| v36f | 3.837606198613569e-5 | 0.50439 | | FAST | 3–5 | |
| `c/q8reuse` (R43, depth 46, 283 CX) | 3.8370177458227455e-5 | 0.51013 | −5.9e-9, +0.0057 acc | SLOW, 141 atoms | 251 | PASS |
| `c/v36f_nopairs22` (control: the five identity pairs crossing tick 22 dropped, R44) | 3.842604122720407e-5 | 0.49939 | +5.0e-8 | FAST | | |
| `c/sx_full` (SX/SX† on all 7 data) | 3.851637006654448e-5 | 0.50440 | **+1.40e-7 (+0.37%)** | SLOW, 306 atoms | 324 | PASS |
On v36f tick 22 carries five identity CX pairs, so the q8 port drops them and shifts every later op one tick. Against the
control, the one-tick compression is worth −5.6e-8 and +0.0107 acceptance: it removes a tick inside the cultivation and
only translates the late data wait (EARLY's ≈ 0.56e-6 per tick was for shortening the wait). The SX layer, −2.2% on
v35a, now loses.

## Mechanism (toy circuits in `toy_rules.py`)
xtim compiles a measurement as a CX onto a fresh wire (MX as H–CX–H) and a reset as a new wire; a measurement that ends
its wire is a terminal read, which tolerates the phases T gates leave on propagated errors. The slow path starts when
such a phase meets an H in the middle of a wire. Noise, T, terminal MX: fast; with reset then reuse: fast; MX then reuse:
slow; Z measurement then reuse: fast; noise, T, SX, then CX: slow; noise, T, SX, terminal read: fast.
- q8 reuse: all 141 failing atoms are X errors from before tick 21 (the T-check region) failing at the H inside MX8@21;
  in v36f RX8@22 ends q8's wire, making MX8@21 terminal. A Z measurement after a basis change is the same MX.
- SX: the 306 failing atoms are X errors that pass each data qubit's final T† and hit the H inside SQRT_X, on all seven
  wires; every data qubit has noise before its T†. Diagonal gates and CX keep Z as Z, so no FAST gate set reproduces
  SX's Z→Y conversion.

## Closures (each closes only the recipe tested)
- Critical path: v36f is tight from tick 0 to 46; removing all 35 identity pairs leaves depth 47. The only single reset
  whose removal reaches depth 46 is RX8@22; the other reset-after-measure points on the path (MX2@27→RX2@28, MX2@35→R2@36)
  are SLOW (141, 206 atoms); dropping source checks c54–c57 alone keeps depth 47.
- All 27 measure-then-reset pairs screened: 22 FAST, none on the critical path with a matching basis.
- Blue-check reorders that free q8 by tick 31: all four orders make a detector non-deterministic; an exhaustive search of
  q2's gate sequences at ticks 29–34 finds no equivalent (the check also exchanges the data on q3 and q8).
- Re-encoding on another hub: q8 is the only qubit adjacent to q2, q7, q9 and q14, so its four CX at 23–26 stay serial.
- A/B role swap (Y-check dual for the SX benefit): not built; A-encoder noise on v36f is 1.48e-6 (Z-containing 1.24e-6),
  so at most ≈ 0.6e-6 to gain, against B/C X-containing errors of 6.52e-6 that would return as Z errors (inferred).

## Open
R43 needs a depth-3 re-encode after the MX8 readout, a cultivation fold whose second hub is not measured inside the
T-check region, or a blue check with a different gate set that frees q8 by tick 31 plus a new A encoder; and then the
acceptance (+0.0107) must be spent on gadgets to pay.

## Verified vs inferred
Verified: every price and acceptance, ideal and single-fault certificates (c1 = 3.09e-19), atom counts and failing gates,
toy rules, speeds (2 × 20k shots), judge 1e5 passes, depth analysis, the reorder failures and exhaustive search.
Inferred: the A/B swap's net; that other fold trees cannot help (only the adjacency fact was checked).

## Files
`results.json` (every number), `c/` (circuits with all-orders, atom, certificate, speed outputs), `fr.py` (toolkit),
`port_q8.py`, `port_sx.py`, `port_sx_v35b.py`, `scan_reuse.{py,json}`, `asap.py`, `asap2.py`, `crit.py`, `blue.py`,
`blue_search.py`, `toy_rules.py`, `sparse/` (SX-capable `frontend.py`, `region_type.py` for error-type counterfactuals;
evaluator symlinked to `MAIN/sparse`), `spec_*.json`, `logs_*`.
