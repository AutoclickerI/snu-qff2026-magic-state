# Public leaderboard and official constraints, 2026-10-27

## Verified first place

The public leaderboard currently reports **Placeholder** first:

- Official sampled score: **3.0423837010265e-5**.
- Three-significant-figure ranking key: **3.04e-5**.
- Two-qubit gates: **277**.
- Acceptance: **0.50059432**.
- Submission timestamp: **2026-10-27 12:05:13.919 KST** (03:05:13.919 UTC).

Second is **초정밀모델제어학회쨩**, sampled score 3.30430020090153e-5,
key 3.30e-5, 412 two-qubit gates, acceptance 0.5010138.

Machine-readable public evidence is in `leaderboard.json`. This was read from
the same sanitized public table and with the same columns and sorting that
the official page uses. Only the public leaderboard was queried.

**The winning circuit and its design are not exposed by this endpoint.**
The official frontend exposes team name, sampled score, rounded score key,
two-qubit gate count, acceptance, and submission time. Its wrapper expressly
states that circuit text and judge diagnostics do not reach the browser.
Public searches did not locate an independently published Placeholder circuit.

## What the comparison does establish

Compared with the repository's v37j baseline (412 CX), 277 CX is **32.77% fewer
two-qubit gates**. The winner's sampled loss is **7.93% lower** than the current
second-place sampled loss. Against v37j's exact expectation of
3.58709500347e-5, its sampled loss is 15.19% lower, but this is **not a
comparison of exact expectations**. We do not know Placeholder's true mean,
sampling variance, or whether its submission was selected across equivalent
sample draws.

This is concrete evidence that 412 CX is unnecessary for a competitive
legal circuit. It does not establish which gates to remove, which encoding
or verification protocol Placeholder uses, or how much expected loss its
design improves.

An appropriate engineering target for structural work is an independently
validated exact mean at or below 3.0e-5, with native grid legality and
acceptance above 0.5. This is a target, not a performance prediction or a
claim that the public winner has that exact mean.

## Official constraints relevant to redesign

Pinned official problem source: `76fe47c0324f1c1f8b72a7d55af200e88043b522`.

1. There are 36 qubits on a 6 by 6 grid. CX is the only two-qubit primitive,
   only between vertical/horizontal neighbors, with either direction allowed.
   Output locations and spare-qubit use are free.
2. Gates allowed are id, x, y, z, h, s, sdg, sx, sxdg, t, tdg, cx,
   measure, reset, and barrier. Conditional physical gates and arbitrary
   rotation primitives are excluded.
3. The simulator must accept the circuit. In the documented class, propagated
   non-Clifford Pauli rotations form one mutually commuting layer.
   There is **no official 20-T cap**.
4. Noise is uniform circuit depolarizing noise at p=0.001: preparation and
   measurement bit errors have probability p; each single-qubit gate and
   idle tick has depolarizing probability p; each CX has probability p spread
   uniformly over 15 nonidentity Pauli pairs; measurements additionally have
   postmeasurement depolarizing noise.
5. reset followed by h is one X preparation; h followed by measure is one X
   measurement. h, measure, h retains the measured X eigenstate and is also
   one measurement. The absorbed h gates take no separate noise or time.
6. Operations schedule at the earliest available time in program order.
   There is no idle noise before first use, immediately before reset, or
   after a qubit's terminal measurement. Data wait through circuit end.
7. DETECTOR means a deterministic accepted-branch parity. POSTSELECT can
   restrict random ideal outcomes to an affine value. Logical FRAME_X/Z
   are affine XOR functions of final classical records.
8. Ideal accepted output must already be the target up to its declared
   logical Pauli frame **before** the judge's ideal correction. Arbitrary
   physical Pauli residues cannot be hidden behind ideal correction.
9. The score is infidelity after fixed ideal Steane correction, then logical
   frame correction; single-qubit Pauli errors are correctable.
10. Acceptance must be at least 0.5 with noise; the exact evaluator's
    0.5002 margin is a project choice, not an extra contest requirement.
11. Official scoring uses 100 million shots, one-million-shot chunks with
    seeds 0,1,...,99. Rank compares three significant figures, then fewer
    two-qubit gates, then earlier submission.
12. Size caps are 200,000 UTF-8 bytes, 5,000 noncomment QASM statements,
    and 1,000 combined measure/reset operations. The server runtime limit
    is one hour. These do not fix a protocol, detector list, resource
    boundary, encoding basis, or output roles.

## Design implications, explicitly inference

The strongest accessible architectural evidence is the **gate-count gap**.
A redesign should seek a smaller complete preparation-and-verification
network, not assume a publicly known winning mechanism.

The existing DEEP abstract design (170 CX, 22 ticks and exact mean around
2.7185e-5, per the private repository plan) has enough numerical headroom to
be interesting, but it must pay for real preparation, transport and storage.
The critical executable test is whether its output roles, resource placement
and verification order can change together to produce one legal grid build.
Checking each individual tick's matching does not establish that continuous
qubit worldlines can realize the schedule.

The public score cannot distinguish a lower-noise final check from a cheaper
factory, a different logical-check construction, or a different sample draw.
Do not attribute any of those techniques to Placeholder without its circuit.

## Source URLs

- https://snuquantums.github.io/snu-qff2026/hackathon.html
- https://github.com/SNUQuantums/snu-qff2026/blob/master/assets/supabase.js
- https://github.com/SNUQuantums/snu-qff2026/blob/master/assets/supabase-config.js
- https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/problem.md
- https://github.com/SNUQuantums/snu-qff2026-problem/releases/tag/xtim-3.1.3-qff2

The exact API URL without its public authentication header is recorded in
`leaderboard.json`. Official source and simulator downloads, including
verified hashes, are recorded in `upstream/download_manifest.json`.

