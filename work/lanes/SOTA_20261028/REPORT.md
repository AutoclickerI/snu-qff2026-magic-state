# SOTA search: measured progress and architecture decision

## Result

**SOTA has not been reached.** The best complete native circuit produced in this checkpoint has exact conditional infidelity **3.566732196898089e-5**, acceptance **0.5016443322953218**, 412 CX gates, 49 physical clocks and 15 T/T-dagger gates. It passes raw Steane-state correctness and the official one-million-shot format, class, correctness and acceptance checks. It has not been submitted or given a new official 100-million-shot score.

This is a **0.0391%** improvement over this branch's previous phase candidate, and a **0.5677%** improvement over `MAIN/v37j`. It is maintenance, not the requested architectural jump. The principal deliverable is a broader set of complete, reproducible architecture experiments, including several implementations that do not use CP-SAT to generate their gate structure, and a more precise account of the remaining obstacle.

The [public leaderboard snapshot](leaderboard_final.json), retrieved **2026-10-27 17:29:26 UTC / 2026-10-28 02:29:26 KST**, shows Placeholder at **2.82064394141452e-5**, key **2.82e-5**, 277 CX, acceptance 0.50059491. Our existing entry remains **3.30430020090153e-5**, key 3.30e-5, 412 CX. These are sampled official scores. They are not the competitors' exact expectations. Bringing our new exact mean down to the numerical value of the current leading draw would require another **20.92%** reduction; that is a useful conservative milestone, not an estimate of the leader's true mean or a guarantee of a future ranking.

The hourly race remains parked under the owner's recorded stop instruction, R-20261027-1. This checkpoint did not restart it, submit a circuit, change the judge or shared evaluator, or promote a research candidate into production.

Publication of the broad checkpoint was blocked by automatic approval review. The existing draft PR has not been advanced; the complete selected work is local. [PUBLICATION.md](PUBLICATION.md) records the exact proposed export and approval requirement. Detailed lane reports retain their earlier timestamped benchmark; the later leaderboard refresh is reflected above.

## The best-supported method

The strongest direction supported by the experiments is **joint native synthesis of an earlier source boundary and its final measurement instrument, ranked by the full noisy accepted output**. The circuit, its resource preparation, cell reuse, timing, measurements and legal record-dependent logical frame have to be chosen together. A prescribed intermediate CSS state or a particular grid-free gate list is an optional construction, not the definition of the task.

This is an evidence-based research priority, not a proof that one algorithm is globally best. CP-SAT remains useful for finite geometry models, local state synthesis and schedules. It does not decide which physical architecture to ask for. Replacing it with a generic heuristic while retaining a fixed source boundary and expensive resource interface did not solve the problem either: thousands of constructive, measured-helper CSS proposals produced actual valid modules, but their preparation finished much too late.

Grid-free designs remain useful as **controlled mechanism experiments**. They are not the principal optimization target. A design that is already close to the best native score before routing has little room for additional physical operations. Moreover, conditional infidelity is not monotone under every change of noise or postselection, so a grid-free number is not automatically a rigorous lower bound on all native descendants. Each actual construction must be scored in full.

The practical object to optimize is

\[
L(C)=\frac{\mathbb{E}[\mathbf{1}_{\mathrm{accept}}(1-F)]}{P(\mathrm{accept})},
\qquad P(\mathrm{accept})\ge0.5002,
\]

at the contest's physical error rate, with native adjacency, raw noiseless code-space correctness and all gate, preparation, measurement and idle channels included. CX count, makespan, absence of harmful single faults and the second-order coefficient are proposal diagnostics. None substitutes for this objective. The official acceptance threshold is 0.5; 0.5002 is the repository's research margin.

## 1. Complete native results

Every row below is an actual gate-level construction. The best-candidate row is eligible under the checked gates; several controls fail acceptance or have large error. All quantities in this table are full-noise expectations, not low-shot ranking estimates.

