# Independent strategy review: seeking a large native improvement

## Decision

**The best supported method is to synthesize a complete noisy preparation and its checks directly on the grid, optimizing the accepted quantum operation and its full conditional loss.** Use algebraic state/measurement identities to generate alternative implementations, a diverse beam or large-neighborhood search to explore them, and CP-SAT for small scheduling, placement, or parity-synthesis subproblems. The method is a recommendation based on the measured failures below; no global optimality or future performance guarantee is claimed.

The current evidence does not justify making the best unrestricted-connectivity circuit the mandatory target and spending the whole architecture budget embedding it. It also does not justify abandoning solvers. Several useful exact local results came from CP-SAT. The failure is primarily the chosen representation, interface and cost function: preserving one abstract gate list, optimizing CX count or clock count, and discovering its physical error cost only after placement.

The largest missing comparison is a common **source × ending × preparation** matrix. Change sources and terminal checks independently, then compare the complete native combinations. A new source should not inherit the old ending by default, and a new ending should not be judged using a perfect source or perfect helper preparation.

## Evidence and progress

These are recovered results, not experiments rerun by this review. The native-risk and architecture lanes may add new results after this report.

| Construction | Evidence level | Expected loss | Acceptance | What it establishes |
|---|---|---:|---:|---|
| MAIN/v37j | Complete native circuit | 3.58709500347e-5 | 0.50101790 | Production reference |
| Late native phase pair | Complete native, official 100M validation | 3.56812723913e-5 | 0.50101605 | A reproducible 0.5288% improvement; 412 CX and 49 clocks |
| Joint encoder/phase network | Complete native, raw-valid | 8.48960074708e-5 | 0.68901192 | 134 CX and 31 clocks do not imply low logical loss |
| Shorter native source/resource assembly | Complete native | 3.80823788643e-5 | 0.50385382 | A verified 48-clock construction still loses |
| Shared GHZ flags plus square ending | Complete abstract circuit | 3.26709931735e-5 | 0.68530182 | Useful mechanism; hardware implementation uncompetitive |
| Same abstract family using native bridges | Complete native | 0.18268418 | 0.00033471 | Literal bridge routing fails decisively; 724 CX and 391 clocks |
| DEEP flag-based architecture | Historical documented abstract result; exact artifact not recovered | 2.7185414e-5 | 0.6734 | A research lead, not a reproducible current candidate |
| Latest local small-cat control, `oldA_bell4_mixed_s003_late` | Complete abstract circuit and saved all-orders receipt | 3.34074022672e-5 | 0.75570223 | Smaller checks are plausible but alone leave little implementation margin |

Sources: `EXPAND2_20261027/release_phase/README.md`, `REBUILD20261027/REPORT.md`, `EXPAND2_20261027/REPORT.md`, `CAT3_20261027/old_a_late.json`, and `docs/PLAN.md`.

### The DEEP result needs its actual circuit recovered

The plan and continuation briefs cite `DEEP/cand/final_flagh.json`, a QASM stem ending in `9a83951a37ad3cb5_d0_1_2_3_4_5_6`, 170 CX, 22 clocks, and 36 wires. In the inspected local snapshot `DEEP/` contains only `BRIEF.md` and `CONTINUE1.md`; the local all-ref history has no entry for the report or named JSON. GitHub default-branch fetches for `DEEP/REPORT.md` and `DEEP/cand/final_flagh.json` both returned 404. At research commit `6bfb381d4cdaf8ebb556dd66fbe7c55513102dba`, the GitHub DEEP directory likewise contains only the two briefs.

This establishes that the result cannot currently be replayed from the inspected checkout and refs. It does not establish that the circuit never existed; it may remain on the original hosts or outside tracked history. Do not silently replace it with a newly reconstructed circuit and retain its score. Recover the precise QASM, ordered outputs, detector policy and evaluator receipt before treating 2.7185e-5 as a current baseline.

### The nominal margin is small

Using the verified native loss 3.56812723913e-5:

| Desired native outcome | Target loss | Net score difference above documented DEEP result |
|---|---:|---:|
| Any improvement | 3.56812723913e-5 | 8.49585839e-6 |
| Approximately 16% improvement | 3.00000000000e-5 | 2.81458600e-6 |
| 20% improvement | 2.85450179130e-5 | 1.35960391e-6 |

These differences are screening arithmetic, not additive physical noise budgets. An individual grid-free score is **not a rigorous lower bound** on its routed counterpart: postselection can change the ranking when noise and operations change. The repository already demonstrates this: the square's better isolated tail loses to the path after full helper preparation (`docs/FINDINGS.md`, “Tail-only screens mis-rank endings”).

The newer small-cat abstract result has only 2.27387012e-6 of nominal room before it reaches the current native reference. Repeating the same routing strategy with this circuit is unlikely to produce a large gain. It needs a better full source/ending combination or a particularly cheap native realization.

## Where the search became too narrow

