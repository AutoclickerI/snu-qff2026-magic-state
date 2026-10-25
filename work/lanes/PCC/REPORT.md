# PCC: reviewer 11's partially coherent C resources on v36h

Result: **no finalist; the family stops at stage 2 (routing) on v36h's round layout.** At ideal adjacency with an ideal
|R_V⟩ preparation, only w = 85 ({0,2,4,6}, **−3.73e-7**, acceptance 0.49726) and w = 51 ({0,1,4,5}, −2.29e-7, 0.49726)
beat v36h (3.815473322405639e-5). Both need an X-check partner for code index 4 at the readout tick. Its C cell (5) is a
grid corner whose two neighbours are B cells busy with B→D at that tick, and this holds for every B/C placement that is
compatible with the fixed D and A cells (8 enumerated). The V's that can get partners (45, 75, 102, span{45,75}) lose
even at ideal adjacency: +0.81, +2.04, +0.44 and +2.66e-6.

## Mechanism (measured)
- The prize is real. With an ideal C readout, X(V) removes the X_B Z_C leak of the B→C CX:
  - k=1: −0.84 to −1.22e-6 against the same ideal readout without it (A0);
  - k=2: −1.16 to −1.74e-6;
  - reviewer 11's second-order model gave −0.99 to −1.49e-6.
- The readout tick between B→C (old 44) and the final measurement (old 46) allows one CX per C cell. X(V) needs a check
  CX R_i → C_i on every site of supp(V), so those sites lose v36h's copy edges C_i → helper (C25, C19, C29, C28) and
  C17 → A16.
- Each C site then has one Z witness instead of two. A single flip of C_i after B→C (its measurement, the check CX, or
  an X error on a check ancilla) masks an X on B that occurred before B→C. The data are then left with an undetected
  single X: the same kind of leak the check removes, but fed by B's whole preparation.
- Stripping the copy edges on supp(V) with no check costs +0.65 to +2.30e-6. Against that control, the full-noise check
  gains −0.04 to −1.45e-6 for 11 V's (column "(b) − strip") and costs +0.33, +0.36, +1.08e-6 for 75, span{45,75},
  span{51,75}. For w = 102 it gains −1.16e-6 of its −1.22e-6 ideal prize, but the copy edges it displaces are worth
  +1.60e-6.
- Only V's whose support includes the two uncopied cells C12 (index 0) and C5 (index 4) beat v36h.
- One more tick at the end is not an option: every data qubit idles until the last measurement, and an inserted late
  tick costs +2.6–2.8e-6 (ACCBUY; R43 +2.55–2.76e-6).

