# Strengthened two-tick bound for the inspected judge

The claim is confirmed. Let p=1/1000, q=p/5, and let L be the expected
conditional decoded infidelity. Every admissible circuit under STANDARD obeys

    L >= (1 - sqrt(M))/2
      = 0.000013657850790536654083512357592043628581552997723074420656433066...

where M is the exact rational `max_norm_squared` in `certificate.json`.
In particular L >= 0.00001365785079053665 > 0.000013657.
This is a lower bound, not a claim that a complete admissible circuit attains it.

## Source contract and all noise/schedule assumptions

Source paths below are relative to `upstream/snu-qff2026-problem/tprep/`.
The inspected source hashes are recorded in `source_hashes.txt`.

1. `noise.py:14-32,98-122`: independent D1(p) follows every native one-qubit
   unitary, independent D2(p) follows each CX, and waiting costs D1(p) per tick.
   D1 has probabilities (1-p,p/3,p/3,p/3); D2 has probability p/15 for each
   nonidentity two-qubit Pauli. `faults.py:27-29,103-106` confirms this convention.
   Different locations and different operands of D1 are independent draws.
2. `noise.py:54-88`: gates last one tick, run ASAP in qubit order, and cannot
   overlap on a qubit. Barriers constrain scheduling; TICK annotations do not.
   Define T as the last actual scheduled native-operation tick, not a QASM line.
   Native RX/MX folding happens before this schedule (`qasm.py:107-159,203-205`).
   An output that finishes early idles through T. Consecutive idle noise is
   aggregated by the exact composition law (`noise.py:43-45`); it can be split
   back into separate independent tick channels and commuted past disjoint work.
3. `noise.py:78,85-87,104-114`: exceptions are no waiting charge before reset,
   no charge after an unreused final measurement, and no waiting charge before
   first use. Reset prepares a basis state with orthogonal-state probability p;
   first use other than reset supplies the same noisy |0>. Every M/MX has an
   independent post-measurement D1(p), including when its qubit is reused.
   Measurement flips precede the measurement; reset flips follow preparation.
4. `noise.py:31-32`, `qasm.py:184-200`: CX is the only entangling gate in STANDARD;
   classical conditional gates and custom operations are rejected. Native
   one-qubit gates may be non-Clifford; the proof uses D1's full unitary covariance.
5. `check.py:156-166,253-264,273-302`: acceptance depends only on participant
   measurement records (DETECTOR and POSTSELECT). The ideal final six stabilizer
   measurements never reject and their records cannot be declared in a frame or
   postselection. Frames are products of logical Pauli X^7 and Z^7, with signs
   determined by earlier records. Non-output quantum systems are unobserved
   except through those records; thus they can be traced out when scoring.
6. `grid.py:5-7`, `check.py:14-22,297-302`: the X and Z stabilizer supports are
   {0,2,4,6}, {1,2,5,6}, {3,4,5,6}. A nonzero X-type syndrome changes the signs of
   both X_L and Y_L; a nonzero Z-type syndrome changes Y_L's sign. Physical Y^7
   is -Y_L. The target has logical Bloch vector (1,1,0)/sqrt(2).
7. `exact.py:250-267` checks noiseless code-space membership and target fidelity
   with tolerance 1e-9. A terminally measured/reset/untouched output, or one
   subsequently acted on only locally, is separable from the other outputs on
   each record branch. Every single-qubit reduction of the target is I/2, so a
   separable state has target fidelity at most 1/2. Such circuits are excluded
   with a large margin even by the finite correctness tolerance. Product-Pauli
   frames and postselection confined to the other qubits cannot fix this.

The statement concerns the intended quantum channels at p=1/1000, with no
leading-order approximation. Floating-point judge arithmetic and a finite
1e8-shot Monte Carlo realization are not exact rational quantities. In
particular the lower bound does not constrain an individual seed-0 draw.

## Exhaustive terminal cases

If a CX at T joins two retained outputs, retain just its D2(p). All other final
operations are disjoint and commute with that channel; absorb the rest into an
arbitrary input state. Optimizing the decoded fidelity over all input states
gives loss 0.00033332888592396909..., separately checked for all 21 output pairs
by the reproduced legacy rational and dense-matrix scripts. This exceeds the
claimed bound. Unitality of the other adjoint channels ensures they cannot
increase the largest eigenvalue after this relaxation.

Otherwise every output at T is idle, has a one-qubit unitary, or participates
in a CX with a non-output helper. Such a helper cannot have another operation
at T or later: gates cannot overlap and T is the global final tick. In
particular it is not subsequently measured. The last-measurement idle exemption
on an output is inadmissible by source-contract item 7.

Let S contain all seven outputs AND every helper in those final CXs. Its members
are distinct. Extract an independent D1(q) on each member immediately before
tick T. Crucially, this includes idle/one-qubit outputs, not only CX outputs.

For a member active at T-1: its post-unitary/post-measurement D1(p) factors
D1(q) with a CPTP residual. If its noise is D2(p), put a=1-4q/3 and
lambda=1-16p/15. It factors as (D1(q) tensor D1(q)) composed with a Pauli channel R:

    R_II = (1 + 6 lambda/a + 9 lambda/a^2)/16 = 224745025/224880016
    R_P_I = R_I_P = (1 + 2 lambda/a - 3 lambda/a^2)/16 = 9/224880016
    R_P_Q = (1 - 2 lambda/a + lambda/a^2)/16 = 14993/224880016

The multiplicities are 1,6,9; all probabilities are nonnegative and sum to 1.
This simultaneously extracts both factors when the same T-1 CX joins two
members of S, including two helpers, two outputs, or a helper and an output.
If only one endpoint is in S, absorb the unused factor into the residual.
An idle member has D1(p) at T-1. For reset at T-1 or fresh first use at T,
replace the noisy basis preparation by orthogonal-state probability

    p' = (p - 2q/3)/(1 - 4q/3) = 13/14996.

