# IFACE

**Verdict: no finalist. Three downstream builds are priced and all lose to τ; stop rule reached for the tested interface family.**
Baseline reproduced exactly: L=3.815473322483099e-05, A=0.5016415049479505, SHA `c8e8a44e104a`. The fixed-variable model reproduces all 503 native operations, 77 lifetimes, classical records, guards, and all 56 r3 CXs; byte-identical QASM and an independent judge-schedule comparison pass.
Best modified circuit: [builds/del_echo14.qasm](builds/del_echo14.qasm), L=3.8161690599756685e-05, A=0.5012769903325704, Jτ=3.4875719633672817e-09; removes the known-state CX13→14 at 32. Judge 1e6 seed0 PASS: sampled loss 4.889272935180194e-5 ±8.64e-6, A=.501097, 12.7 s. It is above τ, so `cand/` is empty.

Decisions: use exact prepared-subspace equivalence for local completion, preserve the correlated r3 and actual records, and retain release diversity before selecting downstream builds. Selected the cheapest meaningful hop interface (`if_d`), both-hop release (`if_hde`), and earliest q4 release (`if_hdej`); selection beyond Jτ used distinct release opportunities, not a claim of global optimality.
Archive: 24 distinct occupied-cell schedules, but only eight listed source-release vectors. All have ideal correctness verified, fixed D=[0,20,7,10,3,22,21], R44, and q15 released at 40. This does **not** supply 20 different output geometries. The four-to-six-wire completion scan found only guard/pair shortcuts; none replaces the D6 8→9→15→21 spine.
The downstream builds retain the A encoder and r3 and rebuild available known-state guards/initialization times. Menus screened: 7/7, 10/13, 10/20 slots, followed by joint pricing; this is a ranked greedy search, not an exhaustive suffix synthesis.

| Downstream interface | Final L | A | Jτ | Remaining loss above τ | Protection recovered |
|---|---:|---:|---:|---:|---:|
| [if_d](builds/if_d_downstream.qasm) | 3.825307239599922e-05 | 0.508576066633 | 5.001294887e-08 | 9.833917117e-08 | 5.789371998e-08 |
| [if_hde](builds/if_hde_downstream.qasm) | 3.825492890625878e-05 | 0.507665312621 | 5.086587194e-08 | 1.001956814e-07 | 1.237939218e-07 |
| [if_hdej](builds/if_hdej_downstream.qasm) | 3.849070214498265e-05 | 0.508952792575 | 1.709923201e-07 | 3.359689202e-07 | 1.889545594e-07 |

Measured blockers by approach: deleting the q10 hop completion costs +5.9137411e-8; deleting the extra q15→16 completion costs +5.2555363e-8; commuting the blue c64 readout from 37 to 35 costs +5.5974658e-8. Their joint earlier-release builds recover protection as shown above, but retain the limiting q15 release. These are finite circuit comparisons, not additive channel decompositions.
Verified: every table price is an unchanged all-orders evaluation of a saved circuit; all QASM hashes, ordered outputs, evaluator hashes and log totals were checked. All archive members and completed downstream circuits pass the independent ideal checker. Only the best changed circuit received judge1e6; the three losing downstream builds have no noisy judge receipt.
Inferred/open: q15 is the obstruction for this retained spine, not a bound on different completions. Different final data placements, a genuinely different phase-routing completion, and re-synthesized A/r3 on new cells remain unbuilt. Therefore this report closes the tested guard/completion/retiming family, **not the wider geometry-changing brief**. No claim that all prefix-interface approaches are exhausted.
Files: [PREFIX.md](PREFIX.md) (timeline/interpretation), [model.json](model.json), [archive.json](archive.json), [results.json](results.json), `inputs/completions.json`, `inputs/native_roundtrip.json`, `builds/`, `logs/`; builders `model.py`, `completion.py`, `archive.py`, `downstream.py`, `price.py`. Work ran on zebra with thread caps and ≤3 evaluation workers; hippo was not used. No submission, commit, push, or write outside IFACE.

