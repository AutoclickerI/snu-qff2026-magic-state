# Physical review of quantumn at 42afa8f

Repository pin: `42afa8ff01c3999444336f5bb2fe473c1475d6f4`.
Current physical baseline is v36c; independently reproduced by the parent:
`L=4.1151559437773416e-5`, `A=0.5027278379249299`, 552 effective noise channels.
The source files inspected and retained under `sources/` came from that pin.
The TREP/TREP2 experiments themselves concern the historical v17a/v18 family;
their phase-coordinate names must not be confused with the re-derived v36c basis.

## 1. Strongest fresh physical candidate: the 14-T, rank-four phase family

### What the current published search excluded

`work/lanes/TREP/enumerate.py:45–62` enumerates a complete 64-element phase-polynomial coset:
1 one-T form, 15 fourteen-T forms, 16 fifteen-T forms, 16 sixteen-T forms,
15 seventeen-T forms and one thirty-T form. It records seven harmful phase-axis
pairs in every fourteen-T support. The published physical builder
`work/lanes/TREP2/forms.py:124–128` has the literal guard `f['T']==15`.
`TREP2/REPORT.md:19` reports physical pricing of the 16 protected fifteen-T forms.
Thus those negative physical results did not price the fourteen-T family.

The unused family has a different structural property, beyond saving one T:
every fourteen-T support spans only four binary phase coordinates; every protected
fifteen-T support spans five. This was independently recomputed on current v36c.
The present TREP2 builder explicitly adds a fifth |+> coordinate on q6
(`forms.py:1–7, 22, 89–96`). A rank-four compiler can investigate removing that
coordinate from the phase network. This does not by itself prove that a physical
ancilla or a verification step can be removed: incoming state preparation,
outgoing syndrome information and all noise channels must be re-synthesized.

### Exact ideal identity and a concrete starting support

For a four-dimensional binary subspace H and nonzero t in H,

\[
\sum_{a\in H\setminus\{0\}} (a\cdot y\bmod2)\equiv0\pmod8.
\]

For each y, the sum is either zero or eight. Consequently

\[
-\sum_{a\in H\setminus\{0,t\}}(a\cdot y\bmod2)
\equiv t\cdot y\bmod2\pmod8.
\]

This gives a fourteen-TDG realization of the desired phase with no extra
Clifford phase correction. It is an exact ideal equivalence on the specified
phase-coordinate space, not a fault-tolerance claim.

The historical builder's seven data-coordinate rows are
`[2,31,4,21,14,19,8]` on physical data `[0,20,7,4,3,15,8]`. Their span is

`H = {0,2,4,6,8,10,12,14,17,19,21,23,25,27,29,31}`.

It has rank four and contains historical target `t=25`.
The already enumerated historical support **f14_1** is precisely

`H \ {0,25} = [2,4,6,8,10,12,14,17,19,21,23,27,29,31]`.

The seven phase-axis malignant pairs are
`(2,27), (4,29), (6,31), (8,17), (10,19), (12,21), (14,23)`.
Each XOR is 25. All singleton phase faults are detected.
For this support the fifth q6 coordinate is unnecessary as a phase input;
q6 can still be used as a zero-initialized routing helper.

### New exact phase-only finite-p certificate on v36c

`phase_family_probe.py` re-derived v36c's commuting phase orbit and all 64
supports. In its basis, the target is **31**, not historical target 25.
It evaluated the exact ideal exterior response for all 32 aggregate phase
errors and then convolved independent phase-axis errors over all orders.
Only aggregate error zero and target 31 are accepted; their loss numerators
are respectively zero and one. For every hypothetical T gate the retained
noise component is its phase-axis Pauli, with probability q=p/3. All other
noise is disabled in this diagnostic.

At p=0.001:

| Family | Count | Phase-coordinate rank | Phase-only A | Phase-only L |
|---|---:|---:|---:|---:|
| 14 T | 15 | 4 | 0.9953442077157969 | 7.793347150063815e-7 |
| Protected 15 T | 16 | 5 | 0.9950116511240674 | 1.297594148096679e-9 |
| 1 T | 1 | 1 | 1 | 3.333333333333333e-4 |

For r=1−2q, the fourteen-T result has a rational certificate:

\[
A_{14}=\frac{1+7r^8}{8},\qquad
N_{14}=\frac{1+7r^8-8r^7}{16},\qquad L_{14}=N_{14}/A_{14}.
\]

The leading numerator term is 7q². The exact rational evaluation at q=1/3000
matches the independent 32-state convolution. The isolated phase-only loss
increment over the protected family is **7.780371208582852e-7**.
It is **not** an additive penalty estimate or upper bound for a complete
noisy grid circuit. X/Y components of gate noise, synthesized CNOT faults,
preparations, measurements, idles and interactions with other faults are absent.

