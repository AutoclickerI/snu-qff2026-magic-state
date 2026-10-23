# SNU QFF2026 judge audit

I read `problem.md` in full and audited `tprep/noise.py`, `qasm.py`, `check.py`, and `parse.py`. I also read `exact.py` and `grid.py` where the four requested files call them. The labels below separate **proved** statements, **computed** results, and **conjectures**.

## Result

The tightest lower bound I can prove for every valid submission is

\[
\boxed{1-F\ge 0}.
\]

I cannot prove a strictly positive circuit-independent bound from this judge. The best exact-judge run I constructed is an upper bound on the optimum:

* `1-F = 0.0174734 ± 0.000036` at `p=10^-3`, 10,000,000 shots, seed 0;
* acceptance `1.0000`, correctness and class checks PASS;
* 22 CNOTs, 34 QASM statements, 4 reset operations;
* data qubits `[0, 2, 1, 13, 7, 12, 6]`.

The circuit is [low_0_reset_h.qasm](./low_0_reset_h.qasm), with the full 10-million-shot output in [best_10m.out](./best_10m.out). Thus the evidence-backed interval is `0 <= OPT <= 0.0174734` (the right endpoint is a Monte Carlo estimate, not a certified maximum or minimum).

### Proof of the lower bound

The exact checker defines fidelity using the target projector and divides by accepted probability (`tprep/exact.py:16-21`, `:256-267`). For every physical density operator, a projector expectation satisfies `0 <= F <= 1`; ideal Pauli-frame and syndrome corrections are unitary/lookup corrections and cannot change that. The sampled score is computed as `(1 - expectation)/2` (`tprep/check.py:297-306`) and the accumulated mean is explicitly clamped at zero (`tprep/check.py:307-310`). Therefore no accepted submission can score below zero.

This is the strongest bound I can prove without assuming a particular circuit architecture. A positive bound would require proving that every allowed finite circuit has an accepted harmful fault of some minimum probability. The source imposes syntax, resource, and acceptance constraints, but supplies no such theorem. In particular, postselection and measurement-derived frames are part of the accepted interface (`problem.md:248-259`, `:274-307`), so a `p/3` argument based on one bare T-gate fault is not architecture-independent. I therefore report zero as the proven bound, and the tested circuit above as the best construction I found.

## What the judge actually does

**Parsing and admissibility.** The submission must be OpenQASM 2.0, one quantum register, and at most 200,000 bytes/5,000 statements (`tprep/qasm.py:154-176`; limits are also stated in `problem.md:367-370`). `check_stim` requires exactly seven distinct in-range `data_qubits` (`tprep/check.py:121-130`). Under the official `STANDARD` model, `qasm.convert` rejects operations outside `noise.gates` and non-neighbour CNOTs (`tprep/qasm.py:187-195`); the standard gate set is declared in `tprep/noise.py:31-32`. Format, xtim class, exact noiseless correctness, then noisy acceptance are checked in that order (`tprep/check.py:151-205`).

**Noise insertion and timing.** `STANDARD` has one-qubit and two-qubit depolarization, reset, measurement flip, post-measurement depolarization, first-use preparation noise, native X-basis operations, and one idle depolarization per waiting step (`tprep/noise.py:14-25`, `:31-35`). `noise_blocks` inserts first-use `X_ERROR`, measurement flip/after-noise, reset noise, gate noise, and repeated idle channels (`tprep/noise.py:91-123`). The scheduler runs operations in written order at the earliest free time, records gaps between operations and to the end, and treats a reset as a new preparation (`tprep/noise.py:54-88`).

The QASM converter folds `h; measure` into native `MX` and `reset; h` into native `RX` (`tprep/qasm.py:102-146`, applied at `:203-205`). The official model has `native_x=True`, so the folded H itself has no separate H noise; the measurement/reset noise remains. This is the most useful real optimization I found.

