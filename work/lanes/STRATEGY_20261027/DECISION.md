# A larger improvement: architecture decision and completed experiments

## Decision

**Prioritize joint synthesis of the native resource preparation and final verification, choosing their incoming state and measurement contract together. Rank complete circuits by exact conditional infidelity. Keep CP-SAT for useful local synthesis and scheduling problems.**

The current record does not support selecting a finished unrestricted-connectivity circuit as the sole architecture and treating its grid implementation as a downstream task. Nor does it support replacing CP-SAT wholesale with a heuristic. The central issue is which physical choices are represented and what is optimized.

The practical search should start from complete native candidates and useful local output/check geometries. Structural replacements should jointly change preparation, available cells, helper reuse, measurements and accepted parity relations. The required object is the accepted operation on the data, not a prescribed gate list or an unnecessarily exact intermediate helper state. Algebraic identities and graph constructions generate alternatives; a small diverse set of feasible circuits prevents commitment to one family. Local solvers can synthesize or retime selected windows. Exact full-noise evaluation decides which replacements survive.

No new native performance winner was obtained in this checkpoint. The verified native reference remains **3.5681272391347155e-5** at acceptance **0.501016046737387**, with 412 CX and 49 clocks. Its earlier official 100-million-shot receipt remains valid. The new work supplies completed decision experiments and a sharper architecture priority, not a SOTA claim.

## Work completed in this checkpoint

- Three independent reviews: architecture and geometry; loss objective and physical error mechanisms; historical progress and search restrictions.
- **28 complete noisy abstract circuit evaluations**: 15 crossed source/ending combinations, nine actual small resource verifiers, and four matched controls for measured-codeword reuse with affine logical frames.
- **16 exact interventions on the working native circuit**, preserving operations, timing, output order and detector rows while changing specified noise channels. These are diagnostics, not new circuits.
- A physical fault-pair decomposition that assigns waiting errors to their real clock instead of the earlier gate carrying them in the judge representation.
- Four solver-free native synthesis runs and two independently checked native raw-state controls. The search did not improve the known module; its failure is recorded.

All experiment processes completed. The production racer, submissions, shared evaluator and official judge were not changed.

## 1. What the new source/ending comparison changes

The experiment includes every reset, preparation, gate, read and waiting channel. Only adjacency is relaxed. The original and square controls use the same input source; the actual terminal preparation and measurement circuit changes.

| Source | Ending | CX | Clocks | Exact loss | Acceptance |
|---|---|---:|---:|---:|---:|
| Two interleaved Bell checks | Original | 107 | 19 | 3.4411230402e-5 | 0.782802 |
| Two interleaved Bell checks | Square | 114 | 19 | **3.0093765296e-5** | 0.776974 |
| Four interleaved Bell checks | Original | 123 | 19 | 3.4193744574e-5 | 0.773968 |
| Four interleaved Bell checks | Square | 130 | 19 | **3.0090141775e-5** | 0.768206 |
| Two cats, loads 1/3/3 | Original | 109 | 18 | 3.4619490734e-5 | 0.780159 |
| Two cats, loads 1/3/3 | Square | 116 | 18 | **3.0430129855e-5** | 0.774351 |

All six rows have correct raw output and no harmful single faults. For the two-Bell source, changing the ending saves **4.3174651e-6**. After fixing that ending, adding two more Bell checks saves just **3.6235207e-9**, despite adding sixteen CX gates. This directly prioritizes the terminal/resource mechanism over more repetitions of the same logical source check.

The two-Bell square is the more economical comparison seed unless the four-check variant happens to map substantially better. The 1/3/3 version is one clock shorter and may have useful native geometry, but its abstract loss is 3.3628806e-7 higher. The actual native realization must decide that tradeoff.

This is a mechanism comparison, not another commitment to route the square circuit unchanged. No tested source/ending combination here reaches a 20% improvement even at unrestricted connectivity. A larger gain requires a different joint resource/check implementation or a better complete architecture.

Source and reproduction: [crossed experiment report](../STRATEGY_CROSS_20261027/REPORT.md), [generator](../STRATEGY_CROSS_20261027/cross.py), [15-case results](../STRATEGY_CROSS_20261027/cross_results.json).

### Cheap flags provide a decisive counterexample to the old proxies

Removing C or naively preparing shortened resources leaves seven harmful B-encoder components. These circuits are raw-valid but cost roughly 2.97e-4 to 3.13e-4. We then implemented real three-CX logical-Z verifiers that detect all seven components, including each reset, read and extra waiting interval.

All nine flagged variants have correct raw output and **c1=0**. Their losses nevertheless range from approximately **5.78e-5 to 8.19e-5**, all worse than the working circuit. Two flags improve over one, but neither replaces the broader verification supplied by C cheaply enough. Correctable accepted resource errors still combine with late faults.

