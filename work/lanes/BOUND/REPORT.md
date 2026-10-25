# BOUND — reviewer 14's strengthened universal floor

**Verdict: confirmed for every admissible circuit under the inspected STANDARD judge.**
The extracted-channel optimum is **L* = 1.36578507905366540835e-5**.
An exact rational certificate proves **L >= 0.00001365785079053665**;
in particular reviewer 14's rounded-down **L >= 1.3657e-5** is correct.
Scope: true expected conditional decoded infidelity at p=1/1000, not a finite
1e8-shot realization or a selected seed-0 draw. This is not an attainable-circuit claim.

The existing audit and reviewer 11 code were copied here unchanged and run with
`.venv/bin/python -I`; their JSON results agree byte for byte. Both reproduce
**1.16202963892066882044e-5**; the legacy matrix check differs by **3.63e-16**.

Proof sketch (full derivation and source line references: [PROOF.md](PROOF.md)):

1. Let T be the global last native tick. Final output measurements/resets or
   untouched outputs cannot pass noiseless target fidelity: they leave a separable
   output, whose target fidelity is <= 1/2, far outside the judge's 1e-9 tolerance.
2. A final output–output CX already costs >= 3.33328885923969e-4, optimized over
   all input states and checked separately for all 21 pairs by the existing code.
3. Otherwise extract independent D1(q), q=p/5, just before T on **all outputs
   and all final-CX helpers**. D2=(D1(q) tensor D1(q)) o R has nonnegative residual
   weights (224745025,9,14993)/224880016, with multiplicities (1,6,9).
   This covers shared penultimate CXs. Idle/1q/post-measurement D1(p) also factors q;
   reset and first-use preparations factor q using residual flip probability 13/14996.
4. A final helper is discarded. Its X/Y errors propagate X when it controls the
   output; its Z/Y errors propagate Z when it is the target. Keep these errors.
   The three local tails are D1(p+q-4pq/3), D1(p-16p²/75) o B_X(2p/15), and
   D1(p-16p²/75) o B_Z(2p/15), where B_A(r) applies Pauli A with probability r.
5. All remaining measurements are disjoint from the extracted factors, so the
   factors remain independent after conditioning. Logical Pauli frames commute
   with the tail. Arbitrary residual states, correlations and logical bias are allowed.
6. Maximize the actual decoded-fidelity observable over all 64 two-dimensional
   syndrome sectors. The 2,187 terminal assignments form 60 GL(3,2) orbits;
   the certificate also passes an independent integer check of all 2,187 directly.

The unique minimizing assignment in this relaxation is **seven simultaneous
CX helper→output gates**, with distinct unmeasured helpers and zero input syndrome.
The logical input is the maximizing Bloch direction of that sector. No full
6×6 preparation attaining this relaxed optimum has been constructed or asserted.
Six helper→output plus one reversed CX gives 1.3870044320888314e-5;
all idle/local endings give 1.6721030306692441e-5; all reversed give 1.5697287859570993e-5.

The conservative measured-partner floor is **2.2735790278341725e-5**:
**9.0779394878050713e-6 higher**, or **66.4668% above** the universal floor.
Using its exact instrument factor q0=(2p/5)/(1-8p/15) gives 2.2742699650371855e-5,
a gap of 9.0848488598352005e-6. Both round to the cited 2.274e-5.

Certificates and reproduction:

- [strengthened.py](strengthened.py), [certificate.json](certificate.json),
  [summary.json](summary.json): rational channel identities, orbit coverage and all sector moments.
- [verify_certificate.py](verify_certificate.py), [verification.json](verification.json):
  independent 256-bin integer convolution; **139,968** exact sector inequalities,
  no symmetry reduction; optimum bracket [1.365785079053665e-5, 1.365785079053666e-5].
- [matrix_check.py](matrix_check.py), [matrix_check.json](matrix_check.json): independent
  4×4 CX-noise construction and 128×128 decoder; all **7,680 eigenvalues** checked.
  Maximum spectral disagreement **9.44e-15**; optimum disagreement **2.65e-15**.
- [reproduce.sh](reproduce.sh): run on hippo with `bash work/lanes/BOUND/reproduce.sh`
  from the repository root. Uses one Python process and one BLAS thread at a time.
- `legacy_audit/`, `legacy_reviewer11/`: isolated copies, reproduced results and logs;
  [source_hashes.txt](source_hashes.txt): judge and legacy-code provenance.

Verified: legacy reproduction, exact factors, full assignment/sector coverage, numerical spectra.
Proved from source semantics: universality, including reset/first-use/measurement exceptions,
shared penultimate gates, postselection and frames. Unverified: attainability by a full circuit;
no Monte Carlo score or submission was run. Decision: retain noise on idle/local outputs too,
and distinguish a universal lower bound from the physical optimum. All writes stay in BOUND;
all calculations ran on hippo, single-process; no subagents, commits, pushes or submissions.
