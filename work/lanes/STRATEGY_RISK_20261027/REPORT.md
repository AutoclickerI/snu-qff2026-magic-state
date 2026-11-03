# Native loss audit and search-objective review

## Decision

The strongest supported high-level method is **joint architecture and circuit
search on the actual grid, ranked by complete all-orders conditional loss**.
CP-SAT remains useful for bounded local synthesis or checking a proposed
schedule; selecting an abstract circuit and treating its placement as the final
step is not supported by the measured progress.

The next architecture decision must jointly choose the input preparation,
terminal verification instrument, physical locations, resource lifetimes, and
accepted record contract. A compact source attached to the incumbent-like tail
is not yet a large-gain proposal. Conversely, a cheap perfect-resource tail is
not evidence that its preparation is affordable.

## New measurements on the actual working native circuit

The reference is `EXPAND2_20261027/release_phase/native_incumbent_phase_late`,
QASM SHA256 `bcd6a3fdb6133c5b687993fb10c57c002e13f3e873f05981c48100ba10065b08`.
The complete baseline was reproduced at loss **3.5681272391347155e-5** and
acceptance **0.501016046737387**.

`native_risk.py` evaluates the same physical circuit after selected noise
channels are replaced with identity. Operations, timing, detector rows, and
ordered outputs remain unchanged. Waiting intervals are split by their actual
clock rather than the earlier gate to which the judge appends their noise.
These are diagnostic interventions, not executable improved circuits or
certified additive bounds on a redesign.

| Channels made perfect | Conditional loss | Acceptance | Relative diagnostic reduction |
|---|---:|---:|---:|
| None: working native baseline | 3.56812724e-5 | 0.50101605 | 0% |
| All noise before clock 40 | 3.01607425e-5 | 0.84914418 | 15.47% |
| All noise before clock 46 | 2.84739382e-5 | 0.96097863 | 20.20% |
| All noise before clock 47 | 2.27581381e-5 | 0.97283397 | 36.22% |
| Final B/C cells, clocks 30–45 | 3.20317807e-5 | 0.57052499 | 10.23% |
| Final A cells, clocks 40–45 | 3.45915324e-5 | 0.51332358 | 3.06% |
| Final data-cell waits, clocks 30–45 | 3.34615821e-5 | 0.51826749 | 6.22% |
| B/C-cell channels and data waits, clocks 30–45 | 3.06274269e-5 | 0.59018230 | 14.16% |
| Seven late D→A gate-noise channels | 3.26663490e-5 | 0.50401867 | 8.45% |
| Seven final B→C verification gate-noise channels | 3.22939374e-5 | 0.50381909 | 9.49% |
| Both sets of seven D→A and B→C gate channels | 2.95874352e-5 | 0.50683873 | 17.08% |
| B/C cells at 30–45 plus final B→C verification | 2.87005979e-5 | 0.57372353 | 19.56% |
| Final B→D gate-noise channels | 2.23322954e-5 | 0.50287521 | 37.41% |
| Seven final data waiting channels | 1.03499670e-5 | 0.50101605 | 70.99% |
| Measurement-result flips at clocks 46–48 | 3.47990931e-5 | 0.51262838 | 2.47% |

The B/C plus data-wait intervention demonstrates nonadditivity: the individual
reductions sum to 5.86918e-6; the joint reduction is only 5.05385e-6. Removing a
channel also changes which shots are accepted. Differences from a perfect-noise
counterfactual must not be advertised as engineering overhead budgets.

The final-wait intervention is deliberately unphysical and lies below the
documented universal lower bound. Its large effect does **not** mean that a
legal 71% improvement can be obtained by deleting the final clock. The current
terminal-class floor is already only about 8.5e-7 above the documented universal
floor. This small difference between ideal floors does not limit the improvement
of a complete redesign, which can also change preparation and verification.
It does show why the 71% noise-removal number cannot be used as an attainable
last-layer target. The practical target is the excess loss created by preparation
and verification together with the physical ending.

The role audit corrected a stale map found in an older lane report. The actual
late A block is `[7,14,13,9,8,21,15]`; qubits 0 and 1 are separate helpers.
The seven D→A interactions occur at clocks 45/46; final B→C interactions are at
46; final B→D interactions are at 47. The intervention definitions use exact
code-coordinate edge matchings, excluding unrelated factory and helper gates.

## Physical pair audit, including what gate labels conceal

`native_pairs.py` independently reconstructs every compatible physical fault
pair and subtracts mutually exclusive Pauli alternatives within one channel.
It reproduces **c2 = 31.54888888888883**. Its stage totals include every pair,
not just the largest 100 entries.

| Pair of physical noise sources | Contribution to c2 |
|---|---:|
| Final data idle × final data idle | 11.66666667 |
| Final B→D gate × final data idle | 9.33333333 |
| Final B→D gate × final B→D gate | 1.86666667 |
| Final B→C gate × final data idle | 1.86666667 |
| B/C-cell noise at 30–45 × itself | 1.63555556 |
| Final D→A gate × final data idle | 1.46666667 |
| Final B→C gate × final B→D gate | 0.74666667 |
| Final D→A gate × final B→D gate | 0.58666667 |

All pairs involving the final data wait sum to **24.86666667**, or 78.82% of
c2. Older tables assigning waits to their preceding operation collapse the
first three rows into a final-CX label with coefficient 22.86666667. That label
can misleadingly suggest that reducing CX count is the main remedy.

