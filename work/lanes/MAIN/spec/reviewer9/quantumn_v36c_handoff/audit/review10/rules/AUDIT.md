# Rules and terminal-bound audit — current review

## Pins
- quantumn: 42afa8ff01c3999444336f5bb2fe473c1475d6f4.
- Official judge: 76fe47c0324f1c1f8b72a7d55af200e88043b522. Live GitHub HEAD independently queried; unchanged.
- This note is source review and exact-certificate rerun, not a new physical optimization result.

## Result
The current rule set does not support a legitimate true-mean score below 1e-5 under STANDARD p=0.001. The supplied two-tick terminal proof survives examination of native scheduling, measurement/reset exceptions, first-use preparation, conditional acceptance, and logical Pauli frames. The independently rerun rational enumeration gives minimum relaxed loss 0.00001162029638920668820439987200204524249962631837998654273939265; rounded certificate 1.162e-5. It checks all 64 syndrome sectors and all 21 final output-output pairs (the latter floor 3.333e-4). Outputs are in terminal_bound.json and additional_certificates.json here.

This statement is about the expected decoded physical infidelity, not a selected finite Monte Carlo sample. The 7.44545e-6 number keeps only the last tick and omits a compulsory prior output-noise source. A lower bound below a threshold would in any event not establish an achievable circuit below it.

The proof permits arbitrary conditional pre-tail states, including residual syndromes and bias. It does not prove the lower bound is attainable. Architectural round estimates 2.567e-5 or 2.884e-5 cannot be promoted to universal circuit bounds without their own scope proof.

## Binding rules
Primary source: https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/problem.md
- 36-qubit 6x6 orthogonal nearest-neighbor grid; one quantum register, arbitrary ordered distinct seven outputs: lines112–148,164,357–367.
- Listed one-qubit gates and CX; no arbitrary rotations, custom/3q gates or conditional quantum operations:129–149.
- Accepted noiseless output, after an affine logical Pauli frame, is already exact T_L before judge correction; discarded branches need not be correct:271–319.
- Absolute noisy acceptance >=0.5, not A/A0:245–258.
- Official seed0,1e8 shots,1e6-shot chunks seedk;3-significant-digit score then2q count then earlier submission:343–354.
-200000UTF8 bytes,5000noncomment QASM statements,1000measurement+reset operations,1h server wall-clock:368–376.
- Processability is an actual gate, including the official exact checker MAX_RANK=22 for propagated magic/postselection X-span (tprep/exact.py35,71–76). This is not a20-T-count limit or a literal physical single-time T layer.

## Allowed freedoms, with qualifications
- A0 may be below1; POSTSELECT may select noiselessly random outcomes; detector references may be1 and only deterministic given POSTSELECT (problem.md158–169,245–258).
- Logical FRAME may depend affinely on measurement records (constant XOR bits), and explicitly supplied frame overrides auto-discovery (problem.md280–317). Arbitrary Boolean lookup or S_L feedforward is not a free software feature. A nonlinear predicate can instead be physically computed in allowed gates, paying their noise/time and class cost.
- c1 need not equal0. Official objective is finite-p expected/MC infidelity; fault_scan c1 is a diagnostic (problem.md586–589).
- First-use delaying, reset delaying, terminal helper measurement, and native M_X/R_X folding affect actual idle exposure. No noise before first use, before reset, or after measurement if never used again (problem.md235–243; noise.py54–88).
- All-global barriers, fixed pure A/B/C block roles, fixed data cells, fixed data ordering, creg256 and CX200 are not contest requirements.
- The repository's20s per1m-shots promotion gate is a local proxy for the actual1h wall-time requirement, not the literal official rule. It may be sensible on calibrated server throughput; a slow candidate cannot simply be labeled legal and assumed to finish.
- Comments' textual positions are not a scheduling degree of freedom: qasm.py218–223 places a DETECTOR after its last measurement; noise.schedule ignores TICK and obeys per-qubit barriers. Removing barriers can move resets early and add waits, so validate native schedules.

## Status changes that must alter the final recommendations
The latest PLAN already owns P75 N−L0*A with pair interactions; P77 terminal backward templates and FRAME/POSTSELECT support when needed; P73 mid-preparation B ideal-meter probe and M10 policy oracle. Detector112→85, equivalent POSTSELECT, frame gauges and weighted CEGAR are parked with identities/witnesses. Current FINDINGS says the live ST2 pop35 path retains register size and fills survivors before optional random choices. Do not report these as newly discovered unfixed gaps from legacy population.py/core.py.

Current GOAL also already distinguishes a1.162e-5 universal true-mean floor from the seed0 target. The valuable correction is now in implementation completeness and objective scope, not that the team has never read these rules.

## Candidate refinements for the implementation lead
1. General official-schedule/affine-record adapter as shared infrastructure, beyond TERM-only demand. It unlocks partial barriers, actual postselection references and frame policies for all lanes. First gate: compare native schedule, A and N on existing incumbent and small legal witnesses against unchanged judge. It guarantees coverage/equivalence when implemented, not lower physical loss.
2. Accepted-instrument equivalence for intermediate-state search. Contract only the accepted output plus classical records that affect exterior acceptance/frame, instead of demanding each named A/B/C resource equal a fixed pure state at a fixed boundary. This is justified by accepted-branch rules, but overlaps active TERM/IDEAS and should be treated as an exact contract refinement, not a brand-new lane.
3. A closed M10 four-sector test does not close all affine frame/rejection choices. Before a larger physical flag build, price the joint syndrome-sector distribution under the actual decoder, then optimize a legal affine acceptance/frame family with absolute A>=0.5. This is an extension of active P73, and evaluation support is required. A general Boolean oracle is only an upper-potential screen until realizable in allowed annotation/gates.
4. For every ideal-meter screen, separate a mathematically valid optimistic relaxation from a heuristic intervention. A perfect meter that changes the exterior state or destroys a favorable correlation is not automatically an impossibility certificate. A terminal-template relaxation must include every reachable boundary state and record correlation of the actual template.

## Examined judge implementation
tprep/noise.py31–32,54–88,91–123; qasm.py102–146,154–264; check.py112–205,208–221,273–311; exact.py1–35,71–76,174–267. These local pinned files are retained in the prior v36a handoff audit/review9_resumed/official/tprep.