The result rejects these concrete flag implementations. It does not exclude all smaller resource states or all flag-based instruments. It does establish that minimum CX, minimum depth and c1=0 cannot be the architecture objective.

Receipts: [flag results](../STRATEGY_CROSS_20261027/bflag_results.json).

## 2. Where the native circuit's removable surplus is concentrated

The baseline all-orders result was reproduced exactly. The following controls remove specified noise while leaving the real operations, schedule and detector contract unchanged:

| Noise made perfect | Resulting loss | Diagnostic reduction |
|---|---:|---:|
| No intervention | 3.56812724e-5 | 0% |
| All noise before clock 40 | 3.01607425e-5 | 15.47% |
| B/C-cell channels during clocks 30–45 | 3.20317807e-5 | 10.23% |
| Data waits during clocks 30–45 | 3.34615821e-5 | 6.22% |
| B/C-cell channels and those data waits | 3.06274269e-5 | 14.16% |
| Seven late D-to-A gate channels | 3.26663490e-5 | 8.45% |
| Seven B-to-C verification gate channels | 3.22939374e-5 | 9.49% |
| Both D-to-A and B-to-C sets | 2.95874352e-5 | 17.08% |
| B/C-cell channels plus B-to-C verification | 2.87005979e-5 | 19.56% |

These are artificial controls. Their reductions are neither additive allocations nor certified limits on a redesigned circuit: noise changes acceptance and can change which faults are rejected. They nevertheless identify a useful causal priority. Improving source quality alone leaves the expensive final instrument. Improving B/C preparation alone leaves its verification cost. Their joint redesign has the strongest measured case for a material gain within the current neighborhood.

The physical pair audit also corrects a misleading label. The earlier “final B-to-D” coefficient of 22.8666667 contains:

| Actual physical pair | Contribution to c2 |
|---|---:|
| Final data idle with final data idle | 11.6666667 |
| Final B-to-D gate with final data idle | 9.3333333 |
| Final B-to-D gate with final B-to-D gate | 1.8666667 |

Counting CX gates cannot see this distinction. All pairs involving the final data wait total 24.8666667, or 78.82% of c2. But much of that is the unavoidable terminal noise, rather than freely removable overhead.

Making the final seven waits noiseless produces an artificial 1.0349967e-5 score. That is below the documented universal bound and is not a legal target obtained by deleting a clock. We tested a real alternative: reuse the measured A codeword in a final transversal CX layer, with the appropriate affine logical X frame. It is raw-valid and has no harmful singles, but its full loss worsens from 3.4411230e-5 to **4.7070906e-5**, at the same final clock. Postmeasurement noise, new CX noise and frame correlations are included. The dual controls also lose.

Sources: [native risk report](../STRATEGY_RISK_20261027/REPORT.md), [complete interventions](../STRATEGY_RISK_20261027/ablations.json), [pair decomposition](../STRATEGY_RISK_20261027/native_pairs.json), [physical reuse controls](../STRATEGY_CROSS_20261027/reuse_results.json).

## 3. A serious assessment of grid-free design

Grid-free experiments are useful for testing a mechanism, crossing source and ending choices, and identifying whether a family has any numerical margin. They are weak evidence for selecting the final hardware architecture because:

1. They suppress exactly the cost that has repeatedly defeated this project: preparation and transport on a crowded grid.
2. A low-noise abstract implementation may consume all 36 wires, leaving no routing or preparation space.
3. Equivalent noiseless states can have very different accepted noisy residue distributions.
4. Tail-only rankings already reverse when real preparation is included.
5. Their scores are not universal lower bounds under postselection.

The documented DEEP score of **2.7185e-5** remains a research lead. Its exact QASM and receipt were not recovered from the inspected local snapshot, GitHub main or the PR head: the DEEP folder contains only two briefs, and the named candidate/report requests return 404. It may exist on the original research hosts. Until recovered, it should not be treated as the reproducible baseline that every other architecture must follow. The previous recap repeated the plan's number without this qualification.

Against the verified native reference, the actual targets are:

| Outcome | Required native loss |
|---|---:|
| 10% improvement | 3.2113145152e-5 |
| 20% improvement | 2.8545017913e-5 |
| Documented universal true-mean floor | approximately 2.18925128e-5 |

The new best square control, 3.00901418e-5, has only **2.0230034e-6** of net degradation allowance if a completed native design is to preserve a 10% gain. The historical DEEP score has only approximately **1.36e-6** of allowance for preserving 20%. These are direct score comparisons, not a theorem that every localization change must worsen a conditional score. Any native implementation that changes the design beneficially should be judged by its actual result.

The floor audit is separate from CP-SAT placement. Its documented derivation relaxes geometry, source and incoming states while retaining the judge's actual last-layer noise. No concrete counterexample was found here. The small difference between its universal floor and the current terminal-class floor does not prove which complete preparation is best.

