# SQUARE
Verdict: **no finalist. Gates 1–2 pass; the built and exactly priced grid families lose and fail acceptance.**
Stopped under the step-3 “best >= tau” branch. This closes these implementations, not the square family or all layouts.
tau=3.761821654835085e-05; target L<tau-1e-7, A>=0.5002; J_tau=A*(L-tau). Rank only feasible builds by J_tau.
Incumbent reproduced exactly: L=3.761821654835085e-05, A=0.5007854638217537, SHA256 cdaa719694c647348ca0fc5e3b311f1586df7f974ad993c0249fef18b9ee1b0e.
Best first-order-safe grid: `builds/grid_grid_square_s27_guards_s27.{qasm,json}`; L=0.000892760322528, A=0.155149013612, J=0.000132674454241.
Best grid-free square: `builds/suffix_square_R44.{qasm,json}`; L=3.48962654301e-05, A=0.53940768315, J=-1.46824134635e-06. Not grid-valid.

Gate 1: standard 28.84 p² / 2.8713361272995983e-5; square 25.6666666667 p² / 2.5558431235817117e-5;
eraser 25.6666666667 p² / 2.5584641585513234e-5. All three have single-fault loss <9e-19. Reviewer numbers reproduced.
Main-doc correction: the FINDINGS claim that every Steane-type round pays 28.84 p² is too broad; the square is a measured counterexample.
The actual v37a round counterfactual is 2.903230601583247e-5 at A=0.9471249113533862; early D->A at 45, other round ops>=46, waits>=45.
Gate 2: the square improves the matched standard suffix by 5.52695955836e-06 (>1e-6); eraser also passes but loses to square.
The common prefix is the backwards causal cone of v37a data through tick 43 plus every completed prefix detector; native MX reuse is preserved.
Both grid-free suffixes use 9-CX CSS encoders and all waits. Square adds an explicit three-CX logical-Z check of B; R=44.

Grid decisions and scope:

- Retain that prefix and move data from 44; allow up to 2 hops in the first CP layouts and 3 in the connection-length search.
- Standalone connected A+connected BC, and connected A+connected remaining resource space, were INFEASIBLE in the tested 2-hop/R<=60 models.
- A seven-square layout exists with one extra hop 22->28. Its preparation requires shared routing space; this is not an impossibility proof for other schedules.
- Built 64 reverse-routed CSS preparations, 64 local GF(2) preparations, and 128 state-identity simplifications; shortest routed R94, simplified R91.
- A connection-length CP layout uses seven hops. Its 64 routed builds reach R85 best; 64 B-fenced routes reach R92 best.
- The decoder-safe X/Z joint CSS CP model returned UNKNOWN after 180 s, with no solution; it provides no infeasibility certificate.
- Exact repair tests: delaying preparations, continuous known-state guards, their combination, and state-identity gate deletion. Kept the lowest-loss first-order-safe grid build.
- The faster seven-hop route has c1*p=2e-4; fencing B preparation/verification leaves 1e-4. Rejected, even though the best repaired loss is 6.646605601606709e-4.
- Fault witnesses have zero detector flips, X syndrome 1 and even X parity: an accepted decoder-uncorrectable X residue. A logical-Z check alone does not reject every correlated resource fault.

Measured cost on the best first-order-safe grid (same QASM and schedule; these are overlapping counterfactuals, not redesign bounds):

- Full L=0.000892760322528; perfect preparation L=0.000128601918552, A=0.412400802027; perfect data waits L=0.000400505355873.
- Both perfect L=3.38382411255e-05, A=0.523128659306; round-only L=2.55584312362e-05.
- Relative to both-perfect: preparation alone adds 0.000366667114748; waits alone add 9.47636774262e-05; interaction 0.000397491289229.
- Removing every pre-round detector gives A=0.191854678236. This upper-bounds detector-deletion acceptance buys while retaining the fixed full square checks; it is still below 0.5002.
Preparation/routing and waiting consume the gain. B verification is included in preparation; its independent marginal was not isolated. No acceptance-feasible grid build exists here.

Every exact price (L and A include all orders at p=1e-3; duplicate hashes are distinct noise experiments):

| Saved circuit | L | A | J_tau | SHA256 prefix | What moved |
|---|---:|---:|---:|---|---|
| [v37a](builds/v37a.qasm) | 3.76182165484e-05 | 0.500785463822 | 0 | cdaa719694c6 | incumbent, full noise |
| [round_eraser](builds/round_eraser.qasm) | 2.55846415855e-05 | 0.957525161784 | -1.15224508131e-05 | b8be23730803 | perfect resources; every round channel noisy |
| [round_square](builds/round_square.qasm) | 2.55584312358e-05 | 0.957525136197 | -1.15475475739e-05 | e9055369b631 | perfect resources; every round channel noisy |
| [round_standard](builds/round_standard.qasm) | 2.8713361273e-05 | 0.964702491827 | -8.5905360735e-06 | 25efeb936047 | perfect resources; every round channel noisy |
| [v37a_round](builds/v37a_round.qasm) | 2.90323060158e-05 | 0.947124911353 | -8.131929752e-06 | cdaa719694c6 | actual round; perfect preparation/prefix |
