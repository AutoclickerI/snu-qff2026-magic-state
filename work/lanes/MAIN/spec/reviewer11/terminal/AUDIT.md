# Review 11: terminal architecture audit

Repository snapshot: `AutoclickerI/quantumn@0ff9423a8e69c13998ab1baf7bf09c8e97558a60`.
Official judge snapshot: `76fe47c0324f1c1f8b72a7d55af200e88043b522` (unchanged).
All experiments in this directory are local; no remote compute, submission, or source-repository mutation was performed.

## Findings that should affect the handoff

1. **One concrete new finite physical search is worth a first priced gate:** the 14 intermediate partially coherent C resource states below. Its algebra and a small favorable terminal-noise mechanism are certified. No full candidate or net improvement has been demonstrated.
2. **The target-preserving endpoint W Clifford loses on actual v36g.** It is a useful new negative control, not a recommendation.
3. **FRAME does not rescue the old v36c partial-rank screen**, even under an unrealistically favorable oracle which knows the entire incoming syndrome for free. This strengthens the original identity-frame screen, but is not a closure on another incoming boundary.
4. Terminal reports' regional noise-removal prices are conditional experiments. They must not be presented as universal lower bounds or universal caps on redesign gains.

Current reference: v36g, all-orders loss `3.836054467100275e-5`, acceptance `0.5015149656065663`, 320 CX, 47 native ticks. The complete circuit and the exact evaluator were read at the pinned snapshot.

## 1. Fourteen intermediate C resource contracts

### Exact family

Let C2 be the 3-dimensional binary simplex code whose generator supports, in code order, are

```
{0,2,4,6}, {1,2,5,6}, {3,4,5,6}.
```

For each subspace V of C2 of dimension k, define

\[
|V\rangle=2^{-k/2}\sum_{v\in V}|v\rangle,
\qquad
|R_V\rangle=2^{-(3+k)/2}\sum_{u\in C_2,v\in V}|u\rangle_B|u+v\rangle_C.
\]

The ideal transversal B-to-C CNOT has the exact endpoint contract

\[
CX_{B\to C}|R_V\rangle=|0_L\rangle_B\otimes|V\rangle_C.
\]

There are 16 subspaces total: one k=0 endpoint, seven k=1, seven k=2, and one k=3 endpoint. The **14 intermediate states** are the proposed finite search. Their resource has 3+k binary amplitudes and Schmidt rank `2^(3-k)` across B:C, with uniform nonzero Schmidt weights. C has the seven independent stabilizers `X(V)` and `Z(V^perp)`.

The certificate `finite_contracts.py` explicitly enumerates all supports, checks the post-CX support equality, computes the reduced-state spectrum, and produces independent X/Z stabilizer bases for each V. Results are in `partial_coherence_contracts.json`. Its JSON field `r` is k in this report. **Do not confuse this mathematical parameter with the incumbent resource filename `BFLAG/syn/r3.json`: that filename labels a candidate, and the incumbent is the k=0 endpoint here.**

### Why this is a substantive physical freedom

The existing k=0 endpoint makes all seven C qubits literal zero. That supplies seven Z checks, but sees no Z error on C. The k=3 endpoint prepares two independent logical-zero blocks. The 14 intermediate contracts retain selected coherence on C while reducing the B:C entanglement needed in preparation.

Every nonzero word of C2 has weight four. Consequently no unit vector lies in V. C's remaining Z stabilizers therefore still detect **every single-qubit X_C or Y_C error** for all 14 intermediate choices. Meanwhile the new X(V) checks detect a single Z_C on four sites for k=1, or six sites for k=2. This is a concrete exchange of redundant Z information for complementary X information; it does not simply drop arbitrary terminal syndrome rows.

One useful consequence is immediate. Just after a B-to-C CNOT, the incumbent's literal-zero C cannot distinguish either `X_B I_C` or `X_B Z_C`; each occurs with probability p/15 in its two-qubit depolarizing channel. A C site covered by X(V) detects the latter. Its surviving B-to-data X leakage falls from `2p/15` to `p/15`, before charging the new instrument's own faults. Z_C created before the CNOT can also be propagated to B and now become detectable, but that additional mechanism has not been numerically priced.

### Quantitative optimistic witness

Reusing TERM's unchanged per-qubit data-side second-order model, including the A flag and D10/D21 timing gap, gives:

