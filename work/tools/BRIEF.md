<task>
Lane TOOLS (P118 in docs/PLAN.md) of our SNU QFF2026 hackathon entry (fault-tolerant Steane |T_L> on a 6x6 grid,
scored by conditional 1-F). Read docs/GOAL.md (G2), docs/PLAN.md ("How lanes run", P118), docs/reference/circuit.md
("Evaluators", "Search machinery") and docs/RESOURCES.md first.

Problem: every lane copies the evaluator and helpers into its own dir, so fixes do not propagate (MERGE's committed
write_stem lagged its live fix that keys stems by QASM plus ordered data_qubits), result caches are keyed
inconsistently, and only MERGE's trained detector basis (work/lanes/MERGE/sparse_v37/basis_warm.json) prices v37h-family
circuits in 5-7 s; MAIN's evaluator (work/lanes/MAIN/sparse/) takes 150-350 s on the same circuits.

Build one shared, versioned tool set in work/tools/ (package dir work/tools/qtools/, tests in work/tools/tests/):
1. Stem identity: write_stem(qasm_text, data_qubits, outdir, prefix) -> stem path named
   <prefix>_<first 16 hex of sha256(QASM)>_d<ordered outputs>; idempotent; JSON holds data_qubits (+ optional source);
   identity(stem) -> (qasm sha256, ordered outputs). Same QASM with another output order is a different stem.
2. Pinned evaluator: one copy of the all-orders evaluator (start from work/lanes/MAIN/sparse/sparse_walsh.py and the
   files it imports; diff against MERGE/sparse_v37 and EARLIER's copy, and take their correctness and speed fixes
   only after showing identical losses on the test circuits). EVALUATOR_VERSION = sha256 over its source files.
3. price(stem, processes) -> {loss, acceptance, seconds, width, evaluator_version, qasm_sha256, data_qubits,
   basis}; a result cache under work/tools/cache/ (gitignored) keyed by (qasm sha256, ordered outputs, evaluator
   version); never a hit across keys; atomic writes; safe under concurrent processes on one host.
4. Warm-basis registry: merge MAIN's and MERGE's saved bases into one registry; price() replays all saved bases and
   searches only above the current width threshold; a newly trained basis is added atomically under a file lock.
   Show that warm and cold prices agree to 1e-15 relative on v37h and v37i, and report the speedup.
5. Validity: raw correctness (six noiseless output stabilizers +1, the organizer's exact check; find how lanes call it,
   e.g. EARLIER's candidate JSONs carry a "raw" block), judge gates_ok and judge seconds at 1e6 shots via
   work/fast_check.py, exact A >= 0.5002.
6. Policy: expected_key_delta(L_new, L_inc, t_new, t_inc) = (L_inc - L_new) - 1.1e-7 * log2(t_new / t_inc), and
   is_finalist(...) implementing circuit.md's single promotion policy (lowest exact L at A >= 0.5002, raw-valid,
   gates_ok, positive expected-key delta, judge time <= 20 s per 1e6 shots at one process).
7. Host pinning: a script that rsyncs work/tools to owl, tom, jerry, hippo and sunfish (rsync -a --exclude
   .submit_credentials, identical absolute paths, excluding cache/) and verifies EVALUATOR_VERSION on each (owl via
   docker, command in RESOURCES).
8. Tests (run with the venv python, e.g. python -m pytest work/tools/tests or plain asserts): exact reproduction of
   v37h (3.611954991494179e-5, 0.5015489333258328) and v37i (3.591182404095001e-05, 0.5003576309837844) from
   work/lanes/MAIN; stem identity and output-order regression; cache-key invalidation when the evaluator changes;
   policy examples; a raw-invalid circuit is rejected (reviewer 16's case: H T^4 H = X on one output keeps decoded loss
   0 and fails raw correctness).
Target: a v37i-family single-edit candidate prices in <= 10 s at one process; a cache hit in < 0.1 s.
Done when the tests pass, work/tools/README.md (at most 40 lines) shows usage, and a short REPORT.md states what was
verified. Lanes adopt it at their next restart; do not edit any file outside work/tools.
</task>

<compute>
zebra at most 4 processes; one remote host at a time for the pinning check, at most 2 processes there.
</compute>

<action_safety>
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- No submission, no git commit or push. Write only under work/tools; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Never signal, stop or kill a process you did not start (contest racers included). If a host is over its core count,
  shrink your own jobs and record it in REPORT.md.
- Do not use spawn_agent or any sub-agent.
</action_safety>
