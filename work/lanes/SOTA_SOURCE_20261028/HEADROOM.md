# Native source headroom against physical square endings

These are exact full-noise diagnostics at p=0.001. They retain each source gate, reset, measurement, detector and coherent route, the real data waits, and the ordinary noisy terminal gates and reads. Only the synthetic resource preparation is made perfect and instantaneous. Resource encoders are nonlocal; these QASM files are diagnostic instruments, not eligible native submissions. A perfect-resource intervention is not a monotone lower bound on the conditional loss of every physical resource and does not prove a universal limitation.

The source is the native v37j boundary or its previously constructed eight-CX contraction. The detector/measurement contract is retained. Each row passes the raw output code-space check and has no harmful single-fault components. Terminal clock means the actual first D-to-A/B-to-C clock after removing the artificial ideal-resource time.

| Geometry / source | Terminal clock | Loss | Acceptance |
|---|---:|---:|---:|
| Unmoved six-square, original | 41 | 2.74984614967e-5 | 0.6037358936 |
| Unmoved six-square, original | 42 | 2.77809597187e-5 | 0.5995366615 |
| Unmoved six-square, original | 44 | 2.84558502551e-5 | 0.5912298891 |
| Unmoved six-square, original | 46 | 2.92991016922e-5 | 0.5830438535 |
| Unmoved six-square, contracted | 41 | 2.75492777936e-5 | 0.6061508573 |
| Unmoved six-square, contracted | 42 | 2.78367296403e-5 | 0.6019349812 |
| Unmoved six-square, contracted | 44 | 2.85226542202e-5 | 0.5935952826 |
| Unmoved six-square, contracted | 46 | 2.93784515671e-5 | 0.5853767969 |
| Reflected and routed seven-square, original | 44 | 3.08421856872e-5 | 0.5900544229 |
| Reflected and routed seven-square, original | 46 | 3.21066447042e-5 | 0.5818851073 |
| Reflected and routed seven-square, original | 48 | 3.35652820388e-5 | 0.5738344840 |
| Reflected and routed seven-square, original | 50 | 3.52447192158e-5 | 0.5659007854 |
| Reflected and routed seven-square, contracted | 44 | 3.09076644841e-5 | 0.5924151748 |
| Reflected and routed seven-square, contracted | 46 | 3.21844599174e-5 | 0.5842134746 |
| Reflected and routed seven-square, contracted | 48 | 3.36569582601e-5 | 0.5761309350 |
| Reflected and routed seven-square, contracted | 50 | 3.53517925909e-5 | 0.5681657813 |

The six-square diagnostic uses the actual END2 mask63 contract: A plusL, B zeroL, shortened C, and an ideal B-to-C pre-entangler. This does not assume that C can be prepared independently without that correlation. The seven-square diagnostic uses ideal A/C plusL and B zeroL followed by the physical full-square terminal.

Against the latest reported sampled board key 2.86759593420732e-5 (2026-10-27 16:23:30 UTC), the six-square original-source expectation at clock44 is approximately 2.20109e-7 lower as an arithmetic comparison; at clock46 it exceeds the sampled key. A sampled key and a true mean are different quantities, and this difference is not a statistical win prediction. The tested seven-square source/route/tail control exceeds it even at clock44. Conditional postselection means these allowances are arithmetic comparisons, not guaranteed limits on a redesigned resource.

## Scheduler validation

The native scheduler collapses an entirely idle barrier. The scripts therefore emit a noisy identity on one live data wire for every otherwise empty real wait tick; its p-depolarizing channel equals the idle channel it replaces. They assert every scheduled operation clock equals its declared clock. The perfect preparation occupies separately marked synthetic ticks; the existing exact intervention zeros their gate/reset/read channels and removes only those synthetic ticks from idle-channel durations. This preserves real pre-terminal waiting noise.

An initial unpadded seven-square run gave invalid delayed-clock results; these were discarded and replaced by the validated files in `seven_headroom_results.json` and `diagnostic/seven_*`. The no-gap clock44 result was unchanged by correction.

## Reproduction and source boundaries

Run `unmoved_six_headroom.py` and `seven_headroom.py` with `.venv/bin/python`, `PYTHONPATH=work/tools`, and OMP/OPENBLAS/MKL threads set to 1. Each script uses at most two worker processes. The result JSONs give the source, tail clock, exact expectation and acceptance; each `diagnostic/*.diagnostic.json` retains channel and artificial-idle intervention details.

The original/contracted source release contracts for unmoved mask63 are `unmoved_six_original.release.json` and `unmoved_six_contracted.release.json`. The actual noisy, raw-correct seven-square sources and their explicit native routes are under `tile_boundary/seven_source_*.qasm` with `seven_source_*.release.json`.
