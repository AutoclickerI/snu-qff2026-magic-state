# ACCBUY: spending free acceptance on v36g (PLAN P83)

Result: **`accbuy_f1` = MAIN/v36h, all-orders 3.815473322405639e-5 (−2.058e-7, −0.54% vs v36g), acceptance 0.50164,
327 CX**, depth 47, R44, judge 1e6 PASS (acceptance 0.501579, 79 deterministic detectors), FAST (2.6 s/1e6 single
process; `speed_predict` 3.6–5.7 s). The gain is a new family, **known-state guards**, not acceptance buying.

## Known-state guards
A helper in a known state (|0⟩ as CX control, or |+⟩ as CX target) next to an idle data qubit runs a CX that leaves the
data unchanged: the data's idle DEPOLARIZE1(p) becomes the data marginal of DEPOLARIZE2 (4p/5), and the helper's reset
moves into a tick where it was unused. Leave-one-out on j4 (j5b's base):
| Element | Gain | Δacc |
|---|---:|---:|
| q4: reset 37→36, CX 4→10 @37 (keeps the 4–5 pair @38–39) | −6.51e-8 | ≈ 0 |
| q22: reset 34→33, CX 22→16 @34 | −5.25e-8 | ≈ 0 |
| q19: reset 35→33, CX 19→20 @34 | −2.2e-8 | −0.0003 |
| q12: init 18→16, CX 12→6 @17 | −5.1e-9 | ≈ 0 |
| q11: known-\|0⟩ control, CX 11→10 @32 | −1.11e-8 | +0.0004 |
| q13: known-\|0⟩ control, CX 13→14 @32 | −7.0e-9 | ≈ 0 |
| q18 read variant: reset 40→34, CX 18→19 @35 | −4.27e-8 (unread variant −1.47e-8) | −0.0017 |
| trades c181, c182 (MX→reset) | fund the q18 acceptance | + |
The q18 buy prices acceptance at ≈ 1.6e-5 loss per unit. A greedy round on j5b over 121 single candidates (3 rounds,
floor 0.5005) found nothing more; ±2-tick shifts and moving q1 guard ticks from q6/q13 found nothing on j4.

## Acceptance buyers that cannot be built (each closes only the recipe tested)
- Late stabilizer checks as phantoms (off-grid ancillas, full noise; `sparse40/` evaluator with 40 qubits): S12XZ −2.34e-6
  for −0.0029 acceptance, S123X −1.26e-6 for −0.0010, one-ancilla X ≈ −0.8e-6; Z-only checks lose or barely pay. Room
  for them costs more: one inserted idle tick costs +2.58e-6 at 37, +2.59e-6 at 40, +2.80e-6 at 43 (≥ 1.3e-6 from 34 on),
  and earlier ticks are too early.
- No code stabilizer element has a free neighbour on every support cell at any tick boundary 13–45; the T window folds the
  code (no weight-4 Z element in 17–28); split-Bell/GHZ late checks need role cells busy at 37–43; hop-clear parity
  accumulation completes no element; measuring two weight-2 halves separately disturbs the state.
- v36g adjoint (692 channels, `MAIN/sparse/v36g_adjoint_72.json`): final data idles ≈ 5.4e-6 each, final B→D CX ≈ 2.2e-6
  each, q10/q21 idles at 44 ≈ 1.4e-6 each, q3 10-tick idle 8.6e-7, q0 7-tick idle 6.0e-7.

## Trade bundles (INTEG2's open item)
The 27 cheapest trades together cost +1.55e-6 (acceptance 0.5314) though each costs ≈ 1e-9 alone: back-to-back redundant
measurements of one qubit each look free alone because the partner still checks; dropping both removes the check. c5 +
c284 (q9 @15/16) +2.59e-7; c277 + c302 (q5 @33/35) +2.95e-7; ≈ +1.18e-7 not isolated. Price trades on the same qubit
together.

## Verified vs inferred
Verified: v36g reproduced; the finalist's all-orders loss and acceptance (main session re-ran `MAIN/sparse`:
3.815473322405639e-5, 0.5016415049; judge 1e6 PASS; FAST); native schedule equals the plan; every element pays (leave-one-
out); greedy found no more. Inferred: phantom gains are upper bounds (ideal adjacency); insertion costs show those checks
do not pay, not every late-round restructuring was tried. Not run: 1e8, 3-seed mean, re-draws.

## Files
`accbuy_f1.{qasm,json}`, `c/j5b.plan.json` (native plan) and the `.list` gadget sets; builders `lib.py`, `elements.py`,
`joint.py`, `guards_pc.py`, `moves.py`, `kstate.py`, `gen2.py`, `gen_late.py`, `greedy.py`, `loo.py`, `shift.py`,
`singles.py`, `place.py`, `prerole*.py`, `cellslots.py`, `dataslots.py`, `idlemap.py`; phantom evaluator `sparse40/`
(40-qubit `frontend.py`), `ph.py`, `ph/`, `ph2/`; data `g4q.txt`, `k3.txt`, `loo_sh4.txt`, `sh4.*`, `tr27.txt`,
`greedy_j5b.log`. Candidates `c/*.qasm` were rebuildable and are deleted.