`phase_sign_probe.py` exhaustively checked all 16,384 +/- sign assignments for
each current fourteen-axis support. Every support has 16 signed T/TDG
realizations with zero residual Clifford phase. The all-TDG identity above
is a particularly simple valid seed.

### New adjacent-grid routing witnesses

`phase_route_probe.py` used the published TREP2 `route` and `network` functions
without modifying their routing algorithm. It compared the original protected
f00_0 and historical f14_1 on the same 15 physical cells, with 100 seeds each.
For f14_1 q6 starts with coordinate zero, rather than the fifth variable 16.

| Fragment family | Valid routes / 100 | Best sampled CX count | Its phase-only ASAP depth | Fastest sampled fragment |
|---|---:|---:|---:|---:|
| Protected f00_0 | 96 | 28 | 26 | 32 CX, 15 ticks |
| Rank-four f14_1 | 100 | 18 | 15 | 24 CX, 10 ticks |

These are routing-fragment comparisons, not complete-circuit improvements,
not optima and not a comparison against the native v36c prefix.
The routing witnesses include computation and complete uncomputation.
`check_phase_fragments.py` independently replayed every operation of both
fourteen-T finalists, verified adjacency of all CNOTs, restoration of every
input coordinate row, and the target phase on all 32 assignments.

The files `phase14_min_cx.qasm.inc` and `phase14_min_depth.qasm.inc` are explicitly
marked incomplete fragments. They are not legal stand-alone contest submissions.
They need an encoded input, verified preparation, complete measurement contract,
full output construction and complete-noise pricing.

### First implementation experiment and stop gate

Start with historical f14_1 as an algebra/routing seed; map its four-coordinate
subspace into the current prefix before attaching anything to v36c. Co-synthesize
the prefix's required state and measurements, instead of appending a new parity
network to every old Clifford operation. The historical builder retains all
non-T operations before native step 29 (`forms.py:80`); its comment about dropping
double-cat checks is followed by unconditional copying of every annotation
(`forms.py:82–86`). This is evidence of retained scaffolding, not proof that
any given retained operation is redundant under noisy verification.

Require exact ideal target correctness, a complete single-fault audit under the
actual decoder and records, then the all-orders value and official processability.
A rare nonzero first-order contribution is permissible in principle but must be
priced; there is no blanket permission to ignore it. Prefer synthesis contracts
that preserve harmless/flagged single faults. Stop a realization if the complete
cost of its parity network and verification overwhelms the measured physical
benefit from shorter exposure or simpler preparation. Do not reject the whole
fourteen-T family merely because the seven phase pairs exist.

## 2. Syndrome-subspace coarsening: legal broader policy, negative first probes

The current acceptance constraints have the form Hm=0. Choose a nonzero detector
syndrome delta, a pivot k with delta_k=1, remove row k, and replace each remaining
row i by H_i XOR delta_i H_k. The new zero-reference constraints accept exactly
the original syndrome sectors {0,delta}. This preserves ideal acceptance and
the exact ideal target because all original ideal detector values were zero.
It introduces no quantum gate, measurement or scheduling change.

This strictly extends deleting named detector rows: e.g. replacing d1=0,d2=0
by d1 XOR d2=0 admits 00 and 11 while rejecting 01 and 10. It differs from an
invertible detector-basis rewrite, which preserves the original accepted set.
With logical frames, a retained old pivot parity can select a Pauli correction
on the newly admitted sector; on this two-sector accepted set that correction
is affine and needs no nonlinear quantum gadget.

However, three explicit nontrivial v36c coarsenings selected from harmless
single-fault signatures **all lost badly** when evaluated at all orders:

| Zero-based original detector row indices forming delta | L | A | New sector's conditional L |
|---|---:|---:|---:|
| 17,19 | 1.3717520885301132e-4 | 0.5084991703136376 | 0.008501580238554279 |
| 8,19 | 9.461474548970305e-5 | 0.5074645018910289 | 0.005768952660281813 |
| 21,22,23,55 | 5.473809920595914e-5 | 0.5045725629837737 | 0.0037573666994928927 |
| c43 singleton (row 25), historical-control probe | 4.115182901355832e-5 | 0.5027299283430396 | 1.0598252047806791e-4 |

The last row is also not acceptance-free on current v36c: delta A=2.0904181097e-6
and delta L=2.6957578491e-10. An old v34m independence certificate cannot be
transferred blindly to a different circuit.

