# BCFB

Status: CANCELLED BY MAIN — retargeted to A on v30f; unfinished MC is not claimed complete. Previous status: RUNNING — blue-context ports, speed gates and exact-loss feedback. Prior completed campaign: [REPORT_v23.md](REPORT_v23.md). No submission, commit or push.

Hard gates: full judge PASS, seed-0 acceptance ≥0.5 and zebra 1e6-shot single-process command ≤20 seconds. Rank by 1-F; close finalists require ≥100 seed-0 re-draws.

| Base | Exact second | Cubic | Exact total | exp(-A1) |
|---|---:|---:|---:|---:|
| v25k | 5.069981463e-05 | 1.43502882477e-05 | 6.50501028776e-05 | 0.510621553 |
| v26n | 5.00251570448e-05 | 1.42718345409e-05 | 6.42969915857e-05 | 0.503252176 |

MAIN re-draw references (v26n remains in progress):
- v25k: 300 draws; 6.5912178e-05 ± 6.02e-08 SEM; all passed=True.
- v26n: 110 draws; 6.52204427273e-05 ± 1.06e-07 SEM; all passed=True.

Delta columns are candidate minus base. A1 = -log(exp(-A1)); negative is better acceptance.

| Stem (`blue/finalists/`) | Exact | Δ1-F v25k / v26n | ΔA1 v25k / v26n | exp(-A1) | Zebra s | Judge acc | Exact CLI |
|---|---:|---:|---:|---:|---:|---:|---|
| `reject_blue_d15_c90_s708_00718` | 6.32293964203e-05 | -1.8207e-06 / -1.0676e-06 | +0.028894 / +0.014357 | 0.496078546 | 6.430 PASS | 0.495888 FAIL | False |
| `neighbor_blue_d15_c90_s712_00074_check_19` | 6.32293964203e-05 | -1.8207e-06 / -1.0676e-06 | +0.015413 / +0.00087555 | 0.502811748 | 7.333 PASS | 0.502619 PASS | True |
| `blue_d15_c90_s712_00074` | 6.32384566279e-05 | -1.8116e-06 / -1.0585e-06 | +0.013746 / -0.00079112 | 0.503650466 | 5.626 PASS | 0.504322 PASS | True |
| `blue_d15_c90_s712_00007` | 6.32489489425e-05 | -1.8012e-06 / -1.048e-06 | +0.01355 / -0.00098712 | 0.503749192 | 4.376 PASS | 0.502899 PASS | False |
| `v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1` | 6.33308275399e-05 | -1.7193e-06 / -9.6616e-07 | +0.015018 / +0.0004809 | 0.503010221 | 4.325 PASS | 0.503182 PASS | True |
| `v26n_fast_d15_c105_s526_00356_preserve_rt1` | 6.33397222659e-05 | -1.7104e-06 / -9.5727e-07 | +0.011685 / -0.0028524 | 0.504689719 | 3.922 PASS | 0.503838 PASS | True |
| `v26n_fast_d15_c105_s526_00331_preserve_rt1` | 6.34807117505e-05 | -1.5694e-06 / -8.1628e-07 | +0.011552 / -0.0029858 | 0.504757016 | 4.475 PASS | 0.504252 PASS | True |
| `v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1` | 6.36382567752e-05 | -1.4118e-06 / -6.5873e-07 | +0.016018 / +0.0014809 | 0.502507462 | 3.023 PASS | 0.502085 PASS | False |
| `v26n_fb_d14_c98_s517_00020_preserve` | 6.38465905705e-05 | -1.2035e-06 / -4.504e-07 | +0.0092795 / -0.0052578 | 0.505905136 | 3.573 PASS | 0.504963 PASS | True |
| `neighbor_blue_d15_c105_s706_00405_check_11_19` | 6.39416953756e-05 | -1.1084e-06 / -3.553e-07 | +0.0025422 / -0.011995 | 0.509325092 | 5.427 PASS | 0.508688 PASS | True |
| `blue_d15_c90_s704_00057` | 6.39959882833e-05 | -1.0541e-06 / -3.01e-07 | -0.00079112 / -0.015328 | 0.511025675 | 4.480 PASS | 0.51089 PASS | False |
| `blue_d15_c105_s706_00405` | 6.39959882833e-05 | -1.0541e-06 / -3.01e-07 | -0.00079112 / -0.015328 | 0.511025675 | 4.173 PASS | 0.510842 PASS | True |
| `v25k_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1` | 6.4040497557e-05 | -1.0096e-06 / -2.5649e-07 | +0.0004809 / -0.014056 | 0.510376055 | 3.322 PASS | 0.510732 PASS | True |
| `v26n_fb_d15_c105_s506_00008_preserve_rt1` | 6.40653311369e-05 | -9.8477e-07 / -2.3166e-07 | +0.011018 / -0.0035191 | 0.505026291 | 4.376 PASS | 0.504547 PASS | True |
| `v25k_fast_d15_c105_s526_00356_preserve_rt1` | 6.40945334126e-05 | -9.5557e-07 / -2.0246e-07 | -0.0028524 / -0.01739 | 0.512080147 | 3.925 PASS | 0.51209 PASS | True |
| `v26n_fb_d14_c98_s517_00020_reset` | 6.41992320298e-05 | -8.5087e-07 / -9.776e-08 | +0.010613 / -0.0039245 | 0.505231046 | 2.972 PASS | 0.505324 PASS | False |
| `v25k_fast_d15_c105_s526_00331_preserve_rt1` | 6.4237286298e-05 | -8.1282e-07 / -5.9705e-08 | -0.0029858 / -0.017523 | 0.512148429 | 3.722 PASS | 0.511821 PASS | True |
| `v26n` | 6.42969915857e-05 | -7.5311e-07 / +0 | +0.014537 / +0 | 0.503252176 | 4.325 PASS | 0.503023 PASS | True |
| `v25k_ic_fast_d15_c105_s526_00356_11_19_reset_rt1` | 6.43477542408e-05 | -7.0235e-07 / +5.0763e-08 | +0.0014809 / -0.013056 | 0.509865934 | 2.871 PASS | 0.509008 PASS | False |
| `v25k_fb_d14_c98_s517_00020_preserve` | 6.45503940039e-05 | -4.9971e-07 / +2.534e-07 | -0.0035911 / -0.018128 | 0.512458552 | 3.523 PASS | 0.511883 PASS | True |
| `v25k_fb_d15_c105_s506_00008_preserve_rt1` | 6.48126202463e-05 | -2.3748e-07 / +5.1563e-07 | -0.0035191 / -0.018056 | 0.512421647 | 3.974 PASS | 0.511712 PASS | True |
| `v25k_fb_d14_c98_s517_00020_reset` | 6.49029936241e-05 | -1.4711e-07 / +6.06e-07 | -0.0022578 / -0.016795 | 0.511775729 | 2.871 PASS | 0.511372 PASS | False |
| `v25k` | 6.50501028776e-05 | +0 / +7.5311e-07 | +0 / -0.014537 | 0.510621553 | 3.676 PASS | 0.509966 PASS | True |

