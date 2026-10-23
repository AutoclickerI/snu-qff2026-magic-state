# Resources
Everything usable for G0. Binding usage rules are in CONSTRAINTS (rules 6, 8, 9). Capacity, usage and
free space are measured when needed (`nproc`, `uptime`, `free -g`, `df -h`, `nvidia-smi`), not written
here.

## Setup
From the repo root `/home/jihoon/competitions/quantumn`:
1. Python is `.venv/bin/python` (stim, xtim 3.1.3+qff2, qiskit, OR-Tools). The judge `tprep` is
   installed editable from `upstream/snu-qff2026-problem` (keep it unmodified; `git pull` for organizer
   updates). Sanity: `work/baseline.py` gives 1-F = 0.0251615 at 1e6 shots.
2. Official score, bit-identical to the server, ~10 s at 20 processes: `cd work &&
   ../.venv/bin/python fast_check.py <qasm> <json> [shots] [procs]`, or `fast_check.check(text,
   data_qubits, shots=10**8, seed=0, procs=20)`.
3. True mean: `work/indep_seeds.py <stem>...`, or `work/lanes/me_layout/mseed.py <hash>...` for
   `alapvar/` candidates (~30 s each).
4. Sequential judge plus fault scan (~2 min): `work/seqcheck.py <stem> > work/receipts/seq_<name>.txt`.
5. Cycle proxy (~0.2 s): `GModel.proxy` in `work/lanes/me_layout/gmodel.py`; variants in `run_moves.py`.
6. Anneal: `run_moves.py <variant> <steps> <lmax> <chains> <seed0>`. `BASE=<gen2 json>:<idx>` seeds from
   another schedule; interleaved orders are reachable only this way (random starts never pass validity).
7. ALAP screen: `alap_seeds.py <res json> <idx> <nseeds> <c1 threshold>` (gmodel results) or
   `alap_gen2.py` (gen2 schedules); scores land in `alapvar/<hash>.json`.
8. Loss by idle window: `work/idle_decomp.py <stem> <cycle start step>`.
9. Submit: `work/submit.py submit|status|board`. `work/submit_when_ready.sh <stem>` waits 3605 s
   after our last server-side submission and for `receipts/seq_<name>.txt`, and submits only on PASS.
10. Remote hosts: the uv Python, venv and repo are mirrored at the same absolute paths, without
   credentials or caches. Refresh one host at a time (SSH cap):
   `rsync -a ~/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu ~/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu <h>:~/.local/share/uv/python/`;
   `rsync -a --exclude .submit_credentials --exclude '.xtim_cache/' --exclude 'vendor/' --exclude '.git/' /home/jihoon/competitions/quantumn <h>:/home/jihoon/competitions/`.
   Run with `ssh -q <h> 'cd /home/jihoon/competitions/quantumn/work && ../.venv/bin/python ...'`
   (`-q` hides large banners) and rsync results back.

## Inventory
| Resource | Use for | Access and non-obvious limits |
|---|---|---|
| zebra | Codex lanes, submissions, any job | this machine; credentials live only here; GPU0 is another user's |
| hippo, tom, jerry, sunfish | anneals and MC scoring | mirrored; hippo reproduces the official v8 score bit for bit |
| owl | — | stim fails: system libstdc++ lacks GLIBCXX_3.4.20; needs a newer libstdc++ on `LD_LIBRARY_PATH` first |
| faraday, dragon | GPU-heavy other users | not mirrored |
| pegasus | — | SSH from zebra timed out (2026-10-23) |
| Submission quota | one per hour | `work/submit.py`; board keeps the best entry |
| Codex (`codex:codex-rescue`) | parallel lanes L1–L5 in `work/lanes/` | `codex-companion.mjs status`; job logs under `~/.claude/plugins/data/codex-openai-codex/state/*/jobs/`; a resume while a task runs is unsafe |
| Prior artifacts | starting points and receipts | `work/submissions/`, `work/lanes/me_layout/res_*.json`, `alapvar/`, `work/receipts/`, lane outputs |
| Upstream | judge and cultivation code | `upstream/snu-qff2026-problem` (76fe47c), `upstream/magic-state-cultivation` (871e68f); not in git |

## Consumers
- `/home/jihoon/.claude/projects/-home-jihoon-competitions-quantumn/memory/*.md`
- Codex lane briefs (delegation prompts, no file); lane outputs are `work/lanes/L*/REPORT.md`
