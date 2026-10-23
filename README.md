# SNU Qiskit Fall Fest 2026 — Hackathon workspace

Deadline: **Fri 2026-10-30 12:00 KST**. Submit at https://snuquantums.github.io/snu-qff2026/hackathon.html
(team name + password + `data_qubits` + OpenQASM 2.0 file, ≤200 KB / ≤5,000 statements / ≤1,000 measure+reset;
one submission per team per hour).

## Layout

| Path | What |
|---|---|
| `upstream/snu-qff2026-problem/` | Official problem repo (clone at `76fe47c`). Keep it unmodified; `git pull` for updates. |
| `upstream/*.html` | Snapshots of the event pages (2026-10-23). |
| `work/` | Our circuits and scripts. |
| `.venv/` | Python 3.12 env: qiskit 2.5.2, stim 1.16.0, xtim 3.1.3+qff2 (official judge build), tprep 3.0.3 (editable from upstream). |

Jupyter kernel: `qff2026`.

## Commands

```bash
source .venv/bin/activate
python work/baseline.py          # example circuit, 1e6 shots + fault scan  (1-F = 0.0251615)
python work/baseline.py 1e8      # official setting, seed 0                 (1-F = 0.025172, ~20 s)
(cd upstream/snu-qff2026-problem && python -m pytest tests -q)   # judge self-tests: 41 pass
```

The official score is `tprep.check(text, data_qubits, shots=10**8, seed=0)` on the submission text;
the server runs the same code.

## Submitting

Put the team credentials in `.submit_credentials` (not committed anywhere, `chmod 600`):

```
TEAM=초정밀모델제어학회쨩
PASSWORD=<team password>
```

(The team was renamed on the site; the server rejects the old name 한성재팬티도둑.)

then `python work/submit.py submit work/submissions/<name>.qasm work/submissions/<name>.json`,
`python work/submit.py status`, `python work/submit.py board`.

## Candidates (official setting: 1e8 shots, seed 0)

| File | 1-F | 2q | Notes |
|---|---|---|---|
| `work/submissions/v4_perm_lazy` | 1.534e-4 | 111 | Gidney d3 injection + double cat check + superdense cycle, permuted |
| `work/submissions/v5_gen_anneal` | 1.425e-4 | 111 | final cycle annealed with `proxy2` |
| `work/submissions/v6_gen2_extras` (submitted 2026-10-23 16:50 KST, server 0.000131) | 1.310e-4 | 113 | + extra cat members (1,3),(4,2) doing X-part CNOTs during Bell readout (`gen2_cycle.py`); c1 = 0 |
| `work/submissions/v7_move_d1` (**submitted 2026-10-23 18:04 KST, server 0.000130, rank 1**) | 1.303e-4 | 115 | d1 moved (2,3)→(1,3) by a 2-CNOT hop; vacated (2,3) becomes an X-only extra for d1 (`work/lanes/me_layout/gmodel.py`, variant A1); c1 = 0 |

Seed 0 alone carries ±1.2e-6 of MC noise. Means over seeds 0/1000/2000 (1e8 each): v6 1.325e-4, v7 1.295e-4, so v7's true gain is about 2.3%.
`work/fast_check.py` reproduces the official score bit for bit in ~10 s using parallel chunks.