| Construction | Exact loss | Acceptance | CX / clocks | Outcome |
|---|---:|---:|---:|---|
| `MAIN/v37j`, prior main reference | 3.5870950035e-5 | approximately 0.50102 | 412 / 49 | Previous reference |
| Prior branch phase candidate | 3.5681272391e-5 | 0.501016047 | 412 / 49 | Previous branch reference |
| **Combined early schedule and late reset heralds** | **3.5667321969e-5** | **0.501644332** | **412 / 49** | Best new native circuit; small gain |
| B/C resource resynthesis, safe construction | 5.9625899464e-5 | 0.510239924 | See resource receipt | Worse |
| Resynthesized B/C with forced plus input on q17 | 5.2346408426e-5 | 0.507378273 | See resource receipt | Best tested alternative in that family; worse |
| Seven-square measured-helper joint ABC | 1.2583052890e-3 | 0.219812509 | 447 / 85 | Raw-correct, inadmissible |
| Six-square original-data measured-helper joint ABC | 6.2706103228e-3 | 0.278014264 | 401 / 84 | Raw-correct, inadmissible |
| Direct native stabilizer reads using dirty bridges | 1.9289354924e-2 | 0.369835172 | 345 / 147 | Raw-correct; slow, unflagged pilot fails |
| Final output moved into existing B, three fresh RX sources | 3.7237590934e-5 | 0.497672825 | 412 / 49 | Raw-correct with logical Z frame; inadmissible and worse |

The best artifact is [`native_best/schedule_heralds_c167977fdd48de1f_d6_20_19_10_2_22_16.qasm`](native_best/schedule_heralds_c167977fdd48de1f_d6_20_19_10_2_22_16.qasm), with its ordered-output JSON and [exact receipt](native_best/schedule_heralds_c167977fdd48de1f_d6_20_19_10_2_22_16.result.json). The raw six-stabilizer expectations are all unity within floating-point tolerance and raw infidelity is zero. The exact contraction reports a kernel omission bound of 3.7384e-14.

The [official one-million-shot check](native_best/official_1m.log) passes all gates and reports acceptance 0.500581. Its sampled loss happens to be 1.59814e-5 with SEM 4.47e-6. **That small sample is not evidence of a SOTA mean or leaderboard score.** The exact mean above is the ranking quantity used here. The earlier 100-million-shot receipt belongs to the previous phase candidate, not to this new QASM.

The combined circuit comes from 40 completed whole-native schedule proposals and the independently tested detector/herald changes. It retains the early schedule through clock 25 and the late parent afterwards. The actual new reads include M13 at 34, M33 at 39 and MX14 at 35. Their physical noise and the altered accepted-record sector are included. `combine_native.py` reproduces the combination; `schedule/results.json` preserves the complete schedule-search ledger.

Further native work included actual compact Bell-source constructions, targeted physical flags, early/later source checks, B/C row-space alternatives, a 62-gate deletion control, source symmetries, explicit coherent moves and readout-assisted resource construction. Some had zero harmful singles yet much larger full loss. Their detailed receipts are in the [source report](../SOTA_SOURCE_20261028/REPORT.md) and [resource report](../SOTA_RESOURCE_20261028/REPORT.md). Those finite failures reject the tested constructions, not their entire mathematical families.

## 2. Complete abstract-connectivity results

These circuits include their actual source, resource preparation, measurements and idle noise. They deliberately relax two-qubit adjacency and are **not native or submittable**.

| Construction | Exact loss | Acceptance | CX / clocks | Interpretation |
|---|---:|---:|---:|---|
| Reconstructed shared-flag seven-cat source and square ending | 2.9720782263e-5 | 0.708168212 | 141 / 21 | Best seven-cat-only result reconstructed here |
| **Seven-cat source plus published 14-CX Steane instrument** | **2.9649858252e-5** | **0.640392636** | **155 / 25** | Best new complete abstract result; still above the current leading draw before routing |
| SpiderCSS six-square B/C preparation and complete source | 4.2336779185e-5 | 0.643339760 | 125 / 26 | Correct resource; complete noisy result loses |
| SpiderCSS four-square preparation, best tested timing | 4.3075755491e-5 | 0.752206878 | 117 / 19 | Fewer gates/clocks did not give a better output |
| Gao–Yuan–Yao live-output reconstruction, late T/reset schedule | 4.5215039968e-5 | 0.724118 | 160 / 23 | Raw-correct, corrected physical output; worse before routing |

The [detection report](../SOTA_DETECT_20261028/REPORT.md) includes the exact seven-cat and 14-CX results, full search ledgers, raw checks and selected artifacts. The 14-CX instrument is implemented from the authors' published algorithm; its physical operations are included in the score. Additional encoded K-block verification, K-state reuse and terminal replacement did not improve the complete result in the tested schedules.