| Family | Single-Z_C coverage | Reduction at p=0.001, ideal C resource/readout |
|---|---:|---:|
| k=1, seven choices | 4/7 sites | `0.991111e-6` to `1.008889e-6` |
| k=2, seven choices | 6/7 sites | `1.482222e-6` to `1.493333e-6` |

These are reductions of a restricted second-order terminal model, **not forecasts of full-circuit score**. They do not include preparation, added C measurement circuitry, changed acceptance, or higher-order masking. They support spending a bounded first-gate budget, not launching an unconstrained solver run.

### First priced gate and stop rule

1. Build all 14 ideal instruments from the certified stabilizers; verify ideal acceptance and target fidelity, together with all single-fault effects at the actual current boundary.
2. Price each on the **current v36g incoming boundary**, initially with an ideal C readout to identify whether there is sufficient useful headroom and which C errors matter. This is an optimistic screening calculation; removing noise is not generally a universal lower bound on normalized postselected loss.
3. Jointly synthesize the B/C resource **and its C readout**, charging all CX, measurements, idles, release constraints, and output waiting. Require a complete routed witness, exact all-orders score, acceptance at least 0.5, unchanged-judge correctness, and the current runtime gate before promotion.
4. Stop any fixed-layout family whose only realizations add enough global waiting to erase the approximately `1e-6`–`1.5e-6` ideal terminal benefit. Do not report a general impossibility from that fixed-layout failure.

The principal obstacle is readout. For k=1, |V> contains a four-qubit GHZ state on its nonzero codeword. Reading the X parity by measuring all four in X destroys the simultaneous Z checks; an actual joint stabilizer instrument is required. A conventional inverse encoder needs at least three entangling gates for that component. Current C sites are `[12,25,19,17,5,29,28]`; their induced nearest-neighbor graph has only the edges 25–19 and 29–28. Thus a connected four-site readout cannot be routed within C alone. Existing terminal copy edges, helpers, layout freedom, and synthesis across the preparation/readout boundary must be priced together. A free final decoder is not a valid assumption.

This family retains the measured-helper final-CX-plus-idle architecture if used as described. **It is not a route claimed to cross `1e-5`.**

### Prior-art distinction within this repository

`FRESH/REPORT_prior_architecture.md`, beginning at “Architecture decision,” explicitly describes k=0 correlated resources and separate k=3 blocks. Its failed “relaxed correctable-residue” resources keep C literal zero and permit certain accepted weight-one B residues. Those physical builds scored `8.86e-5`–`1.05e-4`, because a later error combines with the accepted B residue. This is a real warning against residual-error relaxations, but it does **not** test the new C stabilizer state or readout contract above.

No test of the 14 intermediate pure CSS resource/readout contracts was found in the pinned FRESH, BFLAG, BCSYN2, TERM, EARLY, or FASTR43 evidence. This is a newly specified finite subfamily of the earlier broad resource-boundary idea, not a claim that intermediate entanglement is a new quantum-information principle.

## 2. Target-preserving endpoint W: implemented and rejected

Candidate: append S on all seven outputs in their existing final idle tick and declare `FRAME_X(1)`, `FRAME_Z(0)`. Physical transversal S acts as logical S-dagger on this Steane encoding; `X_L S_L^dagger` fixes the target T state up to phase. S-gate noise and idle noise are the same D1(p), so the candidate preserves depth, noise-channel strengths, and CX count.

This is not automatically a score symmetry. The fixed CSS decoder corrects `X_i Z_j` for distinct i,j, while the S-conjugate `Y_i Z_j` has a logical-Z remainder. The test therefore needed an exact contraction.

| Quantity | v36g | Endpoint W |
|---|---:|---:|
| All-orders loss | `3.836054467100275e-5` | `4.5464344742292077e-5` |
| Acceptance | `0.5015149656065663` | same |
| Native ticks / CX | 47 / 320 | 47 / 320 |
| Ideal acceptance / loss | 1 / 0 | 1 / 0 |

Loss increases by **`7.1038000712893266e-6`**, about 18.52%. `endpoint_w.py` pulls the unchanged evaluator's observables and fault signatures back through the endpoint Clifford, with all 73 moments retained in `endpoint_w_result.json`. The explicit QASM was separately passed through the untouched official judge. Format, class, deterministic detectors, and correctness all pass. The 100,000-shot seed-0 sample is a validity check only; its SEM is much too large for ranking.

