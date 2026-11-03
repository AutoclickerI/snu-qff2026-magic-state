# Continuation: native instruments, coherent gauging and live output

## Artifact availability after workspace recovery

**This PR contains a partial recovery of the continuation: 291 of the 885 selected files, plus a recovery manifest.** The temporary workspace was cleared before publication finished. The first thirteen upload batches survived in GitHub tree `1ff17cc3150d2fa8a00b964bcbf9b5d03187185f`; the remaining 594 selected files and the original full manifest were not recovered from the sources checked. The previously published checkpoint and native-best circuit remain intact.

The research narrative below records the completed experiments before that loss. Some linked reports, scripts and supporting receipts are unavailable, so this export does not provide complete reproduction of all 24 lanes. The original `selection_audit.json` describes the pre-loss inventory and must not be read as an audit of the recovered subset. [recovery_manifest.json](recovery_manifest.json) identifies the files actually retained, their source Git blob IDs and their current hashes. [PUBLICATION.md](PUBLICATION.md) explains the recovery and publication scope. No missing experimental artifact has been fabricated or represented as recovered.

## Outcome

**SOTA has not been reached. The best complete native circuit remains unchanged:** exact conditional loss **3.566732196898089e-5**, acceptance **0.5016443322953218**, **412 CX, 49 clocks and 15 T/TDG**. Its QASM SHA-256 is `c167977fdd48de1f6ab3ec8fbb246bd59b4edc13f08d00d032f60bc1658b06a3`; the circuit and exact receipt are in [the previous native-best checkpoint](../SOTA_20261028/native_best/). This continuation has produced new constructive identities, complete alternative circuits and stronger falsification tests, but no better native score. A lower gate count or a successful noiseless proof is not being represented as a performance win.

At **2026-10-28 02:07:35 UTC**, the public board showed Placeholder at **2.7646927086892e-5**, 277 CX, sampled acceptance 0.50059813. Our board entry was **3.30430020090153e-5**, 412 CX. These are submitted finite-shot draws. The leader's exact expected loss is unavailable, so comparing its draw to our exact mean does not establish its underlying mean or the exact improvement required. The timestamped public receipt is [leaderboard_latest.json](leaderboard_latest.json); `fetch_board.py` reproduces the read. No new contest submission or production race was started.