The previously documented `DEEP/cand/final_flagh` value of 2.7185e-5 remains unverified in this workspace. The inspected GitHub path history contains briefs but not its actual QASM or receipt. Personal-context retrieval was unavailable. It may exist on the original research hosts, which are not accessible from this session. The new seven-cat result is an independent reconstruction and is not represented as that historical circuit.

## 3. The most informative geometry experiment

The experiment below keeps the actual source, native terminal gates, measurements and waiting noise, but supplies the desired resource **instantaneously and perfectly**. It answers how much score room a given source/geometry/timing leaves for a future resource construction. It does not supply that resource, establish an achievable score or prove a monotone lower bound for other redesigns.

| Source and final geometry | First terminal clock | Ideal-resource diagnostic loss | Acceptance |
|---|---:|---:|---:|
| Original unmoved source, six square contacts | 41 | 2.7498461497e-5 | 0.603735894 |
| Same | 42 | 2.7780959719e-5 | 0.599536661 |
| Same | 44 | 2.8455850255e-5 | 0.591229889 |
| Same | 46 | 2.9299101692e-5 | 0.583043853 |
| Reflected source, actual ten-CX route, seven squares | 44 | 3.0842185687e-5 | 0.590054423 |
| Same | 46 | 3.2106644704e-5 | 0.581885107 |
| Original unmoved source, five squares preserving B positions | 41 | 2.8011330830e-5 | 0.603579818 |

**One additional terminal square did not pay for the route and delay in the tested construction.** The unmoved six-square case leaves some numerical room at clock 41, and is already above the current leading draw by clock 44. This is why an earlier joint preparation is the main bottleneck. Merely making B/C connected, finding seven tiles or reducing source CX count does not establish a useful circuit.

The four-square reflected source is a real native boundary with only four route CXs, 255 total CX and 42 clocks. The seven-square source uses ten route CXs, 261 total CX and 44 clocks. Both pass raw correctness. However, minimum A and B/C bridge sets share cells, so their separate connectivity is not a simultaneous preparation schedule. A has to be prepared through cells used by B/C, or the whole accepted instrument has to change.

`measured_css.py` relaxed the resource contract: helper output rows need not be uncomputed to zero; helpers can be measured in X, with their records included in the final contract. Dual preparation of A turns its helper-induced phase offsets into readout offsets. This produced actual raw-valid complete circuits, but the tested constructive modules were ready around clock 81 rather than approximately 41–44. The failure is a large timing and noise gap, not a small repair problem. The bounded CP-SAT searches that returned `UNKNOWN` are recorded as budget exhaustion, never infeasibility.

Full data and scope: [source headroom report](../SOTA_SOURCE_20261028/HEADROOM.md), [six-square ledger](../SOTA_SOURCE_20261028/unmoved_six_headroom_results.json), [seven-square ledger](../SOTA_SOURCE_20261028/seven_headroom_results.json), and [resource geometry results](../SOTA_RESOURCE_20261028/REPORT.md).

## 4. Testing methods outside the incumbent search formulation

### Fault-tolerant CSS compilation

