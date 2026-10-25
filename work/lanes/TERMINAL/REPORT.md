# TERMINAL — no realizable improvement from the tested endings

**Verdict:** no redesign finalist. Fresh unmeasured helpers lose; verified helpers improve only the
two-tick sub-tail and fail the tested grid contacts. Decomposed recovery loses through lookup faults
or unprotected waiting. A syndrome postselection check does not remove its own terminal noise.
This closes the concrete witnesses below, **not every possible recovery architecture**.

All prices are conditional true expected `1-F` at p=0.001, with full native noise in the stated tail.
Preparation before the cut is perfect. No MC estimate or finite-shot score is reported.
“Two ticks” starts at the last B→D check; “three ticks” includes D→A and B→C too.
The three-tick checks are the redesign screen; a shorter sub-tail is not a whole-round price.

| Ending | Optimistic L | A | First order | Cells/contact requirement | Full build |
|---|---:|---:|---|---|---|
| Reference v37b, t≥47 / t≥46 | 2.275813812e-5 / 2.847393823e-5 | .972833965 / .960978631 | pass | incumbent layout | full v37b 3.742321460e-5, A=.503479377 |
| SQUARE, three ticks | 2.555843124e-5 | .957525136 | pass | seven D/A/B/C squares | SQUARE lane owns it |
| **(a)** fresh helper→D, reset, two / three ticks | 4.369934987e-5 / 5.438544194e-5 | .975562487 / .964702492 | pass | 35 roles; seven extra D neighbours | fails tail gate |
| **(a)** better measured-zero helpers, two / three ticks | 3.242957210e-5 / 4.130457741e-5 | .961999781 / .951290767 | pass | 35 roles; helper MZ before final CX, all seven records checked | fails tail gate |
| **(b)** check earlier, reads concurrent with fresh-helper CX | exactly (a) at the same relative scope | exactly (a) | pass | same three layers; absolute retiming does not change tail channel | fails tail gate |
| **(a,b) extension:** helper checked through C, two / three ticks | **2.192341878e-5 / 2.865372771e-5** | **.971929843 / .954415669** | pass | 35 roles; F→C at T−1, F→D and C/B reads at T | blocked on v37b and both SQUARE layouts |
| Same extension, A checks helper | 2.192445535e-5 / 2.869205233e-5 | .971929861 / .954415802 | pass | F adjacent D and a retained A checker | same grid obstruction |
| **(c)** unmeasured one-hot controls, RCCX lookup | ≥4.627426529e-5 from just two idle ticks; actual 26-tick factor ≥.0069614925 | relaxation 1; full A=1 (no rejection) | **fail:** native-gate-only c1=40 for both axes | 27 roles; 3 syndrome + 7 controls per axis, then controlled Z/X | ruled out before placement |
| **(d)** linear correction + duplicated measured OR FRAME | ≥4.627426529e-5 from two idle ticks; 24-tick factor ≥.0059890288 | relaxation 1; actual A unpriced | tail passes by fault partition; actual extraction unverified | 21 roles; OR computation and retained-source comparisons | ruled out by independent data-idle factor |
| **(e)** native syndrome-zero postselection, three ticks | 2.871336127e-5; shared SQUARE version 2.555843124e-5 | .964702492 / .957525136 | pass, but accepts nonzero final syndrome | 28 roles, standard/square checks | fails gate; exact final zeroing impossible with unseen last data faults |

## Mechanisms and decisions

**Fresh helpers.** Reset controls carry X error p into D; measured-zero controls retain post-measurement
X/Y probability 2p/3 even when their records are zero. The final CX's smaller marginal noise cannot
pay this cost. Reversing the reset-helper CX is worse: three-tick L=7.589546541e-5.
ARCH's dummy-reset and measured-helper failures reproduce at all orders (not merely third order).
(b) has the identical saved QASM/channel as (a) once its final check and readout are aligned.

**Verified helper survivor.** At T−2 prepare F while D→A and B→C run; at T−1 run B→D and F→C;
at T run F→D and measure B,C. This preserves every original detector and reduces the two-tick
sub-tail by 8.34719e-7, but the three-tick tail is already 1.79889e-7 above v37b's t≥46 tail
and 3.09530e-6 above SQUARE. The C-detector read is delayed, not silently discarded.
The A-check variant was also priced, since it could have different available contacts.

