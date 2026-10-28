# Direct C2 inner-code terminal and source

The ideal-input C2 terminal has attractive headroom, but the concrete source built here does not. Both inner-code orientations, with a perfect encoded input and real terminal noise, give exact L=**2.2755684192274168e-5**, A=**0.9893233123**. A complete direct phase-C2 source with real encoded prechecks and flagged cats is raw-valid but has L=**0.0010331414065**, A=**0.6629493190** before native routing. A real flag removes its seven harmful single faults, but the full loss becomes **0.0011176729316**, A=**0.6387820340**. Neither complete source is competitive or grid-valid.

## Terminal headroom

`ideal_c2.py` prepares an ideal logical T state and an ideal seven-block C2 encoding, suppresses their physical noise and artificial preparation waits, and retains the seven actual nearest-neighbor inverse CX channels, seven noisy inner reads and seven real output D idles during readout. D=`[6,20,19,10,2,22,16]` and K=`[7,14,13,9,8,21,15]` are paired by native edges. The source/encoding in the QASM is an explicitly ideal, nonlocal construction; it is not a submission circuit.

| Inner orientation | Inverse and read | Exact L | Acceptance | Harmful singles |
|---|---|---:|---:|---:|
| X repetition: stabilizer Z_D Z_K | CX D→K, MZ(K) | 2.2755684192e-5 | 0.9893233123 | 0 |
| Phase repetition: stabilizer X_D X_K | CX K→D, MX(K) | 2.2755684192e-5 | 0.9893233123 | 0 |

Both are raw-correct with all Steane output stabilizers +1. The phase orientation's logical X is X_D and logical Z is Z_K Z_D, so a cat-controlled logical X is a single physical cat→D CX, and logical T is implemented by CX K→D, T(D), CX K→D. The two terminal values are 3.8% above the earlier ideal C4 diagnostic of about 2.192e-5 and 10.9% below the ideal square-tail diagnostic around 2.555e-5. These are comparable ideal-input diagnostic scopes, not physical lower bounds or achieved source scores.

## A complete direct phase-C2 pilot

`direct_phase.py` constructs phase-repetition blocks *at the initial state preparation*, rather than wrapping an existing final output in a repetition memory. It uses seven D and seven K wires, two physical encoded prechecks using measured seven-wire blocks, two seven-cat Clifford-measurement rounds with three physical pair flags per cat, 15 physical T/T-dagger gates implementing logical rotations, and the final inner decoder. Each outer logical CX acts transversally on the D and K copies; the Z-type precheck couples both halves to its meter, and the X-type check uses only D. The final decoder CX cancels the final logical-T conjugation CX; the seven K X reads and D read-clock idles remain noisy. The source reuses measured check blocks as cat blocks, uses 34 of 36 wires, and includes all resets, CXs, reads, flags and waits.

The 28-clock, 129-CX circuit is raw-valid, exact L=0.0010331414065463491, A=0.6629493190. Seven harmful singles remain, contributing 0.0001166666667 to the accepted loss numerator at p=.001. Their labels in `direct_phase.singles.json` identify faults in the unverified B-zero precheck encoder, including CX(22,27) and CX(24,26); several flip no record. This is an actual full-noise abstract circuit, not a native implementation.

## Bounded physical repair and two-fault attribution

`direct_phase_flag.py` adds a real B-zero logical-Z verification: a new noisy ancilla reset, three B→flag CXs on code coordinates [6,4,1], and a noisy measurement. It reschedules the B cat and final encoded phase to respect the actual cells. The fully noisy 35-wire, 132-CX/30-clock circuit is raw-valid and its harmful-single count becomes zero. Its exact L=**0.0011176729315915295**, A=**0.6387820340**: the finite-p loss worsens despite the single-fault improvement.

`pair_audit.py` attributes the repaired circuit's accepted-loss numerator at second order, approximately **1145.78**. Major time/module buckets are first encoded logical-phase + later cat/phase (197.31), first logical-phase + precheck (154.80), and pairs within the first logical-phase region (130.95). The labels group noisy model channels by time and operation and are not an additive physical-mechanism proof or a substitute for the all-orders price. They show that, in this circuit, the remaining loss is broadly distributed and not localized to the original seven singles or just the terminal readout.

The direct-source constructions deliberately relax adjacency; they have not been routed to the 6×6 device. The large abstract loss and extra routing cost give no basis to promote this particular source. The ideal C2 terminal remains a possible ingredient of a different jointly synthesized, fault-tolerant source; these two controls do not rule out that larger family.

## In-gadget inner-gauge herald controls

`direct_phase_herald.py` tests an extra physical MX of each K wire at clock 19, while the first seven logical T gadgets have temporarily undone their CX(K,D) encoding and the T gates are acting on D. It also tests a physical MX of K2 during the analogous clock-3 seed injection. The noiseless K read is deterministic +1 at each location; the measurements reuse the same qubits and clock, add no new physical time step or CX, and include actual measurement noise. The full deterministic record contract was rederived for each circuit.

| Added noisy heralds | Exact L | Acceptance | Harmful singles |
|---|---:|---:|---:|
| Seven K reads in first logical T layer | 0.0011127769278534753 | 0.6341569314 | 0 |
| K2 read in seed injection | 0.0011176485143774928 | 0.6381427425 | 0 |
| Both sets of reads | 0.0011127548135962098 | 0.6335222759 | 0 |

All three are raw-valid, 132 CX/30 clocks, 15 T/T-dagger, and abstract connectivity. The combined heralds lower the flagged parent loss 0.0011176729316 by about 0.44%, but remain roughly 31 times the incumbent mean. Their full `.price.json` receipts retain the exact finite-p values. These are the final bounded checks in this source family, not a claim against different jointly synthesized C2 sources.