[SpiderCSS](https://arxiv.org/abs/2610.03714) constructs fault-tolerant CSS preparation circuits using ZX-calculus rewrites. The actual public compiler was run on both the six- and four-square B/C states. Each generated resource passed all target X generators and the full dual Z-space checks after its flag postselection. Its complete circuit nonetheless lost under the contest noise model. This is a concrete test of a different construction method, not a rejection of ZX methods or evidence that CP-SAT is superior in general.

The six-square compiler circuit's static interaction graph is non-bipartite and has a degree-five flag, so it cannot be placed unchanged as a static subgraph of the square grid. Movement or a rewritten circuit is required. The tested static dirty-bridge placement cost is a result for that fixed graph and placement model only.

### New Reed–Muller conversion

The September 2026 [Gao–Yuan–Yao paper](https://arxiv.org/abs/2609.12698) reports a destructive error-detection diagnostic. Its headline value cannot be compared directly with this contest's live, unmeasured Steane output. The reconstruction here supplies the grouped checks and physically compiles the bulk-record-dependent Z corrections into sixteen actual CXs. It passes raw output correctness.

After reducing the schedule from 84 clocks to 23 and moving T gates/resets later, the best complete abstract loss is 4.5215e-5. Our generic source encoder uses 32 CX rather than the paper's 25, so this is not an exact replication of the paper's gate budget or a universal exclusion of the scheme. It is a complete corrected-output control under the present evaluation contract.

### Constant-depth gauging

The September 2026 version of [Hetényi–Brown–Williamson](https://arxiv.org/html/2603.05429v2) uses record-dependent local Clifford corrections. For the literal distance-three product-W byproducts, an exact 128-dimensional calculation checks all 64 complementary frame classes. Under the explicitly stated uniform ideal-frame assumptions, only one class is in Steane code space and recoverable by a logical Pauli alone: conditional acceptance 1/64. Even perfect code-space projection gives total conditional acceptance 11/256. Allowing the best logical Pauli frame for every class does not improve either result.

This rules out simply importing that literal construction without its recovery under the contest's acceptance requirement. It does not rule out physically compiling a different coherent recovery or redesigning the gauging circuit. No claim is made that the paper itself fails under its own assumptions.

### Direct instruments and teleported outputs

The direct native parity-read pilot replaces an exact ABC-resource target with actual stabilizer measurements. Its unflagged serialized bridge implementation is raw-valid but needs 147 clocks and fails badly. At the completed incumbent source boundary, all 29 non-data cells have certified product axes. Reusing useful source entanglement therefore means changing an earlier measurement or boundary, not merely assigning a new name to the completed boundary.

Encoded Bell teleportation was also tested with perfect input/resources and real terminal noise. Its output waits give a 4.6296e-5 diagnostic. A one-bit dual teleportation instrument is better: with a hypothetical perfect receiver prepared just in time, its terminal diagnostic is 2.5576e-5, close to the ideal square control. Without that timing assumption it is 3.4196e-5. These are ideal-resource diagnostics, not gate-level preparation solutions.

That observation motivated a **complete native terminal role swap** on the incumbent: reverse the last seven B→D gates, read the old D in X, retain B and apply a logical Z frame. The unchanged source fails raw code-space correctness even after re-deriving its entire affine detector space: three earlier measured-source records leave physical phase offsets on B that the old destructive B readout had absorbed. Replacing those three inputs with actual fresh RX operations repairs raw correctness, but the full result is 3.7237590934e-5 at acceptance 0.497672825. It fails the acceptance gate and does not supply a performance jump. This distinguishes a real interface obstruction from a presumed routing problem.

## 5. What the next successful construction must change

The current evidence favors changing an **earlier source boundary and the final accepted operation together**. Useful proposals should either preserve and repurpose source entanglement before its measurement, finish the necessary native resources before approximately clock44 on the unmoved output, or realize the required accepted measurement map with a cheaper physical resource. The measured output-relocation control adds a fourth concrete interface constraint: random phases that were harmless on a measured ancilla must be physically removed or made an allowed logical frame if that ancilla becomes the output.

A constructive graph/stabilizer or ZX method can generate these changes. Local solvers can certify a small native gadget, choose compatible cells or schedule a proposed circuit. Search should retain several complete feasible families and their acceptance/lifetime tradeoffs, rather than repeatedly solving larger versions of one fixed gate list. Complete exact evaluation should decide which families deserve repair; bounded failures and counterfactuals should not be promoted into impossibility statements.

The existing phase/schedule candidate is the best verified native artifact in this checkout. None of the alternatives tested here is a SOTA result, and the evidence does not establish a globally optimal method. There is no competitive native joint-source/instrument construction to promote yet.

## Reproduction and evidence

- [Reproduction commands and selected artifacts](REPRODUCE.md).
- [Source, geometry, gauging and Gao lane](../SOTA_SOURCE_20261028/REPORT.md).
- [Resources, helper measurements and direct native instrument lane](../SOTA_RESOURCE_20261028/REPORT.md).
- [Detectors, SpiderCSS, seven-cat, published Steane instrument and teleportation lane](../SOTA_DETECT_20261028/REPORT.md).
- [Previous architecture review and matched mechanism controls](../STRATEGY_20261027/DECISION.md).

The publication manifests retain selected QASM, ordered output specifications, complete evaluation receipts, source scripts, full result ledgers and dependency hashes. External tools are pinned in each lane's provenance. Downloaded environments, unselected candidate bulk and unlicensed third-party full source are not part of the published checkpoint. The original judge and shared evaluation implementation are unchanged.
