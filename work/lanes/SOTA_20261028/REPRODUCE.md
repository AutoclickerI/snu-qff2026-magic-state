# Reproduce the SOTA research checkpoint

Run from the quantumn repository root, using the project's pinned environment. The selected QASM and receipts are the record of the measured results; time-bounded solver reruns may return a different feasible circuit. No command below submits a circuit or starts the hourly race.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=work/tools
```

## Best complete native circuit

The two parent QASM/spec pairs are selected in the publication manifests. Rebuild and run its phase-aware exact evaluator:

```bash
.venv/bin/python work/lanes/SOTA_20261028/combine_native.py
```

The resulting stem is

```
work/lanes/SOTA_20261028/native_best/schedule_heralds_c167977fdd48de1f_d6_20_19_10_2_22_16
```

`combine_native.py` uses the already-pinned lane-local phase frontend in `EXPAND2_20261027/frontend_axis.py` and `axis_echo.py`, plus the shared contraction. The frontend SHA-256 is in the exact receipt. Do not silently parse the phase operations with a narrower frontend. The ordinary official judge accepts the native QASM directly.

The complete `schedule/results.json` ledger contains all 40 schedule proposals and their scopes, raw correctness, exact loss and acceptance. The selected parent retains clock0–25 operations; the detector/herald parent supplies later operations and final detector rows. `native_schedule.py --help` describes how to rerun that bounded proposal generator.

The saved `native_best/official_1m.log` is a one-million-shot validation receipt, not a 100-million-shot official score. Its favorable sampled loss must not replace the exact mean.

## Native geometry and measured-helper controls

`connected_geometry.py` and `tile_geometry.py` generate scoped native geometry models. `a_geometry.py` constructs and checks native A preparations; `measured_css.py` constructs joint resources with freely measured helper rows. Neither a graph witness nor a CSS-state witness is a complete magic-state preparation.

`assemble_geometry.py` combines an actual source boundary and actual native resource module, retains measurement outcomes, derives the full deterministic record contract, checks raw Steane output and evaluates all physical noise. The saved seven-square control is reproduced by:

```bash
.venv/bin/python work/lanes/SOTA_20261028/assemble_geometry.py \
  work/lanes/SOTA_SOURCE_20261028/tile_boundary/seven_source_original_reuse.release.json \
  - \
  work/lanes/SOTA_20261028/joint_modules/seven_constructive_0.json \
  --name seven_measured_baseline
```

Its raw correctness is real, but its 0.2198 acceptance is inadmissible. The six-square control and direct parity-read construction are in the resource lane's manifest and report. They are negative results, not candidates for submission.

## Other methods and counterfactuals

The source lane's [REPRODUCE.md](../SOTA_SOURCE_20261028/REPRODUCE.md) gives commands for the native routed boundaries, headroom diagnostics, gauging frame calculation, corrected live-output Gao circuits and full-noise teleportation probe.

The detection lane's [PROVENANCE.md](../SOTA_DETECT_20261028/PROVENANCE.md) pins the external CSS compiler and research algorithms. Its report distinguishes the complete abstract seven-cat/ULO circuits, the complete native output-role control and ideal-resource terminal experiments. The selected scripts encode the 14-CX instrument independently; downloaded unlicensed upstream source is not bundled.

`fetch_board.py` reads only the public leaderboard. The saved `leaderboard_latest.json` and final `leaderboard_final.json` have their retrieval times and public source URL; no team credential or submission endpoint is involved. A subsequent refresh may return different rankings.

## Integrity

`publish_manifest.json` lists this lane's selected files with SHA-256 and byte counts. `checkpoint_manifest.json` combines those files with the three lane manifests and their selected artifacts. The latter is the upload inventory, not a claim that every generated proposal was published. Full result ledgers and selected witnesses are retained; external environments and caches are excluded.

The main branch advanced while this research was running. The proposed publication tree incorporates the newer main snapshot, including the owner's race-stop record. Publication is blocked by automatic approval review; no new commit or branch update was made. See `PUBLICATION.md`. Nothing in these reproduction instructions reauthorizes the stopped race.
