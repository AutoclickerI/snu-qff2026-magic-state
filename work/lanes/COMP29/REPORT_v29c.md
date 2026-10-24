# COMP29

**Status: SUPERSEDED by the v30f retarget; MAIN stopped these jobs.** Complete native subset enumeration and reference verification are in progress. No submission, commit, push, credential access, or subagent use.

Goal: lowest verified true-mean conditional 1−F among the composed v29c edits, with acceptance ≥0.5 and FAST execution. No additivity assumption is used.

Built 1536 candidates; 521 Fourier third-order screens; 1 unchanged exact2 CLI receipts; 270 speed/judge receipts; 245 full 1e6 passes; 0 all-orders results; 0 complete MC means.

## Methods and scope

The nine elementary choices are copy4, timing10, late q1 commute, extra early q19 X check, BC q11 reset→measure, final 14→15 readout edge, the two ST1 feedback timing moves, and known-zero q5 measurements at t37/t38. All 512 subsets are emitted, including both q5 measurements together. Copy4 is reviewer #1 itself, not a second independent edit. q19 already has an early check in v29c; the LNS2 extra repeated check is nevertheless priced independently.

Native units, per-wire precedence, nearest-neighbour assertions, terminal measurement identity, detector parities and fresh-helper barrier coverage are checked at emission. Every build is fully repriced; no marginal scores are added. `manifest.json` contains provenance and QASM hashes. `build_errors.json` records structural failures. SEPBC t37/t38 singleton prices reproduce its supplied native ports.

The LNS normalizer’s hardcoded c[256] register cannot hold v29c records through c[263]; the local adapter sizes the classical register from actual records. The corrected native copy4 rewrite repairs every detector containing the old terminal q25 record and moves q29/q28 readings after the copy layer. ST2’s older review_copy import is not used. ST1 feedback changes CX9→15 at t29→30 and MX9 at t30→31.

`screen.json` uses BCPOL’s existing exact categorical-channel Fourier contraction. `exact.json` is a separate unchanged `work/lanes/EVAL/exact2.py --third` CLI run (the task’s `work/EVAL/exact2.py` path does not exist). Full-precision screen values are shown below; a CLI receipt is explicitly marked. New CLI receipts retain the original CLI printed precision. The baseline independent CLI agrees within 3.2e-18.

All-orders ranking uses the unchanged BCPOL five-projector evaluator, copied byte-for-byte into COMP29 to keep owl dependencies/cache writes local. Its per-circuit validation checks rotation axes, decoder observables, categorical channel multisets, 1,024 projector sectors, and a nonzero-error three-channel enumeration. Rejected width/contract checks are recorded, not interpreted as scores. Speed uses the unchanged XTIM predictor; the full 1e6 gate uses fast_check. Three 1e8 MC seeds use the unchanged MAIN/spec/mc3.py.

BCFB’s rank-6 clean preparations replace v29c’s rank-5 endpoint through the B→C boundary; their complete output contract and detector frame are rebuilt. The original ±2 exterior timing window was infeasible. A ±12 window permits retiming the q4 release and yields native R48 candidates. The full judge, rather than the local preparation contract alone, decides validity. BCFB init checks preserve basis and record-frame parity. Mutually exclusive preparation replacements are not combined with each other. q5 checks are added only where symbolic CSS propagation proves the same known-zero opportunity.

## Results

Third order is conditional 1−F through cubic order. `A` is exp(−A1); threshold 0.5002. `CLI` means the unchanged exact2 reference has completed. “screen only” is not an independent CLI claim. Judge acceptance is the actual 1e6 seed-0 measurement. MC columns list the three-seed mean when complete; individual seeds remain in the adjacent log. Speed is the XTIM prediction in seconds per 1e6, followed by actual judge wall time. Pending fields are unfinished, not passes.

