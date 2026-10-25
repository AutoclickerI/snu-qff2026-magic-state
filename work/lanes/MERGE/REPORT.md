# MERGE — v37c continuation

Verdict: COMPLETE; exact tau=3.6904034715818095e-05; finalist L<tau−3e-8, exact A≥.5002, judge gates_ok and speed≤1.5×v37c.
Best verified candidate: [cand/merge37_final](cand/merge37_final.qasm). L=3.676346632406467e-05; A=0.5023547642585299; J_tau=-7.061520130149249e-08; SHA256 `dbe6f8db6e0b990c9f0007c8239283a92c95a429a7b83fc49aa01e8892178af4`.
Judge1e6: gates_ok=True; median2.995s; ratio0.970×v37c. Sampler ratio0.695. Both ratios≤1.5.

AJOINT transport: v37c has no q9→q10 guards and A9 prep is at39. Legal transport adds CX9→10@37, moves M9/c32137→38, retains prep39. Full source recipe cannot be shifted literally because q9’s source completion occupies36.
Measured controls: base L=3.690403471559856e-5,A=.5057191647109531; M38 alone3.6904560842016455e-5; post-read guard38 alone3.6913060992615435e-5; joint pre-read guard37/M38 gives3.685327051991586e-5,A=.5057509615191745. Gain5.07641959e-8. The candidate has independent judge/speed verification.
Menu: removals, trades, prep/operation shifts, single CX, both orientations of every idle identity pair, echoes, guards, and the legal AJOINT macro. All proposals are emitted and native-time checked before pricing.
Connected pairs: all overlapping per-qubit enclosing-operation intervals among improving and cheap-acceptance singles, plus additions unlocked by each useful freeing edit. Cheap buyers have ΔA>1e-6 and ΔL≤max(3e-8,2e-5ΔA). Every bundle receives a full exact price.
Greedy extension: consider every improving single/pair and cheap buyer on the current selected set; price joint funding for the five best under-floor proposals; rank by A(L−tau), enforce speed/ideal gates, and stop only when a complete round gains<1e-9 in L.
Speed protocol: v37c baseline median of three1e6 judge runs3.087731s;100k exact-sampler batches repeated three times. Every promoted candidate gets a1e6 judge run and the same sampler benchmark; ambiguous wall-time ratios get paired controls. Short probes reject pathological slow dispatch before a long run.
c37_history: 5 greedy rounds; last gain9.01545796e-10, stop=True; L=3.6765522489801e-05, A=0.503361256554.
repair37_history: 2 greedy rounds; last gain7.96469266e-10, stop=True; L=3.6763466324065e-05, A=0.502354764259.

| Pass / round | L | A | Gain in round | J_tau |
|---|---:|---:|---:|---:|
| c37_history / 1 | 3.683834888463e-05 | 0.506595916177 | 6.5685831e-08 | -3.327617383e-08 |
| c37_history / 2 | 3.678768177788e-05 | 0.506627768384 | 5.0667107e-08 | -5.894762929e-08 |
| c37_history / 3 | 3.677267725018e-05 | 0.502996353596 | 1.5004528e-08 | -6.607232623e-08 |
| c37_history / 4 | 3.67664240356e-05 | 0.502995510124 | 6.2532146e-09 | -6.92175543e-08 |
| c37_history / 5 | 3.67655224898e-05 | 0.503361256554 | 9.015458e-10 | -6.972168814e-08 |
| repair37_history / 1 | 3.676426279333e-05 | 0.50228791665 | 1.2596965e-09 | -7.020574775e-08 |
| repair37_history / 2 | 3.676346632406e-05 | 0.502354764259 | 7.9646927e-10 | -7.06152013e-08 |
Source refresh: Read cand/ and results.json from POLISH, GLOBAL, SQUARE and ENDSEARCH. POLISH’s new guard assignment was reproduced and transported in5 matched controls; its required earlier q23 reset consumes the gain. Deleting the superseded q28→22 guard ties L/A and saves1CX. GLOBAL is unchanged; SQUARE’s round-only number fails when all full-circuit noise is restored (L=.0008927603,A=.155149); ENDSEARCH has no admissible improvement. Full regenerated repair follows on the neutral one-CX reduction.
Completion: AJOINT transport built/priced/verified;1519 original singles and1118 connected/contextual bundles; five greedy rounds. All four requested lane cand/ and ledgers refreshed; POLISH transport controls priced;1498 fresh singles and1098 bundles; two final greedy rounds. Last gains9.01546e-10 and7.96469e-10 satisfy the stop rule.
Final change on v37c: delayed M9/c321 to38 and added CX9→10@37; source c319 omit trade with CX3→4@39; q21 X echo through q27 with CX15→21 advanced; CX2→3 retimed24→25; CX21→20@30; removed neutral CX28→22@29; fresh q1 guard onq7@37 and CX25→31@37. Native depth remains48.
Independent original detector-basis final replay agrees within floating-point roundoff; exact price and stored recipe were verified on the final handoff. No1e8-shot run or submission was made by MERGE.

Verified: saved QASM hashes and ordered data mapping; all-orders baseline agreement within2.2e-16; all promoted candidates pass ideal gates and both speed ratios. Omission bounds and evaluator hashes are in results.json.
Inferred only: finite menu/context coverage; no global optimality claim. Results from other lanes remain source observations until independently reproduced here.
Decisions: use lane-local native parser/toolkit copies so remote workers do not depend on mutable other-lane tooling. Baseline and emitted native schedules agree. Preserve prior merge receipts under archive/ and in the full table.
Scope: MERGE writes only; hippo≤24 processes (currently20 evaluators+controller), zebra≤2 compute jobs; thread caps1; no subagents, GPUs, submission, commit, push or credential access. No standing rule changed.
Ledger: 6849 continuation hashes; 8699 total hashes. Full per-circuit table: [priced_circuits.md](priced_circuits.md). Machine ledger: [results.json](results.json).
Files: cand/; v37c/; res37c/*history.json, baseline_speed.json, judge_*.json; logs37c/; cont37.py,search37.py,judge37.py.