| Choice in the actual work | Scope and evidence | Consequence |
|---|---|---|
| Make the best abstract design the sole embedding target | `FLAGH/CONTINUE2.md`, `EMBED/CONTINUE2.md`; `DEEP/CONTINUE1.md` explicitly says all 36 wires occupy the 36-cell grid | Unrestricted-loss optimization selected away the space needed for preparation and transport before those costs were measured |
| Fix a gate list and limit transfers | `docs/PLAN.md` P116 and `docs/FINDINGS.md` geometry section: fixed prefix, one/two transfers, synchronized motion, fixed templates | INFEASIBLE is a statement about that grammar, not about the architecture or the contest |
| Minimize CXs in a state-preparation subproblem | `CATNATIVE3_20261027/joint_encoder.py:16–36,49–50` fixes the 14 A+D cells, exact-zero A output, four product pivots and one T input, then minimizes CX | The solver does not optimize conditional loss. A minimum-CX solution can expose expensive fault pairs |
| Clear helpers to a stronger interface than needed | Same script, lines 17–19 | The next source resets A. Exact zero is a convenient boundary, not a universal requirement. Product helper outputs or measured helpers inducing a permitted logical frame are alternative interfaces to explore, subject to raw correctness |
| Optimize local adjacency as preparation quality | `CATGEOM3_20261027/geometry.py:55–94` chooses a local A-D-B-C path for every data coordinate and maximizes same-role neighboring pairs | More local edges can help synthesis but do not certify a good noisy resource; this objective must remain a proposal heuristic |
| Use zero harmful singles as an exclusive search filter | `CAT3_20261027/screen2.py:24`, `group_screen.py:11`, `multicat.py:52`; `EXPAND2_20261027/idle_heralds.py:56`, `phase_screen.py:49` | A scoped zero-single track is sensible, but the documented bounded-residue track is not apparent in these screens. The judge does not demand c1=0 |
| Promote pair-order or clock improvements to architecture conclusions | Native 47/48-clock reports; unchanged-c2 acceptance relaxations change all-orders loss | Full expectation and acceptance remain necessary for ranking, including higher-order interactions |

None of these observations invalidates the corresponding circuits or scoped certificates. They identify freedoms the next search should expose.

An appropriate success from CP-SAT is `PREFIX2_20261027/b_quadratic_schedule.py:221–268`: its exact quadratic waiting-cost polynomial is checked against a full pair ledger, and it states that gate order, source, A and terminal times remain fixed. The proved optimum c2=34.9711111 closes that timing-only subproblem. It is a good reason to change the model next, rather than to extend its time limit.

## Recommended search

### 1. Search the required accepted operation

Represent each candidate by the ideal transformation required on the data, the measured parity space and permitted logical frame, rather than one implementation of every intermediate ancilla state. Synthesize source, checks and final readout together where their interfaces are the bottleneck. Allow helper roles to change after measurement, correlated resources, alternative Steane labelings and stabilizer bases, and measured transfers with their real parity records.

Physical correctness remains concrete: the accepted raw output must be the requested code state before the judge's ideal decoder. An ideal state identity does not certify the noisy implementation. Every candidate must include resets, measurements, waits and movement gates.

### 2. Start from geometry and retain multiple viable constructions

Choose local data/check patterns and native preparation graphs first. Maintain a small diverse set by layout, terminal type and source mechanism. Use constructive graph/Steiner methods and algebraic elimination to propose circuits, then allow block replacements that can temporarily increase gates but improve loss. The baseline and its phase variant remain controls; do not limit large changes to the baseline's fixed source boundary.

The immediate promising representation is the current small-cat/moving-control instrument because its parity-flow and Fano-line order conditions have independent audits. That is a useful native building block, not an endorsed winner. Its final check and precheck must be synthesized at the same time; smaller cats are not valuable merely because they reduce the number of ancillas.

### 3. Optimize accepted noisy loss, using pair signatures for guidance

Let A be exact acceptance and N the accepted infidelity numerator. Rank complete candidates by L=N/A at A>=0.5002, retaining a small loss/acceptance frontier. A useful local search objective is N−tau*A with tau refreshed from the current reference; stale tau changes the tradeoff. Fault-pair ledgers identify mechanisms and generate moves, but exact all-orders evaluation decides the shortlist.

Allow a bounded-residue track. c1*p alone is only an asymptotic estimate, not a finite-p exclusion certificate. A rigorous cheap exclusion can instead sum accepted infidelity from exactly-one-fault events, including the exact probability that all other channels are fault-free; this lower-bounds the loss numerator. If that numerator already exceeds a target, the circuit cannot meet it since A<=1. Otherwise spend a small explicit exact-evaluation budget on low-c1 candidates rather than declaring them invalid.

### 4. Keep solvers in roles where they answer the physical question

Useful CP-SAT tasks include selecting compatible native gadget instances, assigning a small code permutation, finding an exact short parity network, and retiming a verified operation window against a physically measured loss model. Beam search or large-neighborhood search can choose which boundary or gadget family to replace. Both are simulation-backed search; neither should be elevated to a project constraint.

Do not fund a new general RL training pipeline before a simple native search establishes a useful reward signal and beats existing methods. Likewise, substituting another router for CP-SAT while preserving the same gate-list target would leave the principal limitation untouched.

