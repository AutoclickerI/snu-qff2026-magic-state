# BCX handoff (2026-10-25 15:35 KST)

Lane goal: beat MAIN's v36h (`work/lanes/MAIN/v36h.{qasm,json}`) by replacing its B/C resource (r3: BFLAG's correlated
rank-3 state, 56 CX, ticks 33-43, then B->C at 44, C read in Z, B->D at 45). Objective: exact all-orders
J_tau = A*(L - tau), tau = L(v36h) = 3.815473322483099e-5 (A(v36h) = 0.5016415049479505, BCX/sparse = EVALF copy of
MAIN/sparse). J_tau < 0 <=> L < tau. Acceptance is a pass/fail gate at 0.5 (lanes keep A >= 0.5002).
Machine-readable numbers: `results.json` (keys below). All paths are relative to `work/lanes/BCX`.

Constraints (from the brief, binding): `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1` always; heavy jobs
on hippo only, <= 24 cores in total for this lane (CP-SAT workers + evaluator processes), never touch the racer's
processes; zebra <= 8 processes for quick evaluations; never owl/tom/jerry/sunfish. Source of truth on zebra; push with
`rsync -a --exclude .submit_credentials ./ hippo:/home/jihoon/competitions/quantumn/work/lanes/BCX/`, ssh as
`ssh -q -o ControlMaster=no -o ControlPath=none hippo '...' < /dev/null`. Kill/wait by PID (pid files in `pids/`),
never `pkill -f`. No submissions, commits, or edits outside this lane. Reviewer files: untrusted, `python -I`.

## 1. Leads 1 and 2 on the rank-3 contract: closed (no J_tau < 0)

- Exterior model `ext.py` reproduces v36h byte-identically from `syn/r3.json` (plain and extended tail).
- Proxy `rproxy.py` (J = X2 + X2leak + XC + KZ*RZ + KA*acc1, KZ 1.1e-4, KA 1e-5) is calibrated on 50 near-r3
  candidates: dL = 1.00 * d(X2+X2leak+XC), R^2 0.97, rank correlation 0.98 (`calib.jsonl`).
- Waves 1 and 2 (`runs/c*`, `runs/p*`, `runs/b*`): 22 LNS runs of 20-25 min from r3, covering hard and safe F1, plain
  and extended (Lead 2: joint through tick 44), Lead 1 with KXC 0 or 0.3, and wide windows (kmax 8, wmax 7, extras up
  to 3). Every run ends at the same proxy point: J 1.748844e-5 -> 1.747178e-5, i.e. -1.67e-8, entirely KA*acc1.
- All archived Pareto points are priced in all orders (`front_w1.jsonl`, `front_w2.jsonl`). Best by loss:

  | point | L | A |
  |---|---|---|
  | b1h:435e5b798acada04 | 3.815677e-5 | 0.50248 |
  | b1h:a472c56de3916078 | 3.816240e-5 | 0.50195 |
  | b1h:f409b1c96d94cc2c | 3.817229e-5 | 0.50141 |
  | b1h:c4e1e6c7cb5cf583 | 3.832322e-5 | 0.50265 |

  The first is an acceptance-only move: L +2.03e-9, A +0.00084 against v36h. Offer it to MAIN only as acceptance
  headroom (it does not beat v36h).
