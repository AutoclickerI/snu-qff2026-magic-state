Continuation from the main session. Your merge_final is verified (all orders 3.6904034715818095e-5, A 0.50572, judge
1e7 3.6902e-5 +- 2.4e-6) and committed as work/lanes/MAIN/v37c.{qasm,json}; it races from the 00:37 slot. Thank you;
the judge slow-path bisection was a good catch. Continue on v37c as the base (tau = 3.6904034715818095e-5;
finalist L < tau - 3e-8 at exact A >= 0.5002, judge gates_ok at 1e6 and judge speed within 1.5x of v37c's):
1. Bring in AJOINT's gain: work/lanes/AJOINT/REPORT.md and cand/ajoint_dd374d5610e8 (joint q9 guard/check reorder:
   M9/c321 37->39 and CX9->10 39->37, keep CX9->10 at 38 and A9 preparation at 40; -7.87e-8 alone on v37a). Transport
   it to v37c's R45 schedule and price.
2. Polish v37c the way BUNDLE took v36h to v36k: price all singles of your regenerated menu on v37c, enumerate the
   connected 2-edit bundles among the positive and acceptance-cheap singles, then run the greedy joint extension to
   convergence (a round gaining < 1e-9 ends it); fund acceptance with cheap singles.
3. Before finishing, merge any newer, better candidates from the still-running lanes POLISH, GLOBAL, SQUARE and
   ENDSEARCH (read their cand/ and results.json; never write there), then repair once more.
Hosts now: hippo <= 24 processes in total, zebra <= 2. Measure judge speed for every candidate you promote to cand/.
Update REPORT.md (<= 100 lines, each < 2,000 characters; keep the full table in a separate file) and results.json.
Do not stop to ask questions; the other rules of your brief stand.