## Immediate decision experiment

The common experiment should cross a small number of independently variable sources and endings: incumbent source versus the native small-cat source; current terminal instrument versus a native alternative with different resource/preparation demands. Include the cheap locally synthesized resource family being developed in parallel. Give each complete combination the same small optimization allowance and record exact L, A, physical operations and data exposure. A short complete matrix is more informative than a deeper search of one unassembled design.

Interpretation:

- If the small-cat source loses with the same physical ending, the lost margin is in source/precheck/movement; stop refining its abstract loss.
- If a source looks good only with an ideal resource, resource synthesis is the active problem. Reopen its boundary and placement instead of adding routing depth.
- If a new ending is worse on every complete source, its isolated tail score is not a reason to continue it.
- If a complete native construction reaches 3.0e-5 or a strong improving trajectory toward it, expand that family immediately. The 2.8545e-5 threshold is a concrete 20% benchmark, not a new standing gate.

No additional approval stage or project-wide rule is proposed. This is a decision experiment for the present request.

## Lower-bound audit

The independently retrieved `work/lanes/FLOOR/REPORT.md` and reviewer18 proof explicitly relax grid geometry, prefix, acceptance amount and incoming density matrices. Their factorization keeps the actual last-two-layer STANDARD noise, raw correctness, allowed record selection and frames. The report checks measurement reuse, RX/MX folding, final barriers, arbitrary syndrome sectors and opposite-axis helper contacts. Therefore the 2.18925128e-5 bound is not simply a CP-SAT result over the incumbent layout.

This review did not independently reproduce the entire spectral certificate, and found no concrete counterexample. The correct status is a documented, independently audited true-mean bound under the pinned judge. Attaining it with a noisy preparation at acceptance >=0.5 is unproved. A finite-shot board value below it is not a contradiction.

The plan's decision to keep the existing terminal class deserves a narrower interpretation. Its floor is only about 8.5e-7 higher than the universal floor, so attacking the last layer alone has limited headroom. That does not prove its full resource preparation is best. Whole-circuit source/ending comparisons remain the right test.

## Primary literature used to check the recommendation

1. Lao and Almudever, *Fault-tolerant Quantum Error Correction on Near-term Quantum Processors using Flag and Bridge Qubits*, PRA 101, 032333 (2020), [arXiv:1909.07628](https://arxiv.org/abs/1909.07628). The paper constructs equivalent syndrome instruments whose flag ancillas also provide connectivity, and explicitly notes that ordinary routing can worsen logical error or fault tolerance. This supports changing the check implementation with geometry; its published scores are not predictions for this judge.
2. Martiel and Goubault de Brugière, *Architecture aware compilation of quantum circuits via lazy synthesis*, Quantum 6, 729 (2022), [paper](https://quantum-journal.org/papers/q-2022-06-07-729/). It combines iterative routing ideas with architecture-aware resynthesis. This supports a hybrid search rather than solver-versus-heuristic ideology; it does not optimize this contest's postselected loss.
3. Goubault de Brugière, Martiel and Vuillot, *A graph-state based synthesis framework for Clifford isometries*, Quantum 9, 1589 (2025), [arXiv:2212.06928](https://arxiv.org/abs/2212.06928). Isometry/state synthesis is a relevant representation when a complete unitary's action outside the used input subspace is unnecessary. Adaptation to noisy accepted instruments is our proposed extension, not a result established by that paper.
4. Chamberland and Noh, *Very low overhead fault-tolerant magic state preparation using redundant ancilla encoding and flag qubits* (2020), [arXiv:2003.03049](https://arxiv.org/abs/2003.03049). Its redundant ancillas combine local stabilizer and global-operator checks on a planar architecture. The repository already investigated a version; the value is in joint physical design, not importing its reported performance at a different noise rate.

## Provenance

Reviewed read-only source: `/workspace/scratch/bb05e419457d/quantumn`, plus GitHub main and PR-head reads on 2026-10-27. No circuit or production process was changed by this reviewer. New text is written only to `STRATEGY_20261027/` in the current isolated checkout. This report introduces no new standing rules.

Selected SHA-256 values of inspected files:

| File | SHA-256 |
|---|---|
| docs/PLAN.md | `0abc1956b0f9bc2a709fe04db241e439625c6cc0b8ee2a63aaa7d09f522ac489` |
| docs/FINDINGS.md | `e8c915f6467d3600ddd5f354b2347c460b6aba234b5d98da885b2ee10fb803aa` |
| CATNATIVE3_20261027/joint_encoder.py | `a34a4f0e9c147e18791b3d083c11c303a6b8f4625050d91817d1d2f9cb6571f6` |
| CAT3_20261027/old_a_late.json | `3bcbff5ccb499a04dd143c235c15466ace81c68c8b9af90042371e6a94127a85` |
| CATREVIEW3_20261027/REPORT.md | `078c68a0c13087294cbc4d1373aa3ebcd5f66e625d270289f3138a43bdfc40f9` |