Artifact SHA256: `3a896a9e04e5abcb7a69987442d472dc217f0370ad4ceed9caae6127021ecab0`.

This differs from FRESH's older S/Sdg gauges: those insert a phase before D-to-A and restore it afterward, thereby changing a check axis. This test changes the endpoint decoder pullback and leaves the prior circuit intact. Both tested forms lose; this does not exclude every possible absorbed Clifford inside a redesigned resource.

## 3. Stronger closure of the old partial-rank FRAME idea

TERM previously screened every one of the 2,825 subgroups of six stabilizer generators on its saved v36c cut after tick43, with the identity logical frame. I reused its saved 64-sector moment table and evaluated both:

- arbitrary syndrome-dependent logical Pauli correction, with access to the full incoming syndrome for free;
- every correction linear in those six syndrome bits, as permitted by the frame syntax if those bits existed as records.

For each accepted syndrome subspace, the arbitrary-frame oracle replaces the two signed target contributions by their absolute values. The linear optimum separately maximizes each of their 64 Walsh characters. Both are optimistic: the meter and the record needed for the correction are not physically supplied.

**None of the 2,824 proper subgroups beats full rank under any of the three original tail models, even with the arbitrary-frame oracle.**

| Tail | Full-rank loss | Best proper subgroup with optimal frame |
|---|---:|---:|
| No tail | `1.78985318505e-6` | `8.32635241539e-6` |
| Final D1(p) idle | `1.34150635271e-5` | `1.99780897860e-5` |
| Measured-helper CX tail plus idle | `2.45255815255e-5` | `3.10990232899e-5` |

The best proper case accepts the syndrome line spanned by 57 and applies X according to syndrome bit0. Its identity-frame loss is worse still, so it is incorrect to say frames can never affect these sectors. They help here, but not enough to win. The exact screen and receipt are `finite_contracts.py` and `optimistic_frame_screen.json`.

Closure scope: the saved **v36c** incoming table and specified tail models. This is not a current-v36g certificate, a universal partial-measurement lower bound, or an implemented record-controlled circuit. No recommendation to resurrect generic M08 follows from it.

## 4. What the terminal evidence does and does not prove

The measured-helper class has a real composable channel floor. For a final data–helper D2(p) fault followed only by a fixed Pauli measurement of that helper, the measurement-commuting helper branch has probability `1-8p/15` and conditional data depolarization

\[
q_0=\frac{2p/5}{1-8p/15}.
\]

The anti-commuting helper branch has fully depolarized data, so the entire instrument factors a common D1(q0) independently of the readout branch. A subsequent data idle composes another D1(p). Using the simpler D1(2p/5) factor in TERM is conservative. This argument has assumptions: the helper is not subsequently coupled to another system before readout, and the data are untouched afterward apart from the stated tail. A different terminal instrument must be analyzed afresh.

By contrast, making A, B/C, or a timing gap noiseless and subtracting the new score is a controlled ablation, not a universal bound on what a redesign of that region can achieve. Conditional acceptance and correlations can change when the architecture changes. Statements such as “maximum possible terminal gain is approximately 0.49e-5” inherit the particular resource and boundary model. They cannot exclude a different terminal instrument or a different incoming state.

Other old routes were checked for concrete overlap before proposing the family above: dummy final CX, FRAME_Z handoff, late C checks, B-first round, fixed-layout D21 reversal, and arbitrary proper subgroups already have direct negative evidence. No renamed version of those routes is recommended here.

## Reproduction

The finite certificates need Python and NumPy only:

```
OPENBLAS_NUM_THREADS=1 python audit/review11/terminal/finite_contracts.py
```

The endpoint test additionally requires the pinned evaluator tree at `quantumn_review11/work/lanes/MAIN/sparse` and the unchanged official package. The script first uses top-level `official/` in the handoff package and falls back to `deliverables/quantumn_v36c_handoff/official` in the original workspace. Its complete candidate and both score/validity receipts are already included.

Pinned repository evidence copied under `source/` includes TERM, EARLY, FASTR43, BFLAG, BCSYN2, INTEG2, FRESH, IDEAS, the current circuit, and the old boundary-moment table. These are evidence snapshots, not modified repository files.