**Acceptance and final score.** `DETECTOR`/`POSTSELECT` records are converted to absolute measurement records and validated (`tprep/qasm.py:211-242`, `tprep/parse.py:100-121`). Exact verification requires an accepted noiseless output in the code space with the declared or discovered logical frame (`tprep/check.py:167-187`; `tprep/exact.py:230-267`). A detector that is deterministic only after POSTSELECT is converted into an additional POSTSELECT, rather than bypassing acceptance (`tprep/check.py:208-221`). The noisy run keeps shots with all detector bits zero and all POSTSELECT parities equal to their requested values (`tprep/check.py:273-296`); the checker then requires sampled acceptance at least 0.5 (`tprep/check.py:54-59`, `problem.md:257-259`).

The judge appends six noiseless `MPP` checks after participant noise has already been inserted (`tprep/check.py:18-21`, `:189-203`). It uses those syndromes as a lookup-table correction: a single-qubit X/Y/Z error is corrected, while multi-qubit errors are not generally corrected (`tprep/check.py:273-302`; the problem states the same distinction at `problem.md:317-338`). The frame only flips the signs used in the logical X/Y expectations (`tprep/check.py:253-264`, `:297-302`); it cannot reject a shot or apply an arbitrary state correction.

## Detours and loopholes tested

### 1. Native `reset; h` preparation — **works as an optimization**

Replacing a first-use `h q[i]` with `reset q[i]; h q[i]` makes the converter emit one native `RX` (`tprep/qasm.py:134-146`, `:203-205`). It replaces first-use X preparation noise plus a noisy H with reset preparation noise and no separate H channel. It does not remove reset noise, T/CNOT noise, or idle noise. On the best 22-CNOT circuit, the code-computed score changed from `0.0182215 ± 0.00012` (1,000,000 shots) to `0.017667 ± 0.00012`; at 10,000,000 shots the reset-H circuit gave `0.0174734 ± 0.000036`.

This is a genuine judge-specific improvement, but it remains nonnegative and therefore does not beat the proven bound.

### 2. Random POSTSELECT and FRAME tricks — **interface works; no useful loophole**

The measured-T probe gives a noiselessly random branch. With the frame declared, acceptance was `1.0` and the score was `0.0282850`; POSTSELECTing the high-probability branch `m=0` gave acceptance `0.85059` and score `0.0254147`; POSTSELECTing the low-probability `m=1` branch gave acceptance `0.14941` and failed the 0.5 floor. These are code-computed from [loopholes.py](./loopholes.py) and [loopholes.out](./loopholes.out).

The reason is explicit in the source: POSTSELECT is applied before scoring, but noisy acceptance must still pass the floor (`tprep/check.py:273-296`; `problem.md:248-259`). FRAME declarations are required in pairs and refer only to existing absolute records (`tprep/parse.py:100-121`, `tprep/check.py:140-149`); they only change the logical expectation signs (`tprep/check.py:255-302`). They cannot turn an incorrect noiseless state into a correct one.

### 3. DETECTOR abuse / conditional detectors — **fails as a bypass**

Noiselessly random detector parities are rejected by exact verification unless they are conditioned on POSTSELECT; conditional detectors are then appended as POSTSELECT conditions (`tprep/exact.py:230-246`, `tprep/check.py:208-221`). A measured-T test at `p=0.01` changed from acceptance `0.81375`, score `0.280817` to acceptance `0.77523`, score `0.268488` after adding a second-readout detector. It catches some faults, but its own noisy measurement and gates cost more than it saves in this small circuit. It cannot make acceptance or score checks disappear.

### 4. Barriers and idle-time scheduling — **fails as a free timing loophole**

QASM barriers are preserved as barrier annotations on the next Stim instruction (`tprep/qasm.py:178-186`, `:245-253`), and the scheduler delays the barrier's qubits (`tprep/noise.py:69-82`). In a direct probe, without a barrier the idle channels included one `DEPOLARIZE1(0.0009999999999999731) 2`; with `barrier q[1],q[2]`, the reset was delayed and the inserted channels became `DEPOLARIZE1(0.001998666666666621) 0` and `DEPOLARIZE1(0.0009999999999999731) 1`. The barrier can prevent a fresh qubit from waiting before reset, but it creates waits on the barrier group and never disables standard idle noise. The complete output is in `loopholes.out`.

