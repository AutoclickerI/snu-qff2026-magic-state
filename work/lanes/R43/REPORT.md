# R43: earlier-round end state (PLAN P84)

Verdict: **closed without a build.** One tick less of pre-round data wait with the incumbent's A and B/C blocks is worth
**−0.68e-6 (−1.8%) for R43 and −1.31e-6 for R42**, a quarter of the ≈ 2.6e-6 that reopened the lane, while a rebuild
re-does A, B/C, hops and every guard. A larger lever, the A-flag gap (−1.61e-6), has no room on the grid at R ≤ 44.

## The prize, exact (`sparse/tickval.py`, all orders; v36h reproduced at 3.815473322405639e-5, acceptance 0.5016415)
The judge charges a whole idle run as one channel after the op that opens it, so shortening a run by one step is exactly
the same circuit with that wait one tick shorter.
| Change on v36h | Δ 1-F | Δ acceptance |
|---|---:|---:|
| every data wait one tick shorter (R43 prize) | **−0.6844e-6** | +0.0035 |
| two ticks shorter (R42 prize) | **−1.3095e-6** | +0.0070 |
| one tick longer (control) | +0.7470e-6 | −0.0035 |
| one tick on q0, q20, q7, q10, q3, q22, q21 alone | −0.084, −0.151, −0.114, −0.106, −0.083, −0.088, −0.088e-6 | +0.0005 each |
| flag-gap idle at tick 44 on q10, q21 made noiseless | −1.370e-6, −1.351e-6 | |
Which tick of each wait disappears moves the R43 prize within −0.58 to −0.68e-6 (EARLY estimated ≈ 0.56e-6). The extra
acceptance is worth ≈ 0.06e-6 at ACCBUY's rate. Removing 1, 2, 3 ticks of one run: −0.151, −0.303, −0.454e-6.

## Why ACCBUY's +2.6e-6 per inserted tick does not transfer (`insert.py`, `ins/`)
| Tick inserted before | Total | Data | A cells | B cells | C cells |
|---|---:|---:|---:|---:|---:|
| 37 | +2.554e-6 (ACCBUY +2.58e-6) | +0.649e-6 | +0.221e-6 | +0.242e-6 | +1.380e-6 |
| 40 | +2.557e-6 | +0.747e-6 | +0.263e-6 | +0.494e-6 | +0.962e-6 |
| 43 | +2.762e-6 | +0.747e-6 | +0.398e-6 | +0.743e-6 | +0.746e-6 |
About three quarters is noise on A, B and C in the middle of their preparation; an earlier round moves those
preparations, it does not shorten them, so only the data share returns.

## What a rebuild needs (EARLY's layout model, fewest moved roles, OPTIMAL; `layout.py`, `lay/`)
R43: 9 of 21 roles move (A1, A2, A6, B1, B2, B6, C1, C2, C6), 6 hops (D1 20→21, D2 7→13, D6 8→14), flag {7, 8, 9}.
R42: 12 roles, 8 hops. Each rebuilt block alone usually costs more than the prize (inferred from other lanes): AENC's
next-best A encoder +1.4e-6; a fresh B/C synthesis lands ≈ 0.7e-6 above r3 (2 of 14 runs reached it); ≈ 3e-6 of
v36c → v36h is layout-bound gadgets, guards and r3; a hop costs 0.1–1.0e-6.

## The A-flag gap (`gapfill.py`, `gap/`, 40-qubit evaluator `sparse40/`)
The A decoder makes the flag data q10, q21 do D→A at 43 and wait at 44 before B→D at 45. An off-grid helper on each
(identity CX at 44): **3.654533979885716e-5, acceptance 0.49950, −1.609e-6 (−4.2%)**; q10 alone −0.82e-6, q21 alone
−0.81e-6; a |0⟩ helper instead of |+⟩ −1.603e-6; the zero-change control reproduces v36h. In v36h every neighbour of
the flag data is busy at 44 for either flag orientation; the layout model finds two helpers infeasible at R43 and R44,
feasible at R45 (12 hops, 17 moved roles) or R46 (10 hops, 15 roles); one helper at R44 needs 10 hops. None looks like
it pays after the extra hops and waiting (inferred).

## Verified vs inferred
Verified: every all-orders number, the insertion split, the off-grid helper prices against a control, the layout solves.
Inferred: that a rebuilt suffix loses more than the prize; that the layout model (calibrated on v36c) holds for new
layouts; that an off-grid helper prices an adjacent one. Not built: no candidate, judge run or speed check.

## Files
`results.json` (every number), `sparse/tickval.py`, `price/`, `insert.py`, `ins/`, `gapfill.py`, `gap/`, `sparse40/`,
`layout.py`, `near.py`, `helper.py`, `lay/`, `crit.py`, `timeline.py`, `v36h.timeline.txt`, `qedit.py`, `runs.py`.
(Written by the main session from the lane's final message; the lane's own write was blocked.)
