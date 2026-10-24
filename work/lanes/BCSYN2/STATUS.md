# BCSYN2 — complete

Completion branch 1 passed. Winner: `best.qasm` / `best.json`, identical to `full/fb_s401_0035.*`.

- MC, 1e8 shots per seed: 7.133396e-5 / 7.160200e-5 / 7.293238e-5.
- Mean: 7.195611e-5; requested v20 bar: 7.282e-5.
- Seed-0 acceptance: 0.54714. Fresh 1e6-shot check of `best.qasm`: PASS.
- Unmodified exact2 --third: 7.10055e-5; c1=2.9236e-19.
- Native R=45; 203 full CX; 82-CX, 14-layer clean prep.
- SHA256: a53818b6f02a14c330cf599b6e4b169b8c06dddb45feea9827c07e0ec019a4ac.

Coverage: 5,297 clean prep files mapped to in-situ prices; 2,965 distinct LNS wire sequences; 3,312 generated full circuits all pass the 1e6-shot judge check. Zero missing prep prices, QASM companion JSONs, or judge checks (`FINAL_AUDIT.json`). Seven finalists/reference circuits have full three-seed MC receipts; seven standard exact CLI receipts cross-check the aggregate evaluator.

All BCSYN2 processes exited (`owl_final_processes.txt`, `tom_final_processes.txt`). Long solvers were stopped after the MC improvement gate passed; stopped CPU time is recorded and is not mislabeled as timeout/UNSAT. Tom capacity stops were earlier resource-limit responses. No official submission, git commit/push, credential access, or changes to other lanes or their jobs.

Read `REPORT.md` for the two requested tables, `synthesis_all.csv` for every prep-to-price mapping, `full_results.csv` for every full-circuit price, and `BEST_VERIFICATION.json` for verification of the actual delivery files.
