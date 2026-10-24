# DK — Daguerre–Kim two-block RM15 → Steane

The complete DK protocol is valid grid-free, but its direct retained-output
version fails the contest acceptance gate under STANDARD.  The best measured
grid-free variant is still above the `6e-5` grid-search trigger, so no 6×6
embedding was attempted.

## Protocol reconstruction

`[dk2410.07327.pdf](dk2410.07327.pdf)` is the downloaded arXiv:2410.07327v3
source.  `[build.py](build.py)` transcribes Figs. 4–7 and implements the
logical sequence in Fig. 3:

1. Prepare RM15 `|+̄⟩` with the 25-CX Fig. 5 encoder, the seven-CX logical-X
   verifier, and the two Fig. 7 plus two Fig. 6 flagged checks.
2. Apply transversal `T/T†` (15 gates).
3. Prepare a verified Steane `|0̄⟩` with Fig. 4 (11 CX), apply the seven
   RM15→Steane transfer CXs, and measure all RM15 wires in X.
4. Postselect the RM15 flags/syndromes and declare the RM15 logical-X parity
   as the Steane logical-Z output frame.

The canonical artifact is `[dk_paper.qasm](dk_paper.qasm)` with metadata and
noiseless proof in `[dk_paper.json](dk_paper.json)`.  It has 100 CX, 15 T/T†,
26 active qubits, 31 measurements, and 20 deterministic detectors.  The
judge's format/class/correctness checks pass with only adjacency bypassed in
process; the circuit is not grid-adjacent.

### Paper metric

`[paper_metric.py](paper_metric.py)` uses the paper's uniform D1/D2 model at
`p=1e-3`, no idle noise, source postselection, and an ideal Steane decoder.
The paper's final X/Y tomography is represented by one D1 channel on each
output wire immediately before that ideal decoder.  The 100-million-shot,
three-seed result is:

| quantity | measured | paper |
|---|---:|---:|
| error-corrected 1−F | **4.81922e-5** | `4.6e-5 ± 1.6e-5` |
| acceptance | **0.826829** | about `0.84` |

Per-seed rows are in `[dk_paper_paper_metric.json](dk_paper_paper_metric.json)`.
This reproduces the paper's reported regime and uncertainty.  The published
polynomial's leading corrected term is `25.5 p²` (about `2.44e-5` at `p=1e-3`);
that fit is a source claim, not the contest score.

## STANDARD grid-free results

All contest scores below use the judge's STANDARD noise, the judge decoder,
`1e8` shots per seed, and seeds 0/1000/2000.  Exact second-order values come
from `score.py`/`exact2.py`; they are screens, not replacements for MC.

| artifact | CX | active | exact 1st | exact 2nd | MC mean 1−F | acceptance | result |
|---|---:|---:|---:|---:|---:|---:|---|
| `[dk_paper.qasm](dk_paper.qasm)` | 100 | 26 | 0 | 9.94854e-4 | **1.56683e-3** | **0.378112** | fails acceptance |
| `dk_steane.qasm` (verified output round) | 148 | 35 | 0 | 4.77244e-5 | 4.15991e-4 (10M screen) | 0.274927 | fails acceptance |
| `[dk_noflag_PA_alap.qasm](dk_noflag_PA_alap.qasm)` (best) | **105** | **28** | ~0 | **6.41495e-5** | **9.02257e-5** | **0.615567** | passes |

The best per-seed official-style rows are in
`[dk_noflag_PA_alap_mc_score.json](dk_noflag_PA_alap_mc_score.json)`:

| seed | 1−F | SEM | acceptance |
|---:|---:|---:|---:|
| 0 | 9.067645e-5 | 1.08114e-6 | 0.615595 |
| 1000 | 9.007766e-5 | 1.07413e-6 | 0.615580 |
| 2000 | 8.992308e-5 | 1.07575e-6 | 0.615526 |

The canonical rows are in `[dk_paper_mc_score.json](dk_paper_mc_score.json)`.
The best variant removes the Fig. 4 Steane flag, keeps only the PA source
check, appends the verified A/B/C Steane output round from
`[build_round.py](build_round.py)`, and schedules all operations ALAP with
`[schedule_alap.py](schedule_alap.py)`.  Removing all source checks and then
adding PA was the best tested acceptance/score tradeoff; the other one-check
and two-check variants are retained as `dk_noflag_*` artifacts.

### Region split for the best variant

`[dk_noflag_PA_alap_regions.json](dk_noflag_PA_alap_regions.json)` uses
100 million shots at seed 0.  “Tail” is the full noise after the last two
data CX operations plus data idle channels; “rest” is every other channel.

| enabled noise | exact 2nd | MC 1−F | acceptance |
|---|---:|---:|---:|
| tail only | 2.56667e-5 | 2.58804e-5 | 0.990712 |
| rest only | 3.43436e-5 | 6.09344e-5 | 0.621324 |
| all | 6.41495e-5 | 9.02257e-5 (3-seed mean) | 0.615567 (3-seed mean) |
| all-order mixed residual | — | 3.41099e-6 | — |

The best artifact passes the in-process judge checks in
`[judge_limits.json](judge_limits.json)`: 105 CX, 28 active qubits, 87
measure/reset operations, 18 deterministic detectors, noiseless fidelity 1,
and format/class/correctness all pass with adjacency disabled.  It is not a
grid circuit.

## Grid decision and reproduction

The best grid-free STANDARD mean, `9.02257e-5`, is above `6e-5`; therefore the
conditional grid-native RM15 encoder search was not started.  Routing the
canonical 100-CX all-to-all circuit would not answer the stated trigger and
would add the known idle/routing penalty.

Re-run the core measurements from this directory with:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/jihoon/competitions/quantumn/.venv/bin/python build.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/jihoon/competitions/quantumn/.venv/bin/python build_noflag_checks.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/jihoon/competitions/quantumn/.venv/bin/python paper_metric.py dk_paper --shots 100000000 --procs 8
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/jihoon/competitions/quantumn/.venv/bin/python score.py dk_noflag_PA_alap --mode mc --shots 100000000 --procs 8
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/jihoon/competitions/quantumn/.venv/bin/python regions.py dk_noflag_PA_alap 100000000 8
```

Every scored QASM has a JSON `data_qubits` entry.  `verify_limits.py` and the
`noiseless` fields in the JSON files use the judge's own exact correctness
engine; no judge source or credentials were changed or read, and no grid
submission was made.
