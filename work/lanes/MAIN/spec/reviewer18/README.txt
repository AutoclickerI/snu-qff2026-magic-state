QUANTUMN LARGE-JUMP STUDY

Start with REPORT.txt. PROOF.txt contains the full mathematical reduction.
PHYSICAL_REVIEW.txt records the separate coverage audit.

Reproduce the new channel certificate (Python standard library only):
  python penultimate_bound_certificate.py

Reproduce the independent matrix calculation (NumPy required):
  OPENBLAS_NUM_THREADS=1 python verify_penultimate_dense.py

Reproduce the C4-to-Steane terminal algebra and exact finite-p tail (standard library):
  python c4_steane_tail.py

Reproduce the finite static tile-packing check (standard library):
  python c4_tile_geometry.py

Reproduce current-v37g chronological noise counterfactuals:
Use your own quantumn checkout at commit
bb98bed0e695e8c94e45aca4088c80a95a7cb98b and its Python/NumPy2 environment.
  OPENBLAS_NUM_THREADS=1 python counterfactuals.py --repo /path/to/quantumn --circuit /path/to/quantumn/work/lanes/MAIN/v37g.qasm --out-dir local_cuts --processes 4
This uses Linux multiprocessing fork. Reduce --processes if memory is limited.
The source circuit/evaluator are referenced by commit and hashes, not duplicated.

These scripts write result JSON files in this extracted directory (or --out-dir).
They perform no remote operations, source-repository mutations or submissions.
No official xtim check or full noisy preparation of the C4 architecture was run.
The new bound concerns a conditional expectation, not a finite-shot score.
The ideal-boundary C4 tail is not a standalone admissible submission.
Counterfactual noise removal is diagnostic and cannot be submitted.

The exact certificate and numerical verification are distinct:
- rational/integer arithmetic certifies the extracted finite channel problem;
- the physical proof establishes why it applies to the inspected judge;
- the independent dense implementation checks the mathematical calculation
  using a different representation, with ordinary floating-point error.

SOURCE_MANIFEST.json records reviewed source identities and deliverable hashes.
