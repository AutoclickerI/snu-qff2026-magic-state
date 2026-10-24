# WALSH all-orders evaluator

**status: validated on the exact2 judge model; finalist scores complete**

The evaluator is [`allorders.py`](./allorders.py). It uses `exact2.Eval` and
`Engine` directly, so channel probabilities, categorical Pauli outcomes,
fault signatures, projectors, decoder observables, and the rotation structure
are the judge model already used by `exact2.py`.

## Method and complexity

For each channel (c), the code builds the categorical characteristic factor

\[
\chi_c(w)=(1-q_c)+\sum_{f\in c}p_f(-1)^{w\cdot v_f}.
\]

The quantum numerator and acceptance functions are Walsh transformed on all
rotation-sign variables and on the nonidentity detector projectors. Identity
detectors still have Fourier variables: eliminating them enforces their noisy
detector bit to be zero. Decoder terms are contracted one character at a time,
so the 72 Pauli terms do not require a (2^{27}) dense quantum table.

The inactive detector variables are eliminated by deterministic min-fill
variable elimination. For a circuit with induced width (w), the largest
intermediate tensor is (O(2^{w+1})) doubles; the final quantum table is
(O(2^K Q)), where (K) is the number of rotation/projector variables and
(Q) is the number of decoder Pauli terms. The implementation accepts
(K\le23) and (w\le26), and raises an error before allocation for wider
circuits. Width 23 is the reviewer-3 v22/v23 case; v24 is width 26.

The returned score is the conditional judge score:

\[
1-F = N/A,
\]

where (N) is the accepted infidelity numerator and (A) is the acceptance.
Mutually exclusive Paulis from one channel stay in one factor and are never
treated as simultaneous faults.

## Validation

| check | result | status |
|---|---:|---|
| Brute-force subset: channels 0, 1, 2 of v22 (8 categorical outcomes) | acceptance difference (2.44\times10^{-15}); numerator difference (6.97\times10^{-16}); conditional-score difference (6.99\times10^{-16}) | verified |
| Low (p=10^{-4}), v22 all orders | (5.6096714658\times10^{-7}) | verified |
| Low (p=10^{-4}), exact2 second order | (5.43740\times10^{-7}) | verified |
| Low (p=10^{-4}), exact2 through third order | (5.6086426215\times10^{-7}); all-orders remainder (1.03\times10^{-10}) | verified |
| v22 seed-0 redraws (380 logs) | mean (7.24049376\times10^{-5}\pm5.63\times10^{-8}); all-orders (7.23645254\times10^{-5}) | verified |
| v23h_c2c9 redraw reference | requested 214-draw reference (7.0298\times10^{-5}\pm7.0\times10^{-8}); current log IDs r0--r213 give (7.02920178\times10^{-5}\pm7.12\times10^{-8}), and all 320 lines give (7.02717491\times10^{-5}\pm5.85\times10^{-8}) | verified, count discrepancy recorded |
| 1e8-shot seed-0 acceptance, v22 | judge (0.53390484), all-orders (0.53386030), difference (4.45\times10^{-5}) | verified |
| 1e8-shot seed-0 acceptance, v23h_c2c9 | judge (0.54097263), all-orders (0.54090296), difference (6.97\times10^{-5}) | verified |

The v23 tom log alone has 160 draws with mean
(7.02982669\times10^{-5}pm8.66\times10^{-8}), consistent with the supplied
214-draw reference. The first 214 redraw IDs have mean acceptance 0.5409084. Per-draw acceptance values in the redraw logs are rounded
to four decimals; the 1e8-shot checks above use `work/fast_check.py`.

## Finalist scores

All runs used `p=1e-3`, the QASM’s JSON data-qubit list, and four worker
processes. Runtime is model construction plus all Walsh contractions.

| circuit | width | all-orders (1-F) | acceptance | third-order value | runtime |
|---|---:|---:|---:|---:|---:|
| v24 | 26 | (6.6810473648\times10^{-5}) | 0.5005742922 | (6.5884766546\times10^{-5}) | 505.1 s |
| v23h_c2c9 | 23 | (7.0261867407\times10^{-5}) | 0.5409029584 | (6.9221039823\times10^{-5}) | 146.8 s |
| v22h_c2c9 | 23 | (7.2364525372\times10^{-5}) | 0.5338602967 | (7.1305956785\times10^{-5}) | 141.0 s |
| v23w_c2c9 | 23 | (7.0509562074\times10^{-5}) | 0.5426754119 | (6.9451376607\times10^{-5}) | 168.6 s |

## Usage

```bash
.venv/bin/python work/lanes/WALSH/allorders.py circuit.qasm \
  [--json circuit.json] [--procs N]
```

The command prints all-orders conditional `1-F`, acceptance, the exact
third-order truncation from the validated moments contraction, and runtime.

## Verified versus inferred

Verified: the factor construction uses the existing exact2 channel/fault
objects; categorical subset enumeration agrees at floating-point roundoff;
the low-(p) limit agrees with exact2 through third order; v22/v23 all-orders
values reproduce the reviewer’s reference values; and judge seed-0 acceptance
agrees within the expected (10^8)-shot binomial fluctuation.

Inferred: the evaluator is floating-point exact rather than an interval
certificate, and the width-26 guard is a measured computational boundary, not
a proof that every wider circuit is impossible. The current v23 log inventory
has 320 draws rather than the 214 stated in the task; both the supplied
reference and the current log aggregate are reported above.