Current feedback checkpoint (screened until its Exact CLI column passes):
- v25k: `blue_d15_c105_s706_00405`, 6.39959882833e-05, prep 86 CX, R=48, exterior native timing changes `{}`.
- v26n: `blue_d15_c90_s712_00074`, 6.32384566279e-05, prep 86 CX, R=48, exterior native timing changes `{}`.

Best independently confirmed exact: `neighbor_blue_d15_c90_s712_00074_check_19`; c1=2.6645352591e-19, second=4.92624887984e-05, cubic=1.39669076219e-05, total=6.32293964203e-05, exp(-A1)=0.502811747583. MC ranking pending.
Diff: prep 86 CX; round 48; options `{"context": "v26n", "init_checks": [19], "mx": [26, 13, 4, 12, 17, 5], "retime_window": 2, "timing": "alap"}`; exterior timing changes `{}`.

| Feedback seed | Context / D / cap | Budget s | Status | Witnesses | Best screened exact |
|---|---|---:|---|---:|---:|
| blue_s701 | v25k / 14 / 82 | 7200 | FINISHED | 2384 | 6.41471750191e-05 |
| blue_s702 | v25k / 15 / 105 | 7200 | FINISHED | 1435 | 6.43594821297e-05 |
| blue_s703 | v25k / 14 / 98 | 7200 | FINISHED | 2114 | 6.41471750191e-05 |
| blue_s704 | v25k / 15 / 90 | 7200 | FINISHED | 2012 | 6.39959882833e-05 |
| blue_s705 | v25k / 14 / 82 | 7200 | FINISHED | 1489 | 6.44616679142e-05 |
| blue_s706 | v25k / 15 / 105 | 7200 | FINISHED | 2166 | 6.39959882833e-05 |
| blue_s707 | v26n / 14 / 98 | 7200 | FINISHED | 2072 | 6.34396718692e-05 |
| blue_s708 | v26n / 15 / 90 | 7200 | FINISHED | 2290 | 6.32293964203e-05 |
| blue_s709 | v26n / 14 / 82 | 7200 | FINISHED | 2272 | 6.34396718692e-05 |
| blue_s710 | v26n / 15 / 105 | 7200 | FINISHED | 1823 | 6.35553640894e-05 |
| blue_s711 | v26n / 14 / 98 | 7200 | FINISHED | 1660 | 6.36601202257e-05 |
| blue_s712 | v26n / 15 / 90 | 7200 | FINISHED | 1977 | 6.32384566279e-05 |
| neighbor_blue_d15_c105_s706_00405.receipt | init toggles and init checks, radius ≤2 | finite | COMPLETE | 211 | 6.39416953756e-05 |
| neighbor_blue_d15_c90_s712_00074.receipt | init toggles and init checks, radius ≤2 | finite | COMPLETE | 211 | 6.32293964203e-05 |
| neighbor_v25k_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1.receipt | init toggles and init checks, radius ≤2 | finite | COMPLETE | 211 | 6.4040497557e-05 |
| neighbor_v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1.receipt | init toggles and init checks, radius ≤2 | finite | COMPLETE | 211 | 6.33308275399e-05 |
| Round shifts R45–R50, windows 4/12 | four leading preps | finite | COMPLETE | 40 | 6.69477168468e-05 |
| Failed schedules retried at window 4 | both contexts | finite | COMPLETE | 85 | 6.36084504666e-05 |