All four QASMs passed the unchanged pinned official judge's format, class,
exact correctness and acceptance gates at 1,000,000 shots / seed 0. Those
Monte Carlo runs establish validity, not exact ranking. The all-orders omitted
kernel bounds are below 1.18e-14 and exclude floating-point roundoff.

This family warrants a cheap sector-risk oracle before searching many QASMs.
For an additional sector with probability a and loss numerator n,
the new loss is (A L+n)/(A+a); it improves exactly when n/a<L. A sector can
also fund a separately beneficial physical check, but that conjunction needs
fresh all-orders pricing. The experiments disprove the shortcut 'harmless
singles imply a useful relaxed acceptance policy'. Files include runnable
builders, full all-orders receipts and official-check receipts.

## 3. Instrument equivalence is a real research freedom only with a changed contract

The proposed new synthesis slice is a B/C resource plus its measurement and
logical-frame instrument, rather than a single pure B/C target state.
Allow measured C branches to carry tracked logical-sector information, and
require the accepted data instrument to be correct. This could admit mixed or
measurement-assisted resources that a pure-state CSS endpoint contract misses.
The first gate should be an explicit Choi/stabilizer rank or branch-equivalence
certificate proving that the admitted resource set is larger than the old one.

Two tempting shortcuts do not establish that freedom:

* A common GL(3,2) basis change in both halves of a maximally correlated rank-three
  resource leaves exactly the same pure state. It is an encoder parametrization,
  not a new physical resource. A state-contract synthesizer already includes it.
* Keeping the current full-rank C=0 conditions, deterministic ideal acceptance,
  zero logical frame and an arbitrary encoded input can force the original pure
  resource. Seven B/C equality constraints, three B X-check constraints, and
  four data-code/logical-action constraints can exhaust all 14 stabilizers.
  Merely tracing out C after its records have been postselected does not free it.

A substantive extension must change the measured/accepted branch contract,
use tracked logical sectors, or deliberately exploit the known incoming state
rather than demand a universal encoded identity. The exact incoming state and
its correlations must still be preserved in any bound. The accessible pin does
not contain FRESH/BCPOL/TERM/IDEAS code despite references in PLAN, so current
live coverage of this extension cannot be independently established.

## 4. Ideas excluded from the fresh list after checking history

* Plain common GL(3,2) re-basing: identical-state reparametrization, as above.
* Plain enumeration of the 30 Fano-plane labellings: ENDSTATE already reports
  107 shapes and 30 labelling classes modulo 168 automorphisms (FINDINGS).
  Joint noise-aware relabelling could be a refinement, not a new unexplored
  30-way search.
* Plain no-A/no-B final rounds: ARCH explicitly priced both on the old sep33
  input. `onlyX` had c1*p=2.747e-4 and total first+second 5.085468e-4;
  `onlyZ` had c1*p=4.667e-4 and total 7.644449e-4. It also tested all 128 A/B
  order masks, flagged hybrids, repeated partial rounds and an encoded Bell
  resource. This does not exclude every incoming-state-conditioned reduced
  instrument, but simply repeating those recipes is not a fresh idea.
* Idle padding/dynamical decoupling: STANDARD gives idle and one-qubit gate the
  same depolarizing strength p, so an idle-replacement Pauli does not lower that
  noise channel.
* Repeating existing backward terminal synthesis, adjoint integration, plain
  acceptance knapsack or mid-preparation B flags as new discoveries: PLAN at
  this pin explicitly assigns those tasks (P73, P75, P77 and current ledger).

## Files and reproduction

Main new certificates:

* `phase_family_probe.py`, `phase_family_certificate.json`
* `phase_sign_probe.py`, `phase_sign_certificate.json`
* `phase_route_probe.py`, `phase_route_certificate.json`
* `check_phase_fragments.py`, `phase_fragment_verification.json`
* `phase14_min_cx.qasm.inc`, `phase14_min_depth.qasm.inc`
* `coarsen_run.py`, `coarsen_results.json`
* `coarsen_official.py`, `coarsen_official_receipts.json`

The scripts resolve the current source from the parent workspace's
`quantumn_review10/work/lanes/MAIN/v36c`; adjust that explicit BASE location if
moving these intermediate audit files to a different directory layout.
The all-orders evaluator copy is under `evaluator/`. The official tests use
the unchanged judge snapshot at `audit/review9_resumed/official` with pin
`76fe47c0324f1c1f8b72a7d55af200e88043b522`.

No improved complete physical circuit was produced in this sub-audit. The
fourteen-T family has exact ideal identities, a current phase-only risk price,
and concrete adjacent-grid phase fragments. The coarsening proposals have
explicit negative complete-circuit results. These evidence classes must remain
separate in the final report.
