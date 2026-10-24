# Detector-only factorization audit on v36c

Source: `AutoclickerI/quantumn@42afa8ff01c3999444336f5bb2fe473c1475d6f4`.
Evaluator: the pinned `work/lanes/MAIN/sparse/{frontend,sparse_walsh}.py`.
Candidate: pinned `work/lanes/MAIN/v36c.{qasm,json}`.

## Result

The proposed cheap way to recover acceptance **does not expose an opportunity
on this incumbent**. There are 552 independent effective noise channels and
72 detector conditions. An ordinary channel-support graph has no nontrivial
detector-only component. A stronger binary-matroid direct-sum decomposition
also has no such component, including after arbitrary invertible changes of
detector coordinates under the stated channel model.

There are **57 completely unobservable channels**, leaving 495 channels in
the relevant core. Their factors are mathematically one for acceptance and
all 72 scored observables. Removing these factors from the *evaluator* is
exact. This is not authorization to delete the associated physical gates,
measurements, or qubit lifetimes, and no wall-clock speedup was measured.

The audit should therefore be cited as a negative screen, not included as a
new physical-loss improvement or as newly recovered acceptance. The previous
q16/c43 acceptance-only example has already been integrated into the team's
search history; this test found no general disconnected counterpart left
in v36c.

## Exact sufficient condition

Each independent physical noise channel is a categorical random variable.
Its atoms carry detector-flip vector `d`, rotation-flip vector `s`, and
observable-sign vector `e`. Atoms of one depolarizing channel are mutually
exclusive outcomes of that channel, **not independent Bernoulli faults**.
Every such channel must remain intact for this certificate.

Suppose detector space is a direct sum `V_core ⊕ V_aux`, the ideal kernel has
support only in `V_core`, every channel affecting rotations or any scored
observable acts only in `V_core`, and all remaining channels are confined to
one of these subspaces. Then total detector syndrome has the unique split
`d = d_core + d_aux`. Its zero condition is equivalent to both components
being zero. Core and auxiliary channel variables are independent. Therefore

    A = A_core A_aux
    N = N_core A_aux
    L = N/A = N_core/A_core

for `A_aux > 0`. Removing the *auxiliary detector constraint* raises or keeps
acceptance and leaves conditional loss exactly unchanged. Physical operation
removal requires a separate analysis of timing, noise, and state preparation.

The implementation conservatively places each nonidentity ideal-projector
coordinate in the core. This can over-connect the core, but cannot produce a
false independence certificate. The scored `e` test uses every nonzero-weight
observable character from `eng.keys`, not an informal logical-X/Z label.

## Why the second test is stronger

The first script joins detector coordinates touched by each entire channel.
This condition depends on the detector basis and can miss hidden direct sums.

The second script builds a binary vector matroid on all detector signature
vectors. Gaussian elimination produces a basis and fundamental circuits.
Each fundamental circuit joins its participating channel owners; all atoms
of one channel share one owner. Active ideal-projector axes and every channel
with a relevant `s` or `e` effect are joined to the core. Separate surviving
components would then span independent direct summands and satisfy the
factorization condition above.

On v36c the rank is 72. All nonzero relevant components join the 495-channel
core; the remaining 57 channels have zero detector, rotation and scored-sign
effects. No nontrivial auxiliary event remains to remove.

This negative result is **not** a general proof that no acceptance-only edit
exists. It does not exhaust identities arising from special numerical channel
probabilities, refactorizations of one channel into several independent
latent channels, exact cancellation in the accepted quantum kernel, or
interventions that change the circuit. It closes only the cheap graph/direct-
sum certificate described here.

## Reproduction

From `/workspace/scratch/a4b592a94a64`:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 audit/review6_validation/venv/bin/python audit/review10/factorization/census.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 audit/review6_validation/venv/bin/python audit/review10/factorization/matroid_census.py
```

Receipts are `census.json` and `matroid_census.json`. No candidate circuit was
modified, no official submission was made, and no remote job was started.
