# BFLAG: B/C resource re-synthesis (PLAN P73)

Result: **`final/bflag_d3` = MAIN/v36e, all-orders 3.9234289e-5 (−2.61% vs v36d), acceptance 0.50771, 281 CX**, judge
1e6 PASS, FAST (5.07 s/1e6). It is v36d with only the 57-CX B/C resource replaced by resource r3 (56 CX). PRECELL then
built v36f on it. Closed: none of 14 further fresh syntheses beats r3, and guarding r3's remaining idles is worth ≤ 1.32e-7.

## Finalists (all orders, `MAIN/sparse`)
| File | Base | Resource CX | 1-F | Acceptance | Judge 1e6 | s/1e6 |
|---|---|---:|---:|---:|---|---:|
| `final/bflag_d3` (r3) | v36d | 56 | 3.9234289e-5 | 0.50771 | PASS | 5.07 |
| `final/bflag_d1` (r1) | v36d | 52 | 3.9743046e-5 | 0.50369 | PASS | 7.94 |
| `final/bflag_d2` (r2) | v36d | 55 | 3.9797011e-5 | 0.50613 | PASS | 6.57 |
| `final/bflag_c3` (r3) | v36c | 56 | 4.0064146e-5 (−2.64%) | 0.50447 | not run | |
| `final/bflag_r1` (r1) | v36c | 52 | 4.0610124e-5 | 0.50047 | 1e6 acceptance 0.499898 (gate fails on sampling noise) | 7.03 |
The resource change composes additively: r3 gains −1.087e-6 on v36c and −1.052e-6 on v36d; r1 −0.541e-6 / −0.543e-6.

## Method (`synth_bc.py`, `lns3.py`, `proxy.py`, `pipe.sh`, `mkcand.py`, `splice.py`)
- CP-SAT synthesis with Z faults penalised (`sb1`, Z weight 6) gives a start; a local search re-solves small windows of
  the resource with the solver, scored by a proxy: Δloss ≈ ΔX2 + 1.11e-4·ΔRZ; objective J = X2 + 1.1e-4·RZ + 3e-5·acc1
  (X2 = second-order X-fault loss, RZ = rate at which Z faults flip B's syndrome, acc1 = first-order rejection).
- The proxy ranked all five v36d candidates in all-orders order (d2 vs d1 is d2 trading loss for acceptance).
- The start decides the end point: all ten runs from r1 ended at J 9.39–9.72e-6, both from sb1 at r3's 8.964e-6 (lowest
  RZ: 0.0249 vs 0.0287), from sb3 at 9.39e-6 / 9.72e-6. Fourteen fresh pipelines (`pd_h1–6`, `pd_j1–8`: synthesis then
  search, varied seeds and Z weights) reached J 8.964e-6 at best: pd_j8 is r3 (its second run differs only in the
  direction of a cancelling CX pair, which gives v36f's loss to the last digit), pd_h5 9.386e-6 (3.9468e-5 on v36d),
  pd_j1 9.504e-6 (3.9746723e-5), the rest 9.69e-6 to 1.33e-5.

## Trap for any new B/C resource on v36d or later
v36d's gadgets reuse cells v36c left untouched: q26 is in \|+⟩ after its measurement at 14, q12 is measured in X at 31,
q25 is reset at 32, q11 has a CX pair until 31. Starting q12 or q26 with a measure-as-zero gives random detectors
(all-orders "detector 21 not deterministic"; `fast_check` 5 anti-deterministic). The builders use a plain reset there,
with earliest starts q11 ≥ 33, q12 ≥ 33, q25 ≥ 34.

## Closures (each closes only the recipe tested)
- A fully fault-tolerant resource with all 8 helper cells, 11 layers from tick 33: infeasible (solver proof), as are the
  earlier variants without helpers, with mid-preparation measurements and with one side robust.
- Robust left side plus helpers (`hlh1`/`hlh2`): worse than r3 on X2 (3.3e-6), RZ (0.033) and acc1 (0.14); not built.
- Cancelling CX pairs on idle resource cells: one slot, +3.8e-8 for +0.001 acceptance.
- Reset-then-measure starts on q12, q19, q26: ≈ −4e-9 for −0.0008 acceptance (loses at 3e-5 to 1e-4 per acceptance).
- Soft synthesis alone: J 10.4–10.6e-6; useful only as a start.
- v36c's q13 reset at 33 then measurement at 36 is worth 1.04e-7 (dropping it: 4.0390e-5).
- Guarding instead of re-synthesising (`sparse/idlebound.py`, all B/C idle noise at ticks 33–43 removed for free): v36e
  3.92343e-5 → 3.83983e-5 (8.36e-7); pd_h5 3.94678e-5 → 3.84139e-5; pd_j1 3.97467e-5 → 3.87672e-5. Perfectly guarded,
  both stay behind perfectly guarded r3. On v36f only six idle B/C slots remain: all removed free 3.82436e-5 (1.32e-7);
  the four live ones (q6@43, q11@39, q11@42, q4@43) 2.9–3.7e-8 each, and their only free neighbours are data qubits
  (data-partner guards lose, INTEG). A guard-aware synthesis objective is not worth a round.

## Open
To pass r3 the resource's own non-idle faults must fall: on r3 X2 is 3.03e-6 and RZ 0.0249. B/C headroom on v36c: all of
B/C 24.4% (preparation 14.0%, B→C coupling 10.2%; `region_v36c.jsonl`, specs in `specs/`).

## Verified vs inferred
Verified: all-orders loss and acceptance for every number above; judge 1e6 and speed for d1, d2, d3; the solver's
infeasibility results; the idle bounds; reproduction of v36f. Main session re-verified `bflag_d3` and promoted it as v36e
(board 3.67131e-5 at 07:37). Inferred: that PRECELL's non-B/C edits help any resource equally (the pd comparisons are on
v36d); not run: 3-seed means.

## Files
Finalists `final/`; resources `syn/r1.json`, `syn/r2.json`, `syn/r3.json` and the search states in `syn*/` (`pd_*` in
`syn_hippo/`, `syn_jerry/`); build `mkcand.py <json> <name> default v36d`, `splice.py`, `synth_bc.py --base v36d`,
`lns3.py`, `pipe.sh`, `pairfill.py`, `initvar.py`; evaluation `ao.sh`/`ao_owl.sh` (all orders on a host, `sparse/aorun.py`),
`judge.sh`; bounds `sparse/idlebound.py` (IDEAS `abl.py`/`chan.py`); region specs `bcspec.py`, `specs/`. Candidates are
rebuilt with `mkcand.py`; the evaluator is `MAIN/sparse` (symlinked).
