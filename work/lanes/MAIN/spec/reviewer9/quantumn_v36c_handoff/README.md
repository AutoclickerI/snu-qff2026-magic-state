# quantumn v36c implementation handoff

This package contains the current-source review, ten implementation candidates, a working evaluator optimization, and independently checked algebra and routed fragments for a rank-four fourteen-T phase construction. **It does not contain a new complete physical submission that beats v36c.**

Start with `REPORT_KO.md` for the full Korean analysis and `IMPLEMENTATION_AGENT.md` for the implementation brief. `TASKS.json` records each task's first experiment, success criterion, stopping criterion, and limits.

## Pinned inputs

| Input | Pin |
|---|---|
| quantumn | `42afa8ff01c3999444336f5bb2fe473c1475d6f4` |
| Historical TREP/TREP2 source | `a58eca7341a7b2c2272205ff689d4780bde11fd5` |
| Official judge | `76fe47c0324f1c1f8b72a7d55af200e88043b522` |
| v36c QASM SHA256 | `49ea05888f6f56f87eee49665f8275e3f0c30e199c67db7958f5318cc07bd3f8` |
| Review date | 2026-10-25 Asia/Seoul |

The final HEAD check also reviewed `e31cec14e20f5d9fec9da759ef0d61cd4a5358ab`: it adds only the v36b_r580 submission and receipt. The analyzed v36c and evaluator are unchanged. `LATEST_UPDATE.md` and `latest_update/` preserve the update and its schedule-equivalence check.

The independently recomputed baseline is **L = 4.1151559437773416e-5, A = 0.5027278379249299**. Its sparse-kernel omission bound on conditional loss is 1.1753492176688352e-14; this excludes floating-point roundoff. The separate one-million-shot, seed-0 official check passed format, class, ideal correctness, and noisy acceptance. Its sampled score is not the expected loss.

This is a selected source snapshot, not a full Git checkout. Upstream history and several publicly referenced live lanes are not included. `SOURCE_PROVENANCE.json` maps included original sources to their Git blobs and pinned URLs; it explicitly records source-list entries omitted from this focused package. `MANIFEST.json` covers all package payload files. `CHECKSUMS.sha256` additionally covers the manifest. These are integrity records, not digital signatures.

## Verify before running experiments

From the extracted package directory, with any compatible Python 3 installation:

```bash
python3 tools/verify_bundle.py
python3 audit/review10/factorization/check_phase_and_subgroups.py \
  --phase-dir audit/review10/physical \
  --output /tmp/quantumn_phase_subgroup_check.json
```

The first command verifies all file hashes, included Git blobs, Python syntax, JSON readability, the ten task IDs, and the baseline QASM pin. It does not import or execute the bundled project code. The second uses only the Python standard library: it rechecks all 64 phase families, all 15 rank-four fourteen-T supports, the zero-residual sign assignments, the exact rational phase-axis noise formula, and all 2,825 binary six-dimensional subspaces. Its input response extraction remains evidence from the circuit-analysis scripts; it does not independently extract that response from QASM.

## Install the evaluator environment

The recorded environment is Linux x86-64 with CPython 3.12. The `xtim` wheel in the lock file is specific to that platform and Python version; other platforms need a corresponding supported upstream build. The wheel itself is not bundled.

```bash
python3.12 -m venv /tmp/quantumn-review-venv
/tmp/quantumn-review-venv/bin/python -m pip install -r requirements.lock.txt
```

All commands below assume that interpreter or an equivalent installed environment. Four-worker evaluation uses POSIX `fork`; `--processes 1` avoids that parallel path.

## Run the implemented evaluator optimization

```bash
/tmp/quantumn-review-venv/bin/python audit/review10/search/evaluate_basis.py \
  --evaluator-dir quantumn_review10/work/lanes/MAIN/sparse \
  --stem quantumn_review10/work/lanes/MAIN/v36c \
  --output /tmp/quantumn_v36c_basis_result.json \
  --processes 4
```

The default certificate is `audit/review10/search/basis_width_probe.json`. The CLI reuses 32 saved row XORs after checking their semantic validity and comparing planning costs; it does not repeat the 19.6-second basis search. It retains the original coordinates if the proposal is incompatible or its min-fill cost is not better. A malformed certificate raises an error.

