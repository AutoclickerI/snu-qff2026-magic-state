# TERM: final round redesigned backward on v36c (PLAN P77, reviewer 8 #10, reviewer 9 M08)

Verdict: **no finalist.** No terminal template beats the Steane round's data-side cost on this grid, and partial-rank
syndrome extraction (all 2,824 proper subgroups) loses to full rank.

## Floors (second order, data side; model exact, not fitted)
- **Class floor 22.87 p² = 2.287e-5 (2.274e-5 all orders)** for any circuit whose outputs make a CX at T−1 with a partner
  measured at T, then idle at T. The partner's measurement cannot see an error in its own basis, so that CX leaves
  D1(2p/5) on each output; the proved 1.162e-5 floor assumes D1(p/5), which no measured partner reaches.
- **Two-check floor 25.67 p²** (an X check at T−2, then a Z check at T−1): adds the unavoidable leaks (I_P, X_D) from
  the T−2 CX and (X_B, I_Q) from B's last CX before use.
- The model gives 28.84 p² for the Steane round (ARCH's exact2 split) and 25.573 for the B→D-first template (exact2
  2.5573e-5). `terminal_model.py`, `terminal_model.json`.

## v36c's loss by part (all-orders counterfactuals, `MAIN/sparse/region.py`)
- **Round, everything before it noiseless: 3.041e-5** (`spec_round_only.json`, 460 of 552 channels perfect, acceptance
  0.949) = 2.274e-5 class tail + 0.768e-5 leaks (model 0.767e-5): 0.28e-5 two-check floor; 0.32e-5 D→A and B→C leaks
  at 2/15 instead of 1/15; 0.17e-5 the D10/D21 idle at tick 44 (the price of the A flag).
- **A, B and C preparation: 0.456e-5** (T14's suffix-only 3.497e-5 minus round-only).
- **Prefix and waiting: 0.618e-5** (T14).
- Adjoint on v36c (`v36c_adjoint_72.json`, now `MAIN/sparse/`): seven final data idles 5.3–5.4e-6 each, seven B→D CX
  2.2e-6 each, D10/D21 idles at 44 1.39e-6 and 1.37e-6.
- So a terminal template can gain at most ≈ 0.49e-5, and every route found is blocked on this grid.

## Templates
| Template | Mechanism | Screen value | Result |
|---|---|---|---|
| Steane round (reference) | D→A leaves 2/15 X undetected on the data; B→C leaves 2/15 X on B, copied by B→D | 28.84 p² | grid-free round 2.871e-5 (total 3.548e-5); v36c round-only 3.041e-5 |
| B→D at T−1, then D→A ∥ B→C at T, reads at T+1 | C checks B after B→D, but A's Z errors reach the data after B's check | round only, A/B/C perfect: 2.5458e-5 (−11%) | closed: grid-free build passes the noiseless judge but c1 = 4.667e-4 (total 5.888e-4); break-even needs ≤ 0.075p single-Z per A qubit, one idle tick alone gives 0.33p (`arch/tmpl_BDfirst.*`) |
| Same with A verified before use | the verification CX leaves Z on A; a Z leak costs twice an X leak | — | closed (ARCH `reverse` 3.464e-5 vs 2.871e-5) |
| C checks B after B→D, extra tick | the data idle one more tick | — | closed (ARCH `C_after` 6.02e-5) |
| A X-parity coverage of all 7 data after D→A | halves the D→A leak | 27.21 p² | blocked: {8,9,15} is the only weight-3 X_L of A forming a grid path; no free cell borders A |
| Halve B's leak | B's checker must see both bases; Z on C's literal-zero state does nothing | → 25.67 p² | blocked by the literal-zero C; terminal B flags closed (COMP29 certificate) |
| Fill the D10/D21 gap at tick 44 with a CX onto a fresh \|+⟩ | leak 5/15 → 2/15 X; the \|+⟩'s Z error is caught by B at 45 | model −1.46 p² (≈ −1.5e-6) | blocked: all 8 grid neighbours of cells 10 and 21 are busy at tick 44 |
| D21 alone reversed (B27→D21 at 44, D21→A15 at 45) | C checks B27 after its data coupling | model −0.85 p² | invalid (`v36c_d21r`): detector 14 non-deterministic, A15 picks up B27's random codeword bit (rank-2 A syndrome) |
| M08 partial-rank extraction, all 2,825 subgroups | the judge decodes all six, so a proper subgroup lets unmeasured incoming syndrome sectors through | perfect meter on v36c cut after tick 43, full rank: 1.79e-6 (no tail) / 1.342e-5 (+ final idle) / 2.453e-5 (+ class tail); **0 of 2,824** proper subgroups beat full rank under any tail; best penalty rank 5 +1.01e-5 (one mixed generator), +3.3e-5 (pure CSS); rank 4 +3.5e-5; rank 3 +1.28e-4 | closed: 7.12% of accepted shots reach the round with a nonzero syndrome; a data qubit uncoupled at T−1 pays D1(p) instead of D1(2p/5), and no subgroup gadget uses fewer data CX than Steane |
| Teleport-style output handoff (FRAME_Z) | same unseen-partner survivors at T−1 | isomorphic | closed (ST_TP) |
| Dummy final CX, synced reads, early A, hybrids, Knill/Bell, repeated rounds, 128 order masks | — | — | ARCH; the model shows why each loses |

## Verification
- M08 boundary moments (all orders) reproduce the evaluator's loss on the cut to 1e-16; the evaluator reproduces v36c
  4.11516e-5; the template value is exact2 third order on a build that passes the noiseless judge.
- Main session re-ran the round-only counterfactual: 3.0413e-5, acceptance 0.9491.
- Not run: official 1e6 judge or MC on any new circuit (none reached finalist stage).

## Files
`terminal_model.{py,json}`; `arch/` (template builds and exact third-order runs); `m08/{truncate,boundary_moments,
screen}.py` with `v36c_b43.{qasm,moments.json,m08_screen.json}`; `spec_round_only.json`; `v36c_adjoint_72.json` →
`MAIN/sparse/`; `v36c_d21r.{qasm,json}` and `build_d21r.py` (invalid build kept as evidence); `ticks.py`.
