# T14: rank-4 14-T phase network on v36c (PLAN P80, reviewer 9 M01)

Verdict: **closed.** A complete grid-legal 14-T circuit scores 4.2× v36c, and no 14-T variant that keeps v36c's
suffix can win. No finalists.

## Circuits
| Circuit | Path | CX | Native ticks | R | All-orders 1-F | Acceptance | Judge 1e6 / seed 0 | Speed |
|---|---|---:|---:|---:|---:|---:|---|---|
| v36c (incumbent) | `work/lanes/MAIN/v36c` | 213 | 47 | 44 | 4.11516e-5 | 0.50273 | PASS | FAST |
| t14a (complete, grid-legal) | `t14a.{qasm,json}` | 140 | 32 | 29 (v36c's tick 44 shifted by 15) | 1.73021e-4 | 0.69371 | passed, 1-F 1.6236e-4, acceptance 0.69291 | FAST |
| t14x (diagnostic: t14a + an X-stabilizer check right after the network) | `t14x.{qasm,json}` | 152 | 38 | 35 | 1.00226e-4 (9.19e-5 with the check noiseless) | 0.65875 | not grid-legal by design (check CXs reach cells 24/30/32) | — |

`exact2.py` on t14a: first order 3.5e-19, so all its loss is second order and above.

## Construction of t14a
- **Removed:** v36c's whole data-side prefix, 115 CX: injection, double-cat check with T/T† layers, blue XZ check,
  hops, storage guards and echoes, and their 31 records/detectors. `decompose.py` finds it from qubit lifetimes.
- **Kept unchanged:** A, the B/C resource, round, decoder, readout and every detector, at v36c's relative times (98 CX).
- **New 42-CX stage on the A cells [1,14,8,9,2,16,15]**, each holding one code position next to its output data cell:
  1. |+_L⟩ by v36c's own 12-CX A encoder.
  2. The 14-T† network: 16 CX, 10 ticks, helper q7. T† on every data qubit plus 7 in-place rotations on even-weight
     parities, one per nonzero syndrome. A replay of the qubit rows confirms the 14 axes are exactly the 14 classes
     (syndrome ≠ 0, parity 0/1) and every row is restored.
  3. One hop per data qubit into its output cell; the 7 vacated cells are measured as detectors.
- No fifth coordinate (no q6 |+⟩, no c54, no cat): ideal acceptance 1, ideal loss 0, judge correctness passes.
- Identity: sort Z-parities on the data by (syndrome s, weight parity w), Z_L = (0,1). On the code space, minus the sum
  of the 14 classes with s ≠ 0 equals Z_L mod 8; the 7 harmful pairs are (s,0) + (s,1) = Z_L.

## Where the loss lands (all-orders counterfactuals, `work/lanes/MAIN/sparse/region.py`: named channels made perfect)
| Counterfactual | t14a | t14x |
|---|---:|---:|
| All noisy | 1.73021e-4 | 1.00226e-4 |
| New stage noiseless (suffix noise only) | 3.49745e-5 | 3.49745e-5 |
| Only the 7 even-parity T† noisy | 4.80878e-5 | 3.51852e-5 |
| Only the 14 T† noisy | 5.03717e-5 | 3.76082e-5 |
| Only the network noisy (16 CX + 14 T†) | 6.65990e-5 | 4.95677e-5 |
| Only the encoder noisy | 7.94267e-5 | 4.60113e-5 |
| Only hops and data wait noisy | 3.90560e-5 | 3.90560e-5 |

**Cap on any prefix change: 6.18e-6.** v36c with its own prefix and pre-round data wait noiseless (335 of 552 channels;
D→A, A, B/C, round, decoder, readout noisy; `spec_prefix.json` from `mkspec.py`): 3.49745e-5 at acceptance 0.839, the
same suffix-only number as t14a.

Mechanism:
- Rank 4 leaves no fifth coordinate to flag faults on the even-parity holders. Any holder fault (the T†'s phase error,
  a CX fault, an idle) becomes a weight-2-class data error: detectable alone, but a logical error together with any
  single Z of the matching class before the next X-check (data idle, encoder init flips and hooks, other CXs, A's Z
  errors copied by D→A before B→D checks X). In the 15-T cultivation the cat measurement catches holder faults, so only
  weight-1 errors reach the data. The isolated phase-only estimate (7.79e-7) misses this term.
- Without an X-check (t14a): the 7 even T† alone add +1.31e-5 (4.809e-5 with the rest of the prefix perfect, above
  v36c); their partners are mostly suffix faults, so no 14-T design without an X-check between the network and D→A can
  win with this suffix (measured at t14a's placement; other placements inferred).
- With an X-check right after the network (t14x): the even T† drop to +2.1e-7, but the network's own CX faults still
  cost +1.46e-5 (2.4× the cap), before the encoder (+1.1e-5), the check as built (+8.3e-6), hops and wait (+4.1e-6).
- The shorter prefix (115 → 42 CX) raised acceptance 0.503 → 0.694; that cannot buy back 1.3e-4.
- No earlier round with this suffix: A, B and C occupy every neighbour of the output cells for ~10 ticks before the
  round, so the data sit in place from ~tick 35 whatever the prefix; t14a's earlier native round is a pure shift.
- v36c's A encoder was reused for the data |+_L⟩ (built to tolerate X faults; its Z hooks cost +4.45e-5 here). A
  Z-tolerant encoder would cut that but cannot change the verdict.

Open (not built): only a different suffix changes this, one with an X-check before A's Z errors are copied onto the
data, or a non-Steane final round (P77).

## Verification
- `fast_check.py lanes/T14/t14a.qasm lanes/T14/t14a.json 1000000 6`: passed.
- All orders (`MAIN/sparse/sparse_walsh.py`): t14a 1.7302051054650784e-4; v36c reproduced
  4.1151559437773416e-5. Main session re-ran the cap: 3.497454802481093e-5, acceptance 0.8392293768569918.
- Speed: `general_atoms.py t14a` FAST. Pair ledger `t14a.exact2.txt` (top pairs: encoder-seed init Z flip × data idle
  at the output cells; even-parity T† Z × the same idle).
- Not run: 3-seed MC or re-draws (4× gap); t14x cannot pass the judge by design.

## Files
`build_t14.py` builds both circuits; `qcirc.py` layered QASM read/write (v36c round-trips exactly); `decompose.py`,
`mkspec.py`, `v36c_prefix_idx.json`, `spec_prefix.json` split v36c and define the cap; `regions_t14*.py` +
`MAIN/sparse/region.py` give the tables (`t14*.regions.log`); `timeline.py`, `records.py` print schedule and record map.
TREP/TREP2 sources: `git show a58eca7:work/lanes/TREP2/...`.
