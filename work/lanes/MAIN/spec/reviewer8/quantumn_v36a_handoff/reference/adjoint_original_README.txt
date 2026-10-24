FINITE-p DIAGNOSTICS FOR THE V30F REVIEW
=====================================

adjoint_ablation.py computes every original channel's perfect-noise
counterfactual with one reverse contraction per observable. It does not remove
the underlying physical gate. Run from the extracted bundle root:

    python3 audit/review5_adjoint/adjoint_ablation.py

Python 3.12 and NumPy 2.3.5 were used. The script uses the included independent
frontend and official scheduling/noise subset. It writes a full 73-moment
receipt, v30f_adjoint_72.json.

Recorded result: 477 channels, 103.6512142 seconds including 12 independent
direct counterfactual moment checks. Baseline A=.5275245061355753 and
L=5.8937742042181006e-5 reproduce the original full score. The maximum discrepancy
against those direct counterfactual contractions is 2.0134e-16; a separate
random tensor test gives 2.2205e-16. These are numerical consistency checks,
not an interval arithmetic guarantee.

Let A be acceptance and N=A L the unnormalized loss numerator. If lambda_j
multiplies the current error probability of channel j, every unnormalized
observable, including A and N, is affine in lambda_j while other channels
remain fixed. Therefore:

    A_off,j = A - dA/dlambda_j
    N_off,j = N - dN/dlambda_j
    L_off,j = N_off,j / A_off,j

This exact one-channel intervention is not a small-p or low-order expansion.
Do not add its per-channel reductions: interactions are counted repeatedly.
Do not interpret a noiseless-channel diagnostic as an executable circuit.
The reverse-pass implementation divides by positive factors; it explicitly
rejects factors with zero or negative entries. The present p=.001 meets that
condition. Sparse-kernel cutoff and floating arithmetic limitations remain.

The strongest seven single-channel effects are the final data idle channels:
making one perfect reduces L by approximately5.27e-6 to5.30e-6. Another large
effect is the long aggregated q10 idle (channel221), with reduction5.092e-6.
The A-encoder CX1->2 (channel371) has hypothetical reduction3.423e-6.
These diagnostics identify targets; they do not show those changes are legal.

Signature-image merging can precede the reverse pass. If a rank-r merged
image has c=1-2^(-r), Lambda=product(lambda_i), and
p_eff=c(1-Lambda), removing source channel i changes it by

    delta p_eff = c(Lambda - product_{j!=i}(lambda_j)).

An unnormalized observable is affine in p_eff. Retaining the source factors
therefore permits exact recovery of individual interventions after merging.
The merged+adjoint combination is derived, not benchmarked in this bundle.

SCHEDULE-SPECIFIC TAIL BOUNDS
----------------------------
Run:

    python3 audit/review5_adjoint/tail_schedule_bound.py

This standalone standard-library script handles unequal terminal idle counts.
For n_i protected-by-nothing terminal ticks on physical output i, it forms
q_i=3/4[1-(1-4p/3)^n_i]. It enumerates all4^7 Pauli errors exactly as rational
weights and optimizes over all64 input syndrome sectors and all logical Bloch
vectors. Hence pre-biasing the input or choosing a different prefix cannot
evade the certified bound for that fixed terminal channel.

For seven equal idle counts:
  one tick:    L >= .000011625247
  two ticks:   L >= .000046274265
  three ticks: L >= .000103609774
  four ticks:  L >= .000183298210

Rounded certificates are rational inequalities. More precise decimal values
are in tail_schedule_bound.json. The heterogeneous example is illustrative,
not an actual measured circuit.

Only independent terminal noise that cannot be observed by any remaining
accepted record can be factored this way. Do not apply the bound to arbitrary
prefix or ancilla-noise ablations. No Monte Carlo seed/sample lower bound is
claimed. The broader universal two-tick argument is included separately in
audit/subthreshold_bound/PROOF.txt for context; it is previous work, not a new
physical optimization from this review.
