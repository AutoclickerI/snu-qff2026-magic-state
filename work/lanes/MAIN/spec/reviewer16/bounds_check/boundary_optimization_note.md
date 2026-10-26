# Acceptance-aware boundary optimization: precise scope

## Problem found

WHOLEEND/BRIEF.md:32–36 rejects a whole-grid ending unless its optimistic tail is <=2.4e-5.
This is a task-specific research target, not a contest rule. WHOLEEND/REPORT.md:15–18 reports
3.3711812301e-5 for its best three-tick tail, with perfect inverse resource and acceptance
0.95453665365; v37d is 3.676347e-5. The numerical difference is 3.051657699e-6. This is
an engineering budget, not an additive or monotonic lower bound on full-circuit loss.

WHOLEEND/MODEL.md:53–63 explicitly excludes other resource families and prices only six
minimum-c2 T-only contracts; ENDSEARCH/REPORT.md:19–27 already demonstrates rank reversal:
path full grid-free L=3.407979867e-5 beats square 3.466519226e-5, although path's round
L=2.708626922e-5 is worse than square 2.555843124e-5. A cheap higher-c2 resource can win overall.

## Exact formulation for a fixed actual native tail

Include all tail gates, waits, measurement errors, accept conditions and logical frames in the
successful completely positive map M_p. Logical frames can be applied mathematically per record;
this is scoring semantics and does not add physical gates. H_dec is the judge's decoded-fidelity
observable on the seven outputs; I-H_dec is positive semidefinite.

Define E_A=M_p^dagger(I), E_N=M_p^dagger(I-H_dec). For the actual boundary density matrix rho,

    A_tail = Tr(E_A rho),
    N_tail = Tr(E_N rho),
    L = N_tail / A_tail.

The current all-orders evaluator computes these scalars for a chosen rho. The proposed extension
optimizes an explicitly stated admissible set of boundary states, so that postselection is inside
the objective. It does not assume deleting preparation noise improves conditional fidelity.

If rho=V sigma V^dagger for a justified subspace/isometry V and sigma is arbitrary, the optimum is
the least generalized eigenvalue of (V^dagger E_N V, V^dagger E_A V), on positive-acceptance support.
Restricting the support is sound only if it contains EVERY actual noisy state in the family.

For a fixed incoming data marginal or extra linear constraints, use trial tau and solve the SDP

    minimize Tr[(E_N-tau E_A) rho]
    subject to rho >= 0, Tr rho=1, Tr_resource rho=rho_in,
               Tr(E_A rho) >= A_min,
               justified linear constraints.

A nonnegative certified optimum excludes L<tau in the relaxed family. A negative optimum is only
an optimistic witness, not a preparable circuit. If the prefix has acceptance A_pre and rho is its
conditioned boundary state, A_min must be 0.5/A_pre for the final acceptance gate. Retain classical
prefix records in the boundary description when tail acceptance/frames use them.

## Noiseless correctness must not be imposed on the noisy state by accident

The ideal resource contract P generally does NOT contain noisy preparation outputs. Therefore
optimizing only P rho P=rho at p=.001 is not a universal full-circuit lower bound. It is only an
ideal-resource-family comparison unless an independent argument establishes the support.

A sound small-family formulation fixes an actual prefix/preparation channel G_p from a variable
logical/gauge input sigma to the boundary, and its noiseless counterpart G_0. Pull E_A and E_N back
through G_p. Separately form E_bad,0 = M_0^dagger(I-Pi_raw_target), with the ideal code-space/target
projector and legal frames. Then impose the linear noiseless constraint

    Tr[G_0^dagger(E_bad,0) sigma] = 0.

This uses the same sigma in the noisy objective and noiseless correctness constraint. Any product,
stabilizer-only or local-preparability restriction relaxed from sigma makes the bound optimistic;
it does not prove the optimum can be synthesized.

## Feasible first experiment

Start with a fixed tail and 1–3 free gauge qubits, e.g. a reduced resource contract or a bounded
preparation window. Contract fixed data, native noise and the exterior into small effects on that
gauge space. Matrices then have size 2^k, k<=3 initially, and can be compared against the current
resource and enumerated stabilizer completions. Extend to 4–8 effective boundary qubits only after
matching the existing all-orders value and demonstrating the reduction preserves all correlations.
For a Clifford suffix and a proven Pauli-diagonal boundary description, a syndrome/Pauli quotient
may replace density matrices; do not assume this for arbitrary non-Clifford states or coherent
resource gauges. A full 36-qubit dense SDP is not proposed.

Validation gates: recover incumbent L/A, match several direct density-matrix small circuits,
use a dual feasible certificate or a conservative numerical tolerance when claiming pruning,
and distinguish a lower bound from an implementable resource. Promotion remains the actual
all-orders score and official correctness/acceptance/speed check of a full native circuit.

## Bound audit completed separately

strengthened.py and verify_certificate.py were independently rerun locally. They reproduce
the universal expected-loss floor 1.36578507905366540835e-5 over 2187 terminal assignments and
64 syndrome sectors, with unique relaxed XXXXXXX minimizer. Pinned official source hashes match
BOUND/source_hashes.txt. The ideal logical-axis relaxation helps only 1.89883e-11 for that minimizer,
so logical-axis steering alone is not a useful optimization candidate.

Stale overstatement: docs/reference/judge.md:36–37 says every final output gate costs at least the
idle it replaces. TERMINAL/REPORT.md:3–6,34–45 and BOUND/PROOF.md:170–194 establish only particular
fresh/verified-helper cases, while the universal and measured-partner floors remain different.