### 5. Supplying noise operations or unsupported gates — **fails at format/conversion**

Participant noise instructions are parsed as invalid QASM; `swap` and `ch` are rejected under the official standard gate set (`tprep/qasm.py:187-195`; `tprep/noise.py:31-32`). The executable probes report the corresponding parse/operation errors in `loopholes.out`. There is no accepted path to inject a noiseless channel or a non-neighbour operation through comments or an alternate gate name.

### 6. “The final ideal correction fixes everything” — **fails for weight two**

Using the judge's own sampler and final tail, a single output `X` fault scored `0`; two output `X` faults scored `0.5`; two output `Z` faults scored `1.0`. These are direct runs of `_sample` in `loopholes.py`. This matches the implementation's `z_fix`/`x_fix` lookup (`tprep/check.py:297-302`) and the problem's statement that multi-qubit faults can remain after ideal correction (`problem.md:317-338`).

### 7. 15-to-1 Reed–Muller distillation — **valid but loses under this judge**

I implemented the five-row 15-to-1 triorthogonal circuit, routed it on the 6x6 grid, and used its four X checks as detectors before the same Steane encoder. The circuit passes exactly at `p=0`, but at `p=10^-3` it scored `0.071985 ± 0.00084` with acceptance `0.7536` and 137 CNOTs (100,000 shots, seed 0; [distill_encode.qasm](./distill_encode.qasm), [distill_run.out](./distill_run.out)). The asymptotic `O(p^3)` input-state argument assumes clean Clifford rotations; here every CNOT, idle, preparation, and measurement location is noisy (`tprep/noise.py:91-123`), so the many routed locations dominate. It is not a lower-scoring construction for this exact hardware/noise model.

### 8. Measurement/reset and statement-limit accounting — **no loophole found**

The converter counts native M/R operations after X-basis folding and rejects more than 1,000 (`tprep/qasm.py:203-208`); statements and bytes are checked before conversion (`tprep/qasm.py:159-164`). The best circuit uses 34 statements, 4 resets, and 22 CNOTs, so it is far from all three limits. Repeated measurements of one classical bit do not expose old records: declarations resolve each named bit to its last write (`tprep/qasm.py:91-99`, `tprep/parse.py:100-121`).

## Best construction details

The best circuit was found by synthesizing the required 7-bit linear encoding with a low-CNOT invertible extension, routing it with Qiskit on the 6x6 coupling map, then inserting `reset; h` for each first-use H. It prepares the target exactly at `p=0` and uses no detectors or POSTSELECT, so acceptance is exactly 1 in the noisy sample. The exact checker and 10-million-shot result are reproduced by:

```bash
/home/jihoon/competitions/quantumn/.venv/bin/python - <<'PY'
import sys
sys.path.insert(0, '/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
from pathlib import Path
import tprep
c = Path('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/low_0_reset_h.qasm').read_text()
d = [0, 2, 1, 13, 7, 12, 6]
print(tprep.check(c, d, p=1e-3, shots=10_000_000, seed=0))
PY
```

The first-order fault scan reports `385 single faults, c1 ~ 17.57`, estimated from 256 shots per fault ([best_fault.out](./best_fault.out)); this explains why adding a large noisy verification or distillation circuit was counterproductive. The construction's remaining score is dominated by accepted single-location faults and idle channels, rather than an acceptance loophole.

## What remains unproved

**Conjecture:** the exact finite-resource optimum is strictly positive because every finite Clifford+T circuit has nonzero full-support Pauli fault paths, and a finite error-detection circuit cannot reject every logical Pauli path while retaining acceptance at least 0.5. I did not turn that into a circuit-independent quantitative theorem: the minimum undetectable fault weight depends on the complete circuit and its measurement/frame relations. It would be incorrect to present `p/3`, `35p^3`, or any other positive number as a universal lower bound for this judge.

