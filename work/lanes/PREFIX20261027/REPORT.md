# Native rank-five prefix experiment — 27 October 2026

## Verdict

**A substantial new native circuit was implemented and tested, but it does not improve the incumbent.**
The best circuit in this experiment has 134 CX, 15 T/T-dagger gates and 31 native ticks. Its exact expected
loss is **8.489600747077256e-5** at acceptance **0.6890119163514336**. It passes the organizer's format,
simulator-class, raw-correctness and acceptance checks. Its expected loss is about **2.37 times v37j's
3.58709500347e-5**, so it is an experimental design, not a finalist or a SOTA claim.

Canonical artifact: `cand/final_phase_random_1.qasm`, with ordered outputs in its `.json` file.
QASM SHA-256: `eb4b06c9233a9c1095a83fcb05909a62f4785a376c65b41475e183edc2dee6ee`.

## What changed

This experiment implements the proposed freedom to choose the encoder, phase network and initial basis
jointly. It does not retain the old encoder or require restoration to the old intermediate wires after
each parity computation.

The source occupies nine native cells, `[1,2,3,7,8,9,14,15,16]`. Seven cells hold the Steane data, one holds
an X-measured flag, and one is a measured-zero helper. The final data order on these cells is
`[1,14,8,9,2,16,15]`. Four Steane code coordinates and the extra flag give a five-dimensional binary space.
The logical phase coordinate is the mask `8`.

For a binary functional `w` with `w·8 = 1`, let S be the 15 non-logical vectors in the affine hyperplane
`w·a = 1`. For every five-bit computational value z,

`-sum(a·z for a in S) = 8·k + (8·z)`

where each dot product is reduced modulo two and k is an integer. Applying T-dagger to these 15 parity
forms therefore implements logical T exactly on the encoded support. It leaves the extra flag in its
known ideal state. `reproduce.py` verifies this identity over all 32 inputs using integers.

The synthesizer starts at the desired data/flag coordinates and works backwards. It searches native CX
operations until all 15 phase forms have appeared and only five independent nonzero rows remain.
Those remaining rows define an arbitrary valid product preparation: five plus states and four zero
states. This removes the requirement to synthesize a particular encoder first. The best source combines
encoding and the 15 rotations in **22 CX**. The whole circuit adds 14 transfer CX and the preserved
98-CX terminal/resource circuit from the existing T14 experiment, for 134 CX total.

Every CX is a nearest-neighbor operation on the 6×6 grid. Resource preparation and the transfer operations
are physically present and noisy. No ideal-resource substitution is used in the reported full scores.

## Fault-aware search and measured results

The first search excluded any intermediate one-site Z error or CX-supported ZZ error that directly equals
the logical phase axis. That condition is useful but insufficient: some X/Y faults change the signs of
later non-Clifford rotations and create accepted logical error. Full single-fault signatures and exact
all-orders prices were therefore evaluated separately.

The next search penalized exposure of unflagged even-parity rows and required safe initial seed rows.
It also tried different placements of a T-dagger along intervals where its parity was unchanged. Initial
preparations were moved immediately before first use, and the unchanged suffix was moved earlier whenever
cell lifetimes allowed. These schedule repairs are included in the final result.

| Tested construction | CX | Exact expected loss | Acceptance | Harmful single faults |
|---|---:|---:|---:|---:|
| First valid free-basis network, `legacy_8_0` | 133 | 3.8693751856400284e-4 | 0.6160610032165443 | 3 |
| Alternative rank-five affine support, `network_f24_s0_first0` | 134 | 1.7832756167537569e-4 | 0.6275011016274032 | 0 |
| Same network, 28 deterministic transient checks | 134 | 1.4116219169170465e-4 | 0.6100733813512701 | 0 |
| Exposure-weighted network, with transient checks | 134 | 1.0467048187797541e-4 | 0.6312589143771541 | 0 |
| Exposure-weighted network, compact schedule | 134 | 9.280427827549576e-5 | 0.6876459084744778 | 0 |
| Final phase-placement repair | 134 | **8.489600747077256e-5** | **0.6890119163514336** | **0** |

The main experiment tables contain 122 phase-placement screens on the first network, 56 candidate variants
from 28 synthesized networks, 32 exposure-weighted variants, ten post-phase syndrome-check variants and
26 final phase-placement variants. Four additional network attempts exhausted their synthesis depth
budget without a witness. These are bounded experiments; they do not exclude the whole family.

The scripts' `c1` field is the first-order accepted-loss contribution evaluated at p=0.001, not the
coefficient after division by p. A zero value means no harmful single-fault outcome was found by the exact
fault-signature calculation. It does not imply small second-order or all-orders loss.

## What failed, and what the failure means

The most compact phase networks retain the fifth coordinate and have exact noiseless correctness, yet
some versions have harmful X/Y single faults. The first valid full network had three such fault locations.
The parent lane independently checked every existing deterministic record parity and found none missing;
changing only its detector equations could not remove those faults.

Other synthesized networks have no harmful single faults but still lose badly at p=0.001. Prefix faults
and their combinations with later faults are the obstruction in these tested circuits. The parent lane's
noise-cut diagnosis of `network_f24_s0_first0` found approximately 9.03e-5 with only early source channels
noisy and 3.50e-5 with only the later source channels noisy. These counterfactuals are not additive error
budgets. The full score was 1.78e-4.

Deterministic measurements on transient plus/zero qubits reduced the loss of one network substantially,
but much of that effect disappeared when its preparations were placed just before first use. Small native
post-phase X- or Z-syndrome projectors added waiting and new fault locations. None of the ten tested
projector recipes improved the full circuit; some introduced harmful singles. Those failures concern
these exact projectors and schedules, not every possible verification architecture.

The result establishes a useful distinction: **retaining rank five and synthesizing a short native
parity network does not preserve the original cultivation circuit's noise suppression.** The original
fault propagation and verification must be redesigned along with the phase polynomial. A smaller CX
count by itself is not evidence of better expected fidelity.

## Validation and reproduction

`best_validate.json` records the organizer's one-million-shot seed-zero check:

- format, class, raw correctness and acceptance: passed;
- judge time: 2.17 seconds on this worker with one process;
- sampled loss: 1.0098691093390362e-4;
- sampled acceptance: 0.688208.

The sampled loss is not the selection metric; the all-orders expected value is reported above.
A 100-million-shot run is not warranted for a candidate that is clearly inferior in exact expectation.

Run from the repository root:

```bash
PYTHONPATH=work/tools:upstream/snu-qff2026-problem .venv/bin/python \
  work/lanes/PREFIX20261027/reproduce.py
```

This verifies the phase identity, the five-dimensional product endpoint, every phase location, native
adjacency, byte-identical reconstruction of the canonical QASM and a fresh all-orders evaluation.
The recorded exact expected result is reproduced in `reproduction.json`. The final stem is fully
specified by its QASM and ordered `data_qubits`; no random search is needed to reproduce it.

Required repository inputs are `work/lanes/T14/qcirc.py`, `t14a.qasm`, and `t14a.stage.json`, plus the shared
`work/tools/qtools` package and its pinned judge dependencies. `selected_files.json` lists the code,
selected controls and evidence needed for handoff, with byte hashes.

An initial attempt to split v37j into preparation components was rejected by the raw checker because its
continuous guards join data and resource components. That splitter was removed. The current generator
uses the fully preserved, checked 98-CX suffix from the T14 artifact and asserts its gate count.