## 4. Why switching the optimizer is insufficient

The repository contains valuable scoped CP-SAT results. A solver can certify the best schedule or state preparation within its stated variables. It cannot decide whether those variables describe the best architecture.

Current optional restrictions include a fixed prefix boundary, fixed physical roles, a particular encoder, one/two transfers, a CX-only synthesis grammar, exact-zero helper outputs and CX/depth objectives. An INFEASIBLE or OPTIMAL result under those choices does not establish a global contest limitation. Several screens also still exclude nonzero c1 even though the project explicitly dropped that as a general eligibility rule.

We tested a replacement heuristic rather than merely recommending one. Four beam searches over native CNOT row transformations, including a relaxed logical-frame helper boundary, failed to rediscover a known 24-CX circuit. The known control and a raw-valid framed helper control both pass the official exact oracle. The failure is search incompleteness, not physical impossibility. There is no evidence here that a generic beam is better than CP-SAT.

The useful hybrid therefore begins with feasible native circuits and meaningful structural replacements. It retains alternatives with different preparation cost, lifetime and accepted error structure. CP-SAT solves selected local subproblems; graph/algebraic construction and guided large-neighborhood moves change the family. A fresh general-purpose RL training project or a new router preserving the same gate list has no stronger evidence for this deadline.

Sources: [independent strategy review](REVIEW.md), [native beam experiment](../STRATEGY_NATIVE_20261027/INPUT_BEAM_REVIEW.md).

## 5. Best-supported next work

### Primary direction: native resource and verification synthesis

Begin with the required final code state, legal local interactions and accepted measurement relations. Jointly choose B/C preparation, the late D-to-A/B-to-C checks, code-coordinate labeling, helper lifetimes and the incoming source boundary. Preserve only the relations the complete accepted operation needs; do not impose independently perfect blocks when correlated resources or a different measurement instrument suffice.

Generate a small set of complete native constructions. Use the existing cultivation source as one anchor and a native logical-check source as a challenger. A two-Bell square control is a compact comparison seed, not a mandatory final gate list. Prefer changes that remove preparation/check work together or reuse measurement information while retaining low-risk accepted residues.

### Search objective and budget

Let A be acceptance and N the accepted infidelity numerator. Select by **L=N/A** at A>=0.5002 under p=0.001. Keep a small frontier including unused acceptance, live cells and execution time because these can finance later changes. Use fault pairs to propose structural replacements, but reserve complete exact evaluations for different families and near-misses as well as the lowest-c2 candidates.

The native reference has c2*p^2=3.15488889e-5, while its full loss is 3.56812724e-5. The **4.1323835e-6** remainder is 11.58% of the full value. Existing Bell2/Bell4 results also reverse c2 ranking. A c2-only decision is inadequate for selecting a 10% improvement.

A small bounded-residue track is justified, without claiming that it already contains a winner. An exact finite-p single-event numerator can reject truly hopeless proposals; the asymptotic c1*p value alone is not a rigorous exclusion. Correct raw noiseless code-space output, including legal frames, remains mandatory.

### What should lose priority

- Open-ended embedding of a fixed abstract champion without a complete native score trajectory.
- More repetitions of the current Bell check: their benefit after the square ending is already negligible.
- Minimum-CX or minimum-clock resource search used as the final ranking.
- Further time on an exhausted fixed-interface solver model.
- Extra sampling as the main path to a genuine expected-loss jump.

This is a one-time research allocation for the user's request, not a new standing rule, approval gate or claim of a globally optimal method. The next success criterion is an actually complete native circuit with a substantial exact loss reduction. The checkpoint has sharpened that target and rejected several plausible shortcuts, but has not achieved it yet.

## Literature context

The recommendation is consistent with primary work on redesigning fault-tolerant checks for connectivity, architecture-aware resynthesis, and synthesizing a state/isometry instead of a full unitary. These papers support the representation choice; their published performance is not a prediction for this judge:

- [Lao and Almudever, flag and bridge qubits](https://arxiv.org/abs/1909.07628).
- [Martiel and Goubault de Brugière, architecture-aware lazy synthesis](https://quantum-journal.org/papers/q-2022-06-07-729/).
- [Goubault de Brugière et al., Clifford isometries](https://arxiv.org/abs/2212.06928).
- [Chamberland and Noh, redundant ancilla encoding](https://arxiv.org/abs/2003.03049).

## Reproduction and evidence

Use the repository's pinned environment and the commands in the linked lane reports. The selected deliverable includes generated QASM, ordered output specifications, raw and all-orders receipts, experiment summaries, source hashes and the code needed to reconstruct the comparisons. All new writes belong to these research lanes; the native reference and judge remain unchanged.
