# Resources
Everything usable for G0 is a resource: machines, accounts and quotas, models and agents, caches and
seeds, prior artifacts, other lanes' outputs. Binding usage rules are in CONSTRAINTS (rules 6, 8, 9);
this file is the inventory. Hosts not listed here, and Parrot, are not ours (rule 9). Repo root: `/home/jihoon/competitions/quantumn`.

## Setup
From the repo root (all steps reuse what is already on disk):
1. Python: `.venv/bin/python` (3.12, stim 1.16.0, xtim 3.1.3+qff2, qiskit 2.5.2, OR-Tools 9.15.6755).
   The judge package `tprep` 3.0.3 is installed editable from `upstream/snu-qff2026-problem` (commit
   76fe47c; keep it unmodified, `git pull` for organizer updates). A bare `python` lacks these modules
   (FINDINGS "Failures"). Jupyter kernel: `qff2026`. Sanity checks: `.venv/bin/python work/baseline.py`
   (starter circuit, 1e6 shots, 1-F = 0.0251615), `work/baseline.py 1e8` (official, 1-F = 0.025172,
   ~20 s), `cd upstream/snu-qff2026-problem && ../../.venv/bin/python -m pytest tests -q` (41 pass).
2. Official score, bit-identical to the server, ~10 s at 20 processes:
   `cd work && ../.venv/bin/python fast_check.py <qasm> <json> [shots] [procs]`, or
   `fast_check.check(text, data_qubits, shots=10**8, seed=0, procs=20)` in code.
3. True mean: `work/indep_seeds.py <stem>...` (seeds 1000, 2000) or `work/lanes/me_layout/mseed.py
   <hash>...` for `alapvar/` candidates (~30 s each).
4. Unmodified sequential judge plus fault scan, ~2 min: `work/seqcheck.py <stem>`.
5. Cycle proxy, ~0.2 s: `work/lanes/me_layout/gmodel.py` `GModel.proxy` (variants in `run_moves.py`).
6. Anneal a variant: `run_moves.py A1 <steps> <lmax> <chains> <seed0>`; `BASE=<gen2 json>:<idx>`
   starts from another schedule (needed to reach interleaved orders), `RANDSTART=1` does not work.
7. ALAP pre-cycle and screen: `alap_seeds.py <res json> <idx> <nseeds> <c1 threshold>` (cm variants,
   seed-0 scores into `alapvar/<hash>.json`); `alap_gen2.py` does the same for gen2-format schedules.
8. Loss by idle window: `work/idle_decomp.py <stem> <cycle start step>`.
9. Submit: `work/submit.py submit <qasm> <json>`, `status`, `board`. Credentials in
   `.submit_credentials` as `TEAM=...` / `PASSWORD=...` (rule 8). `work/submit_when_ready.sh <stem>
   <HH:MM:SS>` waits for the slot and the stem's `receipts/seq_*.txt` and submits only on PASS.
10. Remote hosts (rule 9): the repo, venv and uv Python are mirrored at the same absolute paths, without
   credentials or caches. Mirror or refresh (~1 min per host, one host at a time because of the SSH cap):
   `rsync -a ~/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu ~/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu <h>:~/.local/share/uv/python/`
   then `rsync -a --exclude .submit_credentials --exclude '.xtim_cache/' --exclude 'vendor/' --exclude
   '.git/' /home/jihoon/competitions/quantumn <h>:/home/jihoon/competitions/`. Run with
   `ssh <h> 'cd /home/jihoon/competitions/quantumn/work && ../.venv/bin/python ...'` and rsync results
   back. hippo reproduces the official v8 score bit for bit (2026-10-23 19:57).

## Inventory
| Resource | Capacity | Current use | Headroom | Access / notes |
|---|---|---|---|---|
| zebra (this host) | 64 cores, 188 GB RAM; 2× RTX PRO 6000 96 GB | Codex lanes, submissions, screens; load 13–86 on 2026-10-23 | cap ~75% CPU (rule 9); GPU0 is another user's, never use; GPU1 shared | repo, venv, credentials live here |
| hippo | 48 cores, 123 GB free RAM, `/data/jihoon` (2.2 TB free) | anneal batch since 2026-10-23 20:0x | idle at 19:5x (load 0.0) | mirrored env, verified bit-identical |
| tom | 64 cores, 468 GB free RAM, `/data1`, `/data2` | — | load 7 at 19:5x | mirrored env, imports OK |
| jerry | 64 cores, 482 GB free RAM, `/data1`, `/data2`; no GPU driver | — | load 15 at 20:0x | mirroring 20:0x |
| owl | 96 cores, 122 GB free RAM, `/data`, `/data2`; glibc 2.17 | — | idle at 20:0x | mirroring 20:0x; wheel compatibility unverified |
| sunfish | 32 cores, 180 GB free RAM, `/hdd1/jihoon`; home only 49 GB free | — | idle at 20:0x | mirroring 20:0x |
| faraday | 64 cores, 4 GPUs | busy (load 102, GPUs 56–95%) at 19:5x | little | not mirrored |
| dragon | 24 cores, 4× 3090 | busy (load 27, GPUs ~100%) at 19:5x | little | not mirrored |
| pegasus | allowed (R-20261023-7) | — | unknown | SSH timed out from zebra at 20:0x |
| zebra disk | 1.8 TB, 131 GB free (93%) | `.xtim_cache` dirs ~2 GB | keep caches pruned | caches are rebuildable |
| Submission quota | 1 per hour, best entry shown (rule 6) | v8 at 19:05, next 20:05 | 1 per hour until 2026-10-30 12:00 | `work/submit.py` |
| Codex (`codex:codex-rescue`) | parallel background tasks on the shared app-server | lanes L1–L5 (2026-10-23 17:58→23:00) | more lanes possible | `codex-companion.mjs status`; job logs under `~/.claude/plugins/data/codex-openai-codex/state/*/jobs/` |
| Claude subagents | fork / general-purpose / Explore / deepseek (cheap, simple tasks) | — | available | Agent tool |
| Team | 초정밀모델제어학회쨩 (registered as 한성재팬티도둑, R-20261023-2) | — | — | board name is the new one |
| Prior artifacts | `work/submissions/` (v4–v9), `work/gen2_*.json`, `work/lanes/me_layout/res_A1_*.json`, `alapvar/`, lane outputs | — | reuse before re-running | receipts in `work/receipts/` |
| Upstream | `upstream/magic-state-cultivation` (Strilanc, 871e68f), `upstream/snu-qff2026-problem` (76fe47c), site pages `upstream/*.html` | read-only | — | not in git (own repos) |

## Consumers
Files outside the repo that agents read for this project. They point to rules, never restate them.
- `/home/jihoon/.claude/projects/-home-jihoon-competitions-quantumn/memory/*.md`
- `/home/jihoon/.claude/CLAUDE.md` (Jihoon's global instructions; not edited by agents)
- Codex lane briefs: sent in the delegation prompts of 2026-10-23 17:57 (no file); lane outputs are
  `work/lanes/L*/REPORT.md`