Counts above are recorded proposals, including repeats across seeds and rejected schedules.

| MAIN mc3 stem | Seed 0 | Seed 1000 | Seed 2000 | Mean | Seed-0 acceptance |
|---|---:|---:|---:|---:|---:|
| `blue_d15_c105_s706_00405` | 6.419482e-05 | 6.469406e-05 | 6.482753e-05 | 6.45721367e-05 | 0.51094 |
| `blue_d15_c90_s712_00074` | 6.35218e-05 | 6.491118e-05 | 6.476558e-05 | 6.439952e-05 | 0.50361 |
| `neighbor_blue_d15_c105_s706_00405_check_11_19` | 6.430445e-05 | 6.500229e-05 | 6.661262e-05 | 6.53064533e-05 | 0.50922 |
| `neighbor_blue_d15_c90_s712_00074_check_19` | 6.222491e-05 | 6.455726e-05 | 6.341242e-05 | 6.33981967e-05 | 0.50277 |
| `v25k_fast_d15_c105_s526_00356_preserve_rt1` | 6.591399e-05 | 6.442926e-05 | 6.555228e-05 | 6.529851e-05 | 0.51203 |
| `v25k_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1` | 6.520262e-05 | 6.414728e-05 | 6.488212e-05 | 6.47440067e-05 | 0.51033 |
| `v26n_fast_d15_c105_s526_00356_preserve_rt1` | 6.200674e-05 | 6.503773e-05 | 6.421142e-05 | 6.37519633e-05 | 0.50462 |
| `v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1` | 6.513713e-05 | 6.348285e-05 | 6.386783e-05 | 6.41626033e-05 | 0.50294 |

