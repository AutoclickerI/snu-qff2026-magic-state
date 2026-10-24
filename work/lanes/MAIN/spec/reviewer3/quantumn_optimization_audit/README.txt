QUANTUMN: code-grounded optimization audit / 2026-10-24
====================================================

Pinned repository:
  https://github.com/AutoclickerI/quantumn
  a9cae1c161a5f1713fea0f8bf242680cb2024bea
Pinned official judge inspected:
  76fe47c0324f1c1f8b72a7d55af200e88043b522

This bundle contains newly generated candidate circuits, calculation receipts,
and a scoped reproduction of the new all-order Walsh contraction. It does not
contain a mirror of either repository, and does not submit or modify remote code.

Requirements and paths
----------------------
Python 3.12 with NumPy 2.3.5 was used. The prototype only requires NumPy and the
source files of your existing repository and official judge. It AST-loads the
actual Basis and Engine classes; it does not require Stim or xtim locally.

From the root of this unpacked bundle:

  export QUANTUMN_REPO=/absolute/path/to/quantumn
  export QUANTUMN_JUDGE=/absolute/path/to/snu-qff2026-problem
  python audit/v22_preparation_contracts.py
  python audit/fresh_walsh_validate.py
  python audit/third_order.py circuits/v22_readout_copy4
  python audit/fresh_exact_walsh.py 72 circuits/v22_readout_copy4

If QUANTUMN_JUDGE is absent, it defaults to
  $QUANTUMN_REPO/upstream/snu-qff2026-problem

The all-order command must be given 72 (all decoder terms). Omitting it computes
acceptance only. Baseline reproduction:

  python audit/fresh_exact_walsh.py 72 "$QUANTUMN_REPO/work/submissions/v22_r155"
  python audit/fresh_exact_walsh.py 72 "$QUANTUMN_REPO/work/lanes/MAIN/v23h_c2c9"

Expected computational scope
----------------------------
The new evaluator computes finite-p expectations over all independent Pauli
channels, with the official finite-p aggregated idle probabilities. It neither
samples nor truncates fault weight. Floating-point arithmetic and a 1e-12
roundoff-zero threshold in the Walsh kernel are used; this is not an interval
arithmetic or formal rational certificate. Runtime was about 4.3 minutes per
baseline circuit in this environment, not a portable speed guarantee.

This frontend is deliberately scoped to the supplied v22/v23 circuit family:
15 rotations, rank 5, four active reduced projectors, diagonal projectors,
zero ideal detector values, no explicit FRAME or POSTSELECT declarations. It
rejects explicit frames/postselection and unsupported gates. Do not treat it
as a universal evaluator for arbitrary newly designed circuits. Candidate
correctness and format must still pass the official checker before submission.

Three-channel validation exhaustively enumerates 1,024 outcomes and agrees
with the contraction within 1e-15 in acceptance and error numerator. The
v22 expectation agrees closely with the repository's 380-redraw mean. These
are strong cross-checks, not a full independent reimplementation of the judge.

Candidate circuits
------------------
* v22_readout_copy4: replace the old final CX19->25 with two fresh output copies,
  and copy C29 and C28 too. Copy edges: 19->18,25->31,29->35,28->34 at step46;
  helpers reset at45, both readings at47, equality detectors added. Old detector
  basis is undone where needed. 206 CX, native depth48.
* v23_readout_copy4: the same output transformation on the current unsubmitted
  v23 candidate. Original v23 prep and prefix remain intact.
* v22_verified_init6, if present: one-CX verified initialization at q29,q28,q27,
  q25,q26,q12, with helper readout simultaneous with the output's first main
  operation. 209 CX, depth48. Readout helpers are reused only after earlier
  measurements, when combined variants are present.
* v22_readout_copy4_verified_init6: both changes combined, with helpers returned
  by early measurement and reset before the terminal copies. 212 CX, depth48.

Each .qasm has a sibling .json with the required data_qubits order. Calculation
receipts say whether a value is through third order, an acceptance approximation,
or an all-order finite-p expectation. None is a new official seed-0 board score.

Final computed results
--------------------------------------------------------------------
Circuit                          cubic loss           all-order loss
v22 baseline                     7.13059567854321e-5   7.23645253715270e-5
v22 copy4                        7.08515862406617e-5   7.19023857746563e-5
v22 init6                        7.00020873294243e-5   not separately run
v22 copy4 + init6                 6.95552208089810e-5   7.05812541909729e-5
v23 baseline                     6.92210398227877e-5   7.02618674069663e-5
v23 copy4                        6.87707154979444e-5   not run

Exact acceptance: v22 baseline 0.5338602966998095; v22 copy4
0.528331658320608; v22 combined 0.5229926822994524. All reported
combined/copy QASMs preserve depth48, pass the local noiseless code/target
checks, and have zero harmful accepted single-fault contributions.

Strict local-channel statement
------------------------------
Both terminal copy/equality checking and the overlapping verified initial reset
have herald success alpha=(1+r^3*d)/2 and accepted erroneous-bit mass
beta=(1-r*d+r^3*d-r^2*d)/4, where r=1-2p and d=1-16p/15.
At p=.001, alpha=.996475856270933 and beta/alpha=.000269612689335.
The latter improves a terminal measurement's p, an RX reset's p, and a checked
M-initialization's 2p/3. It is a local-channel guarantee, not a universal theorem
that the conditional logical loss of every circuit must improve.

The init gadget schedules helper readout in the SAME native tick as the first
existing operation on the initialized output. An extra wait on that output
changes the noise channel and invalidates the quoted local comparison.

The ten methodological candidates
---------------------------------
1. Fresh-helper repetition of selected final C readouts, with equality checks.
2. One-CX verified initialization whose helper measurement overlaps first use.
3. All-order Walsh/factor-graph contraction for low-magic-rank ranking.
4. Explore 128 partial-clean policies for seven correctable B-X residue classes.
5. Synthesize the entire B+C verification instrument; relax unused C coherence.
6. Puncture one C verifier position, retaining only correctable accepted classes.
7. Compress A's measurement resource to three bare rails or four GHZ qubits.
8. Move logical data wires inside the prefix and retarget their later gates.
9. Use live data as returned-unchanged dirty workspace for remote CX routing.
10. Compile the fixed suffix into an 11-bit B/C boundary response cache.

Items 4-10 include partial proofs or architectural opportunities; they are not
claimed to improve the full noisy circuit already. The three-rail and four-GHZ
A replacements LOSE on the ideal-geometry reference and are justified only if
freed space saves more B/C routing and data-wait loss. The 11-bit cache applies
only to the stated fixed suffix; entry correlations require an expanded boundary.

See the accompanying Korean chat analysis for the source locations, guarantees,
specific first experiments and rejection criteria for every candidate.

Final combined all-order improvement: 2.464289% versus v22, at the
same native depth48; acceptance decreases by 1.086761 percentage points.
This combined v22 circuit is not asserted to beat the newer v23 baseline.
The v23 copy4 port improves its own baseline through third order; init6 has
not been ported to v23 in this audit.
