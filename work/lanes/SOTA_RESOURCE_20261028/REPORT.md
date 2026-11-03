# Native resource search: completed checkpoint

No competitive complete circuit or SOTA result emerged from this lane. The team's subsequently verified combined native candidate has exact loss 3.566732196898089e-5 and acceptance 0.501644332; its validation and release belong to the parent lane. The latest reported public board key is 2.86759593420732e-5 (a sampled score); numerically matching it with the current best candidate’s exact mean would require a 19.60% reduction, but a sampled key and an exact mean are different statistics. All comparisons below are at p=0.001. An ideal-resource value is explicitly a counterfactual, not a circuit score or a bound on every redesign.

## Complete native circuits

Every row below has complete QASM and ordered-output specification, native adjacent CX gates, raw-state checking before ideal decoding, and a full all-orders noisy result. Source, preparation, measurement, gate and waiting noise are included. The first five rows alter the incumbent B/C resource preparation or instrument; the last two are jointly synthesized ABC measured-helper constructions.

| Construction | Exact loss | Acceptance | Interpretation |
|---|---:|---:|---|
| `resynth_safe` | 5.962589946361928e-5 | .5102399242809769 | Raw-valid 60-CX B/C resource, worse than incumbent |
| `pivot17` | 5.2346408425784915e-5 | .5073782729798796 | Raw-valid 64-CX B/C resource; forcing q17 into a plus input improved this family by 12.2%, but still worse than incumbent |
| `gauge102_safe` | 5.986943948949061e-5 | .5132915084811412 | Raw-valid 54-CX B/C resource with changed C parity instrument, worse |
| `gauge102_soft` | 9.952052716771644e-4 | .5175697849846729 | Raw-valid, first-order constraint relaxed, much worse |
| Three late reset heralds on `resynth_safe` | 5.760272871192392e-5 | .5075242533297032 | Real noisy R/M operations and checks; improves that poor family but remains worse |
| Seven-square joint ABC constructive baseline | .001258305289004034 | .219812508654334 | Raw-valid, 447 CX/85 ticks; inadmissible |
| Six-square original-data joint ABC constructive baseline | .006270610322780911 | .27801426350428343 | Raw-valid, 401 CX/84 ticks; inadmissible |

The seven-square complete artifact is in `SOTA_20261028/geometry_cand/seven_measured_baseline_cc15a1ad0db415a2_d11_22_28_1_2_25_13`. Its two harmful single-fault components are XI on CX 32→33 at tick70 and XX on CX 32→31 at tick71; their total c1 is .0666666667. Repairing those alone would not resolve its acceptance or full loss. The six-square complete artifact is in this lane's `geometry_cand/six_measured_baseline_47612ef3a30c53bd_d6_20_19_10_2_22_16`. All-orders receipts are in their `.result.json` files.

Additional actual deletion probes: removing 62 late CX gates simultaneously is raw-valid and has c1=0 but gives L=4.1536749037422436e-5, A=.4752226629255694. Four random subsets of 14–44 such removals also fail acceptance and are worse. This limited family cannot rule out other joint designs. The exact receipts are saved with their QASM/specs; c1 was used as a diagnostic, never as an eligibility rule.

## Fault evidence and targeted input checks

The complete second-order physical-clock audit of `resynth_safe` gives c2=54.704444444444384; the earlier verified phase incumbent has c2=31.54888888888883. The reset-X fault on q17 at clock32 has 4.10 units of fault-pair participation, q11 reset 1.33333 and q23 reset .76667. Participation is not an additive allocation of the finite-p loss. The all-orders intervention that makes only the q17 reset channel perfect reduces L from 5.962589946361928e-5 to 5.552810310269837e-5 with unchanged acceptance. This is a nonphysical intervention, not an achievable circuit score.

The actual best three-herald circuit uses R17@31/M17@32, R11@35/M11@36 and R23@31/M23@32, with checks and all additional noise included. It reaches the table's 5.76027e-5. Directly reusing the earlier MX result on q17 after H, while removing its reset, produced an uncorrected raw data syndrome; the deterministic-record completion did not make the raw output correct. The forced-plus q17 preparation instead yielded the better `pivot17` circuit reported above.

## Geometry and counterfactual headroom

Exhaustive enumeration with both the original data and all seven incumbent B positions fixed found 160 disjoint A/C layouts. The unique maximum has five square contacts, mask61: A=[7,14,18,4,8,21,15], C=[13,32,24,5,9,27,23]. This finite statement is not a global geometry bound.