| Stem | Edits | Third order | A | Reference | Judge / acc | Speed | All-orders | MC mean |
|---|---|---:|---:|---|---|---|---:|---:|
| `c17f` | copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback + q5t38 | 6.149312002e-05 | 0.499256515 | screen only | pending | pending | pending | pending |
| `c1ff` | copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.149312002e-05 | 0.498757508 | screen only | pending | pending | pending | pending |
| `c16f` | copy4 + timing10 + commute1 + q19check + edge14to15 + feedback + q5t38 | 6.149312002e-05 | 0.500089303 | screen only | pending | pending | pending | pending |
| `c177` | copy4 + timing10 + commute1 + q11measure + edge14to15 + feedback + q5t38 | 6.149312002e-05 | 0.500089303 | screen only | pending | pending | pending | pending |
| `c167` | copy4 + timing10 + commute1 + edge14to15 + feedback + q5t38 | 6.149312002e-05 | 0.5009234801 | screen only | FAIL / 0.499955 | FAST 8.57 / 4.48 | pending | pending |
| `c1ef` | copy4 + timing10 + commute1 + q19check + edge14to15 + feedback + q5t37 + q5t38 | 6.149312002e-05 | 0.4995894637 | screen only | pending | pending | pending | pending |
| `c1f7` | copy4 + timing10 + commute1 + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.149312002e-05 | 0.4995894637 | screen only | pending | pending | pending | pending |
| `c1e7` | copy4 + timing10 + commute1 + edge14to15 + feedback + q5t37 + q5t38 | 6.149312002e-05 | 0.500422807 | screen only | FAIL / 0.499510 | FAST 7.01 / 3.99 | pending | pending |
| `c17d` | copy4 + commute1 + q19check + q11measure + edge14to15 + feedback + q5t38 | 6.151995362e-05 | 0.4992591742 | screen only | pending | pending | pending | pending |
| `c1fd` | copy4 + commute1 + q19check + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.151995362e-05 | 0.4987601645 | screen only | pending | pending | pending | pending |
| `c16d` | copy4 + commute1 + q19check + edge14to15 + feedback + q5t38 | 6.151995362e-05 | 0.5000919666 | screen only | pending | pending | pending | pending |
| `c175` | copy4 + commute1 + q11measure + edge14to15 + feedback + q5t38 | 6.151995362e-05 | 0.5000919666 | screen only | pending | pending | pending | pending |
| `c165` | copy4 + commute1 + edge14to15 + feedback + q5t38 | 6.151995362e-05 | 0.5009261482 | screen only | PASS / 0.500455 | FAST 7.24 / 3.95 | pending | pending |
| `c1ed` | copy4 + commute1 + q19check + edge14to15 + feedback + q5t37 + q5t38 | 6.151995362e-05 | 0.4995921246 | screen only | pending | pending | pending | pending |
| `c1f5` | copy4 + commute1 + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.151995362e-05 | 0.4995921246 | screen only | pending | pending | pending | pending |
| `c1e5` | copy4 + commute1 + edge14to15 + feedback + q5t37 + q5t38 | 6.151995362e-05 | 0.5004254724 | screen only | PASS / 0.500020 | FAST 7.58 / 3.99 | pending | pending |
| `c0ff` | copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback + q5t37 | 6.157817102e-05 | 0.499256515 | screen only | pending | pending | pending | pending |
| `c0ef` | copy4 + timing10 + commute1 + q19check + edge14to15 + feedback + q5t37 | 6.157817102e-05 | 0.500089303 | screen only | pending | pending | pending | pending |
| `c0f7` | copy4 + timing10 + commute1 + q11measure + edge14to15 + feedback + q5t37 | 6.157817102e-05 | 0.500089303 | screen only | pending | pending | pending | pending |
| `c0e7` | copy4 + timing10 + commute1 + edge14to15 + feedback + q5t37 | 6.157817102e-05 | 0.5009234801 | screen only | PASS / 0.500274 | FAST 7.18 / 4.01 | pending | pending |
| `c17b` | copy4 + timing10 + q19check + q11measure + edge14to15 + feedback + q5t38 | 6.158752973e-05 | 0.4992558493 | screen only | pending | pending | pending | pending |
| `c1fb` | copy4 + timing10 + q19check + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.158752973e-05 | 0.498756843 | screen only | pending | pending | pending | pending |
| `c173` | copy4 + timing10 + q11measure + edge14to15 + feedback + q5t38 | 6.158752973e-05 | 0.5000886362 | screen only | pending | pending | pending | pending |
| `c16b` | copy4 + timing10 + q19check + edge14to15 + feedback + q5t38 | 6.158752973e-05 | 0.5000886362 | screen only | pending | pending | pending | pending |
| `c163` | copy4 + timing10 + edge14to15 + feedback + q5t38 | 6.158752973e-05 | 0.5009228122 | screen only | PASS / 0.500676 | FAST 7.75 / 3.99 | pending | pending |
| `c1f3` | copy4 + timing10 + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.158752973e-05 | 0.4995887975 | screen only | pending | pending | pending | pending |
| `c1eb` | copy4 + timing10 + q19check + edge14to15 + feedback + q5t37 + q5t38 | 6.158752973e-05 | 0.4995887975 | screen only | pending | pending | pending | pending |
| `c1e3` | copy4 + timing10 + edge14to15 + feedback + q5t37 + q5t38 | 6.158752973e-05 | 0.5004221398 | screen only | PASS / 0.500743 | FAST 11.24 / 4.26 | pending | pending |
| `c13f` | copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + q5t38 | 6.159590653e-05 | 0.4997507224 | screen only | pending | pending | pending | pending |
| `c1bf` | copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + q5t37 + q5t38 | 6.159590653e-05 | 0.4992512215 | screen only | pending | pending | pending | pending |
| `c12f` | copy4 + timing10 + commute1 + q19check + edge14to15 + q5t38 | 6.159590653e-05 | 0.5005843348 | screen only | PASS / 0.500127 | FAST 7.62 / 4.00 | pending | pending |
| `c137` | copy4 + timing10 + commute1 + q11measure + edge14to15 + q5t38 | 6.159590653e-05 | 0.5005843348 | screen only | FAIL / 0.499889 | FAST 8.70 / 3.97 | pending | pending |
| `c127` | copy4 + timing10 + commute1 + edge14to15 + q5t38 | 6.159590653e-05 | 0.5014193376 | screen only | PASS / 0.500825 | FAST 6.69 / 3.95 | pending | pending |
| `c1af` | copy4 + timing10 + commute1 + q19check + edge14to15 + q5t37 + q5t38 | 6.159590653e-05 | 0.5000840006 | screen only | pending | pending | pending | pending |
| `c1b7` | copy4 + timing10 + commute1 + q11measure + edge14to15 + q5t37 + q5t38 | 6.159590653e-05 | 0.5000840006 | screen only | pending | pending | pending | pending |
| `c1a7` | copy4 + timing10 + commute1 + edge14to15 + q5t37 + q5t38 | 6.159590653e-05 | 0.5009181689 | screen only | PASS / 0.500100 | FAST 7.15 / 3.99 | pending | pending |
| `c0fd` | copy4 + commute1 + q19check + q11measure + edge14to15 + feedback + q5t37 | 6.160500462e-05 | 0.4992591742 | screen only | pending | pending | pending | pending |
| `c0f5` | copy4 + commute1 + q11measure + edge14to15 + feedback + q5t37 | 6.160500462e-05 | 0.5000919666 | screen only | pending | pending | pending | pending |
| `c0ed` | copy4 + commute1 + q19check + edge14to15 + feedback + q5t37 | 6.160500462e-05 | 0.5000919666 | screen only | pending | pending | pending | pending |
| `c0e5` | copy4 + commute1 + edge14to15 + feedback + q5t37 | 6.160500462e-05 | 0.5009261482 | screen only | PASS / 0.500378 | FAST 7.41 / 4.01 | pending | pending |
| `c179` | copy4 + q19check + q11measure + edge14to15 + feedback + q5t38 | 6.161433769e-05 | 0.4992585085 | screen only | pending | pending | pending | pending |
| `c1f9` | copy4 + q19check + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.161433769e-05 | 0.4987594995 | screen only | pending | pending | pending | pending |
| `c171` | copy4 + q11measure + edge14to15 + feedback + q5t38 | 6.161433769e-05 | 0.5000912998 | screen only | pending | pending | pending | pending |
| `c169` | copy4 + q19check + edge14to15 + feedback + q5t38 | 6.161433769e-05 | 0.5000912998 | screen only | pending | pending | pending | pending |
| `c161` | copy4 + edge14to15 + feedback + q5t38 | 6.161433769e-05 | 0.5009254803 | screen only | PASS / 0.500225 | FAST 7.28 / 4.03 | pending | pending |
| `c1f1` | copy4 + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.161433769e-05 | 0.4995914585 | screen only | pending | pending | pending | pending |
| `c1e9` | copy4 + q19check + edge14to15 + feedback + q5t37 + q5t38 | 6.161433769e-05 | 0.4995914585 | screen only | pending | pending | pending | pending |
| `c1e1` | copy4 + edge14to15 + feedback + q5t37 + q5t38 | 6.161433769e-05 | 0.5004248052 | screen only | PASS / 0.500245 | FAST 6.96 / 4.01 | pending | pending |
| `c147` | copy4 + timing10 + commute1 + feedback + q5t38 | 6.162102725e-05 | 0.5013243792 | screen only | PASS / 0.501431 | FAST 7.01 / 4.08 | pending | pending |
| `c1c7` | copy4 + timing10 + commute1 + feedback + q5t37 + q5t38 | 6.162102725e-05 | 0.5008233054 | screen only | PASS / 0.500446 | FAST 7.33 / 4.02 | pending | pending |
| `c14f` | copy4 + timing10 + commute1 + q19check + feedback + q5t38 | 6.162102725e-05 | 0.5004895345 | screen only | PASS / 0.500579 | FAST 6.98 / 4.01 | pending | pending |
| `c157` | copy4 + timing10 + commute1 + q11measure + feedback + q5t38 | 6.162102725e-05 | 0.5004895345 | screen only | PASS / 0.500195 | FAST 7.18 / 4.06 | pending | pending |
| `c15f` | copy4 + timing10 + commute1 + q19check + q11measure + feedback + q5t38 | 6.162102725e-05 | 0.49965608 | screen only | pending | pending | pending | pending |
| `c1df` | copy4 + timing10 + commute1 + q19check + q11measure + feedback + q5t37 + q5t38 | 6.162102725e-05 | 0.4991566737 | screen only | pending | pending | pending | pending |
| `c1d7` | copy4 + timing10 + commute1 + q11measure + feedback + q5t37 + q5t38 | 6.162102725e-05 | 0.4999892951 | screen only | pending | pending | pending | pending |
| `c1cf` | copy4 + timing10 + commute1 + q19check + feedback + q5t37 + q5t38 | 6.162102725e-05 | 0.4999892951 | screen only | pending | pending | pending | pending |
| `c13d` | copy4 + commute1 + q19check + q11measure + edge14to15 + q5t38 | 6.162270062e-05 | 0.4997533842 | screen only | pending | pending | pending | pending |
| `c1bd` | copy4 + commute1 + q19check + q11measure + edge14to15 + q5t37 + q5t38 | 6.162270062e-05 | 0.4992538806 | screen only | pending | pending | pending | pending |
| `c12d` | copy4 + commute1 + q19check + edge14to15 + q5t38 | 6.162270062e-05 | 0.500587001 | screen only | PASS / 0.500064 | FAST 7.10 / 4.12 | pending | pending |
| `c135` | copy4 + commute1 + q11measure + edge14to15 + q5t38 | 6.162270062e-05 | 0.500587001 | screen only | FAIL / 0.499671 | FAST 8.49 / 4.09 | pending | pending |
| `c125` | copy4 + commute1 + edge14to15 + q5t38 | 6.162270062e-05 | 0.5014220083 | screen only | PASS / 0.501427 | FAST 7.17 / 3.99 | pending | pending |
| `c1ad` | copy4 + commute1 + q19check + edge14to15 + q5t37 + q5t38 | 6.162270062e-05 | 0.5000866642 | screen only | pending | pending | pending | pending |
| `c1b5` | copy4 + commute1 + q11measure + edge14to15 + q5t37 + q5t38 | 6.162270062e-05 | 0.5000866642 | screen only | pending | pending | pending | pending |
| `c1a5` | copy4 + commute1 + edge14to15 + q5t37 + q5t38 | 6.162270062e-05 | 0.5009208369 | screen only | FAIL / 0.499870 | FAST 7.97 / 4.02 | pending | pending |
| `c145` | copy4 + commute1 + feedback + q5t38 | 6.16479141e-05 | 0.5013270494 | screen only | PASS / 0.500717 | FAST 7.15 / 4.09 | pending | pending |
| `c1c5` | copy4 + commute1 + feedback + q5t37 + q5t38 | 6.16479141e-05 | 0.5008259729 | screen only | PASS / 0.500453 | FAST 7.51 / 4.10 | pending | pending |
| `c14d` | copy4 + commute1 + q19check + feedback + q5t38 | 6.16479141e-05 | 0.5004922002 | screen only | PASS / 0.500261 | FAST 6.85 / 3.87 | pending | pending |
| `c155` | copy4 + commute1 + q11measure + feedback + q5t38 | 6.16479141e-05 | 0.5004922002 | screen only | PASS / 0.500241 | FAST 7.00 / 3.88 | pending | pending |
| `c15d` | copy4 + commute1 + q19check + q11measure + feedback + q5t38 | 6.16479141e-05 | 0.4996587413 | screen only | pending | pending | pending | pending |
| `c1dd` | copy4 + commute1 + q19check + q11measure + feedback + q5t37 + q5t38 | 6.16479141e-05 | 0.4991593323 | screen only | pending | pending | pending | pending |
| `c1d5` | copy4 + commute1 + q11measure + feedback + q5t37 + q5t38 | 6.16479141e-05 | 0.4999919582 | screen only | pending | pending | pending | pending |
| `c1cd` | copy4 + commute1 + q19check + feedback + q5t37 + q5t38 | 6.16479141e-05 | 0.4999919582 | screen only | pending | pending | pending | pending |
| `c0fb` | copy4 + timing10 + q19check + q11measure + edge14to15 + feedback + q5t37 | 6.167258073e-05 | 0.4992558493 | screen only | pending | pending | pending | pending |
| `c0f3` | copy4 + timing10 + q11measure + edge14to15 + feedback + q5t37 | 6.167258073e-05 | 0.5000886362 | screen only | pending | pending | pending | pending |
| `c0eb` | copy4 + timing10 + q19check + edge14to15 + feedback + q5t37 | 6.167258073e-05 | 0.5000886362 | screen only | pending | pending | pending | pending |
| `c0e3` | copy4 + timing10 + edge14to15 + feedback + q5t37 | 6.167258073e-05 | 0.5009228122 | screen only | PASS / 0.500248 | FAST 6.88 / 3.84 | pending | pending |
| `c0bf` | copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + q5t37 | 6.168095753e-05 | 0.4997507224 | screen only | pending | pending | pending | pending |
| `c0af` | copy4 + timing10 + commute1 + q19check + edge14to15 + q5t37 | 6.168095753e-05 | 0.5005843348 | screen only | FAIL / 0.499845 | FAST 6.64 / 3.87 | pending | pending |
| `c0b7` | copy4 + timing10 + commute1 + q11measure + edge14to15 + q5t37 | 6.168095753e-05 | 0.5005843348 | screen only | FAIL / 0.499741 | FAST 7.07 / 3.80 | pending | pending |
| `c0a7` | copy4 + timing10 + commute1 + edge14to15 + q5t37 | 6.168095753e-05 | 0.5014193376 | screen only | PASS / 0.500708 | FAST 6.35 / 3.75 | pending | pending |
| `c13b` | copy4 + timing10 + q19check + q11measure + edge14to15 + q5t38 | 6.168908661e-05 | 0.4997500561 | screen only | pending | pending | pending | pending |
| `c1bb` | copy4 + timing10 + q19check + q11measure + edge14to15 + q5t37 + q5t38 | 6.168908661e-05 | 0.4992505558 | screen only | pending | pending | pending | pending |
| `c133` | copy4 + timing10 + q11measure + edge14to15 + q5t38 | 6.168908661e-05 | 0.5005836673 | screen only | FAIL / 0.499864 | FAST 7.17 / 3.85 | pending | pending |
| `c12b` | copy4 + timing10 + q19check + edge14to15 + q5t38 | 6.168908661e-05 | 0.5005836673 | screen only | PASS / 0.500103 | FAST 6.35 / 3.83 | pending | pending |
| `c123` | copy4 + timing10 + edge14to15 + q5t38 | 6.168908661e-05 | 0.5014186691 | screen only | PASS / 0.500934 | FAST 6.66 / 3.88 | pending | pending |
| `c1b3` | copy4 + timing10 + q11measure + edge14to15 + q5t37 + q5t38 | 6.168908661e-05 | 0.5000833339 | screen only | pending | pending | pending | pending |
| `c1ab` | copy4 + timing10 + q19check + edge14to15 + q5t37 + q5t38 | 6.168908661e-05 | 0.5000833339 | screen only | pending | pending | pending | pending |
| `c1a3` | copy4 + timing10 + edge14to15 + q5t37 + q5t38 | 6.168908661e-05 | 0.500917501 | screen only | PASS / 0.500783 | FAST 6.48 / 3.84 | pending | pending |
| `c0f9` | copy4 + q19check + q11measure + edge14to15 + feedback + q5t37 | 6.169938869e-05 | 0.4992585085 | screen only | pending | pending | pending | pending |
| `c0f1` | copy4 + q11measure + edge14to15 + feedback + q5t37 | 6.169938869e-05 | 0.5000912998 | screen only | pending | pending | pending | pending |
| `c0e9` | copy4 + q19check + edge14to15 + feedback + q5t37 | 6.169938869e-05 | 0.5000912998 | screen only | pending | pending | pending | pending |
| `c0e1` | copy4 + edge14to15 + feedback + q5t37 | 6.169938869e-05 | 0.5009254803 | screen only | FAIL / 0.499831 | FAST 6.83 / 3.83 | pending | pending |
| `c0c7` | copy4 + timing10 + commute1 + feedback + q5t37 | 6.170607825e-05 | 0.5013243792 | screen only | PASS / 0.501703 | FAST 6.87 / 3.83 | pending | pending |
| `c0cf` | copy4 + timing10 + commute1 + q19check + feedback + q5t37 | 6.170607825e-05 | 0.5004895345 | screen only | PASS / 0.500001 | FAST 6.84 / 3.91 | pending | pending |
| `c0d7` | copy4 + timing10 + commute1 + q11measure + feedback + q5t37 | 6.170607825e-05 | 0.5004895345 | screen only | PASS / 0.500303 | FAST 6.89 / 3.89 | pending | pending |
| `c0df` | copy4 + timing10 + commute1 + q19check + q11measure + feedback + q5t37 | 6.170607825e-05 | 0.49965608 | screen only | pending | pending | pending | pending |
| `c0bd` | copy4 + commute1 + q19check + q11measure + edge14to15 + q5t37 | 6.170775162e-05 | 0.4997533842 | screen only | pending | pending | pending | pending |
| `c0ad` | copy4 + commute1 + q19check + edge14to15 + q5t37 | 6.170775162e-05 | 0.500587001 | screen only | FAIL / 0.499493 | FAST 7.19 / 3.86 | pending | pending |
| `c0b5` | copy4 + commute1 + q11measure + edge14to15 + q5t37 | 6.170775162e-05 | 0.500587001 | screen only | PASS / 0.500093 | FAST 7.18 / 3.88 | pending | pending |
| `c0a5` | copy4 + commute1 + edge14to15 + q5t37 | 6.170775162e-05 | 0.5014220083 | screen only | PASS / 0.500916 | FAST 7.20 / 3.81 | pending | pending |
| `c143` | copy4 + timing10 + feedback + q5t38 | 6.171532938e-05 | 0.5013237108 | screen only | PASS / 0.500723 | FAST 6.84 / 3.85 | pending | pending |
| `c1c3` | copy4 + timing10 + feedback + q5t37 + q5t38 | 6.171532938e-05 | 0.5008226377 | screen only | PASS / 0.501012 | FAST 8.04 / 3.82 | pending | pending |
| `c153` | copy4 + timing10 + q11measure + feedback + q5t38 | 6.171532938e-05 | 0.5004888672 | screen only | FAIL / 0.499870 | FAST 8.08 / 3.88 | pending | pending |
| `c14b` | copy4 + timing10 + q19check + feedback + q5t38 | 6.171532938e-05 | 0.5004888672 | screen only | FAIL / 0.499765 | FAST 7.10 / 3.85 | pending | pending |
| `c15b` | copy4 + timing10 + q19check + q11measure + feedback + q5t38 | 6.171532938e-05 | 0.4996554138 | screen only | pending | pending | pending | pending |
| `c1db` | copy4 + timing10 + q19check + q11measure + feedback + q5t37 + q5t38 | 6.171532938e-05 | 0.4991560081 | screen only | pending | pending | pending | pending |
| `c1d3` | copy4 + timing10 + q11measure + feedback + q5t37 + q5t38 | 6.171532938e-05 | 0.4999886285 | screen only | pending | pending | pending | pending |
| `c1cb` | copy4 + timing10 + q19check + feedback + q5t37 + q5t38 | 6.171532938e-05 | 0.4999886285 | screen only | pending | pending | pending | pending |
| `c139` | copy4 + q19check + q11measure + edge14to15 + q5t38 | 6.171585505e-05 | 0.4997527179 | screen only | pending | pending | pending | pending |
| `c1b9` | copy4 + q19check + q11measure + edge14to15 + q5t37 + q5t38 | 6.171585505e-05 | 0.4992532149 | screen only | pending | pending | pending | pending |
| `c131` | copy4 + q11measure + edge14to15 + q5t38 | 6.171585505e-05 | 0.5005863336 | screen only | PASS / 0.500935 | FAST 7.05 / 3.86 | pending | pending |
| `c129` | copy4 + q19check + edge14to15 + q5t38 | 6.171585505e-05 | 0.5005863336 | screen only | PASS / 0.500324 | FAST 6.74 / 3.83 | pending | pending |
| `c121` | copy4 + edge14to15 + q5t38 | 6.171585505e-05 | 0.5014213398 | screen only | PASS / 0.501602 | FAST 7.01 / 3.81 | pending | pending |
| `c1b1` | copy4 + q11measure + edge14to15 + q5t37 + q5t38 | 6.171585505e-05 | 0.5000859974 | screen only | pending | pending | pending | pending |
| `c1a9` | copy4 + q19check + edge14to15 + q5t37 + q5t38 | 6.171585505e-05 | 0.5000859974 | screen only | pending | pending | pending | pending |
| `c1a1` | copy4 + edge14to15 + q5t37 + q5t38 | 6.171585505e-05 | 0.500920169 | screen only | PASS / 0.500610 | FAST 6.65 / 3.84 | pending | pending |
| `c107` | copy4 + timing10 + commute1 + q5t38 | 6.172381163e-05 | 0.5018206336 | screen only | PASS / 0.501101 | FAST 6.87 / 3.73 | pending | pending |
| `c187` | copy4 + timing10 + commute1 + q5t37 + q5t38 | 6.172381163e-05 | 0.5013190638 | screen only | PASS / 0.500723 | FAST 6.73 / 3.80 | pending | pending |
| `c10f` | copy4 + timing10 + commute1 + q19check + q5t38 | 6.172381163e-05 | 0.5009849625 | screen only | PASS / 0.500815 | FAST 7.00 / 3.84 | pending | pending |
| `c117` | copy4 + timing10 + commute1 + q11measure + q5t38 | 6.172381163e-05 | 0.5009849625 | screen only | PASS / 0.500327 | FAST 7.22 / 3.84 | pending | pending |
| `c11f` | copy4 + timing10 + commute1 + q19check + q11measure + q5t38 | 6.172381163e-05 | 0.500150683 | screen only | pending | pending | pending | pending |
| `c19f` | copy4 + timing10 + commute1 + q19check + q11measure + q5t37 + q5t38 | 6.172381163e-05 | 0.4996507823 | screen only | pending | pending | pending | pending |
| `c197` | copy4 + timing10 + commute1 + q11measure + q5t37 + q5t38 | 6.172381163e-05 | 0.5004842279 | screen only | PASS / 0.500127 | FAST 6.91 / 3.89 | pending | pending |
| `c18f` | copy4 + timing10 + commute1 + q19check + q5t37 + q5t38 | 6.172381163e-05 | 0.5004842279 | screen only | FAIL / 0.498835 | FAST 7.18 / 3.83 | pending | pending |
| `c0c5` | copy4 + commute1 + feedback + q5t37 | 6.17329651e-05 | 0.5013270494 | screen only | PASS / 0.500730 | FAST 7.16 / 3.87 | pending | pending |
| `c0cd` | copy4 + commute1 + q19check + feedback + q5t37 | 6.17329651e-05 | 0.5004922002 | screen only | PASS / 0.500138 | FAST 6.77 / 3.87 | pending | pending |
| `c0d5` | copy4 + commute1 + q11measure + feedback + q5t37 | 6.17329651e-05 | 0.5004922002 | screen only | PASS / 0.500689 | FAST 7.31 / 3.87 | pending | pending |
| `c0dd` | copy4 + commute1 + q19check + q11measure + feedback + q5t37 | 6.17329651e-05 | 0.4996587413 | screen only | pending | pending | pending | pending |
| `c141` | copy4 + feedback + q5t38 | 6.174219083e-05 | 0.501326381 | screen only | PASS / 0.501278 | FAST 6.95 / 3.83 | pending | pending |
| `c1c1` | copy4 + feedback + q5t37 + q5t38 | 6.174219083e-05 | 0.5008253052 | screen only | PASS / 0.500699 | FAST 7.25 / 3.86 | pending | pending |
| `c149` | copy4 + q19check + feedback + q5t38 | 6.174219083e-05 | 0.5004915329 | screen only | FAIL / 0.499471 | FAST 7.05 / 3.86 | pending | pending |
| `c151` | copy4 + q11measure + feedback + q5t38 | 6.174219083e-05 | 0.5004915329 | screen only | FAIL / 0.499601 | FAST 7.19 / 3.93 | pending | pending |
| `c159` | copy4 + q19check + q11measure + feedback + q5t38 | 6.174219083e-05 | 0.4996580751 | screen only | pending | pending | pending | pending |
| `c1d9` | copy4 + q19check + q11measure + feedback + q5t37 + q5t38 | 6.174219083e-05 | 0.4991586668 | screen only | pending | pending | pending | pending |
| `c1d1` | copy4 + q11measure + feedback + q5t37 + q5t38 | 6.174219083e-05 | 0.4999912915 | screen only | pending | pending | pending | pending |
| `c1c9` | copy4 + q19check + feedback + q5t37 + q5t38 | 6.174219083e-05 | 0.4999912915 | screen only | pending | pending | pending | pending |
| `c105` | copy4 + commute1 + q5t38 | 6.175065906e-05 | 0.5018233064 | screen only | PASS / 0.501228 | FAST 7.27 / 3.72 | pending | pending |
| `c185` | copy4 + commute1 + q5t37 + q5t38 | 6.175065906e-05 | 0.5013217339 | screen only | PASS / 0.501350 | FAST 6.77 / 3.75 | pending | pending |
| `c115` | copy4 + commute1 + q11measure + q5t38 | 6.175065906e-05 | 0.5009876308 | screen only | PASS / 0.500685 | FAST 6.63 / 3.79 | pending | pending |
| `c10d` | copy4 + commute1 + q19check + q5t38 | 6.175065906e-05 | 0.5009876308 | screen only | PASS / 0.500699 | FAST 6.64 / 3.79 | pending | pending |
| `c11d` | copy4 + commute1 + q19check + q11measure + q5t38 | 6.175065906e-05 | 0.5001533469 | screen only | pending | pending | pending | pending |
| `c19d` | copy4 + commute1 + q19check + q11measure + q5t37 + q5t38 | 6.175065906e-05 | 0.4996534435 | screen only | pending | pending | pending | pending |
| `c195` | copy4 + commute1 + q11measure + q5t37 + q5t38 | 6.175065906e-05 | 0.5004868936 | screen only | PASS / 0.500513 | FAST 6.62 / 3.80 | pending | pending |
| `c18d` | copy4 + commute1 + q19check + q5t37 + q5t38 | 6.175065906e-05 | 0.5004868936 | screen only | FAIL / 0.499807 | FAST 6.91 / 3.79 | pending | pending |
| `c0bb` | copy4 + timing10 + q19check + q11measure + edge14to15 + q5t37 | 6.177413761e-05 | 0.4997500561 | screen only | pending | pending | pending | pending |
| `c0b3` | copy4 + timing10 + q11measure + edge14to15 + q5t37 | 6.177413761e-05 | 0.5005836673 | screen only | PASS / 0.500352 | FAST 6.77 / 3.82 | pending | pending |
| `c0ab` | copy4 + timing10 + q19check + edge14to15 + q5t37 | 6.177413761e-05 | 0.5005836673 | screen only | PASS / 0.500145 | FAST 6.43 / 3.78 | pending | pending |
| `c0a3` | copy4 + timing10 + edge14to15 + q5t37 | 6.177413761e-05 | 0.5014186691 | screen only | PASS / 0.501313 | FAST 7.00 / 3.80 | pending | pending |
| `c07f` | copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | 6.17860668e-05 | 0.4997564655 | screen only | pending | pending | pending | pending |
| `c077` | copy4 + timing10 + commute1 + q11measure + edge14to15 + feedback | 6.17860668e-05 | 0.5005900874 | screen only | PASS / 0.500860 | FAST 7.01 / 3.84 | pending | pending |
| `c0c3` | copy4 + timing10 + feedback + q5t37 | 6.180038038e-05 | 0.5013237108 | screen only | PASS / 0.501113 | FAST 6.53 / 3.78 | pending | pending |
| `c0cb` | copy4 + timing10 + q19check + feedback + q5t37 | 6.180038038e-05 | 0.5004888672 | screen only | FAIL / 0.499727 | FAST 6.62 / 3.80 | pending | pending |
| `c0d3` | copy4 + timing10 + q11measure + feedback + q5t37 | 6.180038038e-05 | 0.5004888672 | screen only | PASS / 0.500071 | FAST 7.32 / 3.76 | pending | pending |
| `c0db` | copy4 + timing10 + q19check + q11measure + feedback + q5t37 | 6.180038038e-05 | 0.4996554138 | screen only | pending | pending | pending | pending |
| `c0b9` | copy4 + q19check + q11measure + edge14to15 + q5t37 | 6.180090605e-05 | 0.4997527179 | screen only | pending | pending | pending | pending |
| `c0a9` | copy4 + q19check + edge14to15 + q5t37 | 6.180090605e-05 | 0.5005863336 | screen only | PASS / 0.500539 | FAST 6.87 / 3.77 | pending | pending |
| `c0b1` | copy4 + q11measure + edge14to15 + q5t37 | 6.180090605e-05 | 0.5005863336 | screen only | FAIL / 0.499614 | FAST 6.83 / 3.82 | pending | pending |
| `c0a1` | copy4 + edge14to15 + q5t37 | 6.180090605e-05 | 0.5014213398 | screen only | PASS / 0.500348 | FAST 6.81 / 3.78 | pending | pending |
| `c087` | copy4 + timing10 + commute1 + q5t37 | 6.180886263e-05 | 0.5018206336 | screen only | PASS / 0.501140 | FAST 6.92 / 3.74 | pending | pending |
| `c08f` | copy4 + timing10 + commute1 + q19check + q5t37 | 6.180886263e-05 | 0.5009849625 | screen only | PASS / 0.500626 | FAST 6.65 / 3.82 | pending | pending |
| `c097` | copy4 + timing10 + commute1 + q11measure + q5t37 | 6.180886263e-05 | 0.5009849625 | screen only | PASS / 0.500830 | FAST 7.08 / 3.75 | pending | pending |
| `c09f` | copy4 + timing10 + commute1 + q19check + q11measure + q5t37 | 6.180886263e-05 | 0.500150683 | screen only | pending | pending | pending | pending |
| `c07d` | copy4 + commute1 + q19check + q11measure + edge14to15 + feedback | 6.18129004e-05 | 0.4997591273 | screen only | pending | pending | pending | pending |
| `c075` | copy4 + commute1 + q11measure + edge14to15 + feedback | 6.18129004e-05 | 0.5005927537 | screen only | FAIL / 0.499847 | FAST 6.92 / 3.81 | pending | pending |
| `c103` | copy4 + timing10 + q5t38 | 6.181688413e-05 | 0.5018199645 | screen only | PASS / 0.501263 | FAST 6.65 / 3.67 | pending | pending |
| `c183` | copy4 + timing10 + q5t37 + q5t38 | 6.181688413e-05 | 0.5013183954 | screen only | PASS / 0.500766 | FAST 6.81 / 3.76 | pending | pending |
| `c113` | copy4 + timing10 + q11measure + q5t38 | 6.181688413e-05 | 0.5009842945 | screen only | FAIL / 0.499913 | FAST 6.67 / 3.80 | pending | pending |
| `c10b` | copy4 + timing10 + q19check + q5t38 | 6.181688413e-05 | 0.5009842945 | screen only | PASS / 0.500850 | FAST 6.67 / 3.80 | pending | pending |
| `c11b` | copy4 + timing10 + q19check + q11measure + q5t38 | 6.181688413e-05 | 0.5001500161 | screen only | pending | pending | pending | pending |
| `c19b` | copy4 + timing10 + q19check + q11measure + q5t37 + q5t38 | 6.181688413e-05 | 0.4996501161 | screen only | pending | pending | pending | pending |
| `c193` | copy4 + timing10 + q11measure + q5t37 + q5t38 | 6.181688413e-05 | 0.5004835606 | screen only | PASS / 0.501034 | FAST 6.92 / 3.85 | pending | pending |
| `c18b` | copy4 + timing10 + q19check + q5t37 + q5t38 | 6.181688413e-05 | 0.5004835606 | screen only | PASS / 0.500346 | FAST 6.88 / 3.90 | pending | pending |
| `c0c1` | copy4 + feedback + q5t37 | 6.182724183e-05 | 0.501326381 | screen only | PASS / 0.501403 | FAST 6.71 / 3.86 | pending | pending |
| `c0c9` | copy4 + q19check + feedback + q5t37 | 6.182724183e-05 | 0.5004915329 | screen only | PASS / 0.500071 | FAST 6.50 / 3.87 | pending | pending |
| `c0d1` | copy4 + q11measure + feedback + q5t37 | 6.182724183e-05 | 0.5004915329 | screen only | PASS / 0.500560 | FAST 6.80 / 3.85 | pending | pending |
| `c0d9` | copy4 + q19check + q11measure + feedback + q5t37 | 6.182724183e-05 | 0.4996580751 | screen only | pending | pending | pending | pending |
| `c06f` | copy4 + timing10 + commute1 + q19check + edge14to15 + feedback | 6.182862563e-05 | 0.5005900874 | screen only | PASS / 0.500352 | FAST 6.67 / 3.88 | pending | pending |
| `c067` | copy4 + timing10 + commute1 + edge14to15 + feedback | 6.182862563e-05 | 0.5014250999 | screen only | PASS / 0.500931 | FAST 6.81 / 3.82 | pending | pending |
| `c085` | copy4 + commute1 + q5t37 | 6.183571006e-05 | 0.5018233064 | screen only | PASS / 0.501044 | FAST 6.83 / 3.82 | pending | pending |
| `c08d` | copy4 + commute1 + q19check + q5t37 | 6.183571006e-05 | 0.5009876308 | screen only | PASS / 0.500751 | FAST 6.88 / 3.91 | pending | pending |
| `c095` | copy4 + commute1 + q11measure + q5t37 | 6.183571006e-05 | 0.5009876308 | screen only | PASS / 0.500907 | FAST 6.86 / 3.84 | pending | pending |
| `c09d` | copy4 + commute1 + q19check + q11measure + q5t37 | 6.183571006e-05 | 0.5001533469 | screen only | pending | pending | pending | pending |
| `c101` | copy4 + q5t38 | 6.184370616e-05 | 0.5018226373 | screen only | PASS / 0.501393 | FAST 6.99 / 3.91 | pending | pending |
| `c181` | copy4 + q5t37 + q5t38 | 6.184370616e-05 | 0.5013210655 | screen only | PASS / 0.500823 | FAST 6.76 / 3.87 | pending | pending |
| `c109` | copy4 + q19check + q5t38 | 6.184370616e-05 | 0.5009869628 | screen only | PASS / 0.501617 | FAST 6.74 / 3.86 | pending | pending |
| `c111` | copy4 + q11measure + q5t38 | 6.184370616e-05 | 0.5009869628 | screen only | PASS / 0.501106 | FAST 6.93 / 3.90 | pending | pending |
| `c119` | copy4 + q19check + q11measure + q5t38 | 6.184370616e-05 | 0.50015268 | screen only | pending | pending | pending | pending |
| `c199` | copy4 + q19check + q11measure + q5t37 + q5t38 | 6.184370616e-05 | 0.4996527773 | screen only | pending | pending | pending | pending |
| `c191` | copy4 + q11measure + q5t37 + q5t38 | 6.184370616e-05 | 0.5004862263 | screen only | PASS / 0.500625 | FAST 7.30 / 3.88 | pending | pending |
| `c189` | copy4 + q19check + q5t37 + q5t38 | 6.184370616e-05 | 0.5004862263 | screen only | PASS / 0.500549 | FAST 7.32 / 3.87 | pending | pending |
| `c06d` | copy4 + commute1 + q19check + edge14to15 + feedback | 6.185545924e-05 | 0.5005927537 | screen only | PASS / 0.500952 | FAST 7.28 / 3.92 | pending | pending |
| `c065` | copy4 + commute1 + edge14to15 + feedback | 6.185545924e-05 | 0.5014277706 | screen only | PASS / 0.500548 | FAST 6.84 / 3.86 | pending | pending |
| `c07b` | copy4 + timing10 + q19check + q11measure + edge14to15 + feedback | 6.188047651e-05 | 0.4997557991 | screen only | pending | pending | pending | pending |
| `c073` | copy4 + timing10 + q11measure + edge14to15 + feedback | 6.188047651e-05 | 0.5005894199 | screen only | FAIL / 0.499638 | FAST 7.34 / 3.95 | pending | pending |
| `c03f` | copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | 6.188888216e-05 | 0.5002511678 | screen only | FAIL / 0.499904 | FAST 6.78 / 3.97 | pending | pending |
| `c037` | copy4 + timing10 + commute1 + q11measure + edge14to15 | 6.188888216e-05 | 0.5010856149 | screen only | PASS / 0.500842 | FAST 7.17 / 3.91 | pending | pending |
| `c083` | copy4 + timing10 + q5t37 | 6.190193513e-05 | 0.5018199645 | screen only | PASS / 0.501482 | FAST 6.66 / 3.85 | pending | pending |
| `c093` | copy4 + timing10 + q11measure + q5t37 | 6.190193513e-05 | 0.5009842945 | screen only | PASS / 0.501481 | FAST 6.76 / 3.94 | pending | pending |
| `c08b` | copy4 + timing10 + q19check + q5t37 | 6.190193513e-05 | 0.5009842945 | screen only | PASS / 0.500397 | FAST 7.11 / 3.92 | pending | pending |
| `c09b` | copy4 + timing10 + q19check + q11measure + q5t37 | 6.190193513e-05 | 0.5001500161 | screen only | pending | pending | pending | pending |
| `c079` | copy4 + q19check + q11measure + edge14to15 + feedback | 6.190728447e-05 | 0.4997584609 | screen only | pending | pending | pending | pending |
| `c071` | copy4 + q11measure + edge14to15 + feedback | 6.190728447e-05 | 0.5005920862 | screen only | PASS / 0.500329 | FAST 7.30 / 3.89 | pending | pending |
| `c057` | copy4 + timing10 + commute1 + q11measure + feedback | 6.191397403e-05 | 0.5009907197 | screen only | PASS / 0.500895 | FAST 7.14 / 3.92 | pending | pending |
| `c05f` | copy4 + timing10 + commute1 + q19check + q11measure + feedback | 6.191397403e-05 | 0.5001564306 | screen only | pending | pending | pending | pending |
| `c03d` | copy4 + commute1 + q19check + q11measure + edge14to15 | 6.191567625e-05 | 0.5002538322 | screen only | PASS / 0.500015 | FAST 7.40 / 3.91 | pending | pending |
| `c035` | copy4 + commute1 + q11measure + edge14to15 | 6.191567625e-05 | 0.5010882838 | screen only | PASS / 0.500876 | FAST 7.42 / 3.93 | pending | pending |
| `c06b` | copy4 + timing10 + q19check + edge14to15 + feedback | 6.192303534e-05 | 0.5005894199 | screen only | PASS / 0.500226 | FAST 7.07 / 3.91 | pending | pending |
| `c063` | copy4 + timing10 + edge14to15 + feedback | 6.192303534e-05 | 0.5014244313 | screen only | PASS / 0.500863 | FAST 6.91 / 3.89 | pending | pending |
| `c081` | copy4 + q5t37 | 6.192875716e-05 | 0.5018226373 | screen only | PASS / 0.501641 | FAST 6.95 / 3.89 | pending | pending |
| `c089` | copy4 + q19check + q5t37 | 6.192875716e-05 | 0.5009869628 | screen only | PASS / 0.500712 | FAST 7.00 / 3.90 | pending | pending |
| `c091` | copy4 + q11measure + q5t37 | 6.192875716e-05 | 0.5009869628 | screen only | PASS / 0.500077 | FAST 7.02 / 3.87 | pending | pending |
| `c099` | copy4 + q19check + q11measure + q5t37 | 6.192875716e-05 | 0.50015268 | screen only | pending | pending | pending | pending |
| `c166` | timing10 + commute1 + edge14to15 + feedback + q5t38 | 6.192925772e-05 | 0.5061602684 | screen only | PASS / 0.505815 | FAST 8.05 / 3.98 | pending | pending |
| `c16e` | timing10 + commute1 + q19check + edge14to15 + feedback + q5t38 | 6.192925772e-05 | 0.5053173706 | screen only | PASS / 0.505307 | FAST 7.70 / 3.96 | pending | pending |
| `c176` | timing10 + commute1 + q11measure + edge14to15 + feedback + q5t38 | 6.192925772e-05 | 0.5053173706 | screen only | PASS / 0.504965 | FAST 7.41 / 3.98 | pending | pending |
| `c17e` | timing10 + commute1 + q19check + q11measure + edge14to15 + feedback + q5t38 | 6.192925772e-05 | 0.5044758764 | screen only | PASS / 0.504450 | FAST 7.59 / 4.07 | pending | pending |
| `c1e6` | timing10 + commute1 + edge14to15 + feedback + q5t37 + q5t38 | 6.192925772e-05 | 0.5056543611 | screen only | PASS / 0.505079 | FAST 7.56 / 3.98 | pending | pending |
| `c1ee` | timing10 + commute1 + q19check + edge14to15 + feedback + q5t37 + q5t38 | 6.192925772e-05 | 0.5048123058 | screen only | PASS / 0.504579 | FAST 7.43 / 3.95 | pending | pending |
| `c1f6` | timing10 + commute1 + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.192925772e-05 | 0.5048123058 | screen only | PASS / 0.504304 | FAST 7.66 / 3.97 | pending | pending |
| `c1fe` | timing10 + commute1 + q19check + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.192925772e-05 | 0.5039716527 | screen only | PASS / 0.503646 | FAST 7.62 / 3.95 | pending | pending |
| `c02f` | copy4 + timing10 + commute1 + q19check + edge14to15 | 6.193144099e-05 | 0.5010856149 | screen only | PASS / 0.501153 | FAST 6.97 / 3.85 | pending | pending |
| `c027` | copy4 + timing10 + commute1 + edge14to15 | 6.193144099e-05 | 0.5019214539 | screen only | PASS / 0.501645 | FAST 6.99 / 3.81 | pending | pending |
| `c055` | copy4 + commute1 + q11measure + feedback | 6.194086088e-05 | 0.5009933881 | screen only | PASS / 0.501110 | FAST 7.67 / 3.86 | pending | pending |
| `c05d` | copy4 + commute1 + q19check + q11measure + feedback | 6.194086088e-05 | 0.5001590946 | screen only | pending | pending | pending | pending |
| `c069` | copy4 + q19check + edge14to15 + feedback | 6.19498433e-05 | 0.5005920862 | screen only | PASS / 0.500504 | FAST 6.86 / 3.86 | pending | pending |
| `c061` | copy4 + edge14to15 + feedback | 6.19498433e-05 | 0.501427102 | screen only | PASS / 0.500223 | FAST 7.39 / 3.84 | pending | pending |
| `c164` | commute1 + edge14to15 + feedback + q5t38 | 6.195609133e-05 | 0.5061629643 | screen only | PASS / 0.506114 | FAST 7.93 / 4.04 | pending | pending |
| `c16c` | commute1 + q19check + edge14to15 + feedback + q5t38 | 6.195609133e-05 | 0.505320062 | screen only | PASS / 0.504147 | FAST 7.53 / 3.96 | pending | pending |
| `c174` | commute1 + q11measure + edge14to15 + feedback + q5t38 | 6.195609133e-05 | 0.505320062 | screen only | PASS / 0.504859 | FAST 7.59 / 3.94 | pending | pending |
| `c17c` | commute1 + q19check + q11measure + edge14to15 + feedback + q5t38 | 6.195609133e-05 | 0.5044785634 | screen only | PASS / 0.504237 | FAST 7.34 / 3.95 | pending | pending |
| `c1e4` | commute1 + edge14to15 + feedback + q5t37 + q5t38 | 6.195609133e-05 | 0.5056570544 | screen only | PASS / 0.505508 | FAST 7.80 / 3.93 | pending | pending |
| `c1ec` | commute1 + q19check + edge14to15 + feedback + q5t37 + q5t38 | 6.195609133e-05 | 0.5048149945 | screen only | PASS / 0.504933 | FAST 7.55 / 3.99 | pending | pending |
| `c1f4` | commute1 + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.195609133e-05 | 0.5048149945 | screen only | PASS / 0.504563 | FAST 7.28 / 3.94 | pending | pending |
| `c1fc` | commute1 + q19check + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.195609133e-05 | 0.5039743369 | screen only | PASS / 0.503483 | FAST 7.16 / 3.95 | pending | pending |
| `c047` | copy4 + timing10 + commute1 + feedback | 6.195653286e-05 | 0.5018264004 | screen only | PASS / 0.501253 | FAST 6.79 / 3.88 | pending | pending |
| `c04f` | copy4 + timing10 + commute1 + q19check + feedback | 6.195653286e-05 | 0.5009907197 | screen only | PASS / 0.500665 | FAST 6.92 / 3.86 | pending | pending |
| `c02d` | copy4 + commute1 + q19check + edge14to15 | 6.195823508e-05 | 0.5010882838 | screen only | PASS / 0.500655 | FAST 7.02 / 3.90 | pending | pending |
| `c025` | copy4 + commute1 + edge14to15 | 6.195823508e-05 | 0.5019241273 | screen only | PASS / 0.501018 | FAST 6.88 / 3.80 | pending | pending |
| `c03b` | copy4 + timing10 + q19check + q11measure + edge14to15 | 6.198206224e-05 | 0.5002505008 | screen only | PASS / 0.500041 | FAST 7.29 / 3.88 | pending | pending |
| `c033` | copy4 + timing10 + q11measure + edge14to15 | 6.198206224e-05 | 0.5010849468 | screen only | PASS / 0.501112 | FAST 6.69 / 3.90 | pending | pending |
| `c045` | copy4 + commute1 + feedback | 6.198341971e-05 | 0.5018290733 | screen only | PASS / 0.500780 | FAST 7.29 / 3.83 | pending | pending |
| `c04d` | copy4 + commute1 + q19check + feedback | 6.198341971e-05 | 0.5009933881 | screen only | PASS / 0.500783 | FAST 6.95 / 3.92 | pending | pending |
| `c053` | copy4 + timing10 + q11measure + feedback | 6.200827616e-05 | 0.5009900517 | screen only | PASS / 0.500468 | FAST 7.10 / 3.88 | pending | pending |
| `c05b` | copy4 + timing10 + q19check + q11measure + feedback | 6.200827616e-05 | 0.5001557637 | screen only | pending | pending | pending | pending |
| `c039` | copy4 + q19check + q11measure + edge14to15 | 6.200883068e-05 | 0.5002531652 | screen only | FAIL / 0.498835 | FAST 6.90 / 3.90 | pending | pending |
| `c031` | copy4 + q11measure + edge14to15 | 6.200883068e-05 | 0.5010876157 | screen only | PASS / 0.501010 | FAST 7.53 / 3.82 | pending | pending |
| `c0e6` | timing10 + commute1 + edge14to15 + feedback + q5t37 | 6.201678724e-05 | 0.5061602684 | screen only | PASS / 0.505840 | FAST 7.98 / 3.91 | pending | pending |
| `c0ee` | timing10 + commute1 + q19check + edge14to15 + feedback + q5t37 | 6.201678724e-05 | 0.5053173706 | screen only | PASS / 0.505248 | FAST 7.82 / 3.89 | pending | pending |
| `c0f6` | timing10 + commute1 + q11measure + edge14to15 + feedback + q5t37 | 6.201678724e-05 | 0.5053173706 | screen only | PASS / 0.504076 | FAST 7.43 / 3.96 | pending | pending |
| `c0fe` | timing10 + commute1 + q19check + q11measure + edge14to15 + feedback + q5t37 | 6.201678724e-05 | 0.5044758764 | screen only | PASS / 0.503697 | FAST 7.40 / 3.98 | pending | pending |
| `c017` | copy4 + timing10 + commute1 + q11measure | 6.201678726e-05 | 0.5014866438 | screen only | PASS / 0.501269 | FAST 7.01 / 3.83 | pending | pending |
| `c01f` | copy4 + timing10 + commute1 + q19check + q11measure | 6.201678726e-05 | 0.5006515288 | screen only | FAIL / 0.499984 | FAST 6.94 / 3.85 | pending | pending |
| `c162` | timing10 + edge14to15 + feedback + q5t38 | 6.202373046e-05 | 0.5061595935 | screen only | PASS / 0.505683 | FAST 7.63 / 3.93 | pending | pending |
| `c16a` | timing10 + q19check + edge14to15 + feedback + q5t38 | 6.202373046e-05 | 0.5053166968 | screen only | PASS / 0.504741 | FAST 7.58 / 3.94 | pending | pending |
| `c172` | timing10 + q11measure + edge14to15 + feedback + q5t38 | 6.202373046e-05 | 0.5053166968 | screen only | PASS / 0.505395 | FAST 7.81 / 3.90 | pending | pending |
| `c17a` | timing10 + q19check + q11measure + edge14to15 + feedback + q5t38 | 6.202373046e-05 | 0.5044752038 | screen only | PASS / 0.504438 | FAST 7.41 / 3.94 | pending | pending |
| `c1e2` | timing10 + edge14to15 + feedback + q5t37 + q5t38 | 6.202373046e-05 | 0.5056536869 | screen only | PASS / 0.505746 | FAST 7.82 / 3.93 | pending | pending |
| `c1fa` | timing10 + q19check + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.202373046e-05 | 0.5039709807 | screen only | PASS / 0.503504 | FAST 7.22 / 3.92 | pending | pending |
| `c1f2` | timing10 + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.202373046e-05 | 0.5048116327 | screen only | PASS / 0.504807 | FAST 7.66 / 3.89 | pending | pending |
| `c1ea` | timing10 + q19check + edge14to15 + feedback + q5t37 + q5t38 | 6.202373046e-05 | 0.5048116327 | screen only | PASS / 0.503880 | FAST 7.73 / 3.96 | pending | pending |
| `c02b` | copy4 + timing10 + q19check + edge14to15 | 6.202462108e-05 | 0.5010849468 | screen only | PASS / 0.500415 | FAST 6.79 / 3.81 | pending | pending |
| `c023` | copy4 + timing10 + edge14to15 | 6.202462108e-05 | 0.5019207847 | screen only | PASS / 0.501571 | FAST 6.91 / 4.04 | pending | pending |
| `c126` | timing10 + commute1 + edge14to15 + q5t38 | 6.203208344e-05 | 0.5066613098 | screen only | PASS / 0.506629 | FAST 7.94 / 4.36 | pending | pending |
| `c12e` | timing10 + commute1 + q19check + edge14to15 + q5t38 | 6.203208344e-05 | 0.5058175775 | screen only | PASS / 0.505042 | FAST 7.20 / 4.28 | pending | pending |
| `c136` | timing10 + commute1 + q11measure + edge14to15 + q5t38 | 6.203208344e-05 | 0.5058175775 | screen only | PASS / 0.504749 | FAST 7.55 / 4.11 | pending | pending |
| `c13e` | timing10 + commute1 + q19check + q11measure + edge14to15 + q5t38 | 6.203208344e-05 | 0.5049752504 | screen only | PASS / 0.505093 | FAST 10.23 / 5.78 | pending | pending |
| `c1a6` | timing10 + commute1 + edge14to15 + q5t37 + q5t38 | 6.203208344e-05 | 0.5061549017 | screen only | PASS / 0.506201 | FAST 10.80 / 6.82 | pending | pending |
| `c1ae` | timing10 + commute1 + q19check + edge14to15 + q5t37 + q5t38 | 6.203208344e-05 | 0.5053120128 | screen only | PASS / 0.504964 | FAST 8.51 / 4.18 | pending | pending |
| `c1b6` | timing10 + commute1 + q11measure + edge14to15 + q5t37 + q5t38 | 6.203208344e-05 | 0.5053120128 | screen only | PASS / 0.505152 | FAST 12.84 / 6.62 | pending | pending |
| `c1be` | timing10 + commute1 + q19check + q11measure + edge14to15 + q5t37 + q5t38 | 6.203208344e-05 | 0.5044705275 | screen only | PASS / 0.504457 | FAST 7.47 / 4.07 | pending | pending |
| `c051` | copy4 + q11measure + feedback | 6.203513761e-05 | 0.5009927201 | screen only | PASS / 0.501085 | FAST 12.37 / 7.19 | pending | pending |
| `c059` | copy4 + q19check + q11measure + feedback | 6.203513761e-05 | 0.5001584277 | screen only | pending | pending | pending | pending |
| `c0e4` | commute1 + edge14to15 + feedback + q5t37 | 6.204362085e-05 | 0.5061629643 | screen only | PASS / 0.505693 | FAST 8.05 / 4.16 | pending | pending |
| `c0ec` | commute1 + q19check + edge14to15 + feedback + q5t37 | 6.204362085e-05 | 0.505320062 | screen only | PASS / 0.504012 | FAST 9.24 / 4.15 | pending | pending |
| `c0f4` | commute1 + q11measure + edge14to15 + feedback + q5t37 | 6.204362085e-05 | 0.505320062 | screen only | PASS / 0.504715 | FAST 7.74 / 4.12 | pending | pending |
| `c0fc` | commute1 + q19check + q11measure + edge14to15 + feedback + q5t37 | 6.204362085e-05 | 0.5044785634 | screen only | PASS / 0.504137 | FAST 12.58 / 6.61 | pending | pending |
| `c015` | copy4 + commute1 + q11measure | 6.204363469e-05 | 0.5014893148 | screen only | PASS / 0.501216 | FAST 12.75 / 7.48 | pending | pending |
| `c01d` | copy4 + commute1 + q19check + q11measure | 6.204363469e-05 | 0.5006541954 | screen only | FAIL / 0.499686 | FAST 10.71 / 4.15 | pending | pending |
| `c168` | q19check + edge14to15 + feedback + q5t38 | 6.205053842e-05 | 0.5053193883 | screen only | PASS / 0.504971 | FAST 8.22 / 4.20 | pending | pending |
| `c170` | q11measure + edge14to15 + feedback + q5t38 | 6.205053842e-05 | 0.5053193883 | screen only | PASS / 0.504895 | FAST 9.45 / 4.32 | pending | pending |
| `c160` | edge14to15 + feedback + q5t38 | 6.205053842e-05 | 0.5061622895 | screen only | PASS / 0.505875 | FAST 9.03 / 4.27 | pending | pending |
| `c178` | q19check + q11measure + edge14to15 + feedback + q5t38 | 6.205053842e-05 | 0.5044778907 | screen only | PASS / 0.504839 | FAST 8.30 / 6.00 | pending | pending |
| `c1e0` | edge14to15 + feedback + q5t37 + q5t38 | 6.205053842e-05 | 0.5056563802 | screen only | PASS / 0.504744 | FAST 14.08 / 4.59 | pending | pending |
| `c1f8` | q19check + q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.205053842e-05 | 0.503973665 | screen only | PASS / 0.503513 | FAST 13.04 / 7.17 | pending | pending |
| `c1e8` | q19check + edge14to15 + feedback + q5t37 + q5t38 | 6.205053842e-05 | 0.5048143214 | screen only | PASS / 0.504207 | FAST 8.16 / 4.74 | pending | pending |
| `c1f0` | q11measure + edge14to15 + feedback + q5t37 + q5t38 | 6.205053842e-05 | 0.5048143214 | screen only | PASS / 0.503374 | FAST 12.12 / 6.66 | pending | pending |
| `c043` | copy4 + timing10 + feedback | 6.2050835e-05 | 0.5018257313 | screen only | PASS / 0.500856 | FAST 11.32 / 6.48 | pending | pending |
| `c04b` | copy4 + timing10 + q19check + feedback | 6.2050835e-05 | 0.5009900517 | screen only | PASS / 0.501167 | FAST 7.53 / 4.08 | pending | pending |
| `c029` | copy4 + q19check + edge14to15 | 6.205138951e-05 | 0.5010876157 | screen only | PASS / 0.500519 | FAST 7.60 / 4.06 | pending | pending |
| `c021` | copy4 + edge14to15 | 6.205138951e-05 | 0.501923458 | screen only | PASS / 0.501631 | FAST 13.29 / 6.71 | pending | pending |
| `c146` | timing10 + commute1 + feedback + q5t38 | 6.205716496e-05 | 0.5065653586 | screen only | PASS / 0.505983 | FAST 12.99 / 4.22 | pending | pending |
| `c14e` | timing10 + commute1 + q19check + feedback + q5t38 | 6.205716496e-05 | 0.5057217862 | screen only | PASS / 0.505310 | FAST 8.31 / 4.17 | pending | pending |
| `c156` | timing10 + commute1 + q11measure + feedback + q5t38 | 6.205716496e-05 | 0.5057217862 | screen only | PASS / 0.505904 | FAST 13.09 / 4.17 | pending | pending |
| `c15e` | timing10 + commute1 + q19check + q11measure + feedback + q5t38 | 6.205716496e-05 | 0.5048796186 | screen only | PASS / 0.504319 | FAST 12.85 / 4.32 | pending | pending |
| `c1ce` | timing10 + commute1 + q19check + feedback + q5t37 + q5t38 | 6.205716496e-05 | 0.5052163172 | screen only | PASS / 0.504730 | FAST 7.97 / 4.11 | pending | pending |
| `c1d6` | timing10 + commute1 + q11measure + feedback + q5t37 + q5t38 | 6.205716496e-05 | 0.5052163172 | screen only | PASS / 0.504653 | FAST 8.13 / 4.51 | pending | pending |
| `c1c6` | timing10 + commute1 + feedback + q5t37 + q5t38 | 6.205716496e-05 | 0.5060590465 | screen only | PASS / 0.505053 | FAST 8.41 / 4.24 | pending | pending |
| `c1de` | timing10 + commute1 + q19check + q11measure + feedback + q5t37 + q5t38 | 6.205716496e-05 | 0.5043749913 | screen only | PASS / 0.503517 | FAST 12.28 / 4.56 | pending | pending |
| `c124` | commute1 + edge14to15 + q5t38 | 6.205887753e-05 | 0.5066640084 | screen only | PASS / 0.506322 | FAST 9.43 / 6.36 | pending | pending |
| `c12c` | commute1 + q19check + edge14to15 + q5t38 | 6.205887753e-05 | 0.5058202717 | screen only | PASS / 0.505617 | FAST 7.99 / 4.14 | pending | pending |
| `c134` | commute1 + q11measure + edge14to15 + q5t38 | 6.205887753e-05 | 0.5058202717 | screen only | PASS / 0.504857 | FAST 9.70 / 5.07 | pending | pending |
| `c13c` | commute1 + q19check + q11measure + edge14to15 + q5t38 | 6.205887753e-05 | 0.50497794 | screen only | PASS / 0.504768 | FAST 8.20 / 4.11 | pending | pending |
| `c1a4` | commute1 + edge14to15 + q5t37 + q5t38 | 6.205887753e-05 | 0.5061575976 | screen only | PASS / 0.505453 | FAST 14.70 / 7.52 | pending | pending |
| `c1ac` | commute1 + q19check + edge14to15 + q5t37 + q5t38 | 6.205887753e-05 | 0.5053147042 | screen only | PASS / 0.504883 | FAST 8.29 / 4.12 | pending | pending |
| `c1b4` | commute1 + q11measure + edge14to15 + q5t37 + q5t38 | 6.205887753e-05 | 0.5053147042 | screen only | PASS / 0.504874 | FAST 7.85 / 4.16 | pending | pending |
| `c1bc` | commute1 + q19check + q11measure + edge14to15 + q5t37 + q5t38 | 6.205887753e-05 | 0.5044732145 | screen only | PASS / 0.503622 | FAST 7.94 / 4.12 | pending | pending |
| `c007` | copy4 + timing10 + commute1 | 6.20593461e-05 | 0.5023231517 | screen only | PASS / 0.502229 | FAST 7.13 / 4.05 | pending | pending |
| `c00f` | copy4 + timing10 + commute1 + q19check | 6.20593461e-05 | 0.5014866438 | screen only | PASS / 0.502049 | FAST 7.55 / 3.99 | pending | pending |
| `c041` | copy4 + feedback | 6.207769644e-05 | 0.5018284042 | screen only | PASS / 0.501081 | FAST 7.58 / 4.04 | pending | pending |
| `c049` | copy4 + q19check + feedback | 6.207769644e-05 | 0.5009927201 | screen only | PASS / 0.500561 | FAST 7.10 / 4.05 | pending | pending |
| `c144` | commute1 + feedback + q5t38 | 6.20840518e-05 | 0.5065680567 | screen only | PASS / 0.506078 | FAST 11.96 / 5.80 | pending | pending |
| `c154` | commute1 + q11measure + feedback + q5t38 | 6.20840518e-05 | 0.5057244798 | screen only | PASS / 0.505139 | FAST 8.20 / 4.09 | pending | pending |
| `c14c` | commute1 + q19check + feedback + q5t38 | 6.20840518e-05 | 0.5057244798 | screen only | PASS / 0.505743 | FAST 11.99 / 6.48 | pending | pending |
| `c15c` | commute1 + q19check + q11measure + feedback + q5t38 | 6.20840518e-05 | 0.5048823077 | screen only | PASS / 0.505048 | FAST 8.34 / 4.18 | pending | pending |
| `c1cc` | commute1 + q19check + feedback + q5t37 + q5t38 | 6.20840518e-05 | 0.5052190081 | screen only | PASS / 0.503823 | FAST 13.86 / 5.78 | pending | pending |
| `c1c4` | commute1 + feedback + q5t37 + q5t38 | 6.20840518e-05 | 0.5060617419 | screen only | PASS / 0.505369 | FAST 7.82 / 4.30 | pending | pending |
| `c1d4` | commute1 + q11measure + feedback + q5t37 + q5t38 | 6.20840518e-05 | 0.5052190081 | screen only | PASS / 0.505371 | FAST 8.22 / 4.59 | pending | pending |
| `c1dc` | commute1 + q19check + q11measure + feedback + q5t37 + q5t38 | 6.20840518e-05 | 0.5043776777 | screen only | PASS / 0.504196 | FAST 7.94 / 4.46 | pending | pending |
| `c005` | copy4 + commute1 | 6.208619352e-05 | 0.5023258272 | screen only | PASS / 0.502129 | FAST 6.99 / 6.37 | pending | pending |
| `c00d` | copy4 + commute1 + q19check | 6.208619352e-05 | 0.5014893148 | screen only | PASS / 0.500352 | FAST 12.25 / 5.76 | pending | pending |
| `c013` | copy4 + timing10 + q11measure | 6.210985976e-05 | 0.5014859751 | screen only | PASS / 0.501435 | FAST 8.27 / 5.02 | pending | pending |
| `c01b` | copy4 + timing10 + q19check + q11measure | 6.210985976e-05 | 0.5006508613 | screen only | PASS / 0.500619 | FAST 8.43 / 4.20 | pending | pending |
| `c0e2` | timing10 + edge14to15 + feedback + q5t37 | 6.211125998e-05 | 0.5061595935 | screen only | PASS / 0.505567 | FAST 7.86 / 4.12 | pending | pending |
| `c0ea` | timing10 + q19check + edge14to15 + feedback + q5t37 | 6.211125998e-05 | 0.5053166968 | screen only | PASS / 0.505503 | FAST 8.92 / 4.16 | pending | pending |
| `c0f2` | timing10 + q11measure + edge14to15 + feedback + q5t37 | 6.211125998e-05 | 0.5053166968 | screen only | PASS / 0.505419 | FAST 12.55 / 6.39 | pending | pending |
| `c0fa` | timing10 + q19check + q11measure + edge14to15 + feedback + q5t37 | 6.211125998e-05 | 0.5044752038 | screen only | PASS / 0.503602 | FAST 11.72 / 5.71 | pending | pending |
| `c0a6` | timing10 + commute1 + edge14to15 + q5t37 | 6.211961296e-05 | 0.5066613098 | screen only | PASS / 0.506256 | FAST 12.13 / 5.81 | pending | pending |
| `c0ae` | timing10 + commute1 + q19check + edge14to15 + q5t37 | 6.211961296e-05 | 0.5058175775 | screen only | PASS / 0.504741 | FAST 12.89 / 4.56 | pending | pending |
| `c0b6` | timing10 + commute1 + q11measure + edge14to15 + q5t37 | 6.211961296e-05 | 0.5058175775 | screen only | PASS / 0.506089 | FAST 9.05 / 4.91 | pending | pending |
| `c0be` | timing10 + commute1 + q19check + q11measure + edge14to15 + q5t37 | 6.211961296e-05 | 0.5049752504 | screen only | PASS / 0.504833 | FAST 12.35 / 5.46 | pending | pending |
| `c122` | timing10 + edge14to15 + q5t38 | 6.212532655e-05 | 0.5066606342 | screen only | PASS / 0.506495 | FAST 7.81 / 4.75 | pending | pending |
| `c12a` | timing10 + q19check + edge14to15 + q5t38 | 6.212532655e-05 | 0.5058169031 | screen only | PASS / 0.505512 | FAST 8.04 / 5.16 | pending | pending |
| `c132` | timing10 + q11measure + edge14to15 + q5t38 | 6.212532655e-05 | 0.5058169031 | screen only | PASS / 0.505411 | FAST 7.80 / 4.14 | pending | pending |
| `c13a` | timing10 + q19check + q11measure + edge14to15 + q5t38 | 6.212532655e-05 | 0.5049745771 | screen only | PASS / 0.504099 | FAST 7.98 / 4.12 | pending | pending |
| `c1a2` | timing10 + edge14to15 + q5t37 + q5t38 | 6.212532655e-05 | 0.5061542268 | screen only | PASS / 0.506072 | FAST 12.64 / 6.14 | pending | pending |
| `c1ba` | timing10 + q19check + q11measure + edge14to15 + q5t37 + q5t38 | 6.212532655e-05 | 0.5044698549 | screen only | PASS / 0.504016 | FAST 7.77 / 7.03 | pending | pending |
| `c1aa` | timing10 + q19check + edge14to15 + q5t37 + q5t38 | 6.212532655e-05 | 0.505311339 | screen only | PASS / 0.504680 | FAST 7.98 / 4.19 | pending | pending |
| `c1b2` | timing10 + q11measure + edge14to15 + q5t37 + q5t38 | 6.212532655e-05 | 0.505311339 | screen only | PASS / 0.504985 | FAST 13.10 / 7.45 | pending | pending |
| `c011` | copy4 + q11measure | 6.213668179e-05 | 0.5014886462 | screen only | PASS / 0.500909 | FAST 11.49 / 6.54 | pending | pending |
| `c019` | copy4 + q19check + q11measure | 6.213668179e-05 | 0.5006535279 | screen only | PASS / 0.500155 | FAST 7.76 / 4.18 | pending | pending |
| `c0e8` | q19check + edge14to15 + feedback + q5t37 | 6.213806794e-05 | 0.5053193883 | screen only | PASS / 0.505121 | FAST 7.62 / 4.20 | pending | pending |
| `c0f0` | q11measure + edge14to15 + feedback + q5t37 | 6.213806794e-05 | 0.5053193883 | screen only | PASS / 0.504662 | FAST 8.12 / 4.43 | pending | pending |
| `c0e0` | edge14to15 + feedback + q5t37 | 6.213806794e-05 | 0.5061622895 | screen only | PASS / 0.506392 | FAST 11.45 / 4.48 | pending | pending |
| `c0f8` | q19check + q11measure + edge14to15 + feedback + q5t37 | 6.213806794e-05 | 0.5044778907 | screen only | PASS / 0.504344 | FAST 8.13 / 4.76 | pending | pending |
| `c0c6` | timing10 + commute1 + feedback + q5t37 | 6.214469447e-05 | 0.5065653586 | screen only | PASS / 0.506419 | FAST 12.55 / 4.41 | pending | pending |
| `c0ce` | timing10 + commute1 + q19check + feedback + q5t37 | 6.214469447e-05 | 0.5057217862 | screen only | PASS / 0.504742 | FAST 15.66 / 4.83 | pending | pending |
| `c0d6` | timing10 + commute1 + q11measure + feedback + q5t37 | 6.214469447e-05 | 0.5057217862 | screen only | PASS / 0.505401 | FAST 12.61 / 6.24 | pending | pending |
| `c0de` | timing10 + commute1 + q19check + q11measure + feedback + q5t37 | 6.214469447e-05 | 0.5048796186 | screen only | PASS / 0.503852 | FAST 12.28 / 6.48 | pending | pending |
| `c0a4` | commute1 + edge14to15 + q5t37 | 6.214640705e-05 | 0.5066640084 | screen only | PASS / 0.505859 | FAST 12.92 / 5.15 | pending | pending |
| `c0ac` | commute1 + q19check + edge14to15 + q5t37 | 6.214640705e-05 | 0.5058202717 | screen only | PASS / 0.506153 | FAST 8.17 / 4.14 | pending | pending |
| `c0b4` | commute1 + q11measure + edge14to15 + q5t37 | 6.214640705e-05 | 0.5058202717 | screen only | PASS / 0.504366 | FAST 7.87 / 4.15 | pending | pending |
| `c0bc` | commute1 + q19check + q11measure + edge14to15 + q5t37 | 6.214640705e-05 | 0.50497794 | screen only | PASS / 0.505199 | FAST 7.78 / 4.11 | pending | pending |
| `c142` | timing10 + feedback + q5t38 | 6.215153011e-05 | 0.5065646832 | screen only | PASS / 0.506868 | FAST 11.43 / 4.66 | pending | pending |
| `c14a` | timing10 + q19check + feedback + q5t38 | 6.215153011e-05 | 0.5057211119 | screen only | pending | pending | pending | pending |
| `c152` | timing10 + q11measure + feedback + q5t38 | 6.215153011e-05 | 0.5057211119 | screen only | PASS / 0.504335 | FAST 10.17 / 4.19 | pending | pending |
| `c15a` | timing10 + q19check + q11measure + feedback + q5t38 | 6.215153011e-05 | 0.5048789454 | screen only | PASS / 0.504079 | FAST 8.72 / 4.21 | pending | pending |
| `c1ca` | timing10 + q19check + feedback + q5t37 + q5t38 | 6.215153011e-05 | 0.5052156436 | screen only | PASS / 0.505252 | FAST 9.58 / 4.22 | pending | pending |
| `c1c2` | timing10 + feedback + q5t37 + q5t38 | 6.215153011e-05 | 0.5060583717 | screen only | pending | pending | pending | pending |
| `c1d2` | timing10 + q11measure + feedback + q5t37 + q5t38 | 6.215153011e-05 | 0.5052156436 | screen only | pending | pending | pending | pending |
| `c1da` | timing10 + q19check + q11measure + feedback + q5t37 + q5t38 | 6.215153011e-05 | 0.5043743188 | screen only | pending | pending | pending | pending |
| `c120` | edge14to15 + q5t38 | 6.215209499e-05 | 0.5066633328 | screen only | pending | pending | pending | pending |
| `c128` | q19check + edge14to15 + q5t38 | 6.215209499e-05 | 0.5058195972 | screen only | pending | pending | pending | pending |
| `c130` | q11measure + edge14to15 + q5t38 | 6.215209499e-05 | 0.5058195972 | screen only | pending | pending | pending | pending |
| `c138` | q19check + q11measure + edge14to15 + q5t38 | 6.215209499e-05 | 0.5049772667 | screen only | pending | pending | pending | pending |
| `c1a0` | edge14to15 + q5t37 + q5t38 | 6.215209499e-05 | 0.5061569227 | screen only | pending | pending | pending | pending |
| `c1a8` | q19check + edge14to15 + q5t37 + q5t38 | 6.215209499e-05 | 0.5053140305 | screen only | pending | pending | pending | pending |
| `c1b0` | q11measure + edge14to15 + q5t37 + q5t38 | 6.215209499e-05 | 0.5053140305 | screen only | pending | pending | pending | pending |
| `c1b8` | q19check + q11measure + edge14to15 + q5t37 + q5t38 | 6.215209499e-05 | 0.5044725418 | screen only | pending | pending | pending | pending |
| `c003` | copy4 + timing10 | 6.21524186e-05 | 0.502322482 | screen only | pending | pending | pending | pending |
| `c00b` | copy4 + timing10 + q19check | 6.21524186e-05 | 0.5014859751 | screen only | pending | pending | pending | pending |
| `c106` | timing10 + commute1 + q5t38 | 6.215998855e-05 | 0.507066801 | screen only | pending | pending | pending | pending |
| `c10e` | timing10 + commute1 + q19check + q5t38 | 6.215998855e-05 | 0.5062223935 | screen only | pending | pending | pending | pending |
| `c116` | timing10 + commute1 + q11measure + q5t38 | 6.215998855e-05 | 0.5062223935 | screen only | pending | pending | pending | pending |
| `c11e` | timing10 + commute1 + q19check + q11measure + q5t38 | 6.215998855e-05 | 0.5053793922 | screen only | pending | pending | pending | pending |
| `c186` | timing10 + commute1 + q5t37 + q5t38 | 6.215998855e-05 | 0.5065599876 | screen only | pending | pending | pending | pending |
| `c18e` | timing10 + commute1 + q19check + q5t37 + q5t38 | 6.215998855e-05 | 0.5057164241 | screen only | pending | pending | pending | pending |
| `c196` | timing10 + commute1 + q11measure + q5t37 + q5t38 | 6.215998855e-05 | 0.5057164241 | screen only | pending | pending | pending | pending |
| `c19e` | timing10 + commute1 + q19check + q11measure + q5t37 + q5t38 | 6.215998855e-05 | 0.5048742654 | screen only | pending | pending | pending | pending |
| `c0c4` | commute1 + feedback + q5t37 | 6.217158132e-05 | 0.5065680567 | screen only | pending | pending | pending | pending |
| `c0cc` | commute1 + q19check + feedback + q5t37 | 6.217158132e-05 | 0.5057244798 | screen only | pending | pending | pending | pending |
| `c0d4` | commute1 + q11measure + feedback + q5t37 | 6.217158132e-05 | 0.5057244798 | screen only | pending | pending | pending | pending |
| `c0dc` | commute1 + q19check + q11measure + feedback + q5t37 | 6.217158132e-05 | 0.5048823077 | screen only | pending | pending | pending | pending |
| `c140` | feedback + q5t38 | 6.217839156e-05 | 0.5065673813 | screen only | pending | pending | pending | pending |
| `c148` | q19check + feedback + q5t38 | 6.217839156e-05 | 0.5057238055 | screen only | pending | pending | pending | pending |
| `c150` | q11measure + feedback + q5t38 | 6.217839156e-05 | 0.5057238055 | screen only | pending | pending | pending | pending |
| `c158` | q19check + q11measure + feedback + q5t38 | 6.217839156e-05 | 0.5048816345 | screen only | pending | pending | pending | pending |
| `c1c8` | q19check + feedback + q5t37 + q5t38 | 6.217839156e-05 | 0.5052183345 | screen only | pending | pending | pending | pending |
| `c1c0` | feedback + q5t37 + q5t38 | 6.217839156e-05 | 0.5060610671 | screen only | pending | pending | pending | pending |
| `c1d0` | q11measure + feedback + q5t37 + q5t38 | 6.217839156e-05 | 0.5052183345 | screen only | pending | pending | pending | pending |
| `c1d8` | q19check + q11measure + feedback + q5t37 + q5t38 | 6.217839156e-05 | 0.5043770052 | screen only | pending | pending | pending | pending |
| `c001` | copy4 | 6.217924062e-05 | 0.5023251575 | screen only | PASS / 0.502231 | FAST 7.08 / 3.87 | pending | pending |
| `c009` | copy4 + q19check | 6.217924062e-05 | 0.5014886462 | screen only | pending | pending | pending | pending |
| `c104` | commute1 + q5t38 | 6.218683597e-05 | 0.5070695017 | screen only | pending | pending | pending | pending |
| `c114` | commute1 + q11measure + q5t38 | 6.218683597e-05 | 0.5062250898 | screen only | pending | pending | pending | pending |
| `c10c` | commute1 + q19check + q5t38 | 6.218683597e-05 | 0.5062250898 | screen only | pending | pending | pending | pending |
| `c11c` | commute1 + q19check + q11measure + q5t38 | 6.218683597e-05 | 0.505382084 | screen only | pending | pending | pending | pending |
| `c184` | commute1 + q5t37 + q5t38 | 6.218683597e-05 | 0.5065626857 | screen only | pending | pending | pending | pending |
| `c18c` | commute1 + q19check + q5t37 + q5t38 | 6.218683597e-05 | 0.5057191177 | screen only | pending | pending | pending | pending |
| `c194` | commute1 + q11measure + q5t37 + q5t38 | 6.218683597e-05 | 0.5057191177 | screen only | pending | pending | pending | pending |
| `c19c` | commute1 + q19check + q11measure + q5t37 + q5t38 | 6.218683597e-05 | 0.5048769545 | screen only | pending | pending | pending | pending |
| `c0a2` | timing10 + edge14to15 + q5t37 | 6.221285607e-05 | 0.5066606342 | screen only | pending | pending | pending | pending |
| `c0aa` | timing10 + q19check + edge14to15 + q5t37 | 6.221285607e-05 | 0.5058169031 | screen only | pending | pending | pending | pending |
| `c0b2` | timing10 + q11measure + edge14to15 + q5t37 | 6.221285607e-05 | 0.5058169031 | screen only | pending | pending | pending | pending |
| `c0ba` | timing10 + q19check + q11measure + edge14to15 + q5t37 | 6.221285607e-05 | 0.5049745771 | screen only | pending | pending | pending | pending |
| `c07e` | timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | 6.223181586e-05 | 0.5049810535 | screen only | pending | pending | pending | pending |
| `c076` | timing10 + commute1 + q11measure + edge14to15 + feedback | 6.223181586e-05 | 0.5058233903 | screen only | pending | pending | pending | pending |
| `c0c2` | timing10 + feedback + q5t37 | 6.223905963e-05 | 0.5065646832 | screen only | pending | pending | pending | pending |
| `c0ca` | timing10 + q19check + feedback + q5t37 | 6.223905963e-05 | 0.5057211119 | screen only | pending | pending | pending | pending |
| `c0d2` | timing10 + q11measure + feedback + q5t37 | 6.223905963e-05 | 0.5057211119 | screen only | pending | pending | pending | pending |
| `c0da` | timing10 + q19check + q11measure + feedback + q5t37 | 6.223905963e-05 | 0.5048789454 | screen only | pending | pending | pending | pending |
| `c0a8` | q19check + edge14to15 + q5t37 | 6.223962451e-05 | 0.5058195972 | screen only | pending | pending | pending | pending |
| `c0a0` | edge14to15 + q5t37 | 6.223962451e-05 | 0.5066633328 | screen only | pending | pending | pending | pending |
| `c0b0` | q11measure + edge14to15 + q5t37 | 6.223962451e-05 | 0.5058195972 | screen only | pending | pending | pending | pending |
| `c0b8` | q19check + q11measure + edge14to15 + q5t37 | 6.223962451e-05 | 0.5049772667 | screen only | pending | pending | pending | pending |
| `c086` | timing10 + commute1 + q5t37 | 6.224751806e-05 | 0.507066801 | screen only | pending | pending | pending | pending |
| `c096` | timing10 + commute1 + q11measure + q5t37 | 6.224751806e-05 | 0.5062223935 | screen only | pending | pending | pending | pending |
| `c08e` | timing10 + commute1 + q19check + q5t37 | 6.224751806e-05 | 0.5062223935 | screen only | pending | pending | pending | pending |
| `c09e` | timing10 + commute1 + q19check + q11measure + q5t37 | 6.224751806e-05 | 0.5053793922 | screen only | pending | pending | pending | pending |
| `c102` | timing10 + q5t38 | 6.225312407e-05 | 0.5070661249 | screen only | pending | pending | pending | pending |
| `c10a` | timing10 + q19check + q5t38 | 6.225312407e-05 | 0.5062217185 | screen only | pending | pending | pending | pending |
| `c112` | timing10 + q11measure + q5t38 | 6.225312407e-05 | 0.5062217185 | screen only | pending | pending | pending | pending |
| `c11a` | timing10 + q19check + q11measure + q5t38 | 6.225312407e-05 | 0.5053787184 | screen only | pending | pending | pending | pending |
| `c18a` | timing10 + q19check + q5t37 + q5t38 | 6.225312407e-05 | 0.5057157499 | screen only | pending | pending | pending | pending |
| `c192` | timing10 + q11measure + q5t37 + q5t38 | 6.225312407e-05 | 0.5057157499 | screen only | pending | pending | pending | pending |
| `c182` | timing10 + q5t37 + q5t38 | 6.225312407e-05 | 0.5065593122 | screen only | pending | pending | pending | pending |
| `c19a` | timing10 + q19check + q11measure + q5t37 + q5t38 | 6.225312407e-05 | 0.5048735923 | screen only | pending | pending | pending | pending |
| `c07c` | commute1 + q19check + q11measure + edge14to15 + feedback | 6.225864947e-05 | 0.5049837431 | screen only | pending | pending | pending | pending |
| `c074` | commute1 + q11measure + edge14to15 + feedback | 6.225864947e-05 | 0.5058260844 | screen only | pending | pending | pending | pending |
| `c0c0` | feedback + q5t37 | 6.226592108e-05 | 0.5065673813 | screen only | pending | pending | pending | pending |
| `c0c8` | q19check + feedback + q5t37 | 6.226592108e-05 | 0.5057238055 | screen only | pending | pending | pending | pending |
| `c0d0` | q11measure + feedback + q5t37 | 6.226592108e-05 | 0.5057238055 | screen only | pending | pending | pending | pending |
| `c0d8` | q19check + q11measure + feedback + q5t37 | 6.226592108e-05 | 0.5048816345 | screen only | pending | pending | pending | pending |
| `c084` | commute1 + q5t37 | 6.227436549e-05 | 0.5070695017 | screen only | pending | pending | pending | pending |
| `c08c` | commute1 + q19check + q5t37 | 6.227436549e-05 | 0.5062250898 | screen only | pending | pending | pending | pending |
| `c094` | commute1 + q11measure + q5t37 | 6.227436549e-05 | 0.5062250898 | screen only | pending | pending | pending | pending |
| `c09c` | commute1 + q19check + q11measure + q5t37 | 6.227436549e-05 | 0.505382084 | screen only | pending | pending | pending | pending |
| `c066` | timing10 + commute1 + edge14to15 + feedback | 6.227561396e-05 | 0.5066671322 | screen only | pending | pending | pending | pending |
| `c06e` | timing10 + commute1 + q19check + edge14to15 + feedback | 6.227561396e-05 | 0.5058233903 | screen only | pending | pending | pending | pending |
| `c100` | q5t38 | 6.227994609e-05 | 0.5070688256 | screen only | PASS / 0.507344 | FAST 9.54 / 3.90 | pending | pending |
| `c108` | q19check + q5t38 | 6.227994609e-05 | 0.5062244148 | screen only | pending | pending | pending | pending |
| `c110` | q11measure + q5t38 | 6.227994609e-05 | 0.5062244148 | screen only | pending | pending | pending | pending |
| `c118` | q19check + q11measure + q5t38 | 6.227994609e-05 | 0.5053814101 | screen only | pending | pending | pending | pending |
| `c180` | q5t37 + q5t38 | 6.227994609e-05 | 0.5065620103 | screen only | pending | pending | pending | pending |
| `c188` | q19check + q5t37 + q5t38 | 6.227994609e-05 | 0.5057184434 | screen only | pending | pending | pending | pending |
| `c190` | q11measure + q5t37 + q5t38 | 6.227994609e-05 | 0.5057184434 | screen only | pending | pending | pending | pending |
| `c198` | q19check + q11measure + q5t37 + q5t38 | 6.227994609e-05 | 0.5048762813 | screen only | pending | pending | pending | pending |
| `c064` | commute1 + edge14to15 + feedback | 6.230244756e-05 | 0.5066698308 | screen only | pending | pending | pending | pending |
| `c06c` | commute1 + q19check + edge14to15 + feedback | 6.230244756e-05 | 0.5058260844 | screen only | pending | pending | pending | pending |
| `c07a` | timing10 + q19check + q11measure + edge14to15 + feedback | 6.23262886e-05 | 0.5049803802 | screen only | pending | pending | pending | pending |
| `c072` | timing10 + q11measure + edge14to15 + feedback | 6.23262886e-05 | 0.5058227159 | screen only | pending | pending | pending | pending |
| `c03e` | timing10 + commute1 + q19check + q11measure + edge14to15 | 6.233467043e-05 | 0.5054809275 | screen only | pending | pending | pending | pending |
| `c036` | timing10 + commute1 + q11measure + edge14to15 | 6.233467043e-05 | 0.5063240982 | screen only | pending | pending | pending | pending |
| `c082` | timing10 + q5t37 | 6.234065359e-05 | 0.5070661249 | screen only | pending | pending | pending | pending |
| `c08a` | timing10 + q19check + q5t37 | 6.234065359e-05 | 0.5062217185 | screen only | pending | pending | pending | pending |
| `c092` | timing10 + q11measure + q5t37 | 6.234065359e-05 | 0.5062217185 | screen only | pending | pending | pending | pending |
| `c09a` | timing10 + q19check + q11measure + q5t37 | 6.234065359e-05 | 0.5053787184 | screen only | pending | pending | pending | pending |
| `c078` | q19check + q11measure + edge14to15 + feedback | 6.235309656e-05 | 0.5049830698 | screen only | pending | pending | pending | pending |
| `c070` | q11measure + edge14to15 + feedback | 6.235309656e-05 | 0.50582541 | screen only | pending | pending | pending | pending |
| `c05e` | timing10 + commute1 + q19check + q11measure + feedback | 6.23597231e-05 | 0.5053851999 | screen only | pending | pending | pending | pending |
| `c056` | timing10 + commute1 + q11measure + feedback | 6.23597231e-05 | 0.5062282109 | screen only | pending | pending | pending | pending |
| `c03c` | commute1 + q19check + q11measure + edge14to15 | 6.236146452e-05 | 0.5054836198 | screen only | pending | pending | pending | pending |
| `c034` | commute1 + q11measure + edge14to15 | 6.236146452e-05 | 0.506326795 | screen only | pending | pending | pending | pending |
| `c080` | q5t37 | 6.236747561e-05 | 0.5070688256 | screen only | PASS / 0.507033 | FAST 7.47 / 3.85 | pending | pending |
| `c088` | q19check + q5t37 | 6.236747561e-05 | 0.5062244148 | screen only | pending | pending | pending | pending |
| `c090` | q11measure + q5t37 | 6.236747561e-05 | 0.5062244148 | screen only | pending | pending | pending | pending |
| `c098` | q19check + q11measure + q5t37 | 6.236747561e-05 | 0.5053814101 | screen only | pending | pending | pending | pending |
| `c062` | timing10 + edge14to15 + feedback | 6.237008669e-05 | 0.5066664567 | screen only | pending | pending | pending | pending |
| `c06a` | timing10 + q19check + edge14to15 + feedback | 6.237008669e-05 | 0.5058227159 | screen only | pending | pending | pending | pending |
| `c026` | timing10 + commute1 + edge14to15 | 6.237846853e-05 | 0.5071686753 | screen only | pending | pending | pending | pending |
| `c02e` | timing10 + commute1 + q19check + edge14to15 | 6.237846853e-05 | 0.5063240982 | screen only | pending | pending | pending | pending |
| `c05c` | commute1 + q19check + q11measure + feedback | 6.238660994e-05 | 0.5053878918 | screen only | pending | pending | pending | pending |
| `c054` | commute1 + q11measure + feedback | 6.238660994e-05 | 0.5062309072 | screen only | pending | pending | pending | pending |
| `c060` | edge14to15 + feedback | 6.239689465e-05 | 0.5066691553 | screen only | pending | pending | pending | pending |
| `c068` | q19check + edge14to15 + feedback | 6.239689465e-05 | 0.50582541 | screen only | pending | pending | pending | pending |
| `c046` | timing10 + commute1 + feedback | 6.240352119e-05 | 0.5070726281 | screen only | pending | pending | pending | pending |
| `c04e` | timing10 + commute1 + q19check + feedback | 6.240352119e-05 | 0.5062282109 | screen only | pending | pending | pending | pending |
| `c024` | commute1 + edge14to15 | 6.240526261e-05 | 0.5071713766 | screen only | pending | pending | pending | pending |
| `c02c` | commute1 + q19check + edge14to15 | 6.240526261e-05 | 0.506326795 | screen only | pending | pending | pending | pending |
| `c03a` | timing10 + q19check + q11measure + edge14to15 | 6.242791354e-05 | 0.5054802535 | screen only | pending | pending | pending | pending |
| `c032` | timing10 + q11measure + edge14to15 | 6.242791354e-05 | 0.5063234231 | screen only | pending | pending | pending | pending |
| `c044` | commute1 + feedback | 6.243040804e-05 | 0.5070753289 | screen only | pending | pending | pending | pending |
| `c04c` | commute1 + q19check + feedback | 6.243040804e-05 | 0.5062309072 | screen only | pending | pending | pending | pending |
| `c05a` | timing10 + q19check + q11measure + feedback | 6.245408826e-05 | 0.5053845261 | screen only | pending | pending | pending | pending |
| `c052` | timing10 + q11measure + feedback | 6.245408826e-05 | 0.506227536 | screen only | pending | pending | pending | pending |
| `c038` | q19check + q11measure + edge14to15 | 6.245468198e-05 | 0.5054829459 | screen only | pending | pending | pending | pending |
| `c030` | q11measure + edge14to15 | 6.245468198e-05 | 0.5063261199 | screen only | pending | pending | pending | pending |
| `c01e` | timing10 + commute1 + q19check + q11measure | 6.246257554e-05 | 0.5058854741 | screen only | pending | pending | pending | pending |
| `c016` | timing10 + commute1 + q11measure | 6.246257554e-05 | 0.5067293195 | screen only | pending | pending | pending | pending |
| `c022` | timing10 + edge14to15 | 6.247171163e-05 | 0.5071679991 | screen only | pending | pending | pending | pending |
| `c02a` | timing10 + q19check + edge14to15 | 6.247171163e-05 | 0.5063234231 | screen only | pending | pending | pending | pending |
| `c058` | q19check + q11measure + feedback | 6.24809497e-05 | 0.5053872179 | screen only | pending | pending | pending | pending |
| `c050` | q11measure + feedback | 6.24809497e-05 | 0.5062302322 | screen only | pending | pending | pending | pending |
| `c01c` | commute1 + q19check + q11measure | 6.248942296e-05 | 0.5058881685 | screen only | pending | pending | pending | pending |
| `c014` | commute1 + q11measure | 6.248942296e-05 | 0.5067320185 | screen only | pending | pending | pending | pending |
| `c042` | timing10 + feedback | 6.249788635e-05 | 0.507071952 | screen only | pending | pending | pending | pending |
| `c04a` | timing10 + q19check + feedback | 6.249788635e-05 | 0.506227536 | screen only | pending | pending | pending | pending |
| `c020` | edge14to15 | 6.249848007e-05 | 0.5071707004 | screen only | PASS / 0.506935 | FAST 6.92 / 3.66 | pending | pending |
| `c028` | q19check + edge14to15 | 6.249848007e-05 | 0.5063261199 | screen only | pending | pending | pending | pending |
| `c006` | timing10 + commute1 | 6.250637363e-05 | 0.5075745726 | screen only | pending | pending | pending | pending |
| `c00e` | timing10 + commute1 + q19check | 6.250637363e-05 | 0.5067293195 | screen only | pending | pending | pending | pending |
| `c040` | feedback | 6.25247478e-05 | 0.5070746528 | screen only | PASS / 0.507193 | FAST 6.96 / 3.57 | pending | pending |
| `c048` | q19check + feedback | 6.25247478e-05 | 0.5062302322 | screen only | pending | pending | pending | pending |
| `c004` | commute1 | 6.253322105e-05 | 0.507577276 | screen only | PASS / 0.506501 | FAST 6.80 / 3.65 | pending | pending |
| `c00c` | commute1 + q19check | 6.253322105e-05 | 0.5067320185 | screen only | pending | pending | pending | pending |
| `c01a` | timing10 + q19check + q11measure | 6.255571106e-05 | 0.5058847995 | screen only | pending | pending | pending | pending |
| `c012` | timing10 + q11measure | 6.255571106e-05 | 0.5067286439 | screen only | pending | pending | pending | pending |
| `c018` | q19check + q11measure | 6.258253309e-05 | 0.505887494 | screen only | pending | pending | pending | pending |
| `c010` | q11measure | 6.258253309e-05 | 0.5067313428 | screen only | PASS / 0.506213 | FAST 7.77 / 4.02 | pending | pending |
| `c002` | timing10 | 6.259950915e-05 | 0.5075738958 | screen only | PASS / 0.506776 | FAST 6.63 / 3.65 | pending | pending |
| `c00a` | timing10 + q19check | 6.259950915e-05 | 0.5067286439 | screen only | pending | pending | pending | pending |
| `v29c` | v29c control | 6.262633118e-05 | 0.5075765993 | CLI | PASS / 0.507146 | FAST 6.47 / 3.65 | pending | pending |
| `c008` | q19check | 6.262633118e-05 | 0.5067313428 | screen only | PASS / 0.506486 | FAST 7.99 / 3.69 | pending | pending |
| `bc06` | bcfb:blue_d15_c90_s704_00057 | 6.394161736e-05 | 0.5098893605 | screen only | pending | pending | pending | pending |
| `bc00` | bcfb:blue_d15_c90_s712_00007 | 6.394730267e-05 | 0.5099893095 | screen only | pending | pending | pending | pending |
| `bc01` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 | 6.398605583e-05 | 0.5092398392 | screen only | pending | pending | pending | pending |
| `bc02` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 | 6.404009168e-05 | 0.5109401376 | screen only | pending | pending | pending | pending |
| `bc03` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 | 6.418265378e-05 | 0.5110082675 | screen only | pending | pending | pending | pending |
| `bc04` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 | 6.429146746e-05 | 0.5087308539 | screen only | pending | pending | pending | pending |
| `bc05` | bcfb:v26n_fb_d14_c98_s517_00020_preserve | 6.430150412e-05 | 0.5104792506 | screen only | pending | pending | pending | pending |
| `bc08` | bcfb:v26n_fb_d14_c98_s517_00020_reset | 6.464830641e-05 | 0.5097990652 | screen only | pending | pending | pending | pending |
| `bc07` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 | 6.476898851e-05 | 0.5109477767 | screen only | pending | pending | pending | pending |
| `bc00_001` | bcfb:blue_d15_c90_s712_00007 + copy4 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_002` | bcfb:blue_d15_c90_s712_00007 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_003` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_004` | bcfb:blue_d15_c90_s712_00007 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_005` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_006` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_007` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_008` | bcfb:blue_d15_c90_s712_00007 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_009` | bcfb:blue_d15_c90_s712_00007 + copy4 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_00a` | bcfb:blue_d15_c90_s712_00007 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_00b` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_00c` | bcfb:blue_d15_c90_s712_00007 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_00d` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_00e` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_00f` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_010` | bcfb:blue_d15_c90_s712_00007 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_011` | bcfb:blue_d15_c90_s712_00007 + copy4 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_012` | bcfb:blue_d15_c90_s712_00007 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_013` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_014` | bcfb:blue_d15_c90_s712_00007 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_015` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_016` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_017` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_018` | bcfb:blue_d15_c90_s712_00007 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_019` | bcfb:blue_d15_c90_s712_00007 + copy4 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_01a` | bcfb:blue_d15_c90_s712_00007 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_01b` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_01c` | bcfb:blue_d15_c90_s712_00007 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_01d` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_01e` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_01f` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_020` | bcfb:blue_d15_c90_s712_00007 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_021` | bcfb:blue_d15_c90_s712_00007 + copy4 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_022` | bcfb:blue_d15_c90_s712_00007 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_023` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_024` | bcfb:blue_d15_c90_s712_00007 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_025` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_026` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_027` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_028` | bcfb:blue_d15_c90_s712_00007 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_029` | bcfb:blue_d15_c90_s712_00007 + copy4 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_02a` | bcfb:blue_d15_c90_s712_00007 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_02b` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_02c` | bcfb:blue_d15_c90_s712_00007 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_02d` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_02e` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_02f` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_030` | bcfb:blue_d15_c90_s712_00007 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_031` | bcfb:blue_d15_c90_s712_00007 + copy4 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_032` | bcfb:blue_d15_c90_s712_00007 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_033` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_034` | bcfb:blue_d15_c90_s712_00007 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_035` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_036` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_037` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_038` | bcfb:blue_d15_c90_s712_00007 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_039` | bcfb:blue_d15_c90_s712_00007 + copy4 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_03a` | bcfb:blue_d15_c90_s712_00007 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_03b` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_03c` | bcfb:blue_d15_c90_s712_00007 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_03d` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_03e` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_03f` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_040` | bcfb:blue_d15_c90_s712_00007 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_041` | bcfb:blue_d15_c90_s712_00007 + copy4 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_042` | bcfb:blue_d15_c90_s712_00007 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_043` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_044` | bcfb:blue_d15_c90_s712_00007 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_045` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_046` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_047` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_048` | bcfb:blue_d15_c90_s712_00007 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_049` | bcfb:blue_d15_c90_s712_00007 + copy4 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_04a` | bcfb:blue_d15_c90_s712_00007 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_04b` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_04c` | bcfb:blue_d15_c90_s712_00007 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_04d` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_04e` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_04f` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_050` | bcfb:blue_d15_c90_s712_00007 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_051` | bcfb:blue_d15_c90_s712_00007 + copy4 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_052` | bcfb:blue_d15_c90_s712_00007 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_053` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_054` | bcfb:blue_d15_c90_s712_00007 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_055` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_056` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_057` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_058` | bcfb:blue_d15_c90_s712_00007 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_059` | bcfb:blue_d15_c90_s712_00007 + copy4 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_05a` | bcfb:blue_d15_c90_s712_00007 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_05b` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_05c` | bcfb:blue_d15_c90_s712_00007 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_05d` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_05e` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_05f` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_060` | bcfb:blue_d15_c90_s712_00007 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_061` | bcfb:blue_d15_c90_s712_00007 + copy4 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_062` | bcfb:blue_d15_c90_s712_00007 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_063` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_064` | bcfb:blue_d15_c90_s712_00007 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_065` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_066` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_067` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_068` | bcfb:blue_d15_c90_s712_00007 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_069` | bcfb:blue_d15_c90_s712_00007 + copy4 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_06a` | bcfb:blue_d15_c90_s712_00007 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_06b` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_06c` | bcfb:blue_d15_c90_s712_00007 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_06d` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_06e` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_06f` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_070` | bcfb:blue_d15_c90_s712_00007 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_071` | bcfb:blue_d15_c90_s712_00007 + copy4 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_072` | bcfb:blue_d15_c90_s712_00007 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_073` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_074` | bcfb:blue_d15_c90_s712_00007 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_075` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_076` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_077` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_078` | bcfb:blue_d15_c90_s712_00007 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_079` | bcfb:blue_d15_c90_s712_00007 + copy4 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_07a` | bcfb:blue_d15_c90_s712_00007 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_07b` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_07c` | bcfb:blue_d15_c90_s712_00007 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_07d` | bcfb:blue_d15_c90_s712_00007 + copy4 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_07e` | bcfb:blue_d15_c90_s712_00007 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc00_07f` | bcfb:blue_d15_c90_s712_00007 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_001` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_002` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_003` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_004` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_005` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_006` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_007` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_008` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_009` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_00a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_00b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_00c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_00d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_00e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_00f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_010` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_011` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_012` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_013` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_014` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_015` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_016` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_017` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_018` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_019` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_01a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_01b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_01c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_01d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_01e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_01f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_020` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_021` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_022` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_023` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_024` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_025` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_026` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_027` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_028` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_029` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_02a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_02b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_02c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_02d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_02e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_02f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_030` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_031` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_032` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_033` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_034` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_035` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_036` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_037` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_038` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_039` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_03a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_03b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_03c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_03d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_03e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_03f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_040` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_041` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_042` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_043` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_044` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_045` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_046` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_047` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_048` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_049` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_04a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_04b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_04c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_04d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_04e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_04f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_050` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_051` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_052` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_053` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_054` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_055` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_056` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_057` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_058` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_059` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_05a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_05b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_05c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_05d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_05e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_05f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_060` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_061` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_062` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_063` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_064` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_065` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_066` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_067` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_068` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_069` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_06a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_06b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_06c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_06d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_06e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_06f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_070` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_071` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_072` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_073` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_074` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_075` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_076` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_077` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_078` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_079` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_07a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_07b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_07c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_07d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_07e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc01_07f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_001` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_002` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_003` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_004` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_005` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_006` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_007` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_008` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_009` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_00a` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_00b` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_00c` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_00d` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_00e` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_00f` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_010` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_011` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_012` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_013` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_014` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_015` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_016` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_017` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_018` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_019` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_01a` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_01b` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_01c` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_01d` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_01e` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_01f` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_020` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_021` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_022` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_023` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_024` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_025` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_026` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_027` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_028` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_029` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_02a` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_02b` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_02c` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_02d` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_02e` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_02f` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_030` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_031` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_032` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_033` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_034` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_035` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_036` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_037` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_038` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_039` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_03a` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_03b` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_03c` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_03d` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_03e` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_03f` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_040` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_041` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_042` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_043` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_044` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_045` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_046` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_047` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_048` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_049` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_04a` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_04b` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_04c` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_04d` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_04e` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_04f` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_050` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_051` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_052` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_053` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_054` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_055` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_056` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_057` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_058` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_059` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_05a` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_05b` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_05c` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_05d` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_05e` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_05f` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_060` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_061` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_062` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_063` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_064` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_065` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_066` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_067` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_068` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_069` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_06a` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_06b` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_06c` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_06d` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_06e` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_06f` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_070` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_071` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_072` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_073` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_074` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_075` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_076` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_077` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_078` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_079` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_07a` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_07b` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_07c` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_07d` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_07e` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc02_07f` | bcfb:v26n_fast_d15_c105_s526_00356_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_001` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_002` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_003` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_004` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_005` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_006` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_007` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_008` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_009` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_00a` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_00b` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_00c` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_00d` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_00e` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_00f` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_010` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_011` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_012` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_013` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_014` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_015` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_016` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_017` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_018` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_019` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_01a` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_01b` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_01c` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_01d` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_01e` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_01f` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_020` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_021` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_022` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_023` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_024` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_025` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_026` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_027` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_028` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_029` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_02a` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_02b` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_02c` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_02d` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_02e` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_02f` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_030` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_031` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_032` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_033` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_034` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_035` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_036` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_037` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_038` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_039` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_03a` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_03b` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_03c` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_03d` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_03e` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_03f` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_040` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_041` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_042` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_043` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_044` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_045` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_046` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_047` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_048` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_049` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_04a` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_04b` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_04c` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_04d` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_04e` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_04f` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_050` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_051` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_052` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_053` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_054` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_055` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_056` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_057` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_058` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_059` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_05a` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_05b` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_05c` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_05d` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_05e` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_05f` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_060` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_061` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_062` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_063` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_064` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_065` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_066` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_067` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_068` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_069` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_06a` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_06b` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_06c` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_06d` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_06e` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_06f` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_070` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_071` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_072` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_073` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_074` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_075` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_076` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_077` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_078` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_079` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_07a` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_07b` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_07c` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_07d` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_07e` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc03_07f` | bcfb:v26n_fast_d15_c105_s526_00331_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_001` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_002` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_003` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_004` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_005` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_006` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_007` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_008` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_009` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_00a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_00b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_00c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_00d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_00e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_00f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_010` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_011` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_012` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_013` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_014` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_015` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_016` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_017` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_018` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_019` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_01a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_01b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_01c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_01d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_01e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_01f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_020` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_021` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_022` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_023` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_024` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_025` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_026` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_027` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_028` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_029` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_02a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_02b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_02c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_02d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_02e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_02f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_030` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_031` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_032` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_033` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_034` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_035` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_036` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_037` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_038` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_039` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_03a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_03b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_03c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_03d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_03e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_03f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_040` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_041` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_042` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_043` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_044` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_045` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_046` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_047` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_048` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_049` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_04a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_04b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_04c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_04d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_04e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_04f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_050` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_051` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_052` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_053` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_054` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_055` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_056` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_057` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_058` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_059` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_05a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_05b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_05c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_05d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_05e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_05f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_060` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_061` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_062` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_063` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_064` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_065` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_066` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_067` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_068` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_069` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_06a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_06b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_06c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_06d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_06e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_06f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_070` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_071` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_072` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_073` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_074` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_075` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_076` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_077` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_078` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_079` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_07a` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_07b` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_07c` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_07d` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_07e` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc04_07f` | bcfb:v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_001` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_002` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_003` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_004` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_005` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_006` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_007` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_008` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_009` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_00a` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_00b` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_00c` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_00d` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_00e` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_00f` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_020` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_021` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_022` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_023` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_024` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_025` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_026` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_027` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_028` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_029` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_02a` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_02b` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_02c` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_02d` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_02e` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_02f` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_040` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_041` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_042` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_043` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_044` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_045` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_046` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_047` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_048` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_049` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_04a` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_04b` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_04c` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_04d` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_04e` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_04f` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_060` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_061` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_062` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_063` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_064` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_065` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_066` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_067` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_068` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_069` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_06a` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_06b` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_06c` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_06d` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_06e` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc05_06f` | bcfb:v26n_fb_d14_c98_s517_00020_preserve + copy4 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_001` | bcfb:blue_d15_c90_s704_00057 + copy4 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_002` | bcfb:blue_d15_c90_s704_00057 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_003` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_004` | bcfb:blue_d15_c90_s704_00057 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_005` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_006` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_007` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_008` | bcfb:blue_d15_c90_s704_00057 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_009` | bcfb:blue_d15_c90_s704_00057 + copy4 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_00a` | bcfb:blue_d15_c90_s704_00057 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_00b` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_00c` | bcfb:blue_d15_c90_s704_00057 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_00d` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_00e` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_00f` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_010` | bcfb:blue_d15_c90_s704_00057 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_011` | bcfb:blue_d15_c90_s704_00057 + copy4 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_012` | bcfb:blue_d15_c90_s704_00057 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_013` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_014` | bcfb:blue_d15_c90_s704_00057 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_015` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_016` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_017` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_018` | bcfb:blue_d15_c90_s704_00057 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_019` | bcfb:blue_d15_c90_s704_00057 + copy4 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_01a` | bcfb:blue_d15_c90_s704_00057 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_01b` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_01c` | bcfb:blue_d15_c90_s704_00057 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_01d` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_01e` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_01f` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_020` | bcfb:blue_d15_c90_s704_00057 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_021` | bcfb:blue_d15_c90_s704_00057 + copy4 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_022` | bcfb:blue_d15_c90_s704_00057 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_023` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_024` | bcfb:blue_d15_c90_s704_00057 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_025` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_026` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_027` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_028` | bcfb:blue_d15_c90_s704_00057 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_029` | bcfb:blue_d15_c90_s704_00057 + copy4 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_02a` | bcfb:blue_d15_c90_s704_00057 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_02b` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_02c` | bcfb:blue_d15_c90_s704_00057 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_02d` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_02e` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_02f` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_030` | bcfb:blue_d15_c90_s704_00057 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_031` | bcfb:blue_d15_c90_s704_00057 + copy4 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_032` | bcfb:blue_d15_c90_s704_00057 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_033` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_034` | bcfb:blue_d15_c90_s704_00057 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_035` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_036` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_037` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_038` | bcfb:blue_d15_c90_s704_00057 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_039` | bcfb:blue_d15_c90_s704_00057 + copy4 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_03a` | bcfb:blue_d15_c90_s704_00057 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_03b` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_03c` | bcfb:blue_d15_c90_s704_00057 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_03d` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_03e` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_03f` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_040` | bcfb:blue_d15_c90_s704_00057 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_041` | bcfb:blue_d15_c90_s704_00057 + copy4 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_042` | bcfb:blue_d15_c90_s704_00057 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_043` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_044` | bcfb:blue_d15_c90_s704_00057 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_045` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_046` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_047` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_048` | bcfb:blue_d15_c90_s704_00057 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_049` | bcfb:blue_d15_c90_s704_00057 + copy4 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_04a` | bcfb:blue_d15_c90_s704_00057 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_04b` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_04c` | bcfb:blue_d15_c90_s704_00057 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_04d` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_04e` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_04f` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_050` | bcfb:blue_d15_c90_s704_00057 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_051` | bcfb:blue_d15_c90_s704_00057 + copy4 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_052` | bcfb:blue_d15_c90_s704_00057 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_053` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_054` | bcfb:blue_d15_c90_s704_00057 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_055` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_056` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_057` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_058` | bcfb:blue_d15_c90_s704_00057 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_059` | bcfb:blue_d15_c90_s704_00057 + copy4 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_05a` | bcfb:blue_d15_c90_s704_00057 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_05b` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_05c` | bcfb:blue_d15_c90_s704_00057 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_05d` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_05e` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_05f` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_060` | bcfb:blue_d15_c90_s704_00057 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_061` | bcfb:blue_d15_c90_s704_00057 + copy4 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_062` | bcfb:blue_d15_c90_s704_00057 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_063` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_064` | bcfb:blue_d15_c90_s704_00057 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_065` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_066` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_067` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_068` | bcfb:blue_d15_c90_s704_00057 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_069` | bcfb:blue_d15_c90_s704_00057 + copy4 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_06a` | bcfb:blue_d15_c90_s704_00057 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_06b` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_06c` | bcfb:blue_d15_c90_s704_00057 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_06d` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_06e` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_06f` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_070` | bcfb:blue_d15_c90_s704_00057 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_071` | bcfb:blue_d15_c90_s704_00057 + copy4 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_072` | bcfb:blue_d15_c90_s704_00057 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_073` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_074` | bcfb:blue_d15_c90_s704_00057 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_075` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_076` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_077` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_078` | bcfb:blue_d15_c90_s704_00057 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_079` | bcfb:blue_d15_c90_s704_00057 + copy4 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_07a` | bcfb:blue_d15_c90_s704_00057 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_07b` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_07c` | bcfb:blue_d15_c90_s704_00057 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_07d` | bcfb:blue_d15_c90_s704_00057 + copy4 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_07e` | bcfb:blue_d15_c90_s704_00057 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc06_07f` | bcfb:blue_d15_c90_s704_00057 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_001` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_002` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_003` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_004` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_005` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_006` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_007` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_008` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_009` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_00a` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_00b` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_00c` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_00d` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_00e` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_00f` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_010` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_011` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_012` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_013` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_014` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_015` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_016` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_017` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_018` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_019` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_01a` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_01b` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_01c` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_01d` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_01e` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_01f` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_020` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_021` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_022` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_023` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_024` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_025` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_026` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_027` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_028` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_029` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_02a` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_02b` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_02c` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_02d` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_02e` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_02f` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_030` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_031` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_032` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_033` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_034` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_035` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_036` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_037` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_038` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_039` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_03a` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_03b` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_03c` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_03d` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_03e` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_03f` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_040` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_041` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_042` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_043` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_044` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_045` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_046` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_047` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_048` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_049` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_04a` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_04b` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_04c` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_04d` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_04e` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_04f` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_050` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_051` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_052` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_053` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_054` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_055` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_056` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_057` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_058` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_059` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_05a` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_05b` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_05c` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_05d` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_05e` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_05f` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_060` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_061` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_062` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_063` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_064` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_065` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_066` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_067` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_068` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_069` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_06a` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_06b` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_06c` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_06d` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_06e` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_06f` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_070` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_071` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_072` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_073` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_074` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_075` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_076` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_077` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_078` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_079` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_07a` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_07b` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_07c` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_07d` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_07e` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc07_07f` | bcfb:v26n_fb_d15_c105_s506_00008_preserve_rt1 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_001` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_002` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_003` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_004` | bcfb:v26n_fb_d14_c98_s517_00020_reset + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_005` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_006` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_007` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + commute1 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_008` | bcfb:v26n_fb_d14_c98_s517_00020_reset + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_009` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_00a` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_00b` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_00c` | bcfb:v26n_fb_d14_c98_s517_00020_reset + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_00d` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_00e` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_00f` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + commute1 + q19check | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_020` | bcfb:v26n_fb_d14_c98_s517_00020_reset + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_021` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_022` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_023` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_024` | bcfb:v26n_fb_d14_c98_s517_00020_reset + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_025` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_026` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_027` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + commute1 + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_028` | bcfb:v26n_fb_d14_c98_s517_00020_reset + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_029` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_02a` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_02b` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_02c` | bcfb:v26n_fb_d14_c98_s517_00020_reset + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_02d` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_02e` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_02f` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + commute1 + q19check + edge14to15 | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_040` | bcfb:v26n_fb_d14_c98_s517_00020_reset + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_041` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_042` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_043` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_044` | bcfb:v26n_fb_d14_c98_s517_00020_reset + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_045` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_046` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_047` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + commute1 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_048` | bcfb:v26n_fb_d14_c98_s517_00020_reset + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_049` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_04a` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_04b` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_04c` | bcfb:v26n_fb_d14_c98_s517_00020_reset + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_04d` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_04e` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_04f` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + commute1 + q19check + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_060` | bcfb:v26n_fb_d14_c98_s517_00020_reset + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_061` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_062` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_063` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_064` | bcfb:v26n_fb_d14_c98_s517_00020_reset + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_065` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_066` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_067` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + commute1 + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_068` | bcfb:v26n_fb_d14_c98_s517_00020_reset + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_069` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_06a` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_06b` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_06c` | bcfb:v26n_fb_d14_c98_s517_00020_reset + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_06d` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_06e` | bcfb:v26n_fb_d14_c98_s517_00020_reset + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |
| `bc08_06f` | bcfb:v26n_fb_d14_c98_s517_00020_reset + copy4 + timing10 + commute1 + q19check + edge14to15 + feedback | pending | pending | screen only | pending | pending | pending | pending |

## Selection and limits

True-mean finalist ranking is pending.
Best completed 1e6-passing third-order screen: `c165`, 6.1519953623e-05.

The first c167 and c1e7 serializations fail the 1e6 acceptance draw despite passing the proxy; those failures are retained. No failed gate is relabeled as a pass. Conditional-error performance and acceptance are ranked separately. Server execution has not been tested. This finite composition search is not a global optimum proof.

Best finalist: **pending true-mean verification**.