**Grid tests for both sub-tail survivors:** v37b free cells are {0,1,30,31,32,33,34,35}.
D6's only possible fresh neighbour is F0, which touches neither A nor C; several other outputs
have no fresh neighbour at all. The SQUARE compact and joint layouts also fail: compact has zero
eligible helpers for every D; joint leaves at least four D without one. The test permits arbitrary
checker permutations and ignores preparation/prefix occupancy, so those extra constraints cannot
repair it. No full build is warranted on these layouts. Other placements/routed architectures are unproved.

**Coherent lookup:** four product computations plus linear fanout implement all seven one-hot bits.
Both exact-CCX (47 ticks, 28 T/axis) and cheaper relative-phase RCCX (26 ticks, 16 T/axis) were built.
Every native gate, idle and initialization single Pauli was scanned for all eight input syndromes:
14,168 and 8,264 cases respectively. For zero syndrome the RCCX lookup has 367 harmful cases/axis.
Native gates alone give c1(X)=13.3333333 and c1(Z)=26.6666667; this is a coefficient, not a finite-p score.
An explicit exact-CCX witness is X after the final product's H: fanout flips all seven controls,
giving logical X/Z with zero syndrome and loss 1/2 or 1. Keeping controls unmeasured does not flag it.

**Linear/FRAME:** verified the correction identity for all 128 single-axis masks, hence 16,384 Paulis.
The duplicate RCCX OR lookup passed 4,952 single-fault/input cases with source-memory comparisons.
The remaining tail faults either reject or leave one correctable data Pauli (`verification.json` partition).
The saved circuit includes input records, duplicate-OR comparisons, final source comparisons and both
legal affine FRAME lines. No 20-T evaluator limit is treated as a contest restriction.
Its data wait is independently fatal even if Boolean logic and extraction are perfect: D1(p)^2
on all seven outputs has optimized decoded loss ≥4.627426529e-5 over all 64 syndrome sectors and
all logical Bloch directions. This factor is independent of the retained records and commutes through
the final controlled Paulis/frames; conditioning cannot remove it. The same bound closes (c) even
if its lookup faults are repaired. Interleaved active protection would be a new architecture, untested here.

**Syndrome-zero check:** after a data qubit's last CX, a data-only Pauli cannot alter later partner
records. The native instrument explicitly accepts such nonzero-syndrome faults (verification.json).
Thus a literal noiseless final projector cannot be implemented by rearranging existing readouts.
Ordinary full-syndrome postselection and its SQUARE sharing realization were priced, including their noise.

## Verified scope and artifacts

Reproduced v37b full/t≥46/t≥47, SQUARE's 2.555843124e-5, all listed tail prices and acceptance,
zero first-order loss for the Clifford tails, native schedules, CCX/RCCX truth tables, correction identity,
lookup scans and relaxed contact infeasibility. `cut.py` retains its operation-owned semantics:
its t0=48 value is ~0 because dropping tick-47 operations also drops their following data idles.
A chronological t≥48 cut gives **1.162525253e-5**, A=.991035923; t≥46 and t≥47 are unaffected.
I capped cut.py/price.py at three workers plus parent and fixed native folding/scheduling in saved witnesses.
Not verified: a universal exclusion of all coherent recovery/protection layouts, full noisy (d) acceptance,
or a new complete preparation. No new grid-valid finalist exists; `cand/` is intentionally empty of circuits.
All computation was on hippo, ≤4 lane Python processes, one BLAS/OpenMP thread; no agents, submissions,
commits or pushes. The task's restrictions were treated as task-scoped, not added as standing rules.
Files: `results.json` (QASM-SHA256 keys, separate cut scopes), `builds/`, `logs/*.receipt.json`,
`logs/*scan.json`, `logs/{grid_test,wait_bounds}.json`, `verification.json`, `manifest.json`;
reproduce with `build.py`, `recovery_build.py`, `price.py STEM 3`, `lookup_scan.py`, `wait_bound.py`,
`grid_test.py`, `verify.py`, `collect.py` under the stated thread environment on hippo.
