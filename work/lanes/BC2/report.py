import json
from pathlib import Path

def f(x): return '—' if x is None else f'{x:.7g}'
rows=[]
for p in Path('.').glob('*.score.json'):
    if p.name=='best.score.json':continue
    s=p.name[:-11]; r=json.loads(p.read_text())
    meta=json.loads(Path(s+'.json').read_text()) if Path(s+'.json').exists() else {}
    x=r.get('exact',r.get('quick',{}))
    rows.append((r.get('mean',1),s,r,meta,x))
rows.sort()
best=next((row for row in rows if row[0]<1 and row[2].get('check_1e6',{}).get('passed')
           and row[2].get('MC',{}).get('0',{}).get('passed')),None)
text=['# BC2 report','',
      'Objective: full-circuit 1-F only, with judge format/class/correctness and official seed-0 acceptance ≥ 0.5. '+
      'No submission was made. All lane writes are contained here.','',
      'The exact columns are evaluations through order three only when |c1| < 1e-12. '+
      '`c1` below is the evaluator’s first-order contribution at p=0.001 (its printed `c1 p`). '+
      '`exp(-A1)` is an estimate. MC entries are 100,000,000 shots each.','',
      'Baseline reference supplied in the brief: 1.0382e-4 (100-redraw mean). '+
      'Our same-text three-seed baseline is recorded in `v14_bcm.score.json`; this is the direct comparison used here.','',
      '| Candidate | Prep depth | Prep CX | Rule/recipe | c1 p | 2nd | 3rd | Total through 3rd | exp(-A1) | MC seed 0 | MC 1000 | MC 2000 | MC mean | Seed-0 acceptance | 1e6 judge | Files |',
      '|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|']
if best:
    _,s,r,m,x=best
    text[2:2]=[f'Best verified: [{s}.qasm]({s}.qasm), mean **{r["mean"]:.8g}**, '+
               f'seed-0 acceptance **{r["MC"]["0"]["acceptance"]:.8f}**; '+
               f'prep {m.get("depth")} layers / {m.get("prep_cx")} CX, round starts at {m.get("round_start")}.','']
for _,s,r,m,x in rows:
    mc=r.get('MC',{})
    depth=m.get('depth',14 if s=='v14_bcm' else None)
    cx=m.get('prep_cx',82 if s=='v14_bcm' else None)
    rec=m.get('rule','baseline' if s=='v14_bcm' else 'see metadata')
    text.append('| '+ ' | '.join([s,str(depth),str(cx),rec,f(x.get('c1')),f(x.get('second')),f(x.get('third')),f(x.get('total')),f(x.get('exp_minus_A1')),
         *[f(mc.get(str(seed),{}).get('score')) for seed in (0,1000,2000)],f(r.get('mean')),f(mc.get('0',{}).get('acceptance')),
         'PASS' if r.get('check_1e6',{}).get('passed') else 'FAIL',f'[{s}.qasm]({s}.qasm), [metadata]({s}.json), [receipt]({s}.score.json)'])+' |')
text += ['', '## Loss attribution', '',
         'The winning B-clean prep with q25/q27/q28/q29 measured at first use has full exact total '+
         '8.4428245e-5 and B+C-noiseless total 6.1564636e-5. Its B+C contribution is therefore '+
         '**2.2863609e-5 versus 4.0329527e-5 for v14_bcm, down 43.3%**. This beats the MC benchmark, '+
         'but does not remove most of the entire B+C contribution. The largest targeted interaction, prep×round, '+
         'falls from 1.837e-5 to 3.029e-6 (83.5%); prep×prep is 8.719e-6 and A×prep is 3.004e-6. '+
         'See `compact_clean_d14_k100_m25_28_pairs.log` and '+
         '`compact_clean_d14_k100_m27_29_m25_28.no_prep.json`.','',
         'For `compact_base_d13_k82_m27_29` versus v14_bcm, exact B+C-noiseless totals are '+
         '5.5654224e-5 versus 6.1564636e-5. Subtracting those from their full totals gives '+
         'B+C-attributable losses 3.1616024e-5 versus 4.0329527e-5: a 21.6% reduction, not removal of most of the share. '+
         'The prep×round second-order term falls from 1.837e-5 to 1.059e-5; prep×prep rises from '+
         '7.047e-6 to 1.090e-5; A×prep falls from 4.271e-6 to 2.991e-6. '+
         'Receipts: `compact_base_d13_k82_pairs.log`, `v14_pairs_reference.txt`, and `*.no_prep.json`.','',
         '## Solver receipts', '',
         'All global jobs use depths 13–16 and CX caps 82 and 100. The original and primed batches use helper cells '+
         '`[18,24,30,31,32,33,34,35]`. Compact and combined batches use no helpers and fix the six pivot cells to the baseline set. '+
         'A timeout is not an infeasibility proof. '+
         'Window jobs freeze all layers outside the named five-layer window of the baseline. '+
         'Primed jobs add violations from the baseline before the first solve and explicitly encode target-basis invertibility.','',
         '| Run | Rule | Depth | CX cap | Status | Seconds | CEGAR constraints | Receipt |',
         '|---|---|---:|---:|---|---:|---:|---|']
