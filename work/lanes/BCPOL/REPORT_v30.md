# BCPOL — v30f resource and endpoint contracts

Status: COMPLETE — finite v30f campaign; no verified improvement. All jobs exited and were collected.

Objective: all-orders conditional 1−F at p=1e-3. Hard gates are the unchanged judge, acceptance ≥0.5 (exp(−A1) target ≥0.5002), and FAST runtime. Previous accepted v25 work is preserved in [REPORT_v25.md](REPORT_v25.md). No submission, commit, push, credential access, or subagent use.

**Best circuit in this campaign remains v30f**: `v30/inputs/v30f`. All-orders **5.89377420422e-05**, acceptance **0.5275245061**. Independent judge-model and boundary-cache results agree within 6.85e-16.
Second 4.62005346087e-05 + cubic 1.20387969055e-05 = 5.82393315142e-05; c1=2.6645e-19; exp(−A1)=0.5276872043. FRESH’s receipts are inherited on byte-identical QASM: MC mean 5.89438407e-05, seed-0 acceptance 0.52751, 2.8 s/1e6 on zebra. The matching exact CLI is copied to `v30/inputs/v30f.inherited_exact.log`.

SEPBC owns the round-start critical path; its report identifies an A/prefix release chain. COMP29 owns the local timing/check pack. This lane retained v30f’s exterior schedule and changed B/C resources, their measurement contracts, and new helper use. The explicitly labeled transversal-H Bell control needs one additional round step; it is a diagnostic.

The best new endpoint is `v30/finalists/feedback_1401_02324`: 193 CX, R48, all-orders 6.04675548781556e-5 (+1.52981283597e-6, +2.596% versus v30f). Its second + third parts are 4.73450672708748e-5 + 1.23995084905158e-5 = 5.97445757613906e-5; exp(−A1)=0.526317703263, ΔA1=+0.00259866312. Judge PASS, FAST, 8.7 s/1e6 on jerry; MC mean 6.005349e-5. It is retained as a checked negative control, not a promotion. The difference of the recommended circuit from v30f is zero.

## In-situ prices

Delta columns are candidate minus v30f. Negative ΔA1 frees acceptance. The table contains 24 completed full-price bundles, with independent exact CLI checks (third order only where |c1|<1e-12), judge 1e6 gates, and XTIM predictions. Only the two MC controls remain unpacked; other recipes and raw logs are in the single `witnesses.tar.xz` archive at the displayed paths. A completed all-orders value does not imply its gates passed.

Fresh baseline gate: PASS, seed-0 acceptance 0.527174, FAST, 3.5 s/1e6 on jerry. The v22h_c2c9 calibration measured 2.7 s there versus 2.3 s on zebra, giving a scaled limit of 23.48 s. Every measured actual runtime is below that limit. The ported rank4_3 circuit is nevertheless excluded by the additional XTIM FAST requirement (its predictor was not FAST). MC uses 1e8 shots per seed; its means are cross-checks, while all-orders values set the ranking.

