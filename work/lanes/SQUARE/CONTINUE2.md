Correction from the main session (I cancelled your turn on purpose and stopped bc_direct.py on hippo and its docker
container on owl; your files are intact). Reviewer 15 (work/lanes/MAIN/spec/reviewer15/REPORT_KO.md, items 1-4;
untrusted, numbers reviewer-reported) removes the constraint that made your grid builds fail. Switch to it now:

1. Relative Steane permutation. Couple C_i -> A_{P(i)} with P one of the 168 automorphisms of the Steane code, keeping
   D_i->A_i, B_i->C_i, B_i->D_i. A k-cycle of P makes a physical 4k-cycle, so the per-index unit square disappears.
   Reviewer: first order clean for all 168, c2(P) = 77/3 + (7 - fix(P))/150 p^2 (at most +4.5e-8). I checked their
   layout: P = [0,2,1,3,4,6,5] (fix 3; it maps the judge's |0_L> codewords onto themselves), D = [6,26,19,10,2,28,16],
   A = [0,32,13,11,8,27,17], B = [7,20,25,4,3,29,22], C = [1,14,31,5,9,23,21]: 28 distinct cells, free
   {12,15,18,24,30,33,34,35}, all 28 round contacts grid neighbours, two data hops from v37b (20->26, 22->28; cells 20
   and 22 become B, so their release time matters). Make P a layout variable in find_layout.py and score layouts by
   preparation depth, single faults and cell release, not contacts alone.
2. Measured helpers instead of coherent uncompute. A preparation that leaves sum_u |Gu>_block |Ku>_helper can MX the
   helpers: the block keeps a known Pauli byproduct. Reviewer: for the square, X_A(a) Z_B(b) X_C(c) Z_C(d) byproducts
   leave D untouched and only flip A_Z by a+c, B_X by b+d, C_X by d (verify), so fold them into the detectors instead
   of reversing the helper CX chain (a clean path of length l: 2l-1 CX -> l CX + l-1 MX). Start with C, one block per
   helper, and re-check every native single fault after removing the reverse CXs.
3. Prepare the 18-stabilizer resource, not three pure states. The square needs only X_A(H_j), X_A,L; X_C(H_j), X_C,L;
   X_B(H_j); Z_B(H_j), Z_B,L; Z_A(H_j)Z_C(H_j) (18 generators on 21 qubits); the remaining three gauge qubits may be
   mixed or entangled with helpers (135 stabilizer completions, 16 CSS). Fixing some gauge-X adds deterministic
   detectors on bits C already reads. Warning from the reviewer: the naive aggressive completion (A by a plain encoder,
   then coupled to C) leaves one native fault giving an undetected Z0Z6 on the data (p/15): synthesize for fault
   safety, do not just weaken the target.
4. Alternative preparation by projectors: A, C from |+>^7 with their three Z stabilizers measured, B from |0>^7 with its
   three X stabilizers measured, keeping all 512 syndrome branches and folding the preparation syndromes into the final
   detectors (H(A_Z) + s_A + s_C, H(B_X) + s_B). Compare it with 1-3 on the same layout; a preparation-record error that
   hides a data error together with a final-detector error rejects the circuit.
Order: build the reviewer's layout with the cheapest preparation you can get from 2-4 and just-in-time starts, price
it exactly; then search P and layouts jointly with the preparation model. Target and finalist: L < L(v37c) - 1e-7,
L(v37c) = 3.6904034715818095e-5 (work/lanes/MAIN/v37c is the incumbent now), A >= 0.5002, judge gates_ok at 1e6, judge
speed within 1.5x of v37c's. Hosts: owl <= 24 inside docker (stop a container with docker kill <id>, since PID 1 in a
container ignores SIGTERM), hippo <= 8. A finalist does not end the lane; do not stop to ask questions; update
REPORT.md (<= 100 lines, each < 2,000 characters) and results.json.