The earlier approved research checkpoint was published to draft [PR #1](https://github.com/AutoclickerI/quantumn/pull/1) at `781ab32058a0567516981f9586338d5cdb6896d1`, followed by metadata corrections at `7cb6d35a735df2630582f7f90efe31105ccc298d`. Main remained `82657bf8e1de91f40e9137f5a517e6f4dacd7518`. Publication of the additional artifacts documented here is tracked separately; this report is not a claim that an unverified candidate has been promoted.

## What the high-level review changes

The appropriate search object is the **complete accepted quantum measurement process on the physical grid**, including its resource preparation, outputs, record dependencies and waiting. Grid-free circuits are useful controls: they can reveal headroom, expose an algebraic identity and rule out a specific design before routing. They cannot select the best native architecture by themselves. Here, a 190-CX native cat construction loses badly to a 412-CX incumbent, and a 33-CX resource preparation lost a crucial verification layer when integrated. Both examples show why optimizing the wrong abstraction can give convincing but misleading progress.

CP-SAT remains useful for a finite local scheduling or matching question. It has not established the best architecture. The strongest new change in this continuation came from an algebraic rewrite of coherent gauging, after which a scheduling solver selected a 15-clock realization. Other work used exact Clifford isometries, purified input-support analysis, constructive GF(2) elimination, graph enumeration and direct fault-response probes. Full noisy loss, rather than the optimizer's internal objective, decides whether a construction advances the task.

The resulting workflow is:

1. Define a live-output process that satisfies the contest's raw Steane-code condition and legal logical-frame rules.
2. Establish the ideal operation and the errors it accepts or rejects, including source-record byproducts.
3. Derive a native construction and its actual qubit lifetimes. Use idealized controls only with explicit scope.
4. Price the entire circuit at p=0.001, including every reset, gate, read and idle. Rank conditional loss subject to acceptance; use harmful singles and pair coefficients to explain results.
5. Run the official validity/runtime checks before promotion. A correct state or zero harmful singles does not replace this gate.

This is an evidence-based search strategy, not a proof that one mathematical family is globally best. The tested fixed-source replacements have mostly exhausted their useful headroom. Any larger improvement must change the source, resource and final measurement together, or exploit a demonstrably better terminal code contraction.

## Complete physical results

All rows below include their real preparation and timing noise. They are native unless a row explicitly says otherwise. Values are expectations from the exact evaluator, not favorable shot samples.

| Construction | Exact loss | Acceptance | CX / clocks | Result |
|---|---:|---:|---:|---|
| Existing native best | 3.5667321969e-5 | 0.5016443 | 412 / 49 | Still the best complete native result |
| Source-isometry reduction, six benign sectors accepted | 3.6503004591e-5 | 0.5010334 | 369 / 49 | 43 fewer CX; 2.34% worse loss |
| Fresh receiver, one benign sector accepted | 3.7247153714e-5 | 0.5002010 | 412 / 49 | Valid, narrowly eligible, worse |
| Joint A isometry and coherent source tag, six sectors accepted | 5.4650093756e-5 | 0.5008874 | 412 / 50 | Valid, worse |
| Earlier-boundary native tag fanout | 6.8332303559e-5 | 0.4263680 | 415 / 54 | Fails acceptance |
| Two native seven-cell cat checks, corrected A contract and transfer heralds | 8.9778785569e-5 | 0.5618978 | 190 / 41 | Corrected native architecture; worse loss |
| Coherent gauging, optimized root14, native final check | 5.7069668460e-4 | 0.5866398 | 150 / 46 | New native architecture, worse |
| Constructive measured-helper B/C resource, restored uncopy | 2.3771450182e-3 | 0.5037079 | 342 / 49 | Valid raw output, harmful accepted singles |
| Published low-overhead Steane checks via native bridges | 3.8948674626e-3 | 0.4424419 | 321 / 88–89 | Fails acceptance and loss |
| Late-coupling Bell terminal, both resources physically verified, abstract | 6.0643544946e-5 | 0.6699696 | 147 / 25 | Valid and zero harmful singles, not native or competitive |

The individual reports contain the precise candidate stems, receipts and limits: [source isometry](../SOURCE_ISOMETRY_20261028/REPORT.md), [receiver](../JIT_RECEIVER_20261028/REPORT.md), [joint A](../JOINT_A_ISOMETRY_20261028/REPORT.md), [earlier boundary](../EARLY_BOUNDARY_20261028/REPORT.md), [native cats](../NATIVE_CAT7_20261028/REPORT.md), [gauging](../COHERENT_GAUGING_20261028/REPORT.md), [measured B/C](../MEASURED_BC_20261028/REPORT.md), [native direct checks](../NATIVE_INSTRUMENT_20261028/REPORT.md) and [Bell resources](../KNILL_RESOURCE_20261028/REPORT.md). These bounded failures do not rule out their entire families.

## Constructive result: physical coherent recovery for gauging

The published [gauging protocol](https://arxiv.org/html/2603.05429v2) measures a transversal Clifford operator using a graph and classical correction. The contest does not provide arbitrary physical feed-forward for free. Earlier analysis of simply discarding the correction would retain too few random branches, but that is not an obstruction to a physical coherent recovery.

For a connected graph with n data vertices and E edge ancillas, let G apply CX from each endpoint to its edge. On each true Steane data vertex, use U = T-dagger X T; the extra boundary vertices use X. Computing a rooted domain assignment from the edge outcomes and controlling the required U corrections gives the desired logical projector. Moving T-dagger through the data-control graph gates allows it to cancel the T preceding coherent correction. The resulting gadget uses the same fourteen data T/TDG gates as the transversal sandwich; the complete source has fifteen including injection.

More strongly, the second graph interaction, edge-domain decoding and controlled-X recovery can be fused into a native tree sweep. For parent p, child c and their edge qubit e, the gates are:

```
CX p,e
CX c,e
CX e,c
```

Process the tree from its root. Each non-tree edge then receives CX from its two updated endpoints and stores a cycle check. The recovery costs **2E+n−1 CX**, so the two graph passes together cost **4E+n−1 CX**. There are no required edge-to-edge nonlocal gates. For the author's ten-vertex, twelve-edge graph this is 57 CX, plus 18 physical flag CX, giving a **75-CX native gadget**.

This identity was independently tested as a full binary permutation, including nonzero cycle inputs, rather than only on the ideal target state. The 10-data/12-edge test exhausts **4,194,304 basis inputs** with no mismatch. A separate small-graph Kraus calculation verifies the accepted operation, and a seven-data path checks all measurement branches on encoded zero and T states. The witnesses are in [GAUGE_NATIVE_IDENTITY](../GAUGE_NATIVE_IDENTITY_20261028/REPORT.md) and [GAUGE_RECOVERY_AUDIT](../GAUGE_RECOVERY_AUDIT_20261028/REPORT.md). Exact CX-map equality establishes full Clifford-unitary equality; it does not make the two noisy realizations equivalent.

The schedule search enumerated all 108 spanning trees and ten roots, then completed the 39 shallow rooted cases. It found a **15-clock** root14 realization and a matching lower bound within the fixed first-pass, T/MX barrier and fused recovery/flag grammar. This is a useful local optimum, not a bound over all gauging circuits. See [GAUGE_SCHEDULE](../GAUGE_SCHEDULE_20261028/REPORT.md).

The resulting full native seed + gadget + final stabilizer check has 150 CX over 46 clocks, raw-correct live output, no harmful accepted singles and loss **5.70697e-4**. The 10,000-shot official check passed, but the one-million-shot timing guard was not completed within the desired promotion runtime. Its correctness and reduced gate count are genuine; its fidelity is not competitive. The old root11 circuit is separately preserved at 54 clocks and loss 7.56807e-4, so a reused filename cannot be mistaken for its historical receipt.

To avoid spending time routing an already weak source, [GAUGE_HEADROOM](../GAUGE_HEADROOM_20261028/REPORT.md) gives the actual noisy gauging source a hypothetical perfect square resource while retaining the actual noisy terminal. With no precheck it costs **1.0697341e-4**; adding the physical 42-CX precheck reduces it to **4.4324142e-5**, acceptance **0.5393211**. Both are still worse than the native incumbent before physical resource preparation. These interventions are not monotone lower bounds on arbitrary redesigns. The [noise-aware recovery-tree comparison](../GAUGE_TREE_NOISE_20261028/REPORT.md) then priced all eighteen existing 15/16-clock shallow schedules under this matched scope. The root14 control remained best; the best different tree cost **4.6447351e-5**, acceptance **0.5350130**. All eighteen passed raw and harmful-single checks. The twenty-one slower existing schedules, different circuits and different resources remain outside this bounded comparison.

## Correcting a measurement-instrument error

The 33-CX measured-helper B/C network initially looked attractive: it prepared the intended correlated resource with only three RX seeds and one measured helper. Its first complete integration had correct noiseless T output, all six Steane stabilizers +1, and zero harmful accepted single faults. Nevertheless, it omitted the seven final B→C uncopy gates, so the instrument no longer detected the same phase errors as the incumbent.

The weakened 335-CX pilot cost **9.45018e-4**, acceptance **0.5514452**. Adding several real parity checks improved that particular pilot but did not restore its missing contract. Once the seven uncopy gates were restored, the full 342-CX circuit cost **0.0023771450**, acceptance **0.5037079**, and exposed 23 harmful accepted single-fault components. The source's affine c366 contribution also had to be handled physically; replacing its original measurement by a reset changes the source noise and is included in these results.

The new [instrument_probe.py](instrument_probe.py) tests specified faults at a fixed input boundary with all other noise absent. Immediately before original clock41:

| Circuit | Accepted single Z errors | Accepted weight-two Z pairs | Harmful accepted Z pairs |
|---|---:|---:|---:|
| Incumbent | 0 / 7 | 0 / 21 | 0 |
| Weakened measured-helper pilot | 7 / 7 | 21 / 21 | 21 |
| Restored uncopy circuit | 0 / 7 | 0 / 21 | 0 |

The incumbent and restored circuit also reject all tested single X/Y errors and same-axis X/Y pairs at this cut. A positive control after the complete circuit accepts the single errors, which the ideal decoder corrects, and the harmful Z pairs, as expected. The full response tables are [instrument_probe.json](instrument_probe.json) and [instrument_probe_controls.json](instrument_probe_controls.json).

This is a targeted diagnostic, not a complete equality test for every input or multi-fault path. It nevertheless catches a real error that raw-state correctness and c1=0 did not catch. The B/C report now labels every pair audit and perfect-noise ablation from the weakened pilot accordingly. None is being used to claim an intrinsic lower bound on the compact resource network.

### A second source-to-resource contract mismatch in the native cat circuit

Applying the same test to the native CAT7 ending found a different weakness. It accepted an X error on D=q2 and three harmful X-error pairs at the boundary after the final T-dagger. The B→C uncopy gates were present. The problem was an assumed input state: the borrowed A circuit did not initialize q15, because the original source supplied q15 in |0>. The new cat source instead ended with an X measurement on q15, leaving a record-dependent |+> or |−> state.

A physical **R15 at clock32** restores that input, but the existing detector list alone does not exploit the repair. Recomputing the complete deterministic contract makes the additional parity **c22 XOR c23 XOR c25 = 0** available. The reset and added detector together restore rejection of all 21 single-qubit and 63 same-axis weight-two errors tested at the source boundary. The repaired circuit remains raw-valid and has c1=0, with exact loss **9.312204487476157e-5**, acceptance **0.5651748131**, 190 CX and 41 clocks. The previous **2.6573379952e-4** number is the historical weakened instrument, not the best correctly initialized CAT7 result.

The corrected unflagged, one-round-flag and alternative-delay controls cost approximately **1.002e-4–1.142e-4**, so the corrected interleaved flags remain best in that finite comparison. A second reused input, q26, also differed: the old source supplied |+>, while the new source supplied |0> before the B factory's first MX. An explicit RX26 repair left loss unchanged in the two priced controls and lowered acceptance. That difference is documented rather than incorrectly called a second score improvement. The B/C X-generator signs are explicitly accounted for by earlier MX records.

The [CAT instrument audit](../CAT_INSTRUMENT_AUDIT_20261028/REPORT.md) contains the state/record proofs, corrected circuits and actual-clock pair attribution; [module_input_audit.json](module_input_audit.json) independently checks all non-reset first touches of the borrowed modules. This correction materially changes the diagnosis of the native cat experiment while leaving the incumbent and SOTA status unchanged.

The final constructive control uses the source-to-cat transition itself as verification. After the source's coherent transfer, its seven A cells are ideally zero. Six first-cat resets were replaced by physical Z reads with zero detectors, while the root's RX was replaced by an actual noisy H on that known-zero state. These operations retain correlated source-error information that a reset discards. The combined circuit costs **8.977878556875212e-5**, acceptance **0.5618977639**, still 190 CX and 41 clocks, with raw and harmful-single checks passed. Both component changes were also priced. This is a **3.59% improvement within the repaired CAT7 family**, but remains 2.52 times the incumbent's loss. The root H has its real gate noise and is not treated as a folded free preparation. See [CAT_TRANSFER_HERALD](../CAT_TRANSFER_HERALD_20261028/REPORT.md).

## Bell teleportation: timing matters, physical preparation still loses

A preformed encoded Bell pair with both receiver waiting clocks noisy gives **4.7545911e-5** on the real native source, even when the Bell preparation itself is perfect. That diagnostic alone does not rule out teleportation: its waiting can change if Bell preparation is interleaved with the input measurement.

Prepare A in encoded zero and B in encoded plus. The Bell coupling B→A commutes with D→A, so it can occur later. A three-clock ending is D→A, then B→A with MX(D), then MZ(A). The output is B, with legal logical-X and logical-Z frames from the two logical measurement parities. The six syndrome rows detect all **21 single-qubit and 189 weight-two Pauli errors** injected on D immediately before this terminal in the ideal-resource test.

With the actual noisy native source, perfect A/B preparation and explicitly suppressed first B idle to model hypothetical just-in-time preparation, this ending gives **2.9810309e-5**, acceptance **0.6112310**. Both terminal CX layers have explicit nearest-neighbor layouts. One layout maximizes fixed-output adjacency at five edges within the enumerated static matching model. None of this supplies a physical resource factory or a free idle removal. Reusing the old A footprint with only one two-CX transfer fails a complete common-neighbor matching enumeration, even allowing arbitrary coordinate relabelings; more movement or a new footprint remains open.

The physical abstract-connectivity resource test used the complete seven-cat source, independent encoded A/B preparations and actual encoded verifiers. Its best complete result is **6.0643545e-5**, acceptance **0.6699696**, 147 CX and 25 clocks. A lower-CX SpiderCSS B-plus preparation was also constructed and raw/single-fault verified, but lost at **1.4762443e-4**. Giving this same source perfect just-in-time resources yields **3.0107572e-5** before any real preparation. Thus neither the native geometry nor the favorable ideal control resolves the actual preparation error. See [KNILL_HEADROOM](../KNILL_HEADROOM_20261028/REPORT.md) and [KNILL_RESOURCE](../KNILL_RESOURCE_20261028/REPORT.md).

## Other structural tests and what they establish

The source-isometry scan uses a purified stabilizer support that includes earlier measurement records and conservatively dephases every T boundary. It proves 43 source CX gates are identities on that support. Their complete removal preserves the ideal output, but changes physical noise propagation and detection. Recovering acceptance by six benign record sectors gives a **369-CX**, 49-clock native circuit with loss **3.6503005e-5**. This is a useful gate-count tradeoff, not an improvement in the ranked objective. A full early retime made both acceptance and loss worse.

The earlier coherent source tag was real quantum information, not a free classical bit. The joint A-isometry construction preserves that correlation and eliminates the old erase/recopy pair, but the native six-clock isometry and acceptance repair finish at **5.4650094e-5**. The fixed five-clock search was exhausted only within its defined local isometry support. It does not rule out a new source encoder.

Gao-style code conversion was reduced from sixteen correction CX to seven plus a legal logical frame, or to ten coherent CX using a postselected parity quotient. The best ten-CX full abstract control improves its own parent to **4.3828212e-5**, acceptance **0.7305515**, 154 CX and 22 clocks. It still loses to the native incumbent before routing; [GAO_QUOTIENT](../GAO_QUOTIENT_20261028/REPORT.md) gives the constructive algebra and controls.

Deleting the final verification entirely does not solve the source-quality problem. The unchanged 251-CX native source alone costs **7.3676202e-4**. The complete abstract seven-cat source alone costs **8.9336502e-4**, with fourteen harmful accepted single-fault components. The three source-only Gao variants cost **0.00295–0.00451** and also admit harmful singles. These are complete controls, not a theorem that every direct-output architecture must fail; see [DIRECT_NATIVE](../DIRECT_NATIVE_20261028/REPORT.md), [DIRECT_CAT](../DIRECT_CAT_20261028/REPORT.md) and [GAO_DIRECT](../GAO_DIRECT_20261028/REPORT.md).

## Direct inner-code preparation: complete C4 and C2 tests

The [C4 architecture audit](../ARCHITECTURE_CONTINUE_20261028/REPORT.md) identifies a genuinely different ending: seven four-qubit tiles with local two-clock contraction into the live Steane output. The ideal-input tail costs approximately **2.192096e-5**, close to the repository's terminal floor, but previous late-growth controls lost badly. An ideal tail is not a complete source.

The follow-up actually constructs the state in the 28-qubit concatenated code from injection. Inner logical X is X_D X_K and logical Z is Z_H Z_D. Logical T uses a two-CX parity gadget around a physical T; two outer cat checks share the transversal T/T-dagger sandwich, keeping fifteen T/TDG gates overall. Outer logical CXs act transversally on the four physical wires, and only eight helper wires remain for cat and stabilizer-meter preparation. The ideal identities were independently checked in [c4_identity_audit.json](c4_identity_audit.json).

The complete unflagged C4 source is raw-valid but costs **0.0065308449** at acceptance **0.3935079594**, 202 CX and 43 clocks. Physical cat flags reduce its harmful-single coefficient from 4.8833 to 0.1167, but the resulting 210-CX/57-clock circuit still costs **0.0061683014**, acceptance **0.2625359812**. The seven remaining harmful components lie in the unverified outer X-meter encoder. A tested serial flagged-meter control also loses. Every tested complete version fails acceptance before routing; [C4_DIRECT](../C4_DIRECT_20261028/REPORT.md) records all controls. This directly tests preparation from creation, rather than merely growing tiles around an already finished seven-qubit source.

The grid also imposes a real extra constraint. A stationary third cat cannot touch both adjacent cells of a tile's two-qubit logical-X representative. A three-CX bridge implements that ideal interaction, but has additional fault locations. Across all 242 seven-tile packings, 28 admit seven distinct cats touching the tiles, and none admits a connected such seven-cat set under the fixed-tile, no-movement model. This does not rule out a moving cat or extra bus. The exact scope and witnesses are in [ARCHITECTURE_AUDIT.md](ARCHITECTURE_AUDIT.md) and [c4_geometry_audit.json](c4_geometry_audit.json).

The smaller asymmetric C2 alternative leaves fourteen resident data qubits and more helpers. Both ideal-input orientations give **2.2755684192e-5**, acceptance **0.9893233**, with the final native CXs, inner reads and output idle noisy. The complete phase-C2 source was then built from initial encoding with real encoded prechecks, two flagged cats and fifteen T/TDG gates. Its first control costs **0.0010331414**, acceptance **0.6629493**. A real three-CX B-zero flag removes all seven harmful singles, but costs **0.0011176729**, acceptance **0.6387820**, 132 CX and 30 clocks on 35 wires. Adding actual known-state X reads inside the logical-T gadgets, with no extra CX or clocks, improves it only to **0.0011127548**, acceptance **0.6335223**. These sources use abstract connectivity and are not native candidates. The ideal terminal is promising, but the tested direct source does not realize it; see [C2_DIRECT](../C2_DIRECT_20261028/REPORT.md).

## Reproducibility and scope

Every completed lane has its own generator, report and exact receipts. `make_checkpoint.py` selects the continuation files and required older helpers; `audit_selection.py` checks hashes, QASM/spec companions, available receipt hashes and locally resolvable report references. The [dependency audit](DEPENDENCY_AUDIT.md) tested the continuation's actual import and raw-validation paths against the exact published `boundary_product.py` in an isolated mirror. The observed results match, so the older published file is preserved; this is not a claim that its local-only additional function is generally equivalent.

The historical 526-file inventory remains unchanged as a record. This continuation explicitly updates `docs/PLAN.md` and `docs/SOTA.md`; the other 524 previously selected files remain unchanged. Vendor downloads, compiler environments, caches, locks and bulk unselected sweep copies are excluded. Full candidate receipts distinguish native circuits, abstract circuits, ideal-resource interventions and source-only controls. There is no inferred score for an unfinished circuit, no numerical SOTA claim from a lucky sample, and no global impossibility claim from a bounded search.