| Stem (`v30/finalists/`) | All-orders 1−F | Δ1−F | ΔA1 | exp(−A1) | Judge | FAST | s/1e6 | Exact CLI | MC mean |
|---|---:|---:|---:|---:|---|---|---:|---|---:|
| `feedback_1401_02324` | 6.0467554878e-05 | +1.52981e-06 | +0.002598663 | 0.526317703 | True | True | 8.7 | True | 6.005349e-05 |
| `port_rank4_3` | 6.0688454767e-05 | +1.75071e-06 | +0.02833333 | 0.51294589 | True | False | 9.5 | True | — |
| `rank4_5_s1105_00001` | 6.0767851667e-05 | +1.83011e-06 | +0.002462668 | 0.526389285 | True | True | 4.9 | True | — |
| `policy_14_s1114_00454` | 6.0911170103e-05 | +1.97343e-06 | -0.004530674 | 0.530083407 | True | True | 3.5 | True | — |
| `feedback_1403_03280` | 6.1236413114e-05 | +2.29867e-06 | -0.004528895 | 0.530082464 | True | True | 4.6 | True | — |
| `helpermx_0_s1302_00294` | 6.1366493937e-05 | +2.42875e-06 | -7.776534e-05 | 0.527728242 | True | True | 4.5 | True | — |
| `helpermx_0_s1302_00294_lazy_init` | 6.1366493937e-05 | +2.42875e-06 | -7.776534e-05 | 0.527728242 | True | True | 5.7 | True | — |
| `policy_9_s1109_00360` | 6.2108446747e-05 | +3.1707e-06 | -0.006861339 | 0.531320295 | True | True | 4.6 | True | — |
| `policy_12_s1112_00315` | 6.4651549169e-05 | +5.71381e-06 | -0.002668444 | 0.529097189 | True | True | 4.0 | True | — |
| `c6_1_s1221_00621` | 6.4901003181e-05 | +5.96326e-06 | +0.0008693286 | 0.52722867 | True | True | 5.9 | True | — |
| `policy_13_s1113_00026` | 6.5460055894e-05 | +6.52231e-06 | -0.009726229 | 0.532844652 | True | True | 3.9 | True | — |
| `c6_0_s1220_00017` | 6.5760543281e-05 | +6.8228e-06 | -0.0008675556 | 0.528145201 | True | True | 3.8 | True | — |
| `c6_5_s1225_00350` | 6.6800730806e-05 | +7.86299e-06 | +0.007466661 | 0.523761816 | True | True | 7.6 | True | — |
| `helpermx_0_s1301_00318` | 6.7303189208e-05 | +8.36545e-06 | +0.01046755 | 0.522192421 | True | True | 8.2 | True | — |
| `helpermx_0_s1301_00318_lazy_init` | 6.7303189208e-05 | +8.36545e-06 | +0.01046755 | 0.522192421 | True | True | 4.4 | True | — |
| `c6_3_s1223_00195` | 6.7839013198e-05 | +8.90127e-06 | +0.003604437 | 0.525788613 | True | True | 3.7 | True | — |
| `c6_6_s1226_00743` | 6.8368226216e-05 | +9.43048e-06 | +0.006918234 | 0.52404914 | True | True | 5.8 | True | — |
| `helper_0_s1211_00906` | 7.0400413612e-05 | +1.14627e-05 | -0.001526674 | 0.528493426 | True | True | 4.6 | True | — |
| `helper_0_s1211_00906_lazy_init` | 7.0400413612e-05 | +1.14627e-05 | -0.001526674 | 0.528493426 | True | True | 4.3 | True | — |
| `c6_4_s1224_00001` | 7.0538328522e-05 | +1.16006e-05 | -0.004267556 | 0.529943951 | True | True | 3.6 | True | — |
| `c6_2_s1222_00036` | 7.2776622529e-05 | +1.38389e-05 | +0.004588901 | 0.525271247 | True | True | 4.0 | True | — |
| `rank4_4_s1104_00404` | 7.3185903083e-05 | +1.42482e-05 | +0.004597778 | 0.525266585 | True | True | 4.7 | True | — |
| `bell4_0_s1201_00010` | 7.6959185967e-05 | +1.80214e-05 | -0.0005933404 | 0.528000395 | True | True | 3.7 | True | 7.635695e-05 |
| `bell7_transversal_h_r1` | 0.00051481355556 | +0.000455876 | +0.05696988 | 0.498465219 | False | True | 3.9 | True | — |

## Contracts and mechanisms

Item 5 / rank-four endpoints: all seven one-dimensional C subspaces were attempted with B=|0_L>, including the earlier rank4_3 network ported to v30f. The new resource target is the inverse of the terminal B→C check, so it can exploit correlated amplitudes. The predicate accepts correctable B boundary residues. C’s full Z-check nullspace is emitted and propagated through the actual readout recoding. Cache feedback improved this family from 6.07678517e-5 to 6.04675549e-5. The best measured resource-plus-check has 68 CX versus baseline 64; its second-order contribution increases from 4.62005e-5 to 4.73451e-5. This closes that recipe only.

