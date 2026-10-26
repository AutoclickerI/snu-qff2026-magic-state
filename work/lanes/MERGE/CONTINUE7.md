# MERGE continuation 7 (main session, 2026-10-26 18:00)
1. Judge speed screens every candidate before it enters cand/. merge5i_d672e9499bad5802 (3.58725e-5) is not
   promotable: paired zebra 1e6 / one-process judge 282.4 s and 304.3 s versus v37i 8.1 s and 6.4 s, beyond the
   one-hour scoring limit at 1e8. Its fuse:RX2@29:M10@28 edit (a measurement reused as an X-basis preparation) sends the
   exact engine onto its general-atom path, as EARLIER found for RX2 reuse. Run the general-atom dispatch check
   (EARLIER/dispatch.py or general_atoms.py) on each proposal before pricing, and a paired 1e6 judge timing on every
   finalist; record both. A finalist needs judge time <= 20 s per 1e6 and a positive expected-key delta
   (qtools.policy.expected_key_delta; loss gain minus 1.1e-7 x log2(time ratio)).
2. Combine with EARLIER's closed lane: its finalist cand EARLIER/cand/r46_209a2c071725d505_d6-20-19-10-2-22-16
   (3.5889779694e-5, A 0.50132, fast: 1.57 s vs v37i 1.52 s on sunfish) is v37i + reset/herald compounds q4@36 and
   RX8@38, measured RX1@17, detector c363 omitted, then herald:RESET25@32:v4, pair:3_4@24, det:362, det:3. Transplant
   these onto your best fast candidates (and yours onto it), price every applicable subset, then one budgeted pass.
3. Price with the shared package (work/tools/qtools, README there; PYTHONPATH=work/tools): price() is cached and replays
   every saved basis; it is the evaluator the main session verifies with.
A fast finalist below v37i - 3e-8 goes to cand/ at once.