Every distinct priced circuit follows (aliases and full precision in `results.json`). h=remove CX15→16@33; d=remove CX10→4@34; e=remove CX13→14@32 and CX20→26@29,30; j=remove CX11→10@30–32. `if_*` also retimes the prefix; blue advances c64. Jτ=A(L−τ).

| Circuit | L | A | Jτ | SHA256 prefix | What changed |
|---|---:|---:|---:|---|---|
| [v36h](builds/v36h.qasm) | 3.815473322483e-05 | 0.501641504948 | 0.00000000e+00 | `c8e8a44e104a` | control |
| [del_hop10](builds/del_hop10.qasm) | 3.821387063586e-05 | 0.501279649289 | 2.96443807e-08 | `b37fe591ad58` | State-specific deletion of CX10->4 at 34 |
| [del_hop16](builds/del_hop16.qasm) | 3.820728858764e-05 | 0.501275348794 | 2.63447078e-08 | `5e132c7b80f6` | State-specific deletion of CX15->16 at 33 |
| [del_echo14](builds/del_echo14.qasm) | 3.816169059976e-05 | 0.501276990333 | 3.48757196e-09 | `5baff65111da` | State-specific deletion of CX13->14 at 32 |
| [retime_all](builds/retime_all.qasm) | 3.821070788281e-05 | 0.501644297380 | 2.80793680e-08 | `2b711b5c7f7c` | Earlier prefix/hop releases with exact commuting constraints |
| [if_h](builds/if_h.qasm) | 3.847771656002e-05 | 0.507935499113 | 1.64054702e-07 | `275a6f779ad9` | h |
| [if_h_blue](builds/if_h_blue.qasm) | 3.853726714882e-05 | 0.507938421992 | 1.94303678e-07 | `03a05440d1ec` | h; early blue |
| [if_d](builds/if_d.qasm) | 3.831096611598e-05 | 0.508542247910 | 7.94510257e-08 | `82e6cf996c23` | d |
| [if_d_blue](builds/if_d_blue.qasm) | 3.837008161542e-05 | 0.508545217234 | 1.09514394e-07 | `7dacb989da4c` | d; early blue |
| [if_e](builds/if_e.qasm) | 3.843681998831e-05 | 0.507733829045 | 1.43224993e-07 | `a8ff5252985f` | e |
| [if_e_blue](builds/if_e_blue.qasm) | 3.849593075787e-05 | 0.507736750583 | 1.73238527e-07 | `e0170af4b334` | e; early blue |
| [if_j](builds/if_j.qasm) | 3.898872553734e-05 | 0.508553037699 | 4.24129324e-07 | `ae05e270d84a` | j |
| [if_j_blue](builds/if_j_blue.qasm) | 3.905187901991e-05 | 0.508556513508 | 4.56249338e-07 | `75684e0028ca` | j; early blue |
| [if_hd](builds/if_hd.qasm) | 3.836487354391e-05 | 0.508171056111 | 1.06787228e-07 | `0a903995a4f7` | hd |
| [if_hd_blue](builds/if_hd_blue.qasm) | 3.842471042702e-05 | 0.508174024099 | 1.37195401e-07 | `3ad3440564b4` | hd; early blue |
| [if_he](builds/if_he.qasm) | 3.849151951591e-05 | 0.507363227783 | 1.70872980e-07 | `dd96a838b109` | he |
| [if_he_blue](builds/if_he_blue.qasm) | 3.855137493394e-05 | 0.507366148042 | 2.01242576e-07 | `f573481ec5f8` | he; early blue |
| [if_hj](builds/if_hj.qasm) | 3.904684483667e-05 | 0.508181840677 | 4.53354921e-07 | `9d0bb280d1c6` | hj |
| [if_hj_blue](builds/if_hj_blue.qasm) | 3.911072346687e-05 | 0.508185314784 | 4.85820202e-07 | `53ce36da189f` | hj; early blue |
| [if_de](builds/if_de.qasm) | 3.832463162912e-05 | 0.507969292853 | 8.63031723e-08 | `6b5bb18e0834` | de |
| [if_de_blue](builds/if_de_blue.qasm) | 3.838402862254e-05 | 0.507972259481 | 1.16475701e-07 | `ff1dc1b7b3fe` | de; early blue |
| [if_dj](builds/if_dj.qasm) | 3.860890008718e-05 | 0.509462151328 | 2.31380827e-07 | `4f9f7806d04d` | dj |
| [if_dj_blue](builds/if_dj_blue.qasm) | 3.867220477771e-05 | 0.509465672261 | 2.63633993e-07 | `f9ea7e8f0409` | dj; early blue |
| [if_ej](builds/if_ej.qasm) | 3.900330779024e-05 | 0.507980071347 | 4.31058968e-07 | `63c66eb4bf20` | ej |
| [if_ej_blue](builds/if_ej_blue.qasm) | 3.906674485889e-05 | 0.507983543892 | 4.63286902e-07 | `bf3eba75e713` | ej; early blue |
| [if_hde](builds/if_hde.qasm) | 3.837872282803e-05 | 0.507598519447 | 1.13696791e-07 | `7dee87af5ab6` | hde |
| [if_hde_blue](builds/if_hde_blue.qasm) | 3.843886411971e-05 | 0.507601484764 | 1.44225264e-07 | `824ae314d005` | hde; early blue |
| [if_hdej](builds/if_hdej.qasm) | 3.867965670435e-05 | 0.508516718236 | 2.66932365e-07 | `42824d6d93ee` | hdej |
| [if_hdej_blue](builds/if_hdej_blue.qasm) | 3.874399035873e-05 | 0.508520234143 | 2.99649176e-07 | `5ae213ce64cb` | hdej; early blue |
| [if_d_g0](builds/if_d_g0.qasm) | 3.825307239600e-05 | 0.508576066633 | 5.00129489e-08 | `5b6ddf370ff7` | if_d: advance_init 4→10@36 |
| [if_d_g1](builds/if_d_g1.qasm) | 3.842319895711e-05 | 0.508306518572 | 1.36462882e-07 | `44d4ddf7db65` | if_d: known 10→4@35 |
| [if_d_g2](builds/if_d_g2.qasm) | 3.826698127541e-05 | 0.508573902354 | 5.70864291e-08 | `1ef84c746e17` | if_d: advance_init 4→3@36 |
| [if_d_g3](builds/if_d_g3.qasm) | 3.840213621138e-05 | 0.508307691290 | 1.25756841e-07 | `01f9a3af01d4` | if_d: known 3→4@35 |
| [if_d_g4](builds/if_d_g4.qasm) | 3.884855903821e-05 | 0.502498383265 | 3.48646349e-07 | `fa8f8a7502dc` | if_d: known 19→20@32 |
| [if_d_g5](builds/if_d_g5.qasm) | 3.881933656094e-05 | 0.502826682977 | 3.34180291e-07 | `253e24049bee` | if_d: known 19→20@31 |
| [if_d_g6](builds/if_d_g6.qasm) | 3.832405763437e-05 | 0.503622474436 | 8.52755781e-08 | `71f1ece58980` | if_d: known 20→26@31 |
| [if_hde_g0](builds/if_hde_g0.qasm) | 3.831348865641e-05 | 0.507631493351 | 8.05892568e-08 | `a820fb782ab1` | if_hde: advance_init 10→16@38 |
| [if_hde_g1](builds/if_hde_g1.qasm) | 3.832013788188e-05 | 0.507632274814 | 8.39647423e-08 | `a45db786d2ba` | if_hde: advance_init 4→10@36 |
| [if_hde_g2](builds/if_hde_g2.qasm) | 3.833180426112e-05 | 0.507630374346 | 8.98866364e-08 | `fbdf922a7e59` | if_hde: advance_init 22→16@38 |
| [if_hde_g3](builds/if_hde_g3.qasm) | 3.849151951591e-05 | 0.507363227783 | 1.70872980e-07 | `c909948cef51` | if_hde: known 10→4@35 |
| [if_hde_g4](builds/if_hde_g4.qasm) | 3.833420827730e-05 | 0.507630114744 | 9.11069415e-08 | `42954e267752` | if_hde: advance_init 4→3@36 |
| [if_hde_g5](builds/if_hde_g5.qasm) | 3.847064260818e-05 | 0.507364398453 | 1.60281174e-07 | `d0d0a6e969bf` | if_hde: known 3→4@35 |
| [if_hde_g6](builds/if_hde_g6.qasm) | 3.892286420674e-05 | 0.501567929277 | 3.85269866e-07 | `1655304c14d0` | if_hde: known 19→20@32 |
| [if_hde_g7](builds/if_hde_g7.qasm) | 3.889328533043e-05 | 0.501895508664 | 3.70675985e-07 | `61fe31e295f1` | if_hde: known 19→20@31 |
| [if_hde_g8](builds/if_hde_g8.qasm) | 3.839502373503e-05 | 0.502027945906 | 1.20632551e-07 | `2216e2672b91` | if_hde: known 20→26@31 |
| [if_hde_g9](builds/if_hde_g9.qasm) | 3.886370562658e-05 | 0.502223525406 | 3.56062619e-07 | `d580a9bae923` | if_hde: known 19→20@30 |
| [if_hde_join2](builds/if_hde_join2.qasm) | 3.825492890626e-05 | 0.507665312621 | 5.08658719e-08 | `fa1e4b56eba3` | if_hde: joint 10→16@38, 4→10@36 |
| [if_hdej_g0](builds/if_hdej_g0.qasm) | 3.861431950531e-05 | 0.508549485685 | 2.33722367e-07 | `393f590607ce` | if_hdej: advance_init 10→16@38 |
| [if_hdej_g1](builds/if_hdej_g1.qasm) | 3.862097152194e-05 | 0.508550268610 | 2.37105611e-07 | `70f19e101446` | if_hdej: advance_init 4→10@36 |
| [if_hdej_g2](builds/if_hdej_g2.qasm) | 3.863064580336e-05 | 0.508548628571 | 2.42024689e-07 | `b8d036b93933` | if_hdej: advance_init 22→16@38 |
| [if_hdej_g3](builds/if_hdej_g3.qasm) | 3.919621757156e-05 | 0.507273984293 | 5.28317914e-07 | `0a0bc9c11188` | if_hdej: known 10→4@35 |
| [if_hdej_g4](builds/if_hdej_g4.qasm) | 3.906163849165e-05 | 0.507609292751 | 4.60353541e-07 | `441863bb03a5` | if_hdej: known 10→4@34 |
| [if_hdej_g5](builds/if_hdej_g5.qasm) | 3.863134090758e-05 | 0.508548367394 | 2.42378059e-07 | `b868566b4c01` | if_hdej: advance_init 4→3@36 |
| [if_hdej_g6](builds/if_hdej_g6.qasm) | 3.892705776771e-05 | 0.507945048885 | 3.92298428e-07 | `72ab569ffa89` | if_hdej: known 10→4@33 |
| [if_hdej_g7](builds/if_hdej_g7.qasm) | 3.913267196539e-05 | 0.507278122843 | 4.96086929e-07 | `e5073ae4d539` | if_hdej: known 3→4@35 |
| [if_hdej_g8](builds/if_hdej_g8.qasm) | 3.879247551992e-05 | 0.508281253290 | 3.24152453e-07 | `612adce8d6ca` | if_hdej: known 10→4@32 |
| [if_hdej_g9](builds/if_hdej_g9.qasm) | 3.861464887270e-05 | 0.508886239245 | 2.34044744e-07 | `f19e83458e5f` | if_hdej: known 11→10@32 |
| [if_hdej_join2](builds/if_hdej_join2.qasm) | 3.854933711855e-05 | 0.508919092065 | 2.00821455e-07 | `785def267bbf` | if_hdej: joint 10→16@38, 11→10@32 |
| [if_hdej_join3](builds/if_hdej_join3.qasm) | 3.849070214498e-05 | 0.508952792575 | 1.70992320e-07 | `e82230bdba02` | if_hdej: joint 10→16@38, 11→10@32, 4→10@36 |
