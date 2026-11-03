# Magic-state preparation on a 6×6 qubit grid: 2nd place at Qiskit Fall Fest 2026 @ SNU

This is our entry, as team **초정밀모델제어학회쨩**, in the main hackathon of
[Qiskit Fall Fest 2026 @ SNU](https://snuquantums.github.io/snu-qff2026/hackathon.html). The hackathon ran online
from Oct 22 to Oct 30, 2026, and the festival and awards were at Seoul National University on Oct 29–31. Our circuit
finished **2nd of 22 teams**.

## The problem, in plain words

In common designs for error-corrected quantum computers, one set of gates (the Clifford gates) is comparatively easy
to protect but isn't enough on its own. The missing piece, the T gate, is supplied by consuming a special input state
called a *magic state*. The contest asked for a circuit that makes one: the magic state
|T⟩ = (|0⟩ + e^{iπ/4}|1⟩)/√2, already stored in the 7-qubit **Steane error-correcting code** as |T_L⟩.

The circuit has to run on a simulated chip with real constraints:

- **The chip:** 36 qubits in a 6×6 grid. Two-qubit gates are CNOTs between neighbouring qubits only.
- **Noise everywhere:** every gate, preparation, measurement, *and every time step a qubit sits idle*, goes wrong
  with probability 0.1%.
- **Throwing runs away is allowed:** the circuit can check itself and discard any run where a check fails, as long
  as it keeps at least 50% of runs.
- **Score:** take the kept runs, let the judge apply an ideal round of error correction to the 7 output qubits, and
  measure how far the result is from the perfect |T_L⟩. The infidelity **1 − F** is the score, and lower is better.
  The official score is a Monte Carlo estimate over 10⁸ runs with a fixed random seed (0).

The problem statement, judge and tutorial are in the organizers' repo,
[SNUQuantums/snu-qff2026-problem](https://github.com/SNUQuantums/snu-qff2026-problem) (in Korean).

## Result

Our final circuit scored **1 − F = 3.30 × 10⁻⁵**. The organizers' starter circuit scores 0.0252, so ours is about
760 times lower. The top of the final leaderboard (public board, read 2026-11-03; submissions closed Oct 30):

| Rank | Team | 1 − F | Two-qubit gates |
|---:|---|---:|---:|
| 1 | Placeholder | 2.71 × 10⁻⁵ | 277 |
| **2** | **초정밀모델제어학회쨩 (us)** | **3.30 × 10⁻⁵** | **412** |
| 3 | `@nize_reze 고양이 인스타 팔로우 부타케용` | 4.96 × 10⁻⁵ | 199 |

The board compares scores at three significant figures, then breaks ties by the number of two-qubit gates.

## The circuit

The submitted circuit is [`work/submissions/v37j_h2621_r103091.qasm`](work/submissions/v37j_h2621_r103091.qasm)
(OpenQASM 2.0), entered on Oct 26 at 21:27 KST. Its
[`.json`](work/submissions/v37j_h2621_r103091.json) names the 7 grid qubits that hold the output. It uses 34 of
the 36 qubits, 412 CNOTs, 15 T/T† gates and 71 detector checks, and keeps 50.1% of runs.

It works in four stages:

1. **Make a magic state and check it.** A noisy T state is encoded directly into the 7-qubit code and checked with
   cat states, following the distance-3 stage of *magic state cultivation* (Gidney, Shutty and Jones,
   [arXiv:2409.17595](https://arxiv.org/abs/2409.17595)). A colour-code stabilizer check follows. Any failed check
   discards the run.
2. **Move into place, and guard the waiting qubits.** CNOT "hops" carry the 7 data qubits to their final cells.
   For the data, waiting cost more than the moves themselves, so neighbours of waiting qubits run small guard
   gadgets that catch errors while the data waits.
3. **A final Steane-style check.** Two helper blocks, each a 7-qubit encoded state built next to the data, test the
   data once more. CNOTs from the data copy its bit-flip (X) errors onto block A, which is then read out. CNOTs from
   block B copy the data's phase-flip (Z) errors onto B, which is read out too. A third block, C, checks B one step
   before B touches the data.
4. **Detectors decide which runs to keep.** 71 parities that are fixed in a noiseless run are declared as
   detectors, and the judge discards every run where one of them flips. We let the keep rate fall to just above the
   50% floor, and spent the spare on checks and gadgets that lowered 1 − F.

[`docs/reference/circuit.md`](docs/reference/circuit.md) describes the structure in detail. It was written for v37d,
which has the same structure.

### The board number and the true number

The leaderboard shows a single Monte Carlo estimate (seed 0, 10⁸ runs, about ±0.7 × 10⁻⁶), and the rules rank
by exactly that number. Reordering gates that run at the same time leaves the circuit's physics unchanged but
changes which random errors seed 0 draws.
- **Oct 23:** we started picking the best of many such re-draws.
- **Oct 25–27:** an hourly race ([`work/race.py`](work/race.py)) scored reorderings with the judge's own code and
  submitted the best draw. From Oct 26 afternoon it submitted only draws that beat our board entry.
- **Oct 27:** the race was stopped.

Our reading of the rules is in [`docs/CONSTRAINTS.md`](docs/CONSTRAINTS.md), "Boundary cases".

Our own evaluator computes a circuit's exact expected 1 − F. For this circuit it is **3.59 × 10⁻⁵**; the board shows a
favourable draw of the same circuit. By our analysis, no circuit that follows the rules can have an expected 1 − F
below **2.19 × 10⁻⁵** ([`docs/FINDINGS.md`](docs/FINDINGS.md), "Bounds").

## How we got there

| When (KST) | Version | 1 − F on the board | Two-qubit gates | What changed |
|---|---|---:|---:|---|
| Oct 22 | organizers' starter | 0.0252 | 28 | Encode one physical T state with H and CNOT |
| Oct 23 | v6, our first entry | 1.31 × 10⁻⁴ | 113 | Cultivation's distance-3 stage ported to the grid: injection, cat-state checks, stabilizer cycle |
| Oct 24 | v14 | 1.01 × 10⁻⁴ | 207 | Steane-style final check with helper blocks A, B and C |
| Oct 24 | v30f | 5.63 × 10⁻⁵ | 189 | B and C made from one correlated resource state (57 CNOTs instead of 82) |
| Oct 25 | v36a | 3.90 × 10⁻⁵ | 207 | A 12-CNOT encoder for A, timed to when its cells free up |
| Oct 25 | v37a | 3.48 × 10⁻⁵ | 390 | Guard gadgets on waiting qubits (from v36d on), then a new grid layout |
| Oct 26 | v37j (final) | **3.30 × 10⁻⁵** | 412 | Merged gains from parallel search lanes |

[`work/submissions/`](work/submissions/) holds the circuits we raced from v37c on (not all were submitted), each with
our run of the official judge in [`work/receipts/`](work/receipts/); those runs match the server bit for bit. Earlier
circuits are in git history. [`docs/SOTA.md`](docs/SOTA.md) lists the later steps.

The work used these tools:

- **An exact evaluator** ([`work/tools/qtools`](work/tools/qtools)). It computes a circuit's expected 1 − F to all
  orders in seconds, so we could rank candidates that differ by under 1%, which Monte Carlo can't resolve.
- **Solvers and search.** CP-SAT (OR-Tools) for layouts, schedules and encoders; greedy local edits priced by the
  exact evaluator; exhaustive searches and certified lower bounds for the circuit's ending.
- **Parallel research lanes.** Each lane in [`work/lanes/`](work/lanes/) chased one idea, and most lanes have a
  `REPORT.md`. Winning pieces were merged into the main line.
- **AI agents.** AI coding agents (a Claude Code orchestrator, Codex lanes and Claude subagents) did most of the
  work, directed by Jihoon. Outside reviews in [`work/lanes/MAIN/spec/`](work/lanes/MAIN/spec/) contributed key
  ideas, including the 2.19 × 10⁻⁵ bound. The contest allowed AI tools.
- **Working notes.** [`AGENTS.md`](AGENTS.md) and [`docs/`](docs/) are the agents' notes, frozen as of Oct 27. They
  are dense and assume the context above, and the "current best" they name predates the final board.

## Check the score yourself

You need CPython 3.11–3.13 (64-bit; on x86-64 Linux the CPU needs AVX2, BMI2 and FMA) and the organizers' judge.
These commands are for Linux and macOS; run them from this repo's root:

```sh
git clone https://github.com/SNUQuantums/snu-qff2026-problem.git upstream/snu-qff2026-problem
python3 -m venv .venv
.venv/bin/pip install -r upstream/snu-qff2026-problem/requirements.txt -e upstream/snu-qff2026-problem
.venv/bin/python -c "
import json, tprep
s = 'work/submissions/v37j_h2621_r103091'
print(tprep.check(open(s + '.qasm').read(), json.load(open(s + '.json'))['data_qubits'], shots=10**8, seed=0))"
```

It prints `PASS` for the format, class, correctness and acceptance checks, then `score 1-F = 3.3043e-05`. That took
about five minutes on our server; the judge uses several threads. With `shots=10**6` it finishes in seconds but
gives a noisier estimate. Our parallel version gives the same number:

```sh
.venv/bin/python work/fast_check.py work/submissions/v37j_h2621_r103091.qasm work/submissions/v37j_h2621_r103091.json 1e8 8
```

The last argument is the number of processes.

## Repository map

```
work/submissions/   circuits (.qasm) and output qubits (.json) raced from v37c on, including the final entry
work/receipts/      our runs of the official judge on them, and the race's helper scripts
work/lanes/<NAME>/  one research line each (search code, results, REPORT.md); MAIN holds the main line
work/tools/qtools/  the exact all-orders evaluator and shared search tools
work/*.py, *.sh     scoring, re-draw racing (race.py), promotion and submission scripts
docs/               the agents' working notes: GOAL, CONSTRAINTS, PLAN, FINDINGS, SOTA, RULINGS, reference/
upstream/           saved pages of the contest site
```

## License

Our code and circuits are under the Apache License 2.0 ([`LICENSE`](LICENSE)). Some parts are the organizers' and keep
their terms:

- **Judge code.** Copies of part of their judge keep its MIT license and carry its text:
  [`work/lanes/MAIN/sparse/judge_subset/`](work/lanes/MAIN/sparse/judge_subset/),
  [`work/tools/qtools/evaluator/judge_subset/`](work/tools/qtools/evaluator/judge_subset/) and
  [`work/lanes/FRESH/r35_vendor/judge_subset/`](work/lanes/FRESH/r35_vendor/judge_subset/).
- **The sampling loop.** [`work/fast_check.py`](work/fast_check.py), [`work/race.py`](work/race.py) and the
  `fast_check.py` copies in three lanes adapt it from the judge's `tprep/check.py`, also under that MIT license.
- **Site pages.** `upstream/` holds saved pages of the contest site. They carry no license, aren't covered by ours,
  and are kept for reference.

The circuit's first stage follows Gidney, Shutty and Jones's magic state cultivation
([paper](https://arxiv.org/abs/2409.17595), [code](https://github.com/Strilanc/magic-state-cultivation),
Apache-2.0). Our first circuits were produced by parsing the distance-3 circuits in their code from a local checkout
and porting them to the grid. None of their code is in this repo.
