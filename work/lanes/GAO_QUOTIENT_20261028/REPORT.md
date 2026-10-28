# Gao correction quotient: complete abstract circuits

These are complete noisy circuit experiments with **abstract connectivity**; none is a native 6×6 submission. The original retimed-late Gao construction has 160 CX, 23 clocks, L=4.521503996806116e-5 and A=0.7241181954. Both proposed algebraic reductions pass the official noiseless exact-state check on the explicitly generated abstract native stream. Their six output stabilizers have expectation +1, all original source and terminal detectors remain deterministic, and the logical frame is included in the seven-CX check and all-orders price.

## Algebra and concrete witnesses

Face masks use bit `i` for physical face qubit `i`, and H has supports [1,2,6,7], [2,3,4,7], [4,5,6,7] in the paper's 1-based coordinates. The exact original correction masks for bulk q7 through q14 are `[72,80,24,90,66,10,18,0]`. Their H syndromes cover all eight possible three-bit values. The span of the three weight-four rows is the Z-stabilizer subgroup.

The seven-CX representative `[1,2,4,8,16,32,64,0]` consists of the matching q0→q7, …, q6→q13. For each of the first seven columns the XOR of old and new masks is an odd zero-syndrome vector, hence logical Z times a Z stabilizer; the last is zero. The output FRAME_Z is parity of records c15–c21. This is a legal whole-code frame and is checked by the frame-aware exact oracle and price.

For a 10-CX representative, choose one bulk column as a star and choose a common odd mask whose syndrome matches the original star column. For each of the seven non-star columns use the unique weight-one mask of the transformed syndrome, and for the star use a weight-three logical Z vector. `quotient.py` verifies each old⊕common⊕new lies in the explicit Z-stabilizer span. The common mask has no accepted ideal action because it is controlled by the even parity of all eight bulk X records, an original detector. This equality concerns the accepted ideal map; noisy measurement and gate faults are included in the full prices.

## Prices

| Variant | Clocks | CX | Exact L | A |
|---|---:|---:|---:|---:|
| Original retimed-late | 23 | 160 | 4.5215039968e-5 | 0.7241181954 |
| Seven-CX, logical frame | 22 | 151 | 5.5275876705e-5 | 0.7334864502 |
| Coherent star 7, logical mask 7 | 22 | 154 | 4.9515749981e-5 | 0.7279907981 |
| Coherent star 0, logical mask 7 | 23 | 154 | 6.2723785219e-5 | 0.7253790695 |
| Coherent star 6, logical mask 7 | 23 | 154 | 7.5961311261e-5 | 0.7103971743 |
| Coherent star 7, logical mask 28 | see metadata | 154 | 6.5122351675e-5 | 0.6995321756 |
| Coherent star 7, logical mask 42 | see metadata | 154 | 4.5280531366e-5 | 0.7239820581 |
| **Same pattern, schedule seed 2** | 22 | 154 | **4.3828212029e-5** | **0.7305514867** |
| Coherent star 2, logical mask 7 | 23 | 154 | 4.5286664105e-5 | 0.7297819160 |
| Coherent star 4, logical mask 7 | 23 | 154 | 5.0223718259e-5 | 0.7271125440 |

These seven coherent patterns are a limited subset of the 56 possibilities, and the schedules differ; no global conclusion follows. Four representative candidates have zero harmful single-fault contribution (`singles.json`), which is only a diagnostic and does not rank the full-noise results. `reschedule_a.log` and `reschedule_b.log` record additional scheduler-seed prices when complete. All kernels include the physical source, resource preparations, terminal measurements and idle channels; no perfect-resource shortcut is used.

A fixed-parent-clock placement model found no available clock for q2→q14 in the star-2 candidate or q1→q14 in the star-7/mask-42 candidate, between the last noncommuting q14 operation and its measurement at clock 15. The seven-CX matching was also infeasible under that fixed schedule. This is an obstruction only to insertion while holding all other operations at their original times; the separately retimed constructions show these circuits do exist. A different schedule for the star-7/mask-42 pattern lowers the full noisy abstract loss by 3.07% relative to the retimed-late parent, but remains far above the latest sampled public score before any routing. This checkpoint does not establish a competitive native architecture or justify treating abstract adjacency as a grid implementation.