for p in sorted(Path('.').glob('*.receipt.json')):
    r=json.loads(p.read_text())
    text.append('| '+' | '.join([p.name[:-13],r.get('rule',''),str(r.get('depth')),str(r.get('cap')),r.get('status',''),f(r.get('elapsed')),str(r.get('constraints','—')),f'[{p.name}]({p.name})'])+' |')
text += ['', '## Interpretation and reproducibility', '',
         '- `sat6.py` and `ft.py` are lane-local modifications of ST_BC. They include single-X faults at every layer boundary and correlated XX errors after selected CX gates. XX is one physical prep fault, not a pair.',
         '- `clean_literal` forbids any nonempty B X support. `clean` forbids a nontrivial B X class modulo the X stabilizers. `robust` forbids dangerous B X classes with either zero C-check difference or the syndrome-plus-logical-parity signature of one C readout flip. `pairs` adds pairs of distinct prep fault locations and includes the robust single-fault rule.',
         '- `both` requires B-clean and readout robustness together; `allpairs` adds the pair-fault condition to both. All 16 combined runs (depths 13–16, caps 82/100) timed out at 240 seconds. The independent rule predicates are also audited in `prep_rule_audit.json`.',
         '- Literal B-clean rejects harmless propagated initial RX-pivot X stabilizers. An X component after a pivot’s first CX (XX if it was the control, X if it was the target) realizes the same propagated error. `proofs.py` records the resulting rank contradiction as a reduced SAT necessary-condition certificate, separate from the depth-bounded full-network timeouts.',
         '- Independent encoders were tested with the necessary condition of no direct B–C CX. In the fixed L5 layout, B cell 6 has no allowed neighbor except C cell 12; C cell 5 has only B neighbors 4 and 11. The UNSAT receipts cover separate encoders with disjoint block supports and the eight free helper cells; they do not cover moving data/A or time-sharing occupied cells.',
         '- `merge.py` reproduced ST_BC `cand_best.qasm` byte for byte before changes. `flags.py` uses the same prefix, A prep, data moves, and ALAP merger. Its extra Z flags measure deterministic two-CX parities on free helpers. Every scored flag and synthesized prep is transformed with the actual `MAIN/minit.py` for q27/q29 when those are eligible first-use resets.',
         '- `score.py` invokes the same `exact2.Eval/run/third_order` functions as `exact2.py --third`, and calls `tprep.check` at 1e6 before MC. MC uses `fast_check.check` at seeds 0, 1000, 2000. Every exact total within 3% of 1.01894e-4, plus a small nonzero first-order contribution, is routed to MC.',
         '- EARLY’s later `early_merge.py` was tested with the 13-layer prep (round 47) and the final winning B-clean prep (round 50). Its emitted unmeasured full circuits are byte-identical to this lane’s merger. `early_compatibility.json` and `FINAL_VERIFICATION.json` record these checks. Prep files are independent of absolute time.',
         '- Jerry’s native CryptoMiniSat import failed on a GLIBC_2.33 dependency (host glibc 2.31). Computation was rerun in the available `fnc-build:22.04` image using the host user UID/GID. Owl uses the required Docker UID/GID and thread caps. Process counts and host load are logged before launches.',
         '- The remaining first-use resets of both leading preps were scanned with MAIN/minit.py. The 13-layer prep selects q23/q28 in addition to q27/q29; the winning B-clean prep selects q25/q28 in addition to q27/q29. Per-site second-order generator measurements are preserved in `*.init_scan.json`; final combined variants received the full exact/MC pipeline. Rebuildable intermediate QASM files were pruned after validation.',
         '', 'This report is regenerated from receipts by `report.py`. A — in an MC column means the circuit was outside the requested MC screening window. `completion_audit.json` checks that no eligible MC result is missing. `best.qasm`/`best.json` are byte-for-byte aliases of the lowest-mean candidate, and `ARTIFACTS.sha256` verifies the delivered files.', '']
Path('REPORT.md').write_text('\n'.join(text))
