# Contract of the actual v37c round

Let H = {0x55, 0x66, 0x78}; L = 0x7f. Physical A/B/C coordinates are in lane.py.
The round is D→A, B→C, B→D, followed by A-Z, B-X and C-Z reads and the A logical-X partial decoder.
It is not the square round in reviewer 15. That report is a proposal, not a certificate for this circuit.

Pulling back the final six data-code stabilizers through the round requires X_A(H) and Z_B(H), six independent generators.
The three A-Z detector equations require Z_A(H). The deterministic partial decoder flag requires X_A(L).
Thus A already has seven commuting independent stabilizers and is uniquely |+_L⟩.
The seven literal C detectors require Z_Bi Z_Ci. The three B-X detector equations, reduced modulo the data-input and A stabilizers, require X_B(H)X_C(H).
These conditions plus Z_B(H) give thirteen stabilizers on B/C. Their one remaining logical degree of freedom acts on the data as a controlled logical X.
After the B-X readout, a resource amplitude α|0_L⟩+β|1_L⟩ gives data Kraus maps proportional to αI ± βX_L.
The target T is not an X_L eigenstate. Preserving the same pure T state in every retained noiseless branch requires β=0; the density-matrix version excludes any weight in the |1_L⟩ sector.
Consequently Z_B(L) is required even for the T-specific target, giving fourteen stabilizers on B/C and twenty-one total.
An external helper cannot remain entangled with these rank-full pure resources. No unrecorded gauge subsystem survives.

contracts.py independently checks rank 21 and mutual commutation of the listed binary Pauli rows. The full native-parser round trip exactly reproduces the original L and A.
The corresponding (b) synthesis endpoint for each block is therefore the same pure resource; b_A_unique and b_BC_unique are emitted and independently priced copies of that endpoint.
This does not close different readout/detector contracts, logical feedforward, different terminal networks or non-CSS T-preserving instruments.

Recorded signs are a different freedom. X_A errors never reach the data; Z_B/Z_C errors only flip reads.
For A use the dual phase-label description with three Z-stabilizer generators. A measured erasure is M followed by RX; its record multiplies an X_A correction.
For B/C use three amplitude labels. An MX followed by R erases a label; its record multiplies a Z_B correction.
For a measured label k, choose a final resource column equal to k. Propagate that single-qubit correction through the actual suffix and XOR the record into every affected detector.
The scripts check that no correction reaches a data output, then independently check every native first-order fault and the complete all-orders noisy circuit.

The projector model starts from released product states, creates exactly three independent stabilizers by retained M (A) or MX (B/C) measurements, and synthesizes their conjugating native CX network.
Each projector's sign is folded into final detectors. No ideal syndrome branch is postselected away. This includes the original encoder in a different measurement ordering, but the CP model also permits different measurement cells and times.
The B/C hard CP constraint requires each single X/XX preparation fault with zero C flag to have zero B syndrome and parity. The full-circuit oracle checks all X/Y/Z alternatives and exterior couplings as an additional hard filter.

Scope of the first native synthesis certificates: existing block cells, incumbent initialization times, fixed exterior guards and round deadlines. A measured-erasure and projector models are infeasible in that five-tick window; one extra occupied tick gives fault-safe witnesses. This UNSAT certificate does not apply to every earlier-release schedule.

An additional release audit moves A initializations to their earliest slots after the preceding actual operation: q7→37, q14→34, q13→39, q9→38, q8→36, q21→38, q15→39. Eight data-to-A waiting guards are explicitly removed and their full noisy cost is priced. The measured-erasure model remains UNSAT on this enlarged window. The projector model is feasible without delaying the round, but its complete 48-tick circuit has L=8.379734920343541e-5 and A=.5050242198757477 (`c_cp_A_d0_s3_0`, SHA d58d20f0d644). Its perfect-A-preparation counterfactual still costs4.066307951807799e-5. Thus the earlier-release experiment does not recover the preparation gain.

The larger B/C solves find feasible witnesses and terminate with UNKNOWN on tighter proxy objectives. These are finite grammar certificates, not global optimality statements.