| Re-draw stem | Completed draws | Mean 1-F | SEM | ΔMC v25k / v26n | Minimum acceptance |
|---|---:|---:|---:|---:|---:|
| `neighbor_blue_d15_c90_s712_00074_check_19` | 13 provisional | 6.47923431553e-05 | 3.81e-07 | -1.1198e-06 / -4.281e-07 | 0.50270136 |
| `v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1` | 100 COMPLETE100 | 6.41759988021e-05 | 9.86e-08 | -1.7362e-06 / -1.0444e-06 | 0.50282308 |

Screened mechanism ablation (validated Fourier evaluator, no independent CLI claim for these rejected variants):
- `ablate_v25k_82_moved`: 6.52580381702e-05, exp(-A1)=0.511131739.
- `ablate_v25k_82_moved_checked`: 6.50747704955e-05, exp(-A1)=0.509430803.
- `ablate_v26n_82_moved`: 6.45041940168e-05, exp(-A1)=0.503754999.
- `ablate_v26n_82_moved_checked`: 6.43650360963e-05, exp(-A1)=0.502078611.
Applying the five exterior timing moves to the original 82-CX prep worsens loss by about 2.07e-7 on either base. The clean replacement network produces the net gain despite that cost.

Network/timing ablation:
- v25k 86-CX network with the old 88-CX port’s five timing moves: 6.42005043625e-05. Removed/added CX multiplicities: `[{'edge': [5, 4], 'count': 2}, {'edge': [12, 6], 'count': 1}]` / `[{'edge': [6, 12], 'count': 1}]`. Full Clifford-map equality with the 88-CX network: True.
- v26n 86-CX network with the old 88-CX port’s five timing moves: 6.34422398457e-05. Removed/added CX multiplicities: `[{'edge': [5, 4], 'count': 2}]` / `[]`. Full Clifford-map equality with the 88-CX network: True.
The new networks fit the unchanged exterior timing. Applying the old port’s timing moves to them adds about 2.04e-7 loss. This explains the context-dependent optimum. R48 is a lower bound for the retained native wire order, through the chain ending at CX 1→2; it is not a global architectural bound. See `blue/critical_path.json`.

Mechanisms and verification: the original 82-CX preparation replays both bases with exact loss agreement <1e-15. All exterior operations and detector definitions are retained, with the old BC frame corrections replaced by the new ones. The q19 speed repair is retained as reset+H when q19 is a pivot, or Z reset when the new prep makes it a nonpivot. Depth-15 ports need retiming in the new blue context; this is measured separately. The Fourier screen uses the unchanged exact2 model/decoder; independent unmodified CLI confirmations are recorded per row. Speed is measured on zebra with the exact requested command. Screened values alone are not verified improvements.

XTIM’s completed [report](../XTIM/REPORT.md) independently supports retaining q19 reset+H and measuring runtime: moving the q19 MX across one T gate remains slow, while generic MX timing/counts do not predict the path. This campaign has not run XTIM’s code or modified its directory. Cache incident: the initial sampler inherited xtim’s default repository `.xtim_cache` path; the twirl environment variable did not redirect the separate reference cache. It was stopped by verified host PID, completed draws were preserved, and resumed with `xtim.cache_dir` under BCFB. Speed/MC subprocesses now also run from the lane directory. Shared cache entries were not deleted. See `blue/cache_restart.json` and `blue/cache_audit.json`. Re-draw comparisons remain in progress; partial means are provisional. No global optimality claim. Early-MX timing is not used as an admissibility proxy: measured speed is the hard gate. The original global-after-last-T probe proved overly restrictive because native T-dagger operations remain at steps 35, 36 and 47 in these bases; those failed schedules do not imply a speed failure.
