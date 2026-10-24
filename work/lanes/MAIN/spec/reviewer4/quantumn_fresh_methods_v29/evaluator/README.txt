SPARSE KERNEL WALSH EVALUATOR: REVIEW PROTOTYPE
============================================

Purpose
-------
Evaluate the current circuit family's true conditional noise-model expectation
including all fault orders, with a much smaller contraction than the original
reviewer-3 dense Walsh prototype. This changes evaluation cost, not physical
circuit performance.

Run from this directory (tested with Python 3.12 and NumPy 2.3.5):

    OPENBLAS_NUM_THREADS=1 python3 sparse_walsh.py examples/v29c 72 canonical

The example is the unchanged committed v29c circuit at repository revision
57e99b97dd2dd6c19fab3f7d706eaaaa9f165610. No remote access is needed to run.

Expected result:
    acceptance = 0.5074319721707059
    1-F        = 0.00006343913669754646

The audited implementation took 27.94 seconds for all 73 contractions in this
environment (acceptance plus the 72 nonzero decoder terms). Machine-dependent.

Method
------
1. Use invertible detector row XORs to turn dependent reduced projectors into
   identity projectors. Their fault-sensitive parity constraints remain present.
   In v29c, replace detector row 38 by row 38 XOR row 17, reducing the active
   non-Clifford kernel from five projector bits to four.
2. Fourier-transform the non-Clifford kernel. Only 244 acceptance entries and
   1145--1146 observable entries survive its numerical zero cutoff.
3. Condition on these sparse kernel assignments. They form a batched selector
   dimension; eliminate the remaining detector variables exactly. The remaining
   width is 9 on v29c, instead of dense width 26 before row reduction.

Validation receipts
-------------------
v23h_c2c9:
    original dense evaluator: 260.69 s
    sparse evaluator:          18.87 s (13.81x in these recorded runs)
    conditional loss: 7.026186740706895e-5
    largest difference over all 73 contraction values: 2.78e-16
    conditional-loss difference: 1.03e-16
v29c:
    sparse without row reduction: 51.59 s
    sparse with row reduction:    27.94 s
    score difference between these implementations: 1.10e-16
    repository's three-seed MC mean: 6.3451e-5
    largest bucket with row reduction: 1,173,504 float64 values (9.39 MB)

Numerical scope
---------------
There is no fault-order truncation or Monte Carlo. Coefficients below 1e-12
in the computed Fourier kernel are omitted; the sum of their absolute values,
divided by 2^kernel_bits, bounds their contribution to each contraction because
every noise characteristic factor has magnitude at most one. The output also
bounds the resulting conditional-loss error; on v29c it is about 1.06e-14.
This bound concerns cutoff error in the computed coefficients. It is not an
interval-arithmetic certificate of all floating-point roundoff.

Frontend scope
--------------
This portable independent frontend is for the validated zero-logical-frame,
no-explicit-POSTSELECT, H/CX/T/Tdg/reset/measurement family with every barrier
covering all used qubits. It rejects explicit frames/postselection, non-diagonal
reduced projectors, nonzero reference values, and more than 20 rotations.
It does not replace the official format, correctness, acceptance or speed gates.
For general circuits, reuse the sparse contraction with the repository's full
EVAL.Model/Engine and generalize the kernel builder as needed.

Provenance
----------
Basis and Engine definitions: repository work/lanes/EVAL/model.py and engine.py
at 57e99b97dd2dd6c19fab3f7d706eaaaa9f165610.
Independent integer-Pauli frontend: earlier review's full_single_audit.py.
Official native-X folding and scheduling/noise: judge_subset contains unchanged
files from SNUQuantums/snu-qff2026-problem at
76fe47c0324f1c1f8b72a7d55af200e88043b522. Its MIT license is included.

This is a local review artifact. It was not pushed, submitted, or run on the
team's remote machines.