Recorded results on the exact pinned input:

- Contraction width: **11 to 9**.
- Min-fill work proxy: **5,636 to 1,911**.
- Largest actual bucket: **4,698,112 to 1,174,528** entries.
- All 73 moments agree with the original evaluator to a maximum absolute difference of **1.6653345369377348e-16**.
- One portable run took 9.084 seconds including planning on the review host. This is an observation, not a portable runtime promise.

`portable_eval.json` and `portable_eval_validation.json` preserve that run and its comparison. `basis_validate.json` preserves a separate ABBA experiment using a semantically identical extra-newline input. Do not combine those timings into a universal speedup claim. This optimization changes computation, not QASM, acceptance, or physical loss.

## Run the pinned official check

```bash
/tmp/quantumn-review-venv/bin/python audit/review10/validate_current.py \
  quantumn_review10/work/lanes/MAIN/v36c 1000000 0 \
  /tmp/quantumn_v36c_official_check.json
```

The generated wrapper imports `official/tprep`, whose sources are unmodified. The fourth optional positional argument sends the receipt outside this package. The existing receipt remains in `audit/review10/v36c.official_1000000_0.json`. This is a local check, not a competition submission.

## Physical construction evidence

| Evidence | Location |
|---|---|
| 64 phase families and rational noise screen | `audit/review10/physical/phase_family_certificate.json` |
| Fourteen-T sign choices | `audit/review10/physical/phase_sign_certificate.json` |
| Same-router, same-cell routing experiment | `audit/review10/physical/phase_route_certificate.json` |
| Minimum-CX fragment | `audit/review10/physical/phase14_min_cx.qasm.inc` |
| Minimum-depth fragment | `audit/review10/physical/phase14_min_depth.qasm.inc` |
| Exhaustive fragment replay receipt | `audit/review10/physical/phase_fragment_verification.json` |
| Three losing syndrome coarsenings and c43 control | `audit/review10/physical/coarsen_results.json` |
| Official checks for those controls | `audit/review10/physical/coarsen_official_receipts.json` |

The fragments require an encoded input and a verified enclosing circuit. They are not standalone QASM submissions. The historical coordinate target is 25; the independently extracted current-coordinate target is 31. Never mix the coordinate labels without an explicit basis map. Rank four establishes the phase operation's coordinate requirement, not deletion of a physical qubit, its preparation, measurement, or record contract.

The phase-only loss of about 7.79335e-7 includes only commuting phase-axis faults on hypothetical T gates. It omits every other error and is neither a full-circuit score nor an additive penalty to the current v36c loss.

## Lower bound and rules evidence

`official/problem.md`, `official/tprep`, `audit/review10/rules/AUDIT.md`, and `bound/PROOF.txt` contain the rule audit and terminal-noise argument. `bound/terminal_bound.py` and `audit/review10/rules/terminal_bound.py` provide rational checks. The verified universal expected-loss floor under the inspected STANDARD p=0.001 model is **L >= 1.162e-5**. The last-tick-only relaxation below 1e-5 omits required noise and does not establish attainability.

The official judge has a propagated-rank guard of 22, not a T-count cap of 20. The present sparse evaluator's T-count cap is an implementation restriction. Read the report's full rule matrix before relaxing other assumptions.

## Portability and provenance

Original receipts intentionally retain the absolute paths and timings of the runs that created them. Those strings document history; use the relative paths in this README for reproduction. Generated helper scripts use their own location or explicit CLI arguments. Two generated official-check wrappers were repointed to `official/`; the primary wrapper also accepts an output path. None of those changes edits the judge.

Running an evidence generator may rewrite its adjacent receipt; use a separate work copy if preserving this package's checksums matters. Verify the supplied bundle before experiments. The sparse baseline and evaluator are reference inputs, not an instruction to overwrite a newer live checkout.

Official code is distributed under its included MIT license. The official problem specification is attributed to Qiskit Fall Fest 2026 @ SNU organizers and follows the included `official/LICENSE-docs` notice. Pinned upstream links are in `SOURCE_PROVENANCE.json` and the report.