For that five-square geometry, the desired C X-space is span of masks 25,45,2,64 and the B/C input is precorrelated by B→C. With the actual complete NATIVE2 source through clock40, but perfect instantaneous A/B/C preparation and the artificial preparation waits removed, the native terminal at clocks41–43 gives L=2.801133083004897e-5, A=.6035798180576972, raw-valid and without harmful single faults. With actual v37j history through clock44, the analogous diagnostic gives L=2.9378185203967135e-5, A=.5719680515767013. Neither result includes physical resource preparation. The first version of the early diagnostic accidentally zeroed only one of the five inserted preparation ticks; it was corrected and recomputed, and the incorrect value is not used here.

The incumbent B verification cannot simply be retained in this five-square layout: its old C cells q18 and q4 overlap the new A block and are used through CX@46 and M@47. Reusing B therefore requires an actual change of verification, routing or timing. No such complete circuit was achieved in this lane.

A separate 108-CX/20-layer mask85 B/C resource on a connected geometry passed all 22 conditional CSS-state checks. Its ideal synthetic D/A input diagnostic, with all resource and terminal noise retained, had L=.0021300683609068115 and A=.7803496818676123. Two physical reset-verification reads improved that counterfactual to L=.0018027725037598273, still poor. These are not complete physical source circuits.

The SpiderCSS 20-wire six-square interaction graph has 24 distinct edges, is planar but non-bipartite, and contains a degree-five flag. Thus its fixed static graph cannot embed directly in a degree-four bipartite square grid; moving or bridge interactions are needed. The separately generated mask85 24-CX/four-flag gate list required at least 481 CX under the specific static output placement, free-flag enumeration and dirty-bridge model tested here; this is not a bound on other circuits or moving layouts.

## Search status and reproducibility

The following 300-second state-only searches ended `UNKNOWN`, without a witness: mask45 measured helpers at depth22, original-data six-square joint ABC at depth23 both with fresh reset and with certified source axes, and the five-square known-source-axis searches at depths22 and24. A fixed-layout borrowed-A four-square state-only search ended `UNKNOWN` after 600 seconds at depth32; the connected mask85 hard fault-aware model ended `UNKNOWN` after 300 seconds at depth20. `UNKNOWN` is not an infeasibility proof. No search process from this lane remains running.

Measured helpers may retain arbitrary linear output rows and are read in X; their outcomes are kept for complete detector-contract derivation. This avoids a forced helper-uncomputation boundary. Both a complete seven-square and a complete six-square circuit using this representation were raw-valid, but neither the bounded solver searches nor the constructive heuristics obtained a competitive preparation. `publish_manifest.json` lists the selected source scripts, complete QASM/specs, exact receipts, diagnostic ledgers and search-status files with SHA-256 hashes. Scripts import the repository's pinned qtools, judge and named earlier-lane helpers; those dependencies were not modified.


## Direct measurement-instrument pilot

`direct_parity.py` implements an actual complete native circuit with the incumbent source prefix followed by six direct data-stabilizer measurements. Each uses a real prepared ancilla, noisy native CX bridges and a measured record; no encoded ABC resource is prepared. Dirty bridge sequences restore intermediate states ideally, and every CX edge is nearest-neighbor. The six readouts are serialized in this bounded construction. Full deterministic-record completion and raw-state checking pass.

The complete result has 345 CX, 147 ticks, c1=6.566666666666661 (92 harmful components), exact L=.019289354923621528 and A=.36983517209735867. Its QASM/spec and all-orders receipt are in `cand/direct_parity_99ce73d2594d76fc_d6_20_19_10_2_22_16` and `direct_parity.receipt.json`. It is inadmissible and not competitive. This rejects this serial, unflagged dirty-bridge implementation; it does not rule out a parallel flag/cat measurement network, graph-state construction or a jointly synthesized instrument.

The source boundary has certified single-cell product axes for all 29 non-data cells (`NATIVE2_20261027/prefix_product_states.json`). Consequently there is no hidden entangled ancilla resource to extract at that particular completed boundary. The record-dependent q17 phase is usable only if the complete record contract and raw output remain valid. Exploiting earlier source entanglement therefore requires changing the boundary or delaying/replacing earlier measurements, not merely relabeling the final product cells. Graph-state local complementations remain a representation option but do not, by themselves, supply a low-cost native preparation or a fault-protected measurement contract. The strongest next concrete direction is to co-design an earlier source boundary with a parallel, flagged local parity or graph-measurement instrument, tracking all measurement-dependent byproducts in the actual terminal detector contract and ranking complete circuits at finite p. The main bottleneck is simultaneously achieving source-compatible cell release, short data lifetime, correct raw output and low accepted fault residue; neither the existing fixed-state solvers nor the serial direct-check pilot demonstrates that combination.
