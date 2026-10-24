**Best verified: `pop35b/phase/phase_010` — all-orders 4.355240105565e-05, acceptance 0.500940886; judge PASS, XTIM FAST; MC3 mean 4.380887333e-05.**

# ST2 — v35b population

Base: MAIN/v35b, all-orders 4.376021340833e-05, acceptance 0.501688349806. Search acceptance floor: 0.5005. Best gain: 2.078123527e-07 (0.47489%). 212 CX, R44, native depth 47.

Delivery: [best.qasm](best.qasm), [best.json](best.json), [best.verify.json](best.verify.json), byte-identical QASM to the source finalist above.

The winner keeps all five storage guards and the A/blue checks. Relative to v35b, it adds the later q7–q13 Z echo, folds the q15–q21 X echo readout into a q21 measurement at tick32, and replaces the q20–q26 Z echo with a later q20–q21 X echo. Guard274/275 use measured initialization parities; selected early known-zero checks are restored; q1 at tick7 uses a checked X measurement; Tdag moves from q16 at34 to q22 at37. The q15 terminal instrument remains. These are the actual native diff, not an additive estimate.

| Finalist under ST2 | All-orders loss | Acceptance | Judge acceptance / seconds | XTIM s/1e6 | MC3 mean |
|---|---:|---:|---:|---:|---:|
| `pop35b/phase/phase_010` | 4.355240105565e-05 | 0.500940886 | 0.500108 / 2.922 | 5.343 | 4.380887333e-05 |
| `pop35b/zebra2/g00_217318e405c66a` | 4.355286690109e-05 | 0.500940886 | 0.500259 / 2.720 | 4.913 | 4.329575000e-05 |
| `pop35b/owl/g02_217318e405c66a` | 4.355286690109e-05 | 0.500940886 | 0.500259 / 4.271 | 7.965 | 4.329575000e-05 |
| `pop35b/owl/g01_3f69baf115032a` | 4.356408955156e-05 | 0.501410578 | 0.501274 / 4.289 | 9.083 | 4.298950333e-05 |
| `pop35b/zebra/g07_616bb71515a2c9` | 4.356443124442e-05 | 0.502346533 | 0.502228 / 2.316 | 3.906 | 4.436761000e-05 |
| `pop35b/focused/q7x_q10z_q7Z_mx1` | 4.356453830409e-05 | 0.502174687 | 0.501859 / 4.825 | 8.428 | 4.427135000e-05 |
| `pop35b/zebra/g06_37a21f3383e778` | 4.356487327656e-05 | 0.505458412 | 0.506071 / 2.297 | 3.657 | 4.360405000e-05 |
| `pop35b/focused/timing_q7Z_mx1` | 4.356487327656e-05 | 0.505458412 | 0.504633 / 3.311 | 5.080 | 4.381423333e-05 |
| `pop35b/zebra/g05_73d5e7aa671fbd` | 4.363804971309e-05 | 0.505121053 | 0.504951 / 2.274 | 3.465 | 4.410565000e-05 |
| `pop35b/zebra/g04_d784e9a3567d39` | 4.364671126165e-05 | 0.501113807 | 0.501215 / 2.333 | 5.628 | 4.325204333e-05 |
| `pop35b/zebra/g03_b21170e18b01f2` | 4.366739265078e-05 | 0.505119834 | 0.504949 / 2.637 | 4.762 | 4.409579000e-05 |
| `pop35b/zebra/g02_5fb503eed352e4` | 4.366859487214e-05 | 0.506466592 | 0.506634 / 2.237 | 3.536 | 4.443718000e-05 |
| `pop35b/zebra/g01_f5d93c77813b4b` | 4.367949260671e-05 | 0.503648105 | 0.503847 / 2.317 | 4.025 | 4.399390333e-05 |
| `pop35b/zebra/g00_ecc15c15da6170` | 4.367982703404e-05 | 0.506941465 | 0.507010 / 2.778 | 3.609 | 4.334462333e-05 |
| `pop35b/seed0/FRESH_feedback_i009_t00` | 4.375872298118e-05 | 0.507722961 | 0.507393 / 2.263 | 3.366 | 4.384948000e-05 |

Total scored alternatives: 563; acceptance-feasible numerical results: 385. There are 16 complete population generation checkpoints. The initial zebra run migrated only after generation7 was fully joined and saved; both final islands then stopped after two nonimproving generations.

All finalists above passed judge1e6, XTIM FAST and MC3 (100M shots at seeds0/1000/2000). All-orders loss ranks this supported zero-frame family; MC3 estimates and SEMs are preserved, without claiming they resolve each small improvement. Hashes bind gates to the delivered QASM. No server runtime or global optimum is claimed.

Search evidence:

