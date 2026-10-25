Main session: I interrupted your turn on purpose to widen the model before the decisive solve (your files and any owl
containers you started are yours: check them by PID/container id first, keep or kill them). Everything in my previous
message stands; add these relaxations from reviewer 16 (work/lanes/MAIN/spec/reviewer16/REPORT_KO.md #3, #7; untrusted,
numbers reviewer-reported) to the joint A/B/C/E layout and preparation model:
1. E is a leaf for the data: in D->A || B->C, then A->E || B->D, E's Z errors reach A only after D->A, so E's
   preparation errors only corrupt records. E needs no fault-tolerant encoder (price the record-error pairs that hide a
   data fault); its seven cells need not be connected. Reviewer 16 built a scattered Steane |+_L> by a graph state with
   local Cliffords and measured helpers: 11 cells (7 outputs in three components + 4 helpers), 15 neighbour CX in 4
   matching layers, 7 native layers, 16 measurement branches each with a tracked Pauli byproduct folded into detectors.
   Let E (and C, which is also a leaf) use such preparations with helpers in any free cell.
2. Coordinate-wise just in time: a block need not be complete before its first contact; a coordinate whose
   preparation is done may couple while other coordinates still prepare, when the remaining preparation gates commute
   with that contact (same target, or disjoint support). Model per-coordinate release times, not one R per block.
3. Rank by the full exact price with real preparation (tail c2 mis-ranks: square tail 2.556e-5 < path 2.709e-5, but
   grid-free full suffix square 3.4665e-5 > path 3.4080e-5), and select finalists by lowest L at exact A >= 0.5002
   (J_tau only as a search heuristic, tau = the incumbent's L). Before ranking any build that changes the outputs or
   the tail, check raw correctness: the six noiseless output stabilizers must be +1 (the all-orders price checks only
   the decoded loss), and name stem files by QASM plus ordered data_qubits.
Incumbent is now v37e (work/lanes/MAIN/v37e, 3.637095528032376e-5, A 0.5024263760643374, judge 1e6 ~1.2-1.5x v37d's
time); a finalist needs L < L(v37e) - 1e-7. Hosts and rules unchanged (owl <= 24 in docker, zebra <= 4; no tom).
