# Resources
Everything usable for G0. Binding usage rules are in CONSTRAINTS (rules 6, 8, 9). Capacity, usage and
free space are measured when needed (`nproc`, `uptime`, `free -g`, `df -h`), not written here.

## Setup
From the repo root `/home/jihoon/competitions/quantumn`:
1. Python is `.venv/bin/python` (stim, xtim 3.1.3+qff2, qiskit, OR-Tools). The judge `tprep` is installed editable from
   `upstream/snu-qff2026-problem` (keep it unmodified; `git pull` for organizer updates).
2. Official score, bit-identical to the server, ~10 s at 20 processes: `cd work && ../.venv/bin/python fast_check.py
   <qasm> <json> [shots] [procs]`. Sanity: `fast_check.py submissions/v36b_r580.qasm submissions/v36b_r580.json`
   gives the server's 3.87794862201698e-5 (another host may differ in the last ulp).
3. Ranking evaluators (all orders, exact 2nd/3rd order, 3-seed MC, speed): `docs/reference/circuit.md` "Evaluators".
4. Sequential judge plus fault scan (~5 min): `work/seqcheck.py <stem> > work/receipts/seq_<name>.txt`.
5. Seed-0 re-draws of one circuit (same noise model, verified per variant): `RACE_THRESHOLD=<x> work/race.py <stem> <n> [procs]
   [first]` → `work/reorder/` (gitignored); it drops a variant once it cannot end below x (`work/reorder.py` holds the
   variant generator and runs every variant to the end).
6. Promote in one step: `work/promote.sh <stem> <host:procs:first:count>...` (speed gate ≤ 20 s per 1e6, re-draws over
   hosts with non-overlapping variant ranges, best passing draw → `submissions/`, sequential judge, commit + push,
   `submit_when_ready.sh`). Stop the draws in time for a slot with `work/receipts/cut_redraws.sh <stem name> "<time,
   e.g. 02:20>" <hosts incl. zebra>`; the slot is at :37 each hour. Hourly loop: `work/receipts/draw_loop.sh <pid of the running cut>`
   re-draws an hour-named copy of the stem in `work/receipts/next_stem.txt` until HH:20 and promotes it. By hand: `work/submit.py submit|status|board|wait`.
7. Remote hosts: the uv Python, venv and repo are mirrored at the same absolute paths, without credentials or caches.
   Refresh one host at a time (zebra caps SSH connections):
   `rsync -a ~/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu ~/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu <h>:~/.local/share/uv/python/`;
   `rsync -a --exclude .submit_credentials --exclude '.xtim_cache/' --exclude 'vendor/' --exclude '.git/' /home/jihoon/competitions/quantumn <h>:/home/jihoon/competitions/`.
   Run with `ssh -q -o ControlMaster=no -o ControlPath=none <h> 'cd /home/jihoon/competitions/quantumn/work && ../.venv/bin/python ...'`
   and rsync results back. Background jobs: `ssh -q <h> "cd <dir>; env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
   MKL_NUM_THREADS=1 nohup nice -n 5 <cmd> > <log> 2>&1 < /dev/null &"`. With `&&` before `nohup`, ssh never returns;
   without the thread caps, screens oversubscribe the host several times over.

## Inventory
| Resource | Use for | Access and non-obvious limits |
|---|---|---|
| zebra (64 cores) | lanes, submissions, any job | this machine; credentials live only here; GPU0 is another user's |
| owl (96) | re-draws, enumeration, lanes | native python cannot load numpy/stim (glibc 2.17); run in docker: `docker run --rm -u 1010:1012 -e HOME=/home/jihoon -v /home/jihoon:/home/jihoon -w <dir> --cpus=N fnc-build:22.04 /home/jihoon/competitions/quantumn/.venv/bin/python ...`; bit-identical official scores |
| hippo (48), tom (64), jerry (64), sunfish (32) | re-draws, lanes, MC | mirrored; tom carries other users' load at times |
| faraday, dragon | not for judge work | not mirrored; dragon cannot run xtim (glibc 2.27); faraday runs Jihoon's other projects |
| pegasus | — | SSH from zebra times out |
| Submission quota | one per hour (slot :37) | `work/submit.py`; the board keeps each team's best entry, so every slot is used |
| Claude subagents | research lanes while Codex is down (R-20261025-1), one dir each under `work/lanes/` | Agent tool, background; the brief names the goal and incumbent numbers, the docs to read, prior lanes' git paths, evaluator commands, host limits, and "no submit, no commit"; the main session verifies and commits |
| Codex | research lanes when it answers | down since 2026-10-25 02:26 KST (Hermes proxy 127.0.0.1:18645: 429, ~6-day retry on every model); test with a one-line `codex-companion.mjs task` before relaunching; briefs forbid `spawn_agent` |
| Reviewer bundles | independent audits with circuits, certificates and task lists | `work/lanes/MAIN/spec/reviewer{8,9}/`; reviewers 3–7: `git show b2a5243:work/lanes/MAIN/spec/reviewer<n>/...` |
| Upstream | judge and cultivation code | `upstream/snu-qff2026-problem` (76fe47c), `upstream/magic-state-cultivation` (871e68f); not in git |

## Consumers
- `/home/jihoon/.claude/projects/-home-jihoon-competitions-quantumn/memory/*.md`
- Subagent briefs (delegation prompts, no file); lane outputs are `work/lanes/<LANE>/REPORT.md`.