## Stage 1 table (all 14 V; Δ in 1-F; v36h = 3.815473322405639e-5, acceptance 0.5016415)
A0 = k0 with the C readout noiseless (ops on C cells at old ticks 45–46, the copy helpers' last window, C17→A16):
3.767847663610049e-5, acceptance 0.51126 (−4.76e-7 vs v36h).
Columns:
- (a): noiseless readout instrument.
- (b): full-noise readout at ideal adjacency in the same ticks.
- (c): (b) plus one noisy CX per support site at the map tick, a proxy for preparation cost.
- strip: copies on supp(V) removed, no X check.
- (bi): (b) with the check block and its check CX noiseless, C's measurements noisy.

| V basis | k | supp(V) | (a) loss | (a) acc | (a) Δ vs A0 | (a) Δ vs v36h | (b) loss | (b) acc | **(b) Δ vs v36h** | (c) Δ vs v36h | (c) acc | strip Δ vs v36h | (b) − strip | (bi) Δ vs v36h | distinct free partners at old tick 45 (some B/C placement, D and A fixed) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 102 | 1 | 1256 | 3.646292e-05 | 0.51099 | -1.216e-06 | -1.692e-06 | 3.859309e-05 | 0.50005 | **+4.384e-07** | +6.545e-07 | 0.49820 | +1.599e-06 | -1.161e-06 | -3.773e-07 | yes |
| 120 | 1 | 3456 | 3.678711e-05 | 0.51065 | -8.914e-07 | -1.368e-06 | 3.894350e-05 | 0.49733 | **+7.888e-07** | +9.968e-07 | 0.49548 | +1.152e-06 | -3.633e-07 | -1.766e-07 | no (idx 4) |
| 30 | 1 | 1234 | 3.650543e-05 | 0.51065 | -1.173e-06 | -1.649e-06 | 3.976528e-05 | 0.49733 | **+1.611e-06** | +1.841e-06 | 0.49548 | +1.827e-06 | -2.160e-07 | -2.450e-07 | no (idx 4) |
| 45 | 1 | 0235 | 3.683109e-05 | 0.51065 | -8.474e-07 | -1.324e-06 | 3.896673e-05 | 0.49733 | **+8.120e-07** | +9.993e-07 | 0.49548 | +1.281e-06 | -4.690e-07 | -2.062e-07 | yes |
| 51 | 1 | 0145 | 3.649428e-05 | 0.51098 | -1.184e-06 | -1.660e-06 | 3.792615e-05 | 0.49726 | **-2.286e-07** | -7.127e-08 | 0.49541 | +9.731e-07 | -1.202e-06 | -6.832e-07 | no (idx 4) |
| 75 | 1 | 0136 | 3.683363e-05 | 0.51065 | -8.449e-07 | -1.321e-06 | 4.019420e-05 | 0.49733 | **+2.039e-06** | +2.263e-06 | 0.49548 | +1.707e-06 | +3.320e-07 | +2.048e-08 | yes |
| 85 | 1 | 0246 | 3.658055e-05 | 0.51098 | -1.098e-06 | -1.574e-06 | 3.778139e-05 | 0.49726 | **-3.733e-07** | -2.602e-07 | 0.49541 | +6.488e-07 | -1.022e-06 | -7.664e-07 | no (idx 4) |
| 30, 102 | 2 | 123456 | 3.614750e-05 | 0.51051 | -1.531e-06 | -2.007e-06 | 3.951517e-05 | 0.49528 | **+1.360e-06** | +1.704e-06 | 0.49252 | +2.291e-06 | -9.304e-07 | -2.146e-07 | no (idx 4) |
| 30, 45 | 2 | 012345 | 3.619676e-05 | 0.51051 | -1.482e-06 | -1.958e-06 | 3.914508e-05 | 0.49389 | **+9.903e-07** | +1.277e-06 | 0.49114 | +2.041e-06 | -1.051e-06 | -4.430e-07 | no (idx 4) |
| 30, 75 | 2 | 012346 | 3.629902e-05 | 0.51051 | -1.379e-06 | -1.856e-06 | 4.021092e-05 | 0.49389 | **+2.056e-06** | +2.340e-06 | 0.49114 | +2.093e-06 | -3.653e-08 | -3.121e-07 | no (idx 4) |
| 45, 75 | 2 | 012356 | 3.652197e-05 | 0.51051 | -1.157e-06 | -1.633e-06 | 4.080980e-05 | 0.49528 | **+2.655e-06** | +2.970e-06 | 0.49252 | +2.295e-06 | +3.599e-07 | +2.328e-08 | yes |
| 45, 85 | 2 | 023456 | 3.647390e-05 | 0.51051 | -1.205e-06 | -1.681e-06 | 3.947884e-05 | 0.49390 | **+1.324e-06** | +1.595e-06 | 0.49114 | +1.542e-06 | -2.176e-07 | -2.872e-07 | no (idx 4) |
| 51, 75 | 2 | 013456 | 3.648952e-05 | 0.51051 | -1.189e-06 | -1.665e-06 | 4.114960e-05 | 0.49390 | **+2.995e-06** | +3.307e-06 | 0.49115 | +1.917e-06 | +1.077e-06 | -7.372e-08 | no (idx 4) |
| 51, 85 | 2 | 012456 | 3.593688e-05 | 0.51085 | -1.742e-06 | -2.218e-06 | 3.831321e-05 | 0.49521 | **+1.585e-07** | +4.010e-07 | 0.49245 | +1.611e-06 | -1.453e-06 | -9.036e-07 | no (idx 4) |

The (a) gate passes: the best prize is −1.74e-6 (k=2, {51, 85}) and −1.22e-6 (k=1, 102). The (b) gate passes only for
w = 85 and w = 51, and their acceptance (0.4973 in (b), 0.4954 in (c)) is below the 0.5005 floor, so ≈ 0.003–0.005 acceptance would
have to be bought (the cheap MX→reset trades exist per INTEG2/ACCBUY).

### How the builds work (`build1.py`, `stage1.py`, evaluator driver `ev/pcc_eval.py`)
- **Preparation as an exact phantom map.** A tick T_INS is inserted between old ticks 43 and 44. A phantom block M (one
  off-grid qubit per support site, prepared in |V⟩) runs CX M_i → C_i at T_INS, which turns r3's |R_0⟩ into |R_V⟩.
  M is then read in X; its records are a Pauli frame Z^m on C after B→C and are XOR'd into the X(V) detectors.
- **The driver removes T_INS exactly.** It drops every channel of T_INS and of M, and shortens every idle run that spans
  T_INS by one step (both the components and the channel's no-fault weight). Check: k0 plus the dummy tick reproduces
  v36h to the last digit (3.815473322405639e-5, 0.5016415049479503).
- **Readout.** On supp(V), v36h's op at old tick 45 (copy edge, early M, or C17→A16) is replaced by CX R_i → C_i from a
  phantom readout block R in |V⟩ (a 4-cat for k=1; 6 qubits for k=2), prepared on off-grid qubits in ticks ≤ 45 (never
  at T_INS). R is read in X and C in Z at the last tick. Sites outside the support keep v36h's ops.
- **Detectors.** C's seven Z rows become a basis of Z(V^⊥). The copy rows of removed copies are deleted, and c24 is
  dropped from A16's rows when C17 is in the support. X(w) rows are the R ⊕ M records over w.
- **Phantom capacity.** The evaluator is ACCBUY's sparse40 with 48 qubits (`ev/frontend.py`). It reproduces v36h
  exactly, and so do sparse40 and MAIN/sparse (MAIN/sparse to 1e-16, a basis roundoff difference).

## Stage 2: routing pre-check (`geom.py`)
At old tick 45 every D and B cell runs B→D, and every A cell except A16 is busy (A16's tick-45 job in v36h is the C17
copy). With D and A fixed, each B_i must neighbour D_i and each C_i must neighbour B_i: 8 placements, v36h's among them.
- **Index 4.** D3 is at cell 3, whose other neighbours are A2 and A9, so B4 is at 4 and C at 5, a corner whose
  neighbours are B4 and B11. No placement gives index 4 a free partner, so no V containing index 4 can be read: w ∈
  {30, 51, 85, 120} and every k=2 space except span{45, 75} = {45, 75, 102}.
- **Moving A2 or A9 does not help.** Cell 2's other neighbours are A1 and A8; cell 9's are A8, D10 and A15, and A9 is in
  A's only connected weight-3 X_L {8, 9, 15}, which carries the decoder flag (×2.05 without it).
- **w = 45, 75, 102 can get four distinct partners** in some placement (e.g. C25 → 32, C28 → 33), but these V's fail
  (b) at ideal adjacency, which also bounds every grid realization from below. Nothing is left to route.

## Closures (each closes only the recipe tested)
- **X(V) readout in the single tick between B→C and the final measurement, on v36h's round layout (D and A fixed;
  B/C/helper cells free).** Closed for all 14 V. The routable V's lose because the check displaces copy edges worth more
  than the check (w = 102: +1.60e-6 vs −1.16e-6). The winning V's need index 4's corner cell.
- **Leaves open:** a round layout, designed together with the prefix and A, in which index 4's C cell (or a relabelled
  equivalent) has a free neighbour at the readout tick. Its prize is at most −3.7e-7 at ideal adjacency and ideal
  preparation, −2.6e-7 with one noisy preparation CX per site (c), and needs ≈ 0.005 bought acceptance. That is below
  the cost of one hop (0.1–1.0e-6) or AENC's next A encoder (+1.4e-6) (inferred from those lanes, not built).
