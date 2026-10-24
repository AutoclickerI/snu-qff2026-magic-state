# XTIM

Status: **complete**. The predictor is implemented and validated. The q8 reuse rewrite reproduces the physics gain but remains on the slow path, so no <=20 s/1e6 q8 unlock was found.

## Trigger rule and evidence

The measured rule for the blue-v23/BCSYN2 family is:

> A B+C initialization that leaves q19 in a random X-basis measurement state (`h; measure; h`, or native `MX`) and reuses that live state through the suffix selects xtim's expensive per-shot path. Replacing that initialization with `reset; h` removes the path. A generic `MX` count, detector count, or moving the same q19 read across one T gate is not sufficient to predict it.

The sampler-only probe applies the judge's `STANDARD` noise at p=1e-3, appends the judge tail, compiles `engine="exact"`, and times 100,000 shots. Results are recorded in `probe_timings.json`:

| circuit | seconds / 1e6 | measurements | detectors |
|---|---:|---:|---:|
| v22h_c2c9 | 3.10 | 60 | 43 |
| v23h_c2c9 | 7.46 | 66 | 43 |
| v24 | **127.97** | 68 | 45 |
| v25k | 5.20 | 76 | 54 |
| safe_best | 6.85 | 82 | 60 |
| q8 reuse (reconstructed) | **124.88** | 76 | 54 |
| v24 with q19 read moved before T_DAG q8 | **120.16** | 68 | 45 |
| v24 with q19 reset+H | 3.84 | 67 | 45 |

These are lines 2–66 of `probe_timings.json`. The q19 relocation remaining slow rules out “the read is after this particular T” as the complete rule. The reset probe changes the state initialization and removes the c50 record in this intentionally non-physics timing control; the physics-preserving q19 reset is the KNAP construction below.

The six B+C MX sites were screened independently. The 10,000-shot judge timing in `work/lanes/KNAP/runtime_profile.jsonl` is 1.643 s for the blue base (line 1), 1.602 s after resetting q26 (line 3), 1.620 s after q12 (line 4), **0.329 s after q19** (line 5), 1.595 s after q17 (line 6), 1.586 s after q5 (line 7), 1.630 s after q4 (line 8), and 0.171 s after resetting all six (line 9). Thus q19 is the necessary repair in this tested family; the other five sites are not individually sufficient.

Small controls do not reproduce the effect: Bell/MX/T and Bell/MX/T_DAG circuits remain 0.041–0.068 s/1e6, including MX-before versus MX-after variants (`minimal_controls.txt:1-10`). The large path therefore needs the surrounding B+C state/Clifford cone; it is not caused by a single random read or a T gate in isolation.

The Python wrapper confirms which work is being measured. `compile_detector_sampler(engine="exact")` selects the legacy exact sampler (`xtim/circuit.py:510-535`), and `_program.sample` is called after compilation with the requested record channels (`xtim/circuit.py:845-851`, `900-930`). The judge inserts gate, measurement, reset, and idle noise around the circuit (`tprep/noise.py:54-88`, `91-128`) and samples the noisy body plus the final tail (`tprep/check.py:189-203`, `273-290`). The exposed compiled API and binary option strings probed here are listed in `api_probe.txt:1-10`; `QEC_FRAMED_MEMO=0` and `QEC_FORCE_FALLBACK=1` timing results are `probe_timings.json:68-87`. Those switches change diagnostic engines globally, so they are not candidate rewrites.

Operational design rule: treat a measured X-basis state as live random frame data until it is reset or consumed. Do not carry a reused `MX` state from the B+C preparation into a late suffix containing the blue check and non-Clifford cone without probing it. For SEPBC teleports, fold the random result into detector parity and reset the measured qubit before any later state use. For prefix moves, run the predictor after every move because the surrounding cone, rather than raw MX count, determines the branch.

## Predictor

`speed_predict.py` accepts a stem with or without `.qasm`:

```text
.venv/bin/python work/lanes/XTIM/speed_predict.py work/lanes/MAIN/v25k
```

It converts the submission, applies `STANDARD` noise, appends the judge tail, compiles the exact sampler once, warms it with 64 shots, then times two 50,000-shot batches. It reports the median seconds per 1e6 and marks `SLOW` at the repository's 20 s/1e6 gate (`speed_predict.py:69-110`, `115-125`). Reference-cache writes are confined to `work/lanes/XTIM/.xtim_cache` (`speed_predict.py:28-35`).

Validation used 50,000 shots. The complete outputs are in `predictor_validation.jsonl`:

| stem | predictor s/1e6 | class | measured probe s/1e6 |
|---|---:|---|---:|
| v22h_c2c9 | 3.46 | FAST | 3.10 |
| v23h_c2c9 | 9.24 | FAST | 7.46 |
| v24 | 130.32 | SLOW | 127.97 |
| v25k | 7.47 | FAST | 5.20 |
| safe_best | 10.42 | FAST | 6.85 |
| q8 reuse | 134.70 | SLOW | 124.88 |

The predictor separates every named fast/slow circuit at the 20 s gate. Its static fields (T count, MX count, detector count, and MX positions) are diagnostic only; the classification is from the short exact noisy run.

## Rewrites and physics cost

- **q19 reset+H:** the physics-preserving KNAP rewrite. On the blue base, exact third-order 1-F changes by `+1.213084e-7` and the circuit runs about 3.0 s/1e6; see `work/lanes/KNAP/REPORT.md:21-30`. The retained q19-reset/timing/check circuit is exact `6.505010288e-5`, exp(-A1) `0.510621553`, and 3.65 s/1e6 (`REPORT.md:11-15`, `29-30`).
- **q8 MX reuse:** reconstructed as `q8_reuse_v25k.qasm`, with exact2 `c1=2.66e-19`, second `5.030297889845e-5`, third `1.400022914044e-5`, total `6.430320803889e-5`, and exp(-A1) `0.516890439` (`q8_reuse_v25k.moments.json:1-13`). The 10,000-shot judge check passes (`q8_judge_10k.txt:1-2`), but the exact sampler is 124.88 s/1e6 (`probe_timings.json:43-49`), so this is not an unlock. LNS2 independently reports the analogous safe_best q8 gain `-7.468948e-7` with speed `>100` s/1e6 (`work/lanes/LNS2/REPORT.md:18-28`).
- No measured rewrite that preserves the q8 gain and reaches <=20 s/1e6 was found. Moving q19 alone does not fix the path (`probe_timings.json:51-57`).

## Verified versus inferred

Verified: the noisy timings and subset timings cited above; exact API signatures and wrapper control flow; predictor separation on v22h_c2c9, v23h_c2c9, v24, v25k, safe_best, and q8 reuse; q8 reconstructed QASM format/judge check at 10,000 shots; q8 exact2 c1/second/third; and q19 reset's exact and speed receipts from KNAP. No installed package or tprep file was modified.

Inferred: xtim's expensive path is per-shot framed-plan branching/materialization around the reused random-MX state. The inference is supported by the q19 subset and q8 reuse timing, and by the compiled binary's `QEC_FRAMED_MEMO`, `QEC_FORCE_FALLBACK`, and `twirl_records` diagnostics, but the C++ source is not present. No global theorem about every circuit or every measured qubit is claimed.
