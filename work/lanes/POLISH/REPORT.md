# POLISH

Verdict: COMPLETE; verified finalist available.
Target: L < 3.7568216548350849e-05, A >= 0.5002; rank feasible circuits by J_tau=A*(L-tau), tau=3.761821654835085e-05.
Baseline reproduced with MAIN evaluator: L=3.761821654835085e-5, A=0.5007854638217537; local GLOBAL-basis replay differs by 1.11e-16.
Data qubits are read from v37a.json: [6,20,19,10,2,22,16]. All operations stay on the 6x6 grid.
Evaluator speed: a lane-local v37a detector basis is replayed; baseline and two edited controls are compared in logs/evaluator_replay_check.json. Earlier evaluator receipts remain retained.
Later rounds freeze an incumbent-specific detector basis and re-check its full price within 1e-13; cache keys include the active basis/configuration and adapter hash. Original ev37 adapter retained as ev37_snapshot.py.
Width-12 search threshold keeps full contractions exact; three saved controls agree within 1.2e-16 while cutting 38-40 s to 8-9 s. logs/width12_benchmark.json; prior adapter ev37_adaptive10_snapshot.py.
Decision: missing BUNDLE/REPORT.md replaced as reference by its source, res logs, FINDINGS and supplied greedy_ref.py.
Corrected inherited CX shift lookup: Unit.qs is unordered, so lookup now matches the footprint and retains actual gate direction. Re-priced eight falsely rejected v37a shifts; new qualifying P1/P2/P4 bundles are recorded in shift_repair.json and shift_pairs_complete.json.
Decision: P1 contexts use improving/neutral singles and cheap acceptance buyers; P2 connects such singles within one tick; P4 joins their same-qubit trades.
Cheap buyers: positive acceptance and loss cost <= max(3e-8, 2e-5 * acceptance gain). Neutral tolerance 5e-14.
Decision: each greedy round prices every valid positive single/pair extension; re-prices the five best under-floor proposals with every cheap buyer. Stop at gain <1e-9.
Numerical ties in later passes (J within 5e-14) prefer fewer CX and fewer edits. An extra CX19->25 gave only a 2.2e-16 L difference in a saved control; it is not a measured gain.
Final fresh menu additionally tests identity pairs in both directions at all idle slots, including data-data pairs used successfully by GLOBAL; all additions receive full prices.
Guard synthesis also tests movable preparations/readouts on final-output cells; the improving CX16->10 connects two such cells. This broadens the proposal grammar, with full coherent-boundary equality and the independent ideal oracle still required.
The A pass includes APROC's relaxed-record family as well as strong boundaries, borrowed wires, decoder windows and record-removal templates. Relaxed witnesses require the full ideal accepted-state oracle before pricing.
Synthesis scope: guard windows have 9 wires, ticks 25-46, baseline internal CX+8, at most 24 witnesses; A windows have 7-9 wires, ticks 33-48 (decoder 43-48), CX+2/+4, at most 200 enumerated or 32 objective witnesses. Each solve has a 180 s bound.
Compute: local zebra only, up to 14 serial workers plus controller; BLAS/OpenMP caps=1. No subagents, GPU, submission, commit or push.
After shared-host load exceeded 64 cores, final closure resumed with 8 evaluation workers. Small 128-item scheduling barriers were removed; completed hash-keyed prices were retained.
Verified: each ledger price was evaluated on saved QASM and its SHA256; cache includes ordered data and evaluator/adapter hashes. Judge receipts distinguish gates_ok from sampled acceptance.
Inferred only: finite local-menu and CP-SAT coverage; no global optimality claim. Exact all-orders A is the acceptance criterion.
Files: results.json (full precision, hashes, aliases); complete.json (coverage and independent verification); best_delta.json; c/; cand/; res/; logs/; polish.py; process_pass.py; synth.py; network.py; collect.py; local evaluators sparse/ and sparse_v37/.
Completed coverage: {"base":{"menu":2464,"singles":2464,"pairs":5766,"rounds":14},"final":{"menu":2790,"singles":2790,"pairs":9375,"rounds":4},"guard":{"jobs":89,"completed":89},"aproc":{"jobs":34,"completed":34}}
Final verification: MAIN evaluator in a clean process agrees within 1e-13; saved ordered data, QASM hash, and 1e6-shot gates_ok checked. No official 1e8-shot draw was run in this lane.
Ranking trade-off: the requested J_tau winner remains primary. Lowest feasible L alternative `cand/polish_9e7c400b0d7d.qasm`: L=3.7387535721133327e-05, A=0.50037804061265345, J_tau=-1.1542762033000996e-07, gates_ok=true.
Lowest-L alternative judge receipt: 1e6 sampled A=0.49995000000000001, passed=False; the task uses gates_ok and exact A, so this binomial estimate does not reject it.
Convergence checked across all feasible direct and funded final-round extensions: largest L gain=1.7057365520316715e-10 <1e-9.
Best: `cand/polish_b1b1dd19e1c1.qasm`, L=3.7387663863425888e-05, A=0.50268195951418426, J_tau=-1.1589467542933642e-07, sha=b1b1dd19e1c1e6c638143c8773a946d5395e9a067562a347ab33715a27c9eb97.

Base-stage gains compare with v37a; guard, A, and final-stage gains compare with their incoming incumbent.
| Stage | L | A | Gain | Final greedy gain |
|---|---:|---:|---:|---:|
| base_singles | 3.756004120897e-05 | 0.5011504669931 | 5.81753394e-08 | 0 |
| base_pairs | 3.760180437315e-05 | 0.5007824474166 | 1.64121752e-08 | 0 |
| base | 3.7402870499645e-05 | 0.50108350935592 | 2.15346049e-07 | 9.97651718e-11 |
| guard | 3.740281209803e-05 | 0.50115014005497 | 5.84016152e-11 | 0 |
| aproc | 3.7401379039559e-05 | 0.50115005403047 | 1.43305847e-09 | 0 |
| final_singles | 3.7395108355097e-05 | 0.50114876733265 | 6.27068446e-09 | 0 |
| final_pairs | 3.7399881761325e-05 | 0.50114977405643 | 1.49727823e-09 | 0 |
| final | 3.7387663863426e-05 | 0.50268195951418 | 1.37151761e-08 | 4.24313626e-11 |

Every priced circuit below; aligned `<br>` entries share column positions. Full edit descriptions/aliases are in results.json.
| QASM / sha prefix | L | A | J_tau | What moved |
|---|---:|---:|---:|---|
