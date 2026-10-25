<task>
You run tooling lane TOOLS of our SNU QFF2026 hackathon entry (fault-tolerant Steane |T_L> on a 6x6 grid; the board keeps
each team's best entry by the official ranking; one submission per hour, raced from seed-0 re-draws). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/TOOLS. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/RESOURCES.md, docs/reference/judge.md, docs/PLAN.md "Critical path", then
work/lanes/MAIN/spec/reviewer13/REPORT_KO.md sections 2, 3, 4, 9, 10 (reviewer 13; its code stayed in its sandbox, so
re-implement from the text), the official rules upstream/snu-qff2026-problem/problem.md and the site text it cites.

Implement and validate, in this order, each as a patched copy inside your lane dir (never edit the live files):
1. Race threshold by the official comparator (section 2): the board compares (formatted score as published, 2q-gate
   count, submission order). Compute, for a candidate with a given CX count, the first losing raw score against our
   current best (key 3.53e-5, raw 3.53130699502577e-5, 327 CX) by binary search over positive IEEE-754 doubles with the
   official formatter; handle equal keys with fewer CX and decade boundaries. Live code: work/promote.sh,
   work/receipts/draw_loop.sh (they subtract half a rounding step). Test against the counterexamples in section 2 and an
   exhaustive grid of keys x CX relations.
2. Observable-unified selector contraction for the all-orders evaluator (section 3): put the observable label into the
   selector so acceptance and the 72 scored moments contract together; keep the 2^K normalization. Live code:
   work/lanes/MAIN/sparse/sparse_walsh.py (frontend.py, fastfill.py beside it). Accept only if all 73 moments match the
   current evaluator within 1e-15 on v36h, v36g, v36c, v29c and five edited circuits from work/lanes/IFACE/builds, and
   end-to-end time at 1 and 16 processes improves (report both).
3. Race decisions with the known exact mean (section 4): work/race.py _p_below re-estimates mean loss sum and accepted
   count from chunk samples; use the exact A and N = A*L of the stem (all re-draws of one stem share them) and
   R = S - tau*K. Validate on recorded chunk traces (work/receipts, race logs) against the current policy: hits per chunk
   at equal compute.
4. Checkpoint and resume of partial races at the hour cut (section 9): work/receipts/cut_redraws.sh kills races; persist
   completed chunks (float.hex, chunk index, seed rule, environment hash) and resume them only when their win
   probability per remaining cost beats a fresh variant. Bit-identical final sums versus an uninterrupted run on a real
   xtim race (use a short race at reduced chunk count to test).
5. Racer allocation (section 10): work/receipts/race_specs.sh. The forced minimum of 4 workers was already removed today
   (a host with no room is skipped). Measure idle core-minutes per hour across hosts from the last runs; only if real
   idle gaps exist, propose a lease design.
Deliver for each item: the patched file in TOOLS/patched/<same relative path>, a test script, a receipt (inputs, outputs,
pass/fail), and a short swap note (exact diff against the live file and how to roll it in at an hour boundary).
</task>

<action_safety>
- Never edit, restart or kill the live loop: work/receipts/draw_loop.sh, work/promote.sh, work/race.py,
  work/receipts/*.sh, work/lanes/MAIN/sparse/*, the racer's processes on any host, or the hourly submission. The main
  session swaps patches in.
- Never submit; never read, print or copy .submit_credentials (also not via work/submit.py).
- zebra <= 8 processes, OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1; no other host.
- Wait on process exit, kill by PID only; never pkill -f or pgrep -f.
- No git commit, push, checkout or reset. Write only under work/lanes/TOOLS. Do not use spawn_agent or sub-agents.
- Do not stop to ask questions: decide within this brief and record decisions in REPORT.md.
</action_safety>

<structured_output_contract>
REPORT.md (<= 80 lines): per item, verdict (adopt / reject), measured effect, test receipts, swap note path. Final answer:
one line per item with the verdict and measured effect.
</structured_output_contract>
