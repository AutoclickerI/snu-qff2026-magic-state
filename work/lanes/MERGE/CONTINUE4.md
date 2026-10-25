Continuation from the main session, pass 4. Your pass 3 is verified and committed as work/lanes/MAIN/v37f.{qasm,json}
(all orders 3.6305606234064893e-5, A 0.5034645094225926, 405 CX, judge 1e6 4.1 s vs v37e 5.7 s on zebra, 4e7 shots
consistent); it races from the 02:20 race. Thank you. Pass 4 on v37f (tau = L(v37f)):

1. Bring in what pass 3 did not take: PREPFREE's measured inits M12@34 and M25@37 (-1.66e-8 on v37d;
   work/lanes/PREPFREE/REPORT.md, cand/prepfree_final; closed lane, read only) and POLISH's converged final edits
   (work/lanes/POLISH/cand/polish_b1b1dd19e1c1, 3.738766e-5 on v37a, -7.7e-9 below the polish_d49f37074d8e you were
   given; closed lane) where they transplant.
2. Widen the greedy move set (reviewer 16 #8, work/lanes/MAIN/spec/reviewer16/REPORT_KO.md; untrusted): ejection moves
   that drop or replace an already selected edit; several acceptance buyers per move instead of one; candidate pairs
   chosen by interaction of error signatures (detector, logical-output and rotation effects), not physical footprint:
   two independent D1(p) on different outputs each cost 0 decoded loss but 5p^2/9 together. Keep the incumbent in every
   candidate set and price whole circuits; never add single gains.
3. Selection: the finalist is the lowest exact L at exact A >= 0.5002. Your campaign.py fixes TAU at v37b's L and
   greedy_pass.choose minimizes A*(L - TAU), which rewards acceptance (it passed over a feasible candidate 6.5e-11 below
   v37d); use tau = the current incumbent's L at every step and break ties by L. Your ev37.write_stem writes the JSON
   once per QASM hash: key stem files by QASM plus ordered data_qubits.

Finalist: L < L(v37f) - 3e-8 at exact A >= 0.5002, judge gates_ok at 1e6, judge time within 1.5x of v37f's (time both
on the same host, 1 process). Stop when the widened greedy converges (< 1e-9 per round) or name why it cannot gain.
Hosts: hippo <= 24 processes in total, zebra <= 4. OMP/OPENBLAS/MKL threads = 1; wait on PIDs, kill by PID. Write only
under work/lanes/MERGE; no submission, commit or push; never read .submit_credentials; no spawn_agent. Update REPORT.md
(<= 100 lines, each < 2,000 characters) and results.json; finalists to cand/.