Item 4 / partial-clean policies: seven singleton relaxations {9}, …, {15}, applied before the literal terminal check to the correlated rank-three resource. This differs from BCFB’s independent rank-six target. The initial runs produced no clean-skipped witness, so removing the old clean-skip filter did not discard a measured candidate. The best is policy 14, all-orders 6.09111701e-5 and ΔA1=−0.00453067: one fewer total CX (188) and more acceptance, but higher loss. Correctable accepted residues can combine with later faults; the full circuit price establishes the negative, while that attribution is a mechanism rather than an isolated causal ablation. No singleton improved loss, so combined relaxations were not retained.

Encoded Bell: joint synthesis targets both the rank-four logical-branch endpoint and the full rank-seven encoded Bell state. FRAME_X is the measured logical C parity, propagated through the C readout network. The X-fault predicate tests B’s syndrome with its parity corrected by C’s inferred branch, preventing an uncorrelated C logical-X fault from being treated as harmless. A separate full Bell construction uses H on B after an independent |0_L>|0_L> preparation. It is noiselessly correct, but has eight harmful single Pauli faults, c1=4e-4, and an acceptance proxy below 0.5. The boundary audit identifies corrected B classes 1 and 8. A C-only logical-X fault on C cells {12,19,25} flips the inferred branch without changing B; mixed hooks also survive. All eight have zero detector signature and loss 0.5 (`v30/bell_h_boundary.json`). Only that construction is rejected by this diagnosis; the joint Bell search is separate.

Item 6 / C6: every omitted position is tested on the correlated resource, with the omitted C cell measured in X as a helper. Its phase byproduct is propagated into the actual measurement records. The corresponding external check and readout use are removed, and all six surviving literal C checks are retained. Best omitted position 1 scores 6.49010032e-5, ΔA1=+0.000869329, 193 total CX. The freed cell did not compensate for the measured preparation/readout cost in these seven networks. Other placements and instrument designs remain open.

Spare cells and helper instruments: coherent zero-return and measured-X helper searches use q18/q24, the bottom row, or both. Measured helpers can retain codeword-dependent X amplitudes at the boundary; a derived Z byproduct restores the B/C state through record corrections. Valid depth-9 and depth-10 resources were found. Local clean-bus Kraus identities and arbitrary-state dirty-bus identities at distances 2–4 are checked in `v30/bus.certificates.json`. No isolated coherent clean-bus packet in v30f met the strict local replacement conditions; that scan is not a general exclusion. Implicit helper initialization uses STANDARD.initial=1, and was repriced as noisy first use. It is not free noiseless preparation.

The two measured-helper depths refer to preparation before the external check. The q18/q24 depth-10 preparation has 186 total CX but all-orders 6.13664939e-5. Cache feedback finds 6.12364131e-5 with 189 total CX; it still loses to v30f. The depth-9 bottom-row-plus-spares preparation scores 6.73031892e-5. The fixed exterior keeps R48, so these local depth reductions do not shorten the shared critical path. A separate clean D10/CX≤70 search on the original cells returned no witness in 601 s; this is not an impossibility proof.

The final dirty-bus scan enumerated 32,946 helper-using linear-map states on four physical squares adjoining dirty data cells q7/q10/q20/q22. The returned-data map was proved to be identity for arbitrary entangled input. Within isolated 2–6-CX B/C windows, helper words of length ≤8 and at most two added CX yielded zero compatible proposals. No physical dirty-bus price is claimed; the tested window/isolation restriction, not a noise measurement, stopped this experiment.

## Finite search receipts

