# EVAL: exact perturbative score of a full submission circuit

Tool: `exact2.py <circuit.qasm> [--top 30] [--json sens.json] [--procs 16] [--p 1e-3] [--third]`
(reads `<circuit>.json` for data_qubits). Files: `model.py` (fault model), `engine.py` (exact state tables),
`exact2.py` (pairs, triples, CLI), `verify_pairs.py` (injects fault sets into the judge's own engine),
`mc.py` (judge MC at several p). Run with `.venv/bin/python`, no host needed (owl only ran the MC checks).

## Method (exact, no sampling)
1. The judge's own channels are enumerated from `tprep.noise.noise_blocks` (idle channel strengths
   0.75(1-(1-4p/3)^n) included) and split into Pauli components with their probabilities.
2. The circuit is put in the deferred-measurement form of `tprep.exact`: |Psi> = C R_k..R_1 |0>, 15 rotations
   exp(i theta P~_j), P~_j in the start frame. A Pauli fault F at time t equals an output Pauli times a sign flip
   of every later rotation whose axis anticommutes with F~ = C_t^-1 F C_t (T <-> T-dagger there). So each fault is
   a bit vector (s = flipped rotations, d = detector flips, e = flips of the 10 decode observables), and a fault
   set is the XOR of its members. This is why a plain DEM fails here and why faults before the T gates are handled.
3. For a class (s, d) the state phi_s lives in a 2^5 = 32-dimensional span (rank of the rotation X parts). The
   engine applies the detector projectors with the reference parities, then evaluates the 72 Pauli expectations that
   the judge's lookup correction needs (64-syndrome sum of its sign rule), giving the exact
   acceptance a(s,d) and, for all 1024 e at once, the accepted infidelity weight n = acc * infidelity.
   This is the quantity the judge averages over the engine's random measurement outcomes.
4. Assembly with independent channels (components of one channel exclusive), n_i = single, n_ij = pair:
   - first order  c1 p = sum_i p_i n_i  (0 for both circuits: every single fault is caught or harmless);
   - second order  sum_{cross-channel pairs} p_i p_j (n_ij - a_j n_i - a_i n_j): the acceptance normalisation is inside;
     for c1 = 0 this is sum p_i p_j n_ij, a ratio N/A so the first-order acceptance loss cancels;
   - `--third`: exact weight-3 term  sum_{triples} p_i p_j p_k n_ijk + sum_{pairs} n_ij p_i p_j (P_chan(i) + P_chan(j) - sum_k p_k a_k)
     (derived from the Moebius expansion of N/A; valid for c1 = 0);
   - acceptance: first order 1 - A1 and second order 1 - A1 + A2; exp(-A1) is reported too.
   All faults are grouped by (s,d); group pairs/triples are evaluated with vectorised member sums, parallel by fork.
5. Sensitivity JSON: per channel (QASM line, qubits, steps, idle/gate/flip) `dloss_dP` = d(1-F)/d(channel probability)
   and `loss_attribution` (pairs credited to both partners, so the column sums to 2x the loss).

## Checks against the judge's engine
`verify_pairs.py` injects chosen fault sets as deterministic Pauli errors (all other noise 0) into `tprep.check._sample`
(20000 shots) and compares (a, n) with the tables: 22 pairs (top pairs, random pairs, T-interacting ones with
a = 0.25, n = 0.125 / 0.5 / 1) and 6 triples on v12 agree within shot noise (max diff 0.005). Noiseless n = 0, a = 1.

## Validation (p = 1e-3 unless noted; MC = judge engine, 1e8 shots per seed)
| circuit | c1 | 2nd order | +3rd order (exact) | MC | residual (MC - exact3) |
|---|---|---|---|---|---|
| v12 | 5e-19 | 1.12195e-4 | 1.14313e-4 | 12-seed mean 1.1422e-4 (sem ~3.5e-7); seed 0 1.12689e-4 | -9e-8 = -0.08% (inside MC error) |
| st_L2_v0 | 3e-19 | 2.57027e-4 | 5.70281e-4 | 6.05e-4 (given), seed 0 6.227e-4 | +3.5e-5 = 6% (fourth order) |

Acceptance: v12 exp(-A1) = 0.69052 vs official 0.6905 (1st order 0.6297, 2nd 0.6982); st_L2_v0 exp(-A1) = 0.38303
vs 0.384 (1st order 0.040, 2nd 0.502; the plain series is useless at this acceptance, use exp(-A1)).

The v12 residual is third order because the series converges fast: 2nd order alone is 1.8% low, 3rd order closes it.
p-scans show the structure (MC seed 0 / exact up to 3rd order): v12 p=2e-3 4.672e-4 / 4.653e-4, p=3e-3 1.067e-3 / 1.065e-3.
st_L2_v0 (8-seed MC mean / exact 3rd): p=2e-4 1.277e-5 / 1.294e-5, 3e-4 3.238e-5 / 3.196e-5, 4e-4 6.335e-5 / 6.185e-5,
6e-4 1.674e-4 / 1.616e-4, 1e-3 6.05e-4 / 5.70e-4: the relative deficit grows ~ linearly in p (0, 1.3%, 2.4%, 3.5%, 5.7%),
as a fourth-order term does, and the second-order coefficient is confirmed by the low-p intercept (c2 = 257 exact).
st_L2_v0 is therefore ranked correctly only if a fourth-order bias of ~6% is acceptable; use it with the same acceptance only.

## Findings
- v12 1-F is entirely second order in pairs: idle 6.7e-5 + gate 3.9e-5 + flip 6.3e-6 (half/half split). Biggest single
  attribution: idle on data qubit 0 (QASM line 236, steps 39..41, dloss/dP = 8.6e-3), qubit 4 (line 245), and the
  1-step idle of qubits 8, 7, 3, 19, 15 at step 41 (the final wait for the last measurement). No pair is above 0.6%.
- st_L2_v0: pair loss is long data idles (steps 36..71) combined with a Z flip of a late measurement or another idle.

## Runtime
v12: model 0.4 s, pairs 1.6 s (16 procs, 2.2 s wall); with `--third` +25 to 32 s. st_L2_v0: pairs 2.6 s wall, `--third` +46 s.
Memory < 1 GB. The code is small because the T-gate rank is 5; if a circuit exceeds rank ~20 (`tprep.exact` limit) the
engine, like the judge's own check, refuses.