- **Zero-gate |R_V⟩ preparations inside r3 do not exist on v36h:**
  - no single init flip R↔RX or M↔MX in ticks 20–43 (13 tried; `flips.py`);
  - no subset of the four helper guards that act as |0⟩ controls on B/C (h18, h24, h32, h33) started in |+⟩ and read in
    X (15 subsets; `hflips.py`): the injected X reaches B through r3's network.
  A real |R_V⟩ needs a re-synthesized resource; not attempted, since no V survives routing.

## Verified vs inferred
Verified:
- v36h reproduced by MAIN/sparse, ACCBUY/sparse40 and `ev/` (48-qubit). The driver's tick removal reproduces v36h exactly.
- Every build passed the evaluator's built-in checks: ideal acceptance 1, ideal loss 0, every detector deterministic.
  The stim check of every build gives B = |0_L⟩ and C stabilized by exactly X(V) and Z(V^⊥) after B→C.
- All 71 all-orders numbers in the table (43 stage-1 jobs plus 28 controls), on jerry at ≤ 24 cores.
- The geometric enumeration.

Inferred:
- That a relayout cannot recover the residual ≤ 3.7e-7 (cost comparisons with other lanes).
- That (b) bounds grid realizations: ideal adjacency and ideal preparation only remove constraints, and nothing else
  differs from a grid build in the same ticks.

Not run: the judge (phantom circuits are not grid-legal), MC, 1e6/1e8 shots; no finalist exists.

## Files
- **Builders:** `build1.py` (phantom builds; `build1.py <basis|0> <out> [strip sites]`), `stage1.py` (builds and job
  lists; `run`/`run2` workers), `table1.py` (table).
- **Analysis:** `lin.py` (stim B/C stabilizer analysis), `flips.py` and `hflips.py` (zero-gate preparation search),
  `geom.py` (routing pre-check).
- **Evaluator:** `ev/` (48-qubit evaluator with `pcc_eval.py`, counterfactual driver: `ins_tick`, `drop_qubits`,
  `drop_ops`, `drop_idle`, `keep_ops`).
- **Launchers:** `ao.sh` (all-orders launcher), `s1/launch.sh`, `s1/chain2.sh` (jerry workers).
- **Results:** `s1/*.{qasm,json}` (15 builds and 13 strip controls), `s1/jobs.json`, `s1/jobs2.json`,
  `s1/res_batch1.jsonl`, `s1/res_batch2.jsonl`, `s1/table1.{json,md}`, `s1c/` (zebra copy-removal controls), `base/v36h.*`,
  `runs/` (reproduction logs). `qedit.py` is a copy of ACCBUY's, kept so the lane runs on jerry.
- **Writes outside the lane:** the two reproduction runs wrote evaluator caches next to the evaluators.
  MAIN/sparse/v36h_canonical_sparse_result.json is gitignored and was rewritten with the same values. The new sparse40
  file was deleted.
