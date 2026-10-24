# Reusable detector-basis evaluator

`evaluate_basis.py` reads the existing sparse evaluator and an existing candidate. It does not modify either one. Its saved row-XOR proposal changes only the internal detector coordinates used for contraction; it cannot lower the physical circuit's loss.

## Run

From a checkout with the current sparse evaluator and its dependencies installed:

```bash
python /path/to/evaluate_basis.py \
  --evaluator-dir /path/to/quantumn/work/lanes/MAIN/sparse \
  --stem /path/to/quantumn/work/lanes/MAIN/v36c \
  --output /path/to/result.json \
  --processes 4
```

Keep `basis_width_probe.json` beside the CLI, or specify `--certificate /path/to/basis_width_probe.json`. `--stem` also accepts a `.qasm` or `.json` suffix. Four workers use the existing evaluator's POSIX `fork` mechanism; use `--processes 1` on a platform without `fork`.

There is no repeated 1,500-proposal basis search. The CLI prepares the current model, checks and applies the saved 32-XOR proposal, and evaluates all 73 moments. It compares original and proposed min-fill `(work_entries, width)` costs and selects the original basis if the saved proposal does not improve that cost tuple. This is a cost proxy, not a wall-time promise.

## Reuse on nearby candidates

The proposal is checked after the evaluator's own canonicalization. Every source and target row must be an identity projector with zero reference; active kernel rows must remain fixed. The complete transformation must have full GF(2) rank. If a nearby circuit lacks one of the referenced rows or changes its semantic role, the CLI falls back to the original basis and records why. Malformed certificate operations raise an error. The evaluator's own input restrictions remain in force.

All independent channel probabilities, observable definitions, kernel states, and kernel weights are retained. Only detector fault-signature coordinates and the elimination order change. Reuse therefore requires the checks above, rather than an exact source hash match; the current input and certificate hashes are recorded for every run.

## Output

The JSON includes the 73 individual moment values, acceptance, conditional loss, sparse-kernel omission bound, largest bucket, selected width/work, original and proposed plans, full-rank transformation certificate, input/evaluator/certificate SHA256 hashes, planning time, contraction time and total time. The omission bound excludes floating-point roundoff, as in the original evaluator.

## One validation on the exact pinned v36c bytes

`portable_eval.json` was produced with the exact source QASM SHA256 `49ea05888f6f56f87eee49665f8275e3f0c30e199c67db7958f5318cc07bd3f8`, not the extra-newline input used in the earlier ABBA benchmark.

It selected the saved basis, reduced width 11 to 9 and work proxy 5,636 to 1,911, with peak bucket 1,174,528 entries. Planning took 0.592 s, contraction 8.491 s, and total 9.084 s on this run. These are observations on the current host.

The separate `portable_eval_validation.json` compares all 73 moments with the root reviewer's baseline result at tolerance 1e-12. It records the actual maximum difference, acceptance/loss differences, both receipt hashes, and PASS. The earlier `basis_validate.json` ABBA timing receipt is preserved separately.