| Run | Status | Witnesses | Full cubic screens / cache hits | Best screen or cache loss |
|---|---|---:|---:|---:|
| `bell4_0_s1201.receipt` | BUDGET_FINISHED | 463 | 463 | 7.6202491826e-05 |
| `bell7_0_s1202.receipt` | BUDGET_FINISHED | 0 | 0 | — |
| `c6_0_s1220.receipt` | BUDGET_FINISHED | 993 | 993 | 6.5043770305e-05 |
| `c6_1_s1221.receipt` | BUDGET_FINISHED | 920 | 920 | 6.4184499088e-05 |
| `c6_2_s1222.receipt` | BUDGET_FINISHED | 952 | 952 | 7.2017898985e-05 |
| `c6_3_s1223.receipt` | BUDGET_FINISHED | 1010 | 1010 | 6.7085760569e-05 |
| `c6_4_s1224.receipt` | BUDGET_FINISHED | 1069 | 1069 | 6.9794812494e-05 |
| `c6_5_s1225.receipt` | BUDGET_FINISHED | 900 | 900 | 6.6020865733e-05 |
| `c6_6_s1226.receipt` | BUDGET_FINISHED | 1083 | 1083 | 6.7595870419e-05 |
| `feedback_1401.receipt` | BUDGET_FINISHED | 3907 | 478 | 6.0467554878e-05 |
| `feedback_1402.receipt` | BUDGET_FINISHED | 2065 | 713 | 6.0911170103e-05 |
| `feedback_1403.receipt` | BUDGET_FINISHED | 3368 | 565 | 6.1236413113e-05 |
| `helper_0_s1210.receipt` | BUDGET_FINISHED | 0 | 0 | — |
| `helper_0_s1211.receipt` | BUDGET_FINISHED | 910 | 910 | 6.9648274639e-05 |
| `helper_0_s1212.receipt` | BUDGET_FINISHED | 0 | 0 | — |
| `helper_0_s1510.receipt` | BUDGET_FINISHED | 0 | 0 | — |
| `helpermx_0_s1301.receipt` | BUDGET_FINISHED | 536 | 519 | 6.6479353493e-05 |
| `helpermx_0_s1302.receipt` | BUDGET_FINISHED | 553 | 553 | 6.0635060358e-05 |
| `policy_10_s1110.receipt` | BUDGET_FINISHED | 0 | 0 | — |
| `policy_11_s1111.receipt` | BUDGET_FINISHED | 0 | 0 | — |
| `policy_12_s1112.receipt` | BUDGET_FINISHED | 441 | 441 | 6.3949468277e-05 |
| `policy_13_s1113.receipt` | BUDGET_FINISHED | 31 | 31 | 6.4768887065e-05 |
| `policy_14_s1114.receipt` | BUDGET_FINISHED | 524 | 524 | 6.02059538e-05 |
| `policy_15_s1115.receipt` | BUDGET_FINISHED | 0 | 0 | — |
| `policy_9_s1109.receipt` | BUDGET_FINISHED | 453 | 453 | 6.1421326599e-05 |
| `rank4_1_s1101.receipt` | BUDGET_FINISHED | 0 | 0 | — |
| `rank4_2_s1102.receipt` | BUDGET_FINISHED | 0 | 0 | — |
| `rank4_3_s1103.receipt` | BUDGET_FINISHED | 0 | 0 | — |
| `rank4_4_s1104.receipt` | BUDGET_FINISHED | 542 | 542 | 7.2417558651e-05 |
| `rank4_5_s1105.receipt` | BUDGET_FINISHED | 447 | 447 | 6.0045710653e-05 |
| `rank4_6_s1106.receipt` | BUDGET_FINISHED | 0 | 0 | — |
| `rank4_7_s1107.receipt` | BUDGET_FINISHED | 0 | 0 | — |

MC cross-checks (seeds 0 / 1000 / 2000): rank-four control 5.945878e-5 / 6.081608e-5 / 5.988560e-5, mean 6.005349e-5; FRAME Bell control 7.632282e-5 / 7.508531e-5 / 7.766273e-5, mean 7.635695e-5. The respective seed-0 acceptances are 0.52616 and 0.52795. All-orders values are 6.04675548782e-5 and 7.69591859672e-5; both MC deviations are consistent with the reported sampling errors.

The initial portfolios use 900-second budgets per case; fixed-pivot cache feedback uses 600 seconds after compilation/validation. Every budget exhaustion is a finite search outcome, never UNSAT. Screens without complete independent receipts remain screens.

## Item 10 / boundary cache API

The v30f cache is `v30/inputs/cache_v30f.boundary_allorders.npz`, with its QASM/JSON reference. Cut=49 (R+1), 14 boundary bits, 16,384 classes, 93 varying region channels. This implementation retains the full reduced detector/decoder signatures rather than the proposed 11-bit quotient; its measured interface has 14 bits. All exterior channels, including prefix/data/A noise and nonrepresentable region-record effects, remain in the response. Compilation took 46.49 s. The full sparse evaluator, the judge-model path, and cache contraction give 5.8937742042181e-5, 5.8937742042286e-5, and 5.8937742042866e-5.

