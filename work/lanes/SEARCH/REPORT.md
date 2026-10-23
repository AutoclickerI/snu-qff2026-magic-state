# SEARCH — public circuits and constructions

Research and grid-free screening completed 2026-10-24. Owner-provided comparison: ours ≈1.10e-4, leader ≈6.29e-5; the board was not refreshed. **No downloaded construction has been demonstrated here to beat the leader under the contest judge.** The strongest actionable code find is the exact MQT fault-set-guided synthesis branch. The strongest complete architectural alternative is the older, two-block Daguerre–Kim code switch.

All work is in this lane. No credentials were read, no submission was made, and GitHub access was read-only. No subagents or remote jobs were used. Compute workers used one thread, with at most two concurrent worker jobs. Suspect contest repositories were excluded before source retrieval.

## Main findings

- **The headline 210p³ result uses the wrong objective for this contest.** [Gao–Yuan–Yao, arXiv:2609.12698](https://arxiv.org/abs/2609.12698), pp. 10–12, assumes no idle faults and ideal destructive output error detection. Its correction comparison is **183.81p²**, or **1.8381e-4 at p=.001 to leading order**, before idle/routing costs. The 19-qubit/82-CX footprint is real; the quoted 2.19e-7 is not a judge-score prediction.
- **The older code switch is a better lead.** [Daguerre–Kim, arXiv:2410.07327](https://arxiv.org/abs/2410.07327), Eq. 23, gives a corrected-output fit beginning **25.5p²** (full fit ≈2.4395e-5 at .001), with ≈84% acceptance. The direct MC estimate is 4.6(1.6)e-5. This omits idles, but leaves more headroom. Table VII counts **100 CX**; reused peak width is 26.
- **Small extraction circuits are not necessarily fast.** Six Poór/PECOS static round variants pass the single-fault diagnostics, but score **3.01e-4–9.01e-4** under STANDARD even with ideal encoded input and no routing. Long data exposure overwhelms their gate-count saving. This rejects the tested schedules, not every possible rewrite.
- **The matching synthesis code was found.** [Zenodo 23183007](https://zenodo.org/records/23183007) identifies MQT branch *ft-stateprep-qubit-perm*, pinned here at **d67b7f8d65fe8f7c0f099c4cde41010ebd92d837**. The branch, circuit archive and mqt.qecc 2.0.0 wheel are saved. Nothing was installed into .venv. The release wheel alone is not the paper's matching snapshot.
- **Other strong-looking numbers change the noise or output boundary.** IBM's square-grid gauging protocol postselects the final ideal syndrome. Its generated d3 prefix has 25 qubits, 245 quantum CX and 18 feedback-X instructions; the paper itself favors ordinary cultivation at d3. Chamberland–Cross uses idle error p/100; the judge uses p.

## Ranked artifact table

Sizes are un-routed unless stated. Reported values are source claims, not reproduced judge scores. A basis-state preparation error is **not** a T-preparation error. NR means no reliable number was established from the inspected material. Every artifact is saved under found/ with provenance; full hashes and licences appear below.

| Priority | Artifact / source | Licence | What; size | Reported numbers and noise | Our STANDARD screen / relevance |
|---|---|---|---|---|---|
| 1 | [MQT synthesis paper](https://arxiv.org/abs/2601.13313), [archive](https://zenodo.org/records/23183007), [branch](https://github.com/munich-quantum-toolkit/qecc/tree/ft-stateprep-qubit-perm) | MIT code; CC BY 4.0 archive data; arXiv paper distribution licence | Compatible C1–C4 CSS ancilla encoders. Four Steane blocks would use 28 qubits before external data; published examples start at 4×17. Table's 92 CX for [[17,1,5]] is the sum of four encoders, excluding transversal verification couplings. | Paper: [[17,1,5]] ≈8e-8, A≈.81. Exact final data in archive. Gate depolarization p, preparation/measurement flip 2p/3, idle p/100. | No integrated factory scored. Targets the local B+C correlated-fault cancellation and long preparation wait. |
| 2 | [SpiderWarp / auto-zx-opt](https://github.com/boldar99/auto-zx-opt); [Jeon et al.](https://arxiv.org/abs/2610.09749) | SpiderWarp has no declared licence; Jeon paper CC BY 4.0 | Executable ZX/path-cover optimizer; paper Bell-reduction rules. Shor round 54→42 CX, 30→18 ancilla preparations. Steane half-gadget 14 CX, 4 ancillas, CX depth 7. | Jeon: ≈21% Shor improvement at p=.001; ≈15% Steane improvement with idle 3p/10. Adaptive basis-state QEC, not this judge. | Literal CX lowering of SpiderWarp's 10q/18-entangler preparation: 8.147(131)e-4 basis error, A=.94393. Use optimizer on our verified round, not that example. Linked Jeon code ijshj10/ftzx returned 404. |
| 3 | [Daguerre–Kim](https://arxiv.org/abs/2410.07327); [Heußen–Hilder circuits](https://zenodo.org/records/15674835) | Paper distribution licence; deposit CC BY 4.0 | RM15 transversal-T followed by transfer to Steane: 26q/100 CX. Separate Heußen primitives: Steane 8q/11 CX, tetrahedral 20q/58 CX, transfer 7 CX. These are related, not identical constructions. | Daguerre corrected fit ≈2.4395e-5, direct MC 4.6(1.6)e-5, A≈.84 at .001. Uniform active-operation noise, no idles. | Heußen's plus-state primitive: 1.492(55)e-4, A=.98661. Full non-Clifford switch unscored. Most promising complete alternative found. |
| 4 | [Flag-at-origin code](https://github.com/Quantinuum/flag_at_origin_paper); [ILP flag synthesis](https://arxiv.org/abs/2607.22498) | MIT code; ILP paper distribution licence | Flag placement at dangerous propagation sites. ILP Steane example: 8-CX encoder + weight-3 check = 11 CX and one measurement, 8q. Paper's 12 operations are not 12 CX. | ILP H2 experiment is [[24,10,4]], with one logical block failure in 7117 accepted shots from 10,000 attempts. The quoted 1.6% is one rejection category, not total acceptance. | No new grid synthesis run. Potentially replace a whole verifier block with local flags; include faults on the added flag circuit. |
| 5 | [PECOS H/T code](https://github.com/PECOS-packages/PECOS/tree/408e9a787940944c14af86ff18707887da837aa2/python/quantum-pecos/src/pecos/slr/qeclib/steane/preps), [Chamberland–Cross](https://arxiv.org/abs/1811.00566), [Postler deposit](https://zenodo.org/records/6244536) | Apache-2.0 code; CC BY 4.0 paper/deposit | H-eigenstate encoding, flagged logical-H measurement, mixed XZZ/ZXX extraction, Clifford conversion to T. Extractor 28 entanglers, 10q reused / 13q separate. Logical-H check: 7 controlled-H + 2 CX. | Chamberland Table 4: (px,py,pz)≈(9.95,4.41,7.87)p²; A≈(1−p)^75; idle p/100. Postler experiment ≈.006 magic infidelity, A=.137(3), hardware-specific noise; 7 data + 8 ancillas. | Mixed extraction alone: 3.411(61)e-4 reused, 3.010(58)e-4 separate. Full H/T protocol unscored. Source extraction requires three ancillas despite one prep docstring saying two. |
| 6 | [Gao–Yuan–Yao single-register switch](https://arxiv.org/abs/2609.12698) | arXiv distribution licence; no public code located | 19q, 82 CX, 15 T/T†; retain seven face qubits after eight bulk-X measurements. Explicit grouped-check orders and gauge frames in appendices. | Destructive ED ≤2.19e-7, A=.86896 at .001; no idles. Correction leading term 183.81p². | Not a competitive ready-made judge circuit. Mine generator grouping; do not import the headline fidelity. |
| 7 | [Poór et al.](https://arxiv.org/abs/2511.13700), [code](https://github.com/boldar99/Steane-Ultra-Low-Overhead) | No declared code licence; paper distribution licence | FT half-round 14 CX/4 ancillas; unflagged recovery 11 CX. Full X/Z round is 28 CX. | Adaptive QEC ≈14.3% improvement over optimized Steane, ≈17.3% over Reichardt. Source p2=.001, p1=.00003, SPAM=.001, Z-only idle=.0001. | Best tested static separate-ancilla round 3.235(59)e-4, A≈.9203; reused 6.071(83)e-4. Worse before routing. |
| 8 | [Gidney–Shutty–Jones code/data](https://zenodo.org/records/13777072), [paper](https://arxiv.org/abs/2409.17595) | Apache-2.0 code; CC BY 4.0 deposit/paper | Saved full source and circuits. d3 perfectionist files: unitary 15q/81 CX; Bell 14q/75 CX; teleport 18q/104 CX. Includes characterization boundaries and Clifford stand-ins. | Published d3 scale ≈6e-7 under full postselection; not a retained-output corrected score. | Already the origin of our preparation. Bell/teleport starts are usable alternatives, but injection-only improvement cannot remove the final-round loss. |
| 9 | [IBM gauging code](https://github.com/IBM/gauging_clifford_measurement), [paper](https://arxiv.org/abs/2603.05429) | Apache-2.0 code | Generated d3 live-prefix surrogate: 25q, 245 quantum CX, 18 feedback-X, 79 records including one padding bit. Output data [0,2,3,4,5,6,9]. | Uniform circuit noise, with final ideal-syndrome rejection included in success. Larger-distance advantage; d3 ordinary cultivation has lower error and volume. | Counts reproduced; no T score. S→T substitution and feedback need explicit validation and lowering. |
| 10 | [Chamberland–Noh](https://arxiv.org/abs/2003.03049) | Paper distribution licence | Redundant-cat logical-H checks on local color-code layouts. d3 minimum 16q; full CX count NR. d5 minimum 55q. | d3: 3.45e-6 at p=1e-4; 8.51e-5 at p=5e-4. d5: 3.6e-8 at 1e-4, A=.81, full circuit model. | d5 exceeds area. d3 does not establish a win at p=.001. No public author code located. |
| 11 | [Zero-level distillation](https://arxiv.org/abs/2403.03991) | Paper distribution licence | Local Steane H test with seven-qubit cat and surface conversion; published simulation 23q. Retained-Steane-prefix CX count NR. | ≈100p², ≈1e-4 at .001; literature comparison gives A≈.7. Output and boundary differ. | Local verification construction source, not an established improvement. |
| 12 | [Surti–Daguerre–Kim simulation](https://arxiv.org/abs/2512.23799) | Paper distribution licence | Clifford-frame simulation through T layers; not one fixed-size preparation. | Method rather than a transferable error/acceptance pair. Code/data available on request. | Useful validation method; no public author implementation located. Existing exact2 already covers much of this need. |
| 13 | [Daguerre et al. experiment](https://arxiv.org/abs/2506.14169) | arXiv distribution licence; journal CC BY 4.0 | RM15→Steane single-/two-copy certification; experimental CX total NR. | Corrected magic infidelity ≤5.1(2.7)e-4, A=.8258; Quantinuum hardware. | Supports architectural feasibility, not a uniform-.001 judge advantage. Code/data on request. |
| 14 | [Postler Steane EC](https://zenodo.org/records/10390470); [Heußen noise study](https://zenodo.org/records/7565571) | CC BY 4.0 | PDF ancilla/preparation/extraction circuits and CSVs; Steane EC uses two 7q blocks plus verification. Noise-study deposit contains data, not circuit source. CX total NR. | Hardware-calibrated ion noise including coherent/crosstalk effects; no uniform judge figure quoted. | Useful circuit evidence and noise caveats; no new small final round identified. |
| 15 | [FTEC QASM corpus](https://github.com/Palatinate-1225/FTEC_flag_protocol_general_verifier) | No licence declared | Published-protocol QASM fixtures, including Steane flagged checks; aggregate width/CX depends on selected protocol and branch. | No comparable logical-error/acceptance result. | Gate-order corpus, not author code for the cited constructions. |
| 16 | [numft](https://github.com/ust-qec/numft) | MIT | CSS algebra, encoders and simulation utilities; no fixed-size T factory. | No relevant end-to-end score found. | Citation-search hit, not an identified implementation of the ILP paper. |
| 17 | [Figshare magic-state dataset](https://figshare.com/articles/dataset/Encoding_a_magic_state_with_beyond_break-even_fidelity_datasets_/23535237) | CC BY 4.0 | Metadata/file inventory saved; 34–532 MB experiment/analysis archives. No identified Steane circuit or count. | Different experimental encoding task; no comparable retained-Steane score. | Metadata only; no actionable circuit identified, so large data archives not downloaded. |
| 18 | [Measurement-free experiment](https://zenodo.org/records/15747203); [Google cultivation data](https://zenodo.org/records/17872003) | CC BY 4.0 | First: code/data for [[4,1,2]] and [[8,3,2]], not Steane. Second: README/example notebook saved; figure archives 0.73–1.55 GB each. No relevant CX count established. | Different codes or hardware protocols. | Not evidence of a drop-in 6×6 solution. Saved to prevent repeating discovery. |

## Top five adoption plans

These rank research investments, not validated candidates. Gains below are mechanisms and screening targets, not invented percentages.

1. **Synthesize compatible verification blocks with the matching MQT branch.** Start from the local A/B/C layouts. Entry points in the saved branch are state_prep.heuristic_reference_prep_circuit, synthesis_utils.fault_set_guided_synthesis, faults.t_distinct, and simulation.SteaneNDFTStatePrepSimulator. Generate dangerous X/Z fault sets including STANDARD initialization and idle faults, and synthesize encoders whose shared faults cannot cancel the verification record. Optimize time to data coupling, not individual encoder CX counts. This targets the documented joint B+C failure and long waits. An 8-CX all-to-all encoder alone cannot evade the locally proved 11-CX grid minimum. Save the abstract circuit and detector map, then score with exact2, third order and full STANDARD. A rough screening budget is final-round loss below ≈4.8e-5 if the present pre-stage contribution stays; the attribution is not an additive theorem.

2. **Reduce the whole verified Steane round using ZX/Bell/path-cover rewrites.** Apply SpiderWarp's path_cover.py and qubit_reuse.py, or independently implement the CC-BY paper's rules, to the existing 28-qubit abstract construction. Preserve data interfaces and the complete detector map. The intended gain is fewer occupied cells and less serialized preparation, resolving the placement bottleneck. Reject transformations that lengthen data exposure or assume a different decoder. The measured 10q preparation and sequential 14-CX gadget are not adoption candidates. No code licence is declared for SpiderWarp; paper rules remain a separately attributable construction source.

3. **Reconstruct the older two-block RM15→Steane protocol.** Use Daguerre–Kim Figs. 4–7/Table VII and the original ten-check basis. Preserve the verified destination and seven-CX transfer, giving a fresh output boundary. Heußen's saved primitives are independently reusable, but mixing them into Daguerre's protocol requires new verification. Reproduce the noiseless channel and active-noise corrected regime first, then enable STANDARD idles and native readout without terminal-syndrome rejection. Route only after the unrouted live-output result beats the leader with margin. Published corrected performance gives headroom; routing and latency remain unknown.

4. **Replace a verifier block with flags at the dangerous propagation sites.** Use Quantinuum's MIT flag-at-origin generator and the ILP circuit-gauge formulation. Target B's X hooks and A's dangerous Z cosets. Include every new flag-gate fault in synthesis, and enforce a bipartite interaction graph to avoid the prior direct-cat grid obstruction. Rank by malignant pairs and completion time. The ILP Steane example merely recovers the known 11-CX preparation; larger-code reductions are not a prediction for this task.

5. **Mine direct H-state verification for a smaller complete preparation.** Start with PECOS PrepHStateFT/Check1Flag and Postler diagrams. Lower controlled-H to the legal gate set; unroll one attempt, express rejection via postselection, and verify the H→T Clifford orientation in this repository's code convention. Preserve all syndrome parities. The adaptive/RUS source is not a valid contest circuit. Its tested XZZ/ZXX final round is already too costly under STANDARD, so this route needs a different final readout or substantially better interleaving.

## Our-noise measurements

[eval_clifford.py](eval_clifford.py) uses tprep.noise.STANDARD at p=.001, its ASAP scheduler and native-X folding. Dependent operations packed on one Stim line are split before noise insertion; otherwise noise would incorrectly be delayed until the end of a CNOT chain. Earlier exploratory logs before this normalization/native folding are superseded by the JSON files and table below.

Extraction begins with an ideal encoded input already present while ancillas initialize. A step-zero identity supplies exactly the first idle-equivalent depolarization, and the scheduler charges later waits. Ancillas use noisy R/RX. Preparation tests include noisy initialization. All intermediate syndrome/flag bits are postselected. The final six stabilizers are ideal **correction information, never rejection conditions**; the logical sign is corrected using the judge's nonzero-syndrome rule.

For these Pauli-diagonal Clifford memory channels, T infidelity is the average of decoded X- and Y-memory failure rates. Each basis uses 5,000,000 shots, seeds 20261024/20261025. Preparation tests use their relevant basis only. SEM is sampling uncertainty; it excludes routing/integration uncertainty. These are not the three official 1e8-shot seeds, and no submission was selected.



<!-- generated appendix -->
| Circuit | Qubits | CX | ASAP steps | Conditional error | SEM | Acceptance | Single-fault diagnostic |
|---|---:|---:|---:|---:|---:|---:|---|
| heussen_steane_plus | 8 | 11 | 7 | 0.000149198 | 5.5e-06 | 0.986608 | 0 malignant mechanisms |
| mqt_plus_ft_heuristic_heuristic | 8 | 11 | 8 | 0.000221498 | 6.7e-06 | 0.981499 | 0 malignant mechanisms |
| mqt_plus_ft_heuristic_opt | 8 | 11 | 8 | 0.000221498 | 6.7e-06 | 0.981499 | 0 malignant mechanisms |
| mqt_plus_ft_opt_opt | 8 | 11 | 8 | 0.000199394 | 6.4e-06 | 0.981975 | 0 malignant mechanisms |
| mqt_plus_non_ft_heuristic | 7 | 8 | 4 | 0.0069156 | 3.7e-05 | 1.000000 | 10 malignant mechanisms |
| mqt_plus_non_ft_opt | 7 | 8 | 6 | 0.0043946 | 3e-05 | 1.000000 | 10 malignant mechanisms |
| mqt_zero_ft_heuristic_heuristic | 8 | 11 | 8 | 0.000161358 | 5.7e-06 | 0.986629 | 0 malignant mechanisms |
| mqt_zero_ft_heuristic_opt | 8 | 11 | 8 | 0.000161328 | 5.7e-06 | 0.985572 | 0 malignant mechanisms |
| mqt_zero_ft_opt_opt | 8 | 11 | 8 | 0.000214497 | 6.6e-06 | 0.989291 | 0 malignant mechanisms |
| mqt_zero_non_ft_heuristic | 7 | 8 | 4 | 0.0055482 | 3.3e-05 | 1.000000 | 10 malignant mechanisms |
| mqt_zero_non_ft_opt | 7 | 8 | 5 | 0.0013866 | 1.7e-05 | 1.000000 | 11 malignant mechanisms |
| pecos_mixed28_reuse | 10 | 28 | 16 | 0.000341114 | 6.1e-06 | 0.908443 | 0 malignant mechanisms |
| pecos_mixed28_separate | 13 | 28 | 14 | 0.000300995 | 5.8e-06 | 0.908624 | 0 malignant mechanisms |
| poor14_XZ_reuse | 11 | 28 | 19 | 0.000900662 | 1e-05 | 0.889121 | 0 malignant mechanisms |
| poor14_XZ_separate | 15 | 28 | 11 | 0.000345656 | 6.1e-06 | 0.920300 | 0 malignant mechanisms |
| poor14_ZX_reuse | 11 | 28 | 19 | 0.000607072 | 8.3e-06 | 0.889199 | 0 malignant mechanisms |
| poor14_ZX_separate | 15 | 28 | 11 | 0.0003235 | 5.9e-06 | 0.920272 | 0 malignant mechanisms |
| spiderwarp_trueft_zero_cx | 10 | 18 | 17 | 0.000814677 | 1.3e-05 | 0.943932 | 0 malignant mechanisms |

The final audit verified SHA-256 for 689 saved source files with zero missing files or mismatches (AUDIT.json). Re-running poor14_ZX_separate and mqt_plus_ft_opt_opt from their saved circuits reproduced accepted/error counts exactly (evaluations/reproduction.log). All scored CSS matrices have seven distinct nonzero syndrome columns and commute.

All 18 scored circuits passed noiseless syndrome/output checks. Stim DEM inspection found no accepted decoded-failure single mechanism for the flagged preparations and extraction rounds. The four unverified MQT encoders expose first-order mechanisms, as expected. DEM decomposition is used only as a first-order diagnostic; finite-p numbers come from direct sampling.

Saved Stim circuits and JSON counts make the screens reproducible with rerun_saved.py. There are 24 sampled bases, 120 million shots in the final set. The archived earlier logs contain superseded adapter results; the table and evaluations/*.json are authoritative. The adapter was corrected to split dependent Stim gates and fold native readout, then all affected measurements were rerun.

**Verified:** primary-source retrieval, pinned source versions, static counts where stated, noiseless Clifford behavior, terminal single-error decoding, and these grid-free Monte Carlo screens. **Unverified:** grid placement, full non-Clifford T preparation, cross terms with our input stage, three-seed official score, and any resulting submission's format/class/correctness.

Basis-state infidelity does not price every correlated error an ancilla can introduce later. Score any adopted block in its actual data-coupling role before ranking it. No perfect terminal syndrome rejection was added to improve these numbers.

## Provenance and coverage

Each found/<slug>/provenance.json records source URLs, commit hashes where available, licences and checksums. arXiv/Zenodo deposits use versions, DOIs and checksums instead of invented git hashes. A paper's licence does not license its accompanying code. Source copies are unmodified; translations/generated circuits and measurements are separate files.

The unavailable Jeon endpoint is documented in found/ijshj10--ftzx/. Gao and Surti explicitly offer data/code on reasonable request; no request was sent. Searches did not identify an author implementation for the ILP paper. Unrelated code citing a paper was not represented as author code.

The final MQT archive explains that its higher-distance comparison circuits remove destructive data readout and selected flag-basis H gates. Its total-CX column sums four constituent encoders; count the three transversal block comparisons separately when assembling a factory. The branch commit here matches the archive's stated simulation dependency.

| Saved artifact | Commit / immutable identifier | Licence |
|---|---|---|
| [IBM--gauging_clifford_measurement](found/IBM--gauging_clifford_measurement/provenance.json) | ce90c09c239b2173612c22cc12a2bbf5a7356680 | Apache-2.0 |
| [PECOS-packages--PECOS](found/PECOS-packages--PECOS/provenance.json) | 408e9a787940944c14af86ff18707887da837aa2 | Apache-2.0 |
| [Palatinate-1225--FTEC_flag_protocol_general_verifier](found/Palatinate-1225--FTEC_flag_protocol_general_verifier/provenance.json) | e65350dd97344dca24f3b511cbe1d2b80967ab9d | not specified |
| [Quantinuum--flag_at_origin_paper](found/Quantinuum--flag_at_origin_paper/provenance.json) | ff5e5eaebc4e5304f7e4332d16606029bfb1db75 | MIT |
| [arxiv-1811.00566](found/arxiv-1811.00566/provenance.json) | version/checksums in provenance | http://creativecommons.org/licenses/by/4.0/ |
| [arxiv-2003.03049](found/arxiv-2003.03049/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2111.12654](found/arxiv-2111.12654/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2301.10017](found/arxiv-2301.10017/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2312.09745](found/arxiv-2312.09745/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2403.03991](found/arxiv-2403.03991/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2409.13465](found/arxiv-2409.13465/provenance.json) | version/checksums in provenance | http://creativecommons.org/licenses/by/4.0/ |
| [arxiv-2409.17595](found/arxiv-2409.17595/provenance.json) | version/checksums in provenance | http://creativecommons.org/licenses/by/4.0/ |
| [arxiv-2410.07327](found/arxiv-2410.07327/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2506.14169](found/arxiv-2506.14169/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2511.13700](found/arxiv-2511.13700/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2512.23799](found/arxiv-2512.23799/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2601.13313](found/arxiv-2601.13313/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2603.05429](found/arxiv-2603.05429/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2607.22498](found/arxiv-2607.22498/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2609.12698](found/arxiv-2609.12698/provenance.json) | version/checksums in provenance | http://arxiv.org/licenses/nonexclusive-distrib/1.0/ |
| [arxiv-2610.09749](found/arxiv-2610.09749/provenance.json) | version/checksums in provenance | http://creativecommons.org/licenses/by/4.0/ |
| [boldar99--Steane-Ultra-Low-Overhead](found/boldar99--Steane-Ultra-Low-Overhead/provenance.json) | 77a0f36f10d881c599e0cc11381fcdd7b07aad46 | not specified |
| [boldar99--auto-zx-opt](found/boldar99--auto-zx-opt/provenance.json) | 21b7ed0213b67aa7c84cf6c35c176ae50130cac0 | not specified |
| [figshare-23535237](found/figshare-23535237/provenance.json) | 10.6084/m9.figshare.23535237.v2 | CC BY 4.0 |
| [figshare-27550992](found/figshare-27550992/provenance.json) | 1 | All rights reserved |
| [ijshj10--ftzx](found/ijshj10--ftzx/provenance.json) | version/checksums in provenance | unknown; repository unavailable |
| [mqt-wheel](found/mqt-wheel/provenance.json) | 2.0.0 | MIT |
| [munich-quantum-toolkit--qecc](found/munich-quantum-toolkit--qecc/provenance.json) | 456c642afb91995819f3484fa77fdc23e569d2f4 | MIT |
| [munich-quantum-toolkit--qecc--ft-stateprep-qubit-perm](found/munich-quantum-toolkit--qecc--ft-stateprep-qubit-perm/provenance.json) | d67b7f8d65fe8f7c0f099c4cde41010ebd92d837 | MIT |
| [ust-qec--numft](found/ust-qec--numft/provenance.json) | 5d157fb2a3f15c7b5316afab19e77312adc119db | MIT |
| [zenodo-10390470](found/zenodo-10390470/provenance.json) | 10.5281/zenodo.10390470 | cc-by-4.0 |
| [zenodo-13777072](found/zenodo-13777072/provenance.json) | 10.5281/zenodo.13777072 | cc-by-4.0 |
| [zenodo-15674835](found/zenodo-15674835/provenance.json) | 10.5281/zenodo.15674835 | cc-by-4.0 |
| [zenodo-15747203](found/zenodo-15747203/provenance.json) | 10.5281/zenodo.17375920 | cc-by-4.0 |
| [zenodo-17872003](found/zenodo-17872003/provenance.json) | 10.5281/zenodo.17872003 | cc-by-4.0 |
| [zenodo-23183007](found/zenodo-23183007/provenance.json) | 10.5281/zenodo.23183007 | cc-by-4.0 |
| [zenodo-6244536](found/zenodo-6244536/provenance.json) | 10.5281/zenodo.6244536 | cc-by-4.0 |
| [zenodo-7565571](found/zenodo-7565571/provenance.json) | 10.5281/zenodo.7565571 | cc-by-4.0 |

## Queries run, with hit counts

Counts are API totals unless marked as returned-page counts. GitHub results were capped at 100 metadata hits per query, not exhaustively scanned. No code-snippet/text-match previews were requested. Broad flag/T/Noh searches returned considerable unrelated material; targeted queries and primary-paper links supplied useful artifacts. Code-search requests were separated by at least seven seconds.

| Search | Exact query | Total hits | Saved / returned metadata |
|---|---|---:|---:|
| GitHub code | language:OpenQASM Steane | 26 | 26 |
| GitHub code | language:OpenQASM "magic" | 90 | 90 |
| GitHub code | language:OpenQASM "reed" | 63 | 63 |
| GitHub code | language:OpenQASM "flag" | 1052 | 100 |
| GitHub code | "Steane" "magic" | 3248 | 100 |
| GitHub code | "Steane" "injection" | 105 | 100 |
| GitHub code | "transversal" "T" "Reed" | 76111 | 100 |
| GitHub code | "gauge" "fixing" "Steane" | 720 | 100 |
| GitHub code | "magic state cultivation" | 766 | 100 |
| GitHub code | "fault-tolerant" "state" "preparation" | 32192 | 100 |
| GitHub code | "flag" "Steane" | 3904 | 100 |
| GitHub code | "DETECTOR" "S_DAG" "OBSERVABLE_INCLUDE" extension:stim | 127 | 100 |
| GitHub code | "DETECTOR" "T" "OBSERVABLE_INCLUDE" extension:stim | 39424 | 100 |
| GitHub code | "2609.12698" | 19 | 19 |
| GitHub code | "2607.22498" | HTTP 408; retried below | 0 |
| GitHub code | "2601.13313" | 16 | 16 |
| GitHub code | "Chamberland" "Cross" "magic" | 980 | 100 |
| GitHub code | "Noh" "flag" | 9322496 | 100 |
| GitHub code | "H_state" "Steane" | 80 | 80 |
| GitHub code | "15" "7" "code switching" | 10944 | 100 |
| GitHub code | "snu-qff2026" | 11 | 11 |
| GitHub code | "tprep" "data_qubits" | 5 | 5 |
| GitHub code | "2607.22498" | 21 | 20 |
| GitHub code | "Chamberland" "Noh" language:Python | 9 | 9 |
| GitHub code | "Reed_Muller" "Steane" language:Python | 34 | 34 |
| GitHub code | "flag" "magic" language:Python | 1449984 | 100 |
| GitHub code | "magic" language:OpenQASM extension:qasm | 90 | 90 |
| GitHub code | "Steane" "preparation" language:Python | 254 | 100 |
| Zenodo | Steane | 211 | 25 |
| Zenodo | "magic state" | 82 | 25 |
| Zenodo | Postler | 48 | 25 |
| Zenodo | Heussen | 43 | 25 |
| Zenodo | "code switching" | 762 | 25 |
| Zenodo | "2607.22498" | 0 | 0 |
| Zenodo | "flag" AND "state preparation" | 2 | 2 |
| Figshare | "Steane" | not exposed | 100 |
| Figshare | "magic state" | not exposed | 8 |
| Figshare | "fault-tolerant" "Postler" | not exposed | 0 |
| Figshare | "Heussen" | not exposed | 100 |

Initial Zenodo requests with size=100 failed HTTP 400. Repeating with size=25 succeeded; failed responses remain in searches/zenodo-0.json through zenodo-3.json. The successful Steane retry also exists as zenodo-retry.json. Figshare Steane/Heussen pages mostly matched unrelated surnames. Its magic-state query returned eight records; only relevant quantum records were inspected.

Supplemental web queries are listed below. The tool did not expose exhaustive hit totals; the API searches above provide the countable results.

| Batch | Exact queries | Hit-total status |
|---|---|---|
| 1 | arxiv "2609.12698"; arxiv "2601.13313"; arxiv "2607.22498" quantum; "Steane" "magic state" github | Not exposed |
| 2 | site.zenodo.org Postler "fault-tolerant" 2022; site.zenodo.org Heussen "magic"; site.figshare.com "Steane"; "2607.22498" github | Not exposed |
| 3 | "Postler" "zenodo" magic; "Heußen" "zenodo" magic; "Chamberland" "Cross" "Noh" magic state flag github; "Steane" site:figshare.com/articles | Not exposed |
| 4 | "Heussen" "zenodo" quantum; "magic" "Steane" site:zenodo.org/records; "flag" "Steane" site:figshare.com; "Extremely Low-Cost Magic State" github | Not exposed |
| 5 | "Code switching revisited" Daguerre Kim code github; "Efficient fault-tolerant code switching via one-way transversal CNOT gates" arxiv; "Sascha" "magic" "zenodo" | Not exposed |

Sources were fetched directly from arXiv, publisher pages, pinned GitHub URLs, Zenodo and Figshare. No research conclusion depends on a secondary search-result summary or memory.

## Other contest entries (not opened)

The first URL explicitly matched the contest-name query. The others are conservative exclusions from combined tprep/data_qubits metadata hits; metadata alone does not establish that they are contest teams. None was opened. Only URLs are listed for owner review.

- https://github.com/zag-quantum/ZAG-Qiskit-FALL-FEST-2026
- https://github.com/Quantinuum/qec_qpe_chem
- https://github.com/unitaryfoundation/metriq-gym
- https://github.com/unitarylab/quantum-practices
- https://github.com/unitarylab/quantum-skills