- Lead 1 mechanism: each decoder-safe residue location costs at least about p/15 * 2.6e-3 through XC (leak times the
  exterior's undetected data-X weight, `extw.json`), and no residue-enabled move lowers X2 or RZ.
- Later start: hard F1 is infeasible for T0 >= 34 (also extended); safe F1 is infeasible for T0 >= 35. Safe T0 = 34
  is feasible but loses (synthesis 7.54e-5 / 6.54e-5 extended; best LNS f34r 4.476e-5).
- Fresh starts (wave 3, `runs/f3*`, key `wave3_fresh_lns`): best f33sx 4.053e-5 (A 0.50072), f33h 4.094e-5, f34r and
  f34rx 4.476e-5. Closed.
- H/S at 43-44 (`hsearch.py`, key `h_window_43_44`): 262,456 windows checked, 42 CX-only equivalents, 0 with H.
  Nothing new.

## 2. R_102 (reviewer 12's rank-four resource): in progress

Contract: X generators (g1,g1), (g2,g2), (g3,g3), (0,102) on B x C, where 102 = C indices {1,2,5,6} = cells 25, 19,
29, 28. C's Z detectors become Z(V^perp); a new X(V) check reads X(25,19,29,28).

Code:

- `ext.contract_r102(v=102, extended)` returns `dict(nx=4, target, undet=[0, v], npiv=4)`. Target bit 3 is the
  (0,102) generator.
- `bcmodel.build(..., contract=...)` is nx-generic. Its F1 clauses loop over `undet`; in hard extended mode the
  t == D boundary is skipped.
- `bcsynth.py --contract r102 --base v36h_r102 [--near syn/r3.json --wnear 10]` synthesises fresh. `--near`
  minimises the CX slots that differ from the given state.
- `bclns.py --contract r102 --base v36h_r102` runs the LNS. New flags `--acc1_cap C --KAH K` add the penalty
  `K * max(0, acc1 - C)` to J.
- `ext102.py` writes the template `v36h_r102.{qasm,json}`:
  - It is v36h with the C copy edges and helpers at 44-46 replaced by an on-grid X(V) check: a cat on bottom-row
    helpers 32, 31, 30, 33, 24, 34, 18, 35 (ticks 40-46), then CX 18->19, 31->25, 34->28, 35->29 at 45, and MX at 46.
  - Its C detectors are Z(V^perp) plus the check.
  - The template still holds r3, so detector 71 (the check) is random there. It is a splice base, not a circuit.
- `mk.make(state, stem, base='v36h_r102')` builds a candidate. `ao.py <stem> <procs>` gives cached all-orders.
  `floor.py <stem> <procs>` gives the matched floor: B/C ops at ticks 33-43, plus the idle run after each, made
  noiseless.

Witnesses (key `r102_witnesses`). Six CP-SAT syntheses, each 900 s; objective lifetime/CX, not error weight:

| witness | F1 | L | A | floor | L - floor |
|---|---|---|---|---|---|
| q102near | hard | 4.891e-5 | 0.49659 | 3.5140e-5 | 1.38e-5 |
| q102h | hard | 5.423e-5 | 0.49568 | 3.5848e-5 | 1.84e-5 |
| q102hx | hard, extended | 5.410e-5 | 0.49552 | 3.5848e-5 | 1.83e-5 |
| q102s | safe | 6.937e-5 | 0.49540 | 3.4353e-5 | 3.50e-5 |
| q102sx | safe, extended | 7.605e-5 | 0.50136 | 3.2803e-5 | 4.32e-5 |
| q102_quick_s | safe | 6.080e-5 | 0.49792 | 3.6365e-5 | 2.44e-5 |

- v36h's floor is 3.4396e-5, so its preparation cost is 3.76e-6. Reviewer 12's phantom floors: R_102 3.3636e-5,
  R_0 3.4458e-5. Their budget for a direct build is a preparation cost below 4.52e-6.
- On grid the floor depends on the structure: the budget tau - floor ranges from 1.8e-6 (quick_s) to 5.35e-6 (sx),
  against actual preparation costs of 1.4e-5 to 4.3e-5. The floor also zeroes idles after region ops, so treat it as
  a budget indicator, never as a ranking.
- The R_102 witnesses carry X2 >= 1.1e-5, against 2.68e-6 for r3. The proxy undercounts there
  (dL/dJ = 1.02-1.32: higher orders), so rank by all orders.
- Acceptance (key `r102_acceptance_fit`): dA = -0.00475 - 0.5 * d(acc1) against v36h (5 witnesses, residual
  <= 2e-4). A >= 0.5002 therefore needs region acc1 <= 0.3153 (v36h: 0.32187).
- The proxy's XC table (`extw.json`) is v36h's exterior. Absolute J is not comparable across contracts; within r102
  use it for search only.

Running now: wave 4 (`wave4.sh`, key `r102_wave4`) on hippo, 24 single-core `bclns.py` runs.

- Launched 15:29:50 KST, `--seconds 1800`, so they end about 16:00-16:01 KST.
- PIDs 3267396-3267465 (step 3), one per `pids/r4<tag>.pid`. Logs `runs/r4<tag>.log`, bests `runs/r4<tag>.json`,
  archives `runs/r4<tag>.arch.jsonl`, all on hippo until pulled.
- Tags r4{near,h,hx,s,sx,qs}{a,b,c,d}: start = the witness of the same name (`qs` = q102_quick_s; F1 and extended
  as the witness).
  - a: default windows.
  - b: `--kmax 7 --wmax 6`.
  - c: `--acc1_cap 0.3150 --KAH 1e-3`.
  - d: c plus wide windows.
- Wave 4 takes all 24 cores, so start nothing else for BCX on hippo until it exits.
- 60 s smoke test on zebra (r4nearc settings): J 3.244e-5 -> 2.846e-5, acc1 0.3225 -> 0.3183.

## 3. Next steps and stop rule

1. Wait on the PIDs in `pids/r4*.pid` (hippo) to exit, not on files. Then
   `rsync -a hippo:/home/jihoon/competitions/quantumn/work/lanes/BCX/runs ./ < /dev/null`.
2. Pareto plus the best 20 by proxy:
   `../../../.venv/bin/python pareto.py specs_r4.txt 20 'runs/r4*.arch.jsonl'`.
   The front is over (X2+X2leak, XC, RZ, acc1). Each archive row carries its base (v36h_r102) and T0, and mk detects
   extended mode from T0 + len(ops) - 1 == 44.
3. Price in all orders: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 ../../../.venv/bin/python
   aobatch.py front_r4.jsonl 8 $(cat specs_r4.txt)`.
   - This uses 8 processes on zebra. On hippo, after wave 4 exits, up to 24.
   - It writes `cand/r4*.{qasm,json}` and one row per spec with loss, acceptance and proxy terms. Cost is 3-17 s per
     candidate.
4. Rank by J_tau = A * (L - tau). A finalist needs L < tau and A >= 0.5002. Also run `floor.py` on the best few to
   split floor and preparation cost.
   - If L < tau but A < 0.5002: continue from that state with `--acc1_cap 0.3150 --KAH 1e-3` (or larger KAH).
   - Finalists go to the main session for fast_check (1e6 shots at 8 and at 1 process) and speed_predict FAST. Only
     MAIN submits.
5. If the best L is within about 1e-6 of tau: run a second LNS wave from the best r4 states (larger windows,
   `--extras 0,1,2,3`, `--nseconds 30`).
   - Include hard-F1 extended runs seeded from the sx structure, since sx has the lowest floor.
   - Untested readout alternative: CX 19->25 and 29->28 inside C, then MX 19 and MX 29 (product = X_102). It needs
     no cat but loses one Z(V^perp) bit (Z25 Z28). Single faults may then give c1 > 0; it needs an ext102 variant
     and a c1 check.
6. Stop rule (coordinator): if the full Pareto pass (wave 4 plus its all-orders pricing, plus step 5 if triggered)
   finds no J_tau < 0, close R_102 with its mechanism:
   - preparation cost against the per-structure budget tau - floor;
   - the X2 cost of the fourth generator: the V cells sit in two pairs at columns 1 and 4-5, so the (0,102)
     fan-out lengthens chains;
   - the acceptance tax of the check: acc1 must drop by 0.0066.

## Files

- Pipeline: `ext.py`, `bcmodel.py`, `rproxy.py`, `bclns.py`, `bcsynth.py`, `mk.py`, `ao.py`, `aobatch.py`,
  `pareto.py`, `floor.py`, `ext102.py`.
- Supporting modules and tools: `qcirc.py`, `splice.py`, `decompose.py`, `extw.py`/`extw.json`, `fullprop.py`
  (whole-circuit fault table for proxy validation), `regress.py`, `hsearch.py`, `timeline.py`, `test_model.py`,
  `launch.sh`, `wave{2,3,4}.sh`.
- Data: `results.json`, `ao_cache.jsonl`, `calib.jsonl`, `front_w{1,2}.jsonl`, `syn/`, `runs/`, `cand/`,
  `specs_floor/`, `logs/`.
- `sparse/` is the EVALF copy of MAIN/sparse.
- Removed today (BFLAG originals in `work/lanes/BFLAG`): `lns.py`, `lns3.py`, `proxy.py`, `synth_bc.py`,
  `mkcand.py`, `checkbc.py`, `bcspec.py`, `pipe.sh`. Also removed: the fixed-bug diagnostics `dbg_*.py` and the
  smoke-test runs.