```python
import os, sys
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"  # set before importing numpy
os.environ["XTIM_TWIRL_CACHE_DIR"] = "/absolute/path/to/your_lane/.xtim_cache"
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/BCPOL")
from boundary_api import prepare_candidate, AllOrdersCache
region = prepare_candidate("/absolute/path/to/candidate_stem")
cache = AllOrdersCache(
    "/home/jihoon/competitions/quantumn/work/lanes/BCPOL/v30/inputs/"
    "cache_v30f.boundary_allorders.npz")
result = cache.score(region)
# result: loss, numerator, acceptance, score_seconds, all_orders
```

Inputs: QASM plus JSON containing data_qubits, R, boundary_step, and preferably init_times and region_qubits. The cut must be a chronological program prefix. prepare_candidate performs the full model audit outside the hot path and returns PreparedRegion(fingerprint, categorical_channels, n_classes). A search with an audited signature map can construct that object directly. Each channel contains mutually exclusive (class, probability) outcomes; the no-fault probability is one minus their sum.

The SHA-256 fingerprint covers the entire exterior categorical distribution, reduced ideal rotations/projectors/decoder and reference signs, and ordered boundary basis. Changes of endpoint, frame, detector basis, initialization, or exterior timing can invalidate reuse. Mismatches are rejected. The equivalent v30f rebuild uses a different C detector basis and therefore requires its own cache; no hash is forced to match. Compile with `v30/cache30.py <reference_stem>`.

The cache computes the XOR distribution P_k of region faults and returns sum(P_k N_k)/sum(P_k A_k), including all noise orders. Sparse kernel selectors retain the boundary Fourier variables, replacing the old dense width-26 contraction; this compilation had conditioned width 9. Model extraction and compilation are excluded from scoring time. Sparse categorical characters reduce scoring to a measured median 0.0354 s over 12 calls on 16,384 classes. The optimized characters agree with the dense transform within 2.23e-16, including randomized categorical tests; invalid inputs and mismatched fingerprints are rejected. Setting the 93 varying channels noiseless gives loss 4.5362828261e-5, acceptance 0.5737611548; this is an ablation, not a lower bound. Final physical candidates still require judge, speed and MC checks.

## Evaluator and verification scope

Non-FRAME circuits use the unchanged serial snapshot of MAIN/sparse/sparse_walsh.py (72 terms, canonical detector rows), with files and output confined to this lane. MAIN subsequently added a parallel row executor; the numerical contraction is unchanged (`v30/sparse_snapshot.diff`). The original allorders_general.py did not support FRAME, contrary to the task’s initial assumption. Its FRAME entry now uses exact2’s complete judge Model, including declared record-dependent logical frames, with the sparse contraction. This path reproduces the non-FRAME v30f control. Its scope rejects unsupported projector/reference bases; sparse-cutoff error bounds and full gate receipts are retained.

The XTIM predictor is copied with filesystem/cache paths relocated. For FRAME circuits its Plan receives the actual declared frame; the unchanged full fast_check independently measures the real 1e6-shot circuit. MC uses the unchanged MAIN/spec/mc3.py at seeds 0/1000/2000 and 1e8 shots each.

Verified: baseline model/cache agreement, stated ideal CSS and finite fault predicates, helper Kraus/unitary certificates, completed all-orders contractions, and the completed gates explicitly marked in the price table. Inferred/open: global optimality; arbitrary placements or instrument layouts; any recipe without full receipts; actual organizer-server runtime. A measured negative closes only the tested recipe.

Execution repairs: JSON signature keys were normalized and seed operations were excluded from contract metadata before SAT candidate reconstruction. Fixed-seed replay verifies the repair. Concurrent model construction in one process stalled; pricing now uses isolated processes. The internal lock was not identified because ptrace was unavailable. A missing mirrored XTIM predictor was copied into this lane; failed gate stages are rerun, while completed all-orders results are reused only with matching circuit hashes.
