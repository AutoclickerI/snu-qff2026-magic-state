# QFF2026 hackathon entry

Our circuits for the SNU Qiskit Fall Fest 2026 main hackathon: prepare the Steane-code magic state
|T_L⟩ on a 6×6 nearest-neighbour grid with the lowest judged infidelity
([problem](upstream/snu-qff2026-problem/problem.md), [site](https://snuquantums.github.io/snu-qff2026/hackathon.html)).

- Agents start at [AGENTS.md](AGENTS.md). Goal, rules and state are in [docs/](docs/).
- Submitted and candidate circuits: `work/submissions/<name>.qasm` plus `.json` (`data_qubits`, score,
  source). Results are in [docs/SOTA.md](docs/SOTA.md).
- Setup and every tool command: [docs/RESOURCES.md](docs/RESOURCES.md) "Setup".

Quick check of a circuit at the official setting (bit-identical to the server, ~10 s):

```
cd work && ../.venv/bin/python fast_check.py submissions/v35a_r188.qasm submissions/v35a_r188.json
```
