# Measurement-based flagged preparation

This candidate uses the measurement route rather than direct magic-state injection. The first stage encodes four `H` inputs through the Steane linear encoder from the problem statement, yielding `|+_L>` on the seven logical data wires before any T gates. The code wires are tracked through routing and are submitted in code order as `[7, 8, 14, 26, 20, 13, 16]`.

For each of two logical measurements, a flag ancilla is prepared in `|+>`, coupled to the syndrome ancilla before and after the seven data interactions, and then measured. The syndrome ancilla is measured twice. The sequence is the nearest-neighbour routed realization of measuring the logical operator `(X-Y)/sqrt(2)`: per data wire it uses `T; H` before the data-CNOT fan-in and `H; Tdg` afterwards. The two logical readout records are compared by a detector; the first readout parity is used as `FRAME_Z`, so the random `-1` result is retained rather than postselected.

The grid placement starts the seven logical wires at physical sites 7, 8, 9, 13, 14, 15, 16. Qiskit Sabre routing is run sequentially over the encoder and the two flagged measurement blocks, preserving the evolving physical placement. The final data locations above are the locations after the complete circuit. The generated OpenQASM has 36 physical wires, 139 CX gates, 36 H gates, 14 T gates, 14 T-dagger gates, four resets, and six measurements.

Detectors check both flag outcomes, the repeated syndrome-readout equalities, and the equality between the two logical readout results. A fault that causes a flag or makes the repeated readout disagree is rejected. A clean logical outcome is accepted with its Pauli frame recorded. This is a deliberately light flag construction; it does not claim that the available flags catch every propagated data fault, which is why the measured first-order scan is reported explicitly.

The authoritative judge code used here is `tprep` from the supplied 3.0.3 environment. I read `problem.md`, `tprep/check.py`, `noise.py`, `qasm.py`, `exact.py`, and `faults.py`. The cited Chamberland--Cross and Postler papers were not fetched during this run; the circuit structure follows the requested flagged logical-measurement style and the paper references in `problem.md`.

## Verification

`measurement_flag.qasm` is generated with `tprep.submission_text`; `measurement_flag.json` is written only from the official `tprep.check(..., shots=10**7, seed=0)` report and `tprep.fault_scan`. The final report must be read from those generated files/output after both jobs complete. Any score, acceptance, or `c1` in this repository is measured, not hand-edited.

## Alternatives tried

* Direct injection/encoding is outside this direction and was not used as the reported design.
* An unflagged two-cat measurement variant used roughly 396 CX gates and had acceptance below the floor or score around 0.44 in short runs.
* Sequential routing of the cat variant reduced CX count but remained below the acceptance floor when its stabilizer checks were retained.
* Removing the checks made acceptance pass but left a score around 0.32, so the checks were not useful enough at that depth.
* The compact flagged circuit gives substantially better short-run score and acceptance, while keeping the detector set small enough to pass the 0.5 acceptance requirement.

## Open ideas

1. Replace the repeated full logical measurement with a distance-3 flag schedule that uses one syndrome ancilla and two flags per support, then search CX ordering on the grid.
2. Search data/flag placements jointly instead of fixing the seven data wires to one compact patch; idle noise and routing depth are likely the dominant second-order cost.
3. Add only those stabilizer detectors whose single-fault acceptance benefit exceeds their added routing and idle noise, using `fault_scan.by_instruction` as the objective.

## Measured artifact

At (p=10^{-3}), (10^7) shots, seed 0, the generated `measurement_flag.qasm` passes all four judge gates with score (1-F=0.1616925943\pm0.0001319256), acceptance 0.7168751, and 139 two-qubit gates. The official single-fault scan reports 2498 fault instances and (c_1\approx187.7678); therefore this compact candidate is **not** first-order fault tolerant despite its flagged measurements. The residual list is recorded in `measurement_flag_scan.txt`, with the largest contributions at the routed data H/CX instructions listed there.