Applying D1(q) afterward restores exactly the original basis preparation.
This is a preparation-channel identity, not an erroneous factorization of
X_ERROR on arbitrary entangled inputs. It applies to RX in its own basis too.
The before-reset idle exemption causes no problem: the reset itself supplies
the factor. Every relevant first-use, measurement and waiting exception is covered.

## Moving the independent factors to the scored output

D1(q) commutes through any final local unitary. Through CX, an output Pauli
retains its output component and may add a helper Pauli, which disappears on
partial trace. A helper-control X or Y additionally contributes X on the output;
a helper-target Z or Y additionally contributes Z on the output. Each event
has probability 2q/3. This identity is valid on entangled input states, because
conjugated Paulis are products and the helper is traced out.

The final CX's D2(p) reduces exactly to D1(4p/5) on the output even on an
entangled input. Therefore, writing B_A(r)(rho)=(1-r)rho+r A rho A, the three
possible retained local channels are

    L: D1(p) o D1(q) = D1(p+q-4pq/3)
    X: D1(p-16p^2/75) o B_X(2p/15),   helper -> output
    Z: D1(p-16p^2/75) o B_Z(2p/15),   output -> helper.

Their exact I,X,Y,Z probabilities share denominator 105468750000:

    L: (105342215625, 42178125, 42178125, 42178125)
    X: (105349259996, 49192504, 35148750, 35148750)
    Z: (105349259996, 35148750, 35148750, 49192504).

After extraction, all remaining T measurements act on systems disjoint from S.
Local noise on S cannot change their record probabilities, even when entangled.
Consequently the extracted product channel is independent of the acceptance
event and factors on each conditioned state. Earlier helper records cause no
exception. Pauli frames commute with all three local Pauli channels. All
residual noise, pre-existing correlations, logical bias and postselection are
absorbed into an arbitrary density matrix just before this extracted channel.
This is an exact channel/instrument factorization, not an assumption that
deleting noise must improve a postselected circuit.

## Decoder optimization and certificate

Let S_X and S_Z be 2 times the projector onto zero X/Z syndrome minus identity.
The scored fidelity observable, directly from the judge, is

    H = [I + (S_X X^7 - S_X S_Z Y^7)/sqrt(2)]/2.

The adjoint product channel preserves the 64 simultaneous stabilizer sectors,
each of dimension 2. In sector (x0,z0), use the representative with one X at
column x0 if nonzero, and one Z at column z0 if nonzero. For an error with
X/Z syndromes (sx,sz) and X/Z parities (px,pz), define

    fx = px xor [x0 != 0] xor [sx xor x0 != 0]
    fz = pz xor [z0 != 0] xor [sz xor z0 != 0]
    vx = E[(-1)^fz],  vy = E[(-1)^(fx xor fz)].

The two eigenvalues are (1 +/- sqrt((vx^2+vy^2)/2))/2. These are all 128
eigenvalues: no code-space-input assumption is imposed. Maximizing the squared
radius uses rationals only. The 168 GL(3,2) column permutations preserve the
actual stabilizer row space and X^7,Y^7. They partition the 3^7 assignments
into 60 orbits. `strengthened.py` explicitly checks this group, enumerates all
4^7 noise patterns for each representative, and stores all 64 sector moments.

`verify_certificate.py` independently convolves a 256-state syndrome/parity
distribution for EVERY one of the 2,187 assignments, with no symmetry reduction.
It checks all 139,968 sector inequalities, verifies all representative moments,
and brackets the optimum between 0.00001365785079053665 and
0.00001365785079053666 using exact rational squared comparisons.
`matrix_check.py` constructs H as a 128x128 matrix and independently propagates
4x4 Pauli Kraus operators through both CX orientations. It compares the complete
128-eigenvalue spectrum for all 60 cases. Numerical errors are in `matrix_check.json`.

## Minimizer, scope, and measured-partner comparison

The unique minimizing assignment is XXXXXXX: seven simultaneous CXs from seven
distinct discarded controls to the outputs. Its best sector is (0,0), with
logical Bloch vector proportional to (vx,vy,0). The next assignment is six X
and one Z, with floor 1.3870044320888314e-5. All-local LLLLLLL costs
1.6721030306692441e-5; all-reversed ZZZZZZZ costs 1.5697287859570993e-5.

These are optima of the extracted-channel relaxation. A full circuit need not
realize the optimal residual input or avoid the additional noise discarded by
the relaxation. No matching preparation circuit or tight universal optimum is
claimed. The proof nevertheless covers every admissible circuit, not just the
seven-helper subclass: all other terminal cases were bounded or enumerated.
Layout, circuit depth, acceptance amount and preparation architecture were relaxed.

For the measured-partner class (CX at T-1, partner measured at T, output idle
at T), the conservative extracted channel is D1(p) o D1(2p/5). Its optimized
loss is 2.2735790278341725e-5, 9.0779394878050713e-6 above the strengthened
universal floor, a factor 1.6646682283346555 (66.4668% higher).
For completeness the measured-helper instrument exactly factors the slightly
larger q0=(2p/5)/(1-8p/15): grouping helper Paulis by whether they commute with
the measurement gives a no-flip branch of weight 1-8p/15 with normalized data
D1(q0), and a flip branch with completely depolarized data. Both factor D1(q0).
Including the final idle gives 2.2742699650371855e-5, gap 9.0848488598352005e-6.
Both explain the rounded 2.274e-5 class floor; neither is a full-circuit optimum.
