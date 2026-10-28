# Native flagged coherent gauging

This is an actual, fully noisy 6×6 implementation of the d=3 source/gauging mechanism, including physical seed preparation, flag and syndrome circuits, the full coherent recovery, measurement and idle noise. The best complete control here is raw-valid with L=0.0005706966845959146 and A=0.5866398052161582; it uses 150 CX, 46 clocks and 15 T/T-dagger gates. Its loss is about 16.0 times the incumbent loss, so it is **not a SOTA**. It meets the research acceptance margin but the required 1M-shot server-time guard has not been established. The valid circuit and exact receipt are `module_best_post.qasm` and `module_best_post.price.json`.

## Provenance and geometry

The primary sources are [Hetényi, Brown and Williamson, arXiv:2603.05429v2](https://arxiv.org/html/2603.05429v2) and [IBM/gauging_clifford_measurement](https://github.com/IBM/gauging_clifford_measurement), Apache 2.0. GitHub's latest repository head observed was `ce90c09c239b2173612c22cc12a2bbf5a7356680`; the actual `color_code.py` and `utils.py` source last changed at `3a5bb25eddcce5945f43b8f6ca462b0a48d2b25b`. Direct git clone was blocked by this environment, so the authors' source was inspected in the GitHub UI; independent native code transcriptions are included here with attribution and modification notices, without vendoring the source repository.

`geometry.py` independently implements the authors' coordinate rules. The 25-site geometry fits a 5×6 portion of the chip via q=6(row+1)+(column−1). The seven output sites in the judge's canonical Steane coordinate order are `[0,11,9,26,12,21,14]`, the three extra boundary vertices are `[2,23,24]`, and the three flags are `[7,16,19]`. Their plaquette data supports are `[0,9,12,14]`, `[9,11,14,21]`, `[12,14,21,26]`. `geometry.json` lists all 12 edges and maps each actual physical edge qubit to its two data vertices and flag.

The cycle detector supports in physical edge identifiers are `[3,13,1,8,6]`, `[8,22,10,17,15]`, `[15,25,13,20,18]`. In the fused-recovery circuit, the three non-tree chord readouts encode the corresponding independent cycle syndromes; the tree-edge outputs carry recovery-domain information and are not individually postselected.

## Seed and check

`seed.py` transcribes the authors' d=3 unitary initialization layers with their S-dagger seed replaced by T on q13. The 33-CX/18-clock native seed has exact noiseless encoded |T_L⟩, all six output stabilizers +1, and four deterministic source records. With T-dagger the raw infidelity is 0.5, so that alternative is rejected. The isolated T-seed finite-p loss is 0.0202275419; it is an unverified physical seed, not a complete cultivation result.

`stab.py` transcribes the authors' 10-layer flagged superdense stabilizer round, plus real reset and read clocks. Its 42 CX operations are all nearest-neighbor, and its 9 flag/syndrome readouts are deterministic on the clean encoded state. An actual seed plus this round gives L=0.00114175155, A=0.7443318354; this demonstrates the module but is not a competitive source. The round has three harmful single-fault terms in that standalone control.

## Complete gauging implementation and controls

`assemble.py` builds the native graph's first gauge contraction and first flag pass in three edge-colored CX layers. The second flag-to-edge pass occurs after gauge data MX and before the tree recovery's edge-to-child CX. The flagged edge sets are 7→{1,6,8}, 16→{10,15,17} and 19→{13,18,20}. Boundary sites start RX, participate in the first gauge MX as X vertices, and are checked again with MX after recovery.

The fused recovery traverses a spanning tree outward. For each parent p, child c and edge e, its action is CX p→e, CX c→e, CX e→c, with child-to-edge gates precomputed before overwriting child values. Each chord then receives the two adjacent data-to-edge CXs. This uses native interactions only, and the published per-basis bit identity was exhaustively checked independently by the publisher lane for every data-plus-edge input, including nonzero cycles. Seven T gates precede the first data MX; seven T-dagger gates are delayed until after coherent recovery. Together with the one seed T this meets the judge's 15-rotation exact-contraction scope. All deterministic affine records are rederived on the complete assembled circuit, and the official exact raw check precedes pricing.

| Complete physical circuit | CX / clocks | Exact loss | Acceptance | Harmful singles |
|---|---:|---:|---:|---:|
| Seed + flagged gauge | 108 / 42 | 0.0299575985583 | 0.6582949471 | 235 |
| Seed + pre-stabilizer + flagged gauge | 150 / 55 | 0.0143560583750 | 0.5463046684 | 33 |
| Seed + flagged gauge + post-stabilizer | 150 / 55 | 0.0008348867992 | 0.5044065082 | 0 |
| Seed + root-11 gauge module + post-stabilizer | 150 / 54 | 0.0007568072955 | 0.5225913789 | 0 |
| Seed + root-14 gauge module + post-stabilizer | 150 / 46 | 0.0005706966846 | 0.5866398052 | 0 |
| Seed + pre-stabilizer + flagged gauge + post-stabilizer | 192 / 68 | 0.0006574032924 | 0.4327630939 | 0 |

All six are raw-valid with output stabilizers +1. The pinned 10,000-shot judge sanity check of the root-14 circuit passes all gates (sample acceptance 0.5883); the sample is too small to rank loss. A separate 1M-shot run did not exit after approximately 40 seconds and was interrupted; the 20-second-per-million promotion guard remains unverified. The optimized gauge uses the independently synthesized root-14/15-clock module from `GAUGE_SCHEDULE_20261028`, with its complete detector space rederived; its companion `assemble_module.py` preserves the full seed and final syndrome noise. The final row misses acceptance; the post-only row is acceptable but its loss is substantially worse than the incumbent. Zero harmful single faults is only a diagnostic and does not imply good finite-p loss.

The two optimized rows have distinct preserved circuit and receipt pairs. The earlier root-11/23-clock module is `module_root11_post.qasm` with `module_root11_post.price.json`; it yields the 54-clock result. The current root-14/15-clock module is `module_best_post.qasm` with `module_best_post.price.json`; it yields the 46-clock result. The completed physical raw/singles run receipts are `module_best.log` for root 11 and `module_new.log` for root 14; `official_10k.log` is the separate root-14 judge sanity check. The earlier price receipt's internal `stem` still says `module_best_post`, and its metadata names the then-current `GAUGE_SCHEDULE_20261028/best.json`, which has since been replaced by the root-14 module. Use the preserved root-11 QASM and its receipt hash for that historical result, not the mutable path inside the old metadata. Both complete circuits have 150 CX and 15 T/T-dagger gates; neither is a SOTA result.

`pairs.py` groups the baseline post-only control's second-order accepted-loss coefficient, obtaining approximately 776.03. The largest grouped contribution, approximately 393.34, pairs faults within the final 13-clock stabilizer round; another 82.23 combines that round with gauge recovery. For the optimized root-14 module, `pairs_best.py` gives c2≈536.79, including the same ≈393.34 from within the final round. These labels group model channels and do not prove a lower bound or replace the all-orders finite-p result. They identify the final native instrument and waiting time as the key measured cost in this concrete implementation.