- `focused/`: 9 scored; 9 acceptance-feasible; best 4.356453830409e-05.
- `owl/`: 142 scored; 81 acceptance-feasible; best 4.355286690109e-05.
- `phase/`: 8 scored; 2 acceptance-feasible; best 4.355240105565e-05.
- `seed0/`: 41 scored; 39 acceptance-feasible; best 4.375872298107e-05.
- `seed1/`: 52 scored; 45 acceptance-feasible; best 4.375872298086e-05.
- `zebra/`: 226 scored; 162 acceptance-feasible; best 4.356443124442e-05.
- `zebra2/`: 85 scored; 47 acceptance-feasible; best 4.355286690109e-05.
- `owl/generation_00.json`: best 4.356453830409e-05, gain 0.000000e+00, consecutive nonimproving generations 1.
- `owl/generation_01.json`: best 4.356408955156e-05, gain 4.487525e-10, consecutive nonimproving generations 0.
- `owl/generation_02.json`: best 4.355286690109e-05, gain 1.122265e-08, consecutive nonimproving generations 0.
- `owl/generation_03.json`: best 4.355286690109e-05, gain 0.000000e+00, consecutive nonimproving generations 1.
- `owl/generation_04.json`: best 4.355286690109e-05, gain 0.000000e+00, consecutive nonimproving generations 2.
- `zebra/generation_00.json`: best 4.367982703404e-05, gain 7.889595e-08, consecutive nonimproving generations 0.
- `zebra/generation_01.json`: best 4.367949260671e-05, gain 3.344273e-10, consecutive nonimproving generations 0.
- `zebra/generation_02.json`: best 4.366859487214e-05, gain 1.089773e-08, consecutive nonimproving generations 0.
- `zebra/generation_03.json`: best 4.366739265078e-05, gain 1.202221e-09, consecutive nonimproving generations 0.
- `zebra/generation_04.json`: best 4.364671126165e-05, gain 2.068139e-08, consecutive nonimproving generations 0.
- `zebra/generation_05.json`: best 4.363804971309e-05, gain 8.661549e-09, consecutive nonimproving generations 0.
- `zebra/generation_06.json`: best 4.356487327656e-05, gain 7.317644e-08, consecutive nonimproving generations 0.
- `zebra/generation_07.json`: best 4.356443124442e-05, gain 4.420321e-10, consecutive nonimproving generations 0.
- `zebra2/generation_00.json`: best 4.355286690109e-05, gain 1.122265e-08, consecutive nonimproving generations 0.
- `zebra2/generation_01.json`: best 4.355286690109e-05, gain 0.000000e+00, consecutive nonimproving generations 1.
- `zebra2/generation_02.json`: best 4.355286690109e-05, gain 0.000000e+00, consecutive nonimproving generations 2.

The population uses full 72-observable canonical all-orders fitness and exact acceptance before evaluating loss. It retains low-loss elites and acceptance alternatives; all complete crossovers are repriced. Unsupported or nondeterministic circuits are recorded as failures. No first-order or truncated-order rank filter is applied. The initial reusable scorer also calculated a single-fault diagnostic; subsequent workers omit that unused diagnostic and keep the identical all-orders calculation.

Moves exercised: slack retiming, commuting gate reordering, reset/checked-measurement choices, MX/MZ helper bases, guard/echo endpoints, neighboring helper substitutions, guard274 removal plus replacement gadgets, detector row add/remove, new idle echoes, whole-window timing, terminal readout-edge changes, and crossovers of measured improvements. Helper substitutions shrink to a legal available interval when the original full window is occupied. All physical rewrites remain subject to native schedule, geometry and ideal correctness checks.

FRESH’s measured timing recipes and WAITPROT’s current menu were ported as native patches; standalone SX and timing sweeps were not repeated. New record IDs are reassigned. The released q7 helper and measured-X initialization at q1 were combined through the evolving population. Menus and rejected ports are preserved under `patches_catalog.json`, `patches.json`, seed logs and generation summaries.

The winning sparse-kernel cutoff omission bound is 1.1970659100562574e-14; it excludes floating-point roundoff. The sparse evaluator is byte-identical to MAIN’s current evaluator.

The final phase screen tested all eight masks of the three legacy transfer choices on the current schedule: the unchanged mask and q16-to-q22 relocation passed; the other six fixed variants failed ideal detector determinism. The q16-to-q22 gain is 4.658454349e-10 in all-orders loss, too small for these MC draws to resolve. No broader phase-transfer impossibility is claimed.

`best_changes.json` records the exact final changes from v35b. `all_results.json` indexes every numerical result and rejection. Prior acceptance knapsack work remains in [REPORT_before_population.md](pop35b/REPORT_before_population.md).

Complete: all ST2 search and validation jobs exited. All writes remained under ST2. No submissions, credentials, commits, pushes or collaboration tools were used.
