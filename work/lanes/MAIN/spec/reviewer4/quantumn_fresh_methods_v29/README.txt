QUANTUMN FRESH METHODS / v29c REVIEW
===================================

Start with REPORT_KO.txt (Korean, complete analysis of all ten candidates).
Pinned repository: AutoclickerI/quantumn at
57e99b97dd2dd6c19fab3f7d706eaaaa9f165610.

This bundle contains independent local review experiments, not a new valid
contest submission. No new complete nearest-neighbour circuit beating v29c
has been demonstrated. Ideal identities, grid-free full-circuit experiments,
storage-only toy models and speculative synthesis methods are marked separately.

Requirements
------------
Python 3.12 and NumPy >=2.0 (tested with NumPy 2.3.5). No Stim/xtim needed for
these independent checks. The official judge still governs all submission gates.

Reproduce the full current-v29 expectation:
    cd evaluator
    OPENBLAS_NUM_THREADS=1 python3 sparse_walsh.py examples/v29c 72 canonical

Expected: A=0.5074319721707059, 1-F=6.343913669754646e-5.
The 72 argument requests 72 decoder observables plus acceptance (73 values).
The evaluator writes its output in its current working directory. Original full
receipts are protected from default output-name collisions in evaluator/receipts/.
Timings in receipts are machine-dependent observations, not universal guarantees.

Reproduce the complete grid-free bus probes:
    cd preparation
    OPENBLAS_NUM_THREADS=1 python3 clean_bus_round.py
    cd ../evaluator
    OPENBLAS_NUM_THREADS=1 python3 sparse_walsh.py ../preparation/bus_bus_r34 72 canonical

The builder recreates five full circuits and checks ideal correctness/singles.
They use an old v11 prefix, not v29c, and do not satisfy the 6x6 adjacency gate.
The bus suffix uses 35 cells; the full prefix+suffix uses all 36 physical cells.
Run the analogous evaluator command for bus_direct_r34 for the matched control.

Other checks
------------
architecture/: exact moving-check, dirty-bus, hybrid-uncompute identities;
two-private-port impossibility enumeration; graph-resource search and its
measurement-byproduct obstacle. Most scripts use only Python; uncompute uses
NumPy. Run scripts within that directory so sibling graph modules are found.

preparation/: clean-bus and encoded-Bell logical-branch certificates, rational
noise-channel identity, selective noisy storage toy, and the negative frame
admission screen. See preparation/README.txt and AUDIT_NOTES.txt. The latter
records the original workspace paths; use the replay scripts here instead.
The pair-screening script may take materially longer than the small identities.

evidence/phase_byproducts.json is the recorded current-v29 byproduct screen.
Candidates 7, 8 and 10 include methods yet to be implemented or completed;
their proposed full physical gains are not measured results.

Frontend limits
---------------
The portable evaluator rejects explicit FRAME and POSTSELECT annotations and
non-diagonal reduced projectors, assumes all-used-qubit barriers, and handles
the validated current H/CX/T/Tdg/reset/measurement family. It cannot evaluate
candidate 4 as-is. Extend and validate its frontend, or use the full official
model, before pricing a new family. Do not remove assertions to force a result.
The Fourier-cutoff error bound does not certify all floating-point roundoff.

Provenance
----------
The unchanged official judge subset has its MIT license in evaluator/judge_subset/.
SOURCE_MANIFEST.json records source URLs and hashes of inspected source files.
FILE_HASHES.json hashes the included artifacts (excluding itself).
No repository push, official submission, or remote-machine job was performed.
