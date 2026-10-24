# AENC: flag-aware A encoder on v36c (PLAN P59)

Verdict: **closed, no finalist.** Within the space searched, v36c's own 12-CX A encoder is the exact all-orders optimum
for its cell releases, D→A ticks and flag. The acceptance-trading variants cost 4.1e-5 to 7.6e-5 of loss per unit of
acceptance, far more than INTEG's trades, and acceptance is not the limit on v36d.

## Method: A-region class table (`bmodel.py`, `enc.py`, `evalx.py`, `table_v36c.json`)
Every fault inside A's encoder region (each A cell from its release to its D→A CX) reaches the rest of the circuit only
through which of 128 classes it leaves on A at the cut, so loss is a ratio of two sums over those classes. One table of
128 all-orders runs prices any encoder in microseconds; a new surroundings needs a new table (16–20 min on 16 processes
over two hosts). It reproduces full all-orders runs to ≈ 11 digits:
| Circuit | Decomposition | Full all orders |
|---|---:|---:|
| v36c | 4.1151559437663e-05 | 4.1151559437773e-05 |
| `deliver/aenc_nochk16` | 4.1215272046e-05 | 4.121527204640e-05 |
| `cand/check14` | 4.255640390533e-05 | 4.255640390551e-05 |
| drop15 base, own table (`table_drop15.json`) | 4.122250784865e-05 | 4.122250784852e-05 |
| drop15 + q9 check | 4.1216599324e-05 | 4.121659932401e-05 |

## Headroom on v36c (exact, all orders, `headroom.py`, `headroom_v36c.txt`)
| Made perfect | Gain | % |
|---|---:|---:|
| whole A region | 1.982e-6 | 4.82 (acceptance 0.51866) |
| region idles | 9.60e-7 | 2.33 |
| region CX | 6.19e-7 | 1.50 |
| region inits | 3.91e-7 | 0.95 |
| q16 check noise | 1.27e-7 | 0.31 |
| X/Y parts on A | 9.75e-7 | 2.37 |
| Z/Y parts on A | 1.551e-6 | 3.77 |
By cell (%): 1: 1.32, 2: 1.32, 8: 1.11, 16: 0.96, 14: 0.61, 9: 0.34, 15: 0.29; idles of cells 1, 2, 16 waiting for D→A
at 44: 0.94, 0.72, 0.54. By fault type: single Z on cells 1, 14, 2, 16 landing on a data qubit and completing a pair of Z
errors already on waiting data 0.96e-6; X parts (the same masking on the X side; cell 14 also second order) 0.82e-6;
flag-blind weight-2 Z_L terms 0.115e-6 (none at first order: the flag works); flagged Z_L terms 0.078e-6.

## Search (`asearch.cpp`, `mkin.py`, `rank.py`, `pareto.py`, `out_all_16.jsonl`)
Every CX-only encoder on A's 7 cells within each cell's window (ticks 36–43), all 35 pivot sets, up to 16 CX (87
distinct circuits); each input a reset (R or RX), RX then an MX check, or reuse of its release measurement (978
combinations), all ranked exactly. v36c's encoder is optimal; swapping the roles of cells 8 and 2 ties; the next distinct
circuit is +1.405e-6 (v36c's plus one A–A pair).

## Closures (each closes only the recipe tested)
| Recipe | Result |
|---|---|
| reuse q2 / q14 after their MX releases | no gain (first-order screen) |
| drop the hop checks on q8 / q9 / q16 | no gain (screen); none of those ticks binds |
| remove M57 and use q15 unmeasured | best of 58 full builds 4.5087e-5 (+9.6%) |
| remove M57 and reset q15 inside the encoder (1074 variants, exact) | best +6.5e-8 for +0.0009 acceptance, +7.1e-8 for +0.0017; next point +1.5e-6 |
| remove the q16 check (`deliver/aenc_nochk16`, judge PASS, 8.0 s/1e6) | +6.37e-8 for +0.00084 acceptance |
| decoder using cells {8,9} at 43 | no legal encoder |
| flag measured on q9 | not built; ≤ 0.08e-6 at stake |
| A–data and A–A idle pairs (30 full builds, `apairs.py`) | +7.6e-7 to +1.86e-6; only (20,14) at 39/40 gains (−4.5e-8), already in v36d |
| remove the 14→15 edge / the C17→A16 copy | +7.4e-8 / +1.34e-6 (acceptance 0.4996) |

## v36d gadgets on A cells
The q16 parity guard (RX 38, CX10→16 at 39, MX16 at 40) and the q14–q20 pair at 40–41 lie inside A's region; v36c's
encoder keeps both legal. `aenc_nochk16` removes MX16 (breaks the guard); the drop15 variants move q14/q16 gates to 40–41
(break both). q14's pairs at 19–26 precede its release at 36. Any future A encoder: keep q14 idle at 40–41 and q16's
38–40 slots free, or drop those gadgets.

## Prices for other directions
All A releases one tick earlier −0.45e-6 (−1.1%), two ticks −0.73e-6 (−1.8%) (first-order screens on v36c, excluding the
cost of freeing the cells; EARLY found no placement that releases them earlier). No free ancilla touches two A cells
(only data 3, 7, 10 do), so in-region stabilizer checks have no host (argued, not built). Moving D→A of cells 1, 2, 16 to
43 would trade their A idle for data idle at 44, which costs ≈ 1.4e-6 per data qubit (TERM): not pursued.

## Verified vs inferred
Verified: the decomposition against full all-orders runs on 6 circuits; optimality over the space above; full builds for
every closure quoting a number; judge and speed for `aenc_nochk16`. Inferred or not run: the earlier-release prices
(first-order screens); the q9-flag and in-region-check closures (argued); the drop15 variants were not judged.

## Files
Tools `bmodel.py`, `enc.py`, `evalx.py`, `analyze.py`, `asearch.cpp`, `mkin.py`, `scen.py`, `rank.py`, `pareto.py`,
`build.py`, `allorders.py`, `evalbatch.py`, `apairs.py`, `tail.py`, `dets.py`, `partners.py`, `triples.py`, `headroom.py`,
`ext15.py`, `sync.sh`; tables `table_v36c.json`, `table_drop15.json`; evidence `headroom_v36c.txt`, `apairs_v36c.log`,
`out_all_16.jsonl`, `sout_*.jsonl`, `res_drop15.jsonl`; builds `cand/`, `deliver/`.