At p=0.001, c2·p² is 3.15488889e-5. The full expected loss is higher by
**4.13238350e-6**, about **11.58%** of the full result. This remainder includes
higher orders and noisy-acceptance normalization. A c2-only architecture
shortlist is not accurate enough for a claimed 10% improvement.

## What the progress says about grid-free candidates

The small-cat lane contains 216 saved results with single-fault audits. Four
have nonzero c1, each approximately 0.0166667; the other 212 have c1=0 within
numerical tolerance. The hard c1 filter in `group_screen.py` and `multicat.py`
conflicts with the documented policy, but this audit found no discarded tiny-c1
winner. Correct the rule without suggesting that this change by itself is a
large-gain discovery.

More concretely, the latest complete noisy abstract small-cat candidate
`oldA_bell4_mixed_s003_late` has loss **3.34074023e-5**, acceptance **0.75570223**,
129 CX, and 20 clocks. It already includes noisy preparation and waits, but
relaxes adjacency. It improves on the actual native incumbent by only 6.37%
before physical-grid implementation. It supplies no demonstrated 10% headroom:
reaching that target requires additional beneficial changes to the circuit,
its schedule, or its accepted operation while implementing it.

For decision-making, compare candidate results directly with complete native
targets, rather than treating a positive abstract gain as enough:

| Abstract reference | Loss | Difference to a 10% native-gain target | Difference to a 20% target |
|---|---:|---:|---:|
| DEEP grid-free design recorded in PLAN | 2.7185e-5 | 4.92815e-6 | 1.36002e-6 |
| Latest small-cat plus original-A design | 3.34074023e-5 | −1.29426e-6 | −4.86238e-6 |

The 10% and 20% complete-native targets are respectively 3.21131452e-5 and
2.85450179e-5. The table lists arithmetic score differences, not additive or
monotone noise budgets. A different native synthesis can improve the abstract
schedule as well as add physical cost.

### A concrete ranking reversal in the current work

| Abstract candidate | c2 | Full loss |
|---|---:|---:|
| `oldA_bell2_same_s000_late` | **31.80166667** | 3.37023199e-5 |
| `oldA_bell4_mixed_s003_late` | 31.90333333 | **3.34074023e-5** |

The full-loss winner has the worse pair coefficient. Earlier FINDINGS also
records a square-versus-path reversal between perfect-resource terminal cost
and full noisy preparation. Restricting full prices to the lowest few c2
candidates is a speed heuristic, not a justified architecture exclusion.

## High-level method and practical search changes

1. Start with a native terminal verification instrument and a physical region
   in which its ancillas can actually be prepared. Co-design the incoming source
   around that region. Keep the code-coordinate assignment, helper lifetimes,
   preparation method, checks, and detector contract variable together.
2. Generate legal native circuit neighborhoods using measurement-assisted moves,
   stabilizer-equivalent preparation networks, reuse of measured cells, different
   cat partitions, and alternate check/readout contracts. Use stochastic search
   or beam search across these discrete choices. CP-SAT can solve a bounded
   scheduling or placement subproblem after the physical circuit family exists.
3. Compare complete native circuits by exact conditional loss at p=0.001 and
   A≥0.5002. Retain a small Pareto set over loss, acceptance, resource footprint,
   lifetime and evaluator time. Depth, gate count, c1 and c2 diagnose the designs;
   they do not replace this objective.
4. Allocate full prices across qualitatively different families and some c2
   near-misses. When a source-only improvement has less than the target headroom,
   first test a source × ending combination before spending on general embedding.
5. Run the raw noiseless output check before trusting decoded loss. Affine
   logical frames and postselection are legal but require the appropriate
   evaluator; shared qtools rejects FRAME/POSTSELECT. Removing physical checks
   because the final ideal decoder corrects their noiseless mistake is invalid.

The current evidence favors changing the native verification mechanism and its
resource production together. Pure prefix shortening, a lower CX count, more
CP-SAT time on the same fixed gadget, or repeated sampled redraws each address
only a limited part of the remaining gap.

## Freedoms already explored and semantic limits

- `FRAME20261027` already built a legal full-block teleportation candidate; its
  best loss 3.67299886e-5 was worse than the incumbent. It also tested accepting
  extra syndromes with affine logical frames; the best priced recovery case was
  2.30220612e-4. This rejects those concrete constructions, not all teleportation.
- Nonlinear selection is not an unrestricted classical decoder in the format.
  It needs a noisy legal quantum implementation; existing measured NAND and
  extra-syndrome experiments did not support a large improvement.
- Raw code-space correctness is checked before the judge's ideal decoder. An
  output teleport requires the recorded physical byproducts to be logical
  Paulis or to be absorbed into appropriate measured-resource records.
- The native gate/noise model, two-qubit adjacency, acceptance, simulator class,
  and submission limits remain binding. The evaluator's zero-frame, rotation
  count, or c1 restrictions are implementation limits, not extra contest rules.

## Reproduce

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python work/lanes/STRATEGY_RISK_20261027/native_risk.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python work/lanes/STRATEGY_RISK_20261027/native_pairs.py
```

The lane uses one CPU per process. The ablation script retains complete channel
metadata, actual clock ranges, and interventions in `ablations.json`.
`native_pairs.json` contains the full stage decomposition. No shared qtools,
official judge, source QASM, or production submission file was modified.

The numerical contraction uses the pinned engine and the previously validated
lane-local Clifford frontend. Baseline equality and c2 equality are checked in
the scripts. These floating-point results are not a fresh symbolic proof of the
repository's universal lower bound. No new performance-winning native circuit
is claimed by this diagnostic lane.
