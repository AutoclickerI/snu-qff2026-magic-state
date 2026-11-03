# Verified native phase improvement

The selected full native circuit is `native_incumbent_phase_late.qasm` with output specification `native_incumbent_phase_late.json`. It adds **Sdg on q5 at tick39 and S on q12 at tick45** to the literal MAIN/v37j circuit. Both pulses occupy existing idle slots. Every original quantum operation, measurement record, and all71 declared detector rows are retained. Every gate and waiting interval uses the original noisy judge model.

**This is a working improvement, not a SOTA result.** The latest checked public leader has sampled loss3.0423837010265e-5; this release's official draw does not beat it.

| Metric | MAIN/v37j | Selected circuit |
|---|---:|---:|
| Exact loss at p=.001 | 3.5870950034704206e-5 | **3.568127239134716e-05** |
| Exact acceptance | .5010179047299785 | **.501016046737387** |
| CX / native ticks / T gates | 412 /49 /15 | **412 /49 /15** |
| Full harmful single-fault coefficient |0|**0**|
| Second-order coefficient |31.7222222222|**31.5488888889**|

The relative exact improvement is **0.528778%**. The official100-million-shot receipt reports loss **3.519834672545982e-5**, SEM **7.2e-7**, acceptance **.50101785**, `gates_ok=True`, and `passed=True`. Sampling fluctuation explains the difference from the deterministic expected loss. The receipt is `official_late_100m.txt`; machine-readable metrics are in `official_late_result.json`.

Ordered output qubits: `[6,20,19,10,2,22,16]`.

QASM SHA256: `bcd6a3fdb6133c5b687993fb10c57c002e13f3e873f05981c48100ba10065b08`.

## Reproduce

From the repository root, with the repository's runtime and pinned judge/qtools:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  .venv/bin/python work/lanes/EXPAND2_20261027/reproduce_phase_working.py --late --price

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  .venv/bin/python work/fast_check.py \
  work/lanes/EXPAND2_20261027/release_phase/native_incumbent_phase_late.qasm \
  work/lanes/EXPAND2_20261027/release_phase/native_incumbent_phase_late.json 100000000 2
```

The reproducer reconstructs the candidate byte-for-byte from MAIN/v37j, verifies both hashes and free pulse slots, checks raw correctness before ideal decoding, and audits every single-Pauli component. Optional `--price` uses the independently checked lane-local S/Sdg/SX/SXdg frontend with the unchanged pinned all-orders contraction. It does not modify the official judge or shared evaluator.

Baseline SHA256: `ac2d9dfbfb4967baacf85a25f2a1eaac35dd7039abe2069dc858cd5a5f4ca5cd`.
Judge: `76fe47c0324f1c1f8b72a7d55af200e88043b522`.
qtools: `94d0bfed2b6ff678c667dd24a5e57a249e01da0febc72bec4adf0d987fb9c83f`.

## Same-clock control and search evidence

`native_incumbent_phase.qasm` uses S12 at39 instead of45. Its exact loss is3.568237324665328e-5 at A=.501016048187977; its separate official100M run passed with loss3.570043484655553e-5, SEM7.26e-7, and A=.50097429. Its reproduction and official receipts are retained under the original filenames. The late placement improves expectation by only1.1008553061e-9 beyond that control.

The phase-pair search checked136 distinct-clock, repeated-parity S/Sdg choices with both signs. All136 pass full raw and single-fault checks. Four pair-order ties received all-orders prices. The complete ledgers, generators, and selected source metadata are retained in the parent EXPAND2 lane. The selected circuit is not substituted into the production racer and has not been submitted from this research lane.
