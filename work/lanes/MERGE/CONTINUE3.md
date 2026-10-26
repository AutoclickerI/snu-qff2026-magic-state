Continuation from the main session, pass 3. Your pass 2 is verified and committed as work/lanes/MAIN/v37d.{qasm,json}
(all orders 3.676346632406467e-5, A 0.5023547642585299, 406 CX, judge 1e6 3.2 s, gates_ok); it is the incumbent and
races from the 01:37 slot. New lane gains to bring onto v37d (all on v37a's line, so port them by footprint as before):

1. GLOBAL's BC3 B/C resource (work/lanes/GLOBAL/REPORT.md "Direction 1"; GLOBAL is still running, read only): actual
   earlier releases, checked same-basis measurements and fresh measured-plus sources with propagated detector
   byproducts. Best collected price builds/bc3rt_000_o206_t20 3.6761994831948519e-5 (A 0.50372); qualified finalist
   cand/global_bc3_fast 3.6768519555745145e-5 (A 0.50373, judge 6.1 s per 1e6). Over GLOBAL's bc2_polish_port
   (3.7225517523189325e-5) that is about -4.6e-7, against v37c's GLOBAL core (bc2fix_007). Watch judge speed: a
   reused MX on q12@26 put GLOBAL's version on xtim's slow path (285 s per 1e6) until RX12@26 restored it, and even
   the fast version takes 6.1 s against v37d's 3.2 s; find what costs the remaining time.
2. POLISH's latest edits since v37b (work/lanes/POLISH/REPORT.md, cand/polish_d49f37074d8e 3.739510835520767e-5 on
   v37a, -2.8e-8 below v37b; POLISH is still running, read only): regenerate the ones that transplant.
3. Then joint greedy repair to convergence with your regenerated menu.

Target: tau = L(v37d) = 3.676346632406467e-5; finalist L < tau - 5e-8 at exact A >= 0.5002, judge gates_ok at 1e6,
judge speed within 1.5x of v37d's 3.2 s per 1e6 (time fast_check at 1e6 with 1 process). A finalist does not end the
pass: stop when greedy repair converges (< 1e-9 per round) or the measured reason the gains do not combine is named.
Hosts: hippo <= 24 processes in total (ssh -q hippo '...' < /dev/null; rsync
-a --exclude .submit_credentials both ways), zebra <= 4. OMP/OPENBLAS/MKL threads = 1; wait on PIDs, kill by PID.
Write only under work/lanes/MERGE; no submission, commit or push; never read .submit_credentials; no spawn_agent.
Update REPORT.md (<= 100 lines, each < 2,000 characters) and results.json; finalists to cand/.
