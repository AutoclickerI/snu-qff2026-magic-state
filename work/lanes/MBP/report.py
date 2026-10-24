"""Rebuild compact receipts and REPORT from completed experiment results."""
from pathlib import Path
import json,csv,math
OUT=Path(__file__).resolve().parent
byname={}
if (OUT/'results.csv').exists():
    for rr in csv.DictReader((OUT/'results.csv').open()):
        r=dict(rr)
        for k in ['c1','second','third','total','expA1','seconds']:
            r[k]=float(rr[k]) if rr.get(k) else None
        for k in ['R','cx','stim_detectors','n_qubits','red_mask']:
            r[k]=int(rr[k]) if rr.get(k) else (7 if k=='red_mask' else 0)
        for k in ['order','perm']:r[k]=json.loads(rr[k]) if rr.get(k) else []
        r['grid_free']=rr.get('grid_free')=='True'
        r['check']=dict(acceptance=float(rr['acceptance']),score=float(rr['check_score']),passed=rr['check_passed']=='True',correct=rr['check_correct']=='True')
        byname[r['name']]=r
for p in sorted(OUT.rglob('*.result.json')):
    if 'inputs' in p.parts:continue
    r=json.loads(p.read_text());r['name']=str(p.relative_to(OUT)).removesuffix('.result.json');byname[r['name']]=r
rows=[byname[k] for k in sorted(byname)]
fields=['name','pre','blocks','kind','red_mask','R','cx','order','perm','c1','second','third','total','expA1','stim_detectors','acceptance','check_passed','check_correct','check_score','n_qubits','grid_free','seconds']
with (OUT/'results.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for r in rows:
        rr={k:r.get(k,'') for k in fields};ch=r.get('check',{});rr.update(acceptance=ch.get('acceptance'),check_passed=ch.get('passed'),check_correct=ch.get('correct'),check_score=ch.get('score'));w.writerow(rr)
g={}
for r in rows:
    if r.get('grid_free') and r.get('total') is not None:
        key=(r['pre'],r['blocks'],r['kind']+(f" mask={r['red_mask']}" if r.get('red_mask',7)!=7 else ''));g.setdefault(key,[]).append(r)
status='No eligible physical improvement found. Grid-free pricing is complete for the listed recipes; the broad grid-embedding question remains unresolved.' if (OUT/'DONE').exists() else 'In progress; no eligible physical improvement established.'
lines=['# MBP', '', '**Status: '+status+'**', '',
       'Ranking is by infidelity only. The hard acceptance gate is 0.5; 0.505 is the practical floor. No submission, commit or push was performed. All lane writes are under this directory.', '',
       'Noise and score semantics come from the organizers\' [noise implementation](../../../upstream/snu-qff2026-problem/tprep/noise.py) and [judge](../../../upstream/snu-qff2026-problem/tprep/check.py). Numerical expansion uses the repository\'s [exact evaluator](../EVAL/exact2.py).', '',
       'The supplied physical bar is `../MAIN/v22h_c2c9`: 203 CX, R45, c1=2.9236e-19, second=5.43199e-5, third=1.69860e-5, total=7.13060e-5, exp(-A1)=0.53384. These are from the existing [exact receipt](../MAIN/v22h_c2c9.exact.txt); the supplied seed-0 re-draw mean is approximately 7.23e-5 and is not a new MBP measurement.', '',
       '**Matched R45 result:** [redundant 1+3-cat MB-B+C](matched_cat13_BC.qasm) has exact total **5.1130377e-5** and three-seed MC mean **5.1351965e-5**, versus the [unitary reference](matched_ref.qasm) at exact **5.1207368e-5**, MC **5.2076372e-5**. The observed mean is 1.39% lower, about one combined standard error; this is noise-competitive, not a resolved true gain. Both are explicitly grid-free diagnostics. The promising two-member-cat graph fails stationary embedding; the embeddable reused three-helper variant misses the practical acceptance floor.', '',
       'The requested contexts contain **2,116 recipe/order evaluations**: 1,058 at sep33 and 1,058 using the exact v22h pre-stage at R45. The table also preserves pilot and diagnostic runs. All completed prices pass noiseless correctness; acceptance failures are retained and excluded from eligibility.', '',
       '## Scope and verification', '',
       '- Grid-free prices relax adjacency and use dedicated virtual preparation helpers. They preserve the judge noise, all exact noiseless correctness conditions, and the 1e6-shot seed-0 check. Their format PASS is **under these explicit relaxations**, so it is not a physical eligibility claim.',
       '- `sep` uses the exact sep33 prefix and R33. **`v22h` is the matched R45 sweep:** all 129 pre-stage operations at v22h_c2c9\'s native times, with all 18 pre-stage detectors. Separate unitary reference blocks replace grid data hops and the 82-CX joint B+C for this grid-free comparison.',
       '- `v22` is the preserved pilot sweep, not the exact-current control: five pre-stage operations were one step later and four early M-init detectors were omitted by the legacy builder. Every R45 recipe was rerun as `v22h` after the [prefix audit](prefix_comparison.json). The pilot\'s internal comparisons remain measured, but final conclusions use the matched context. The per-wire gate DAG is identical, so the placement models\' free-timing feasible spaces are unchanged.',
       '- Every measured row below passed Stim detector determinism (T/T_DAG removed for the known valid X_L Clifford surrogate) and the full non-Clifford exact correctness check in `tprep.check(..., shots=1e6, seed=0)`. Acceptance failures remain visible.',
       '- Exact evaluation uses `exact2.run` or its algebraically pruned equivalent in `fast_pairs.py`, plus TREP2\'s pruned `exact2.third_order`. [Pair validation](pair_validation.json) agrees on loss to floating-point precision; [unchanged third-order validation](exact_validation.json) agrees exactly on the MB frame circuit. Third order is omitted unless |c1|<1e-12. exp(-A1) is an estimate, not the acceptance gate.',
       '- Repeated exact quantum tables are memoized within a single model. Both the [reference](cache_validation.json) and [matched MB circuit](cache_mb_validation.json) reproduce uncached third order exactly; 86–88 thousand table requests require only 6,756 distinct tables. This changes computation time, not the noise model or score.',
       '- Three independent checks use all six orders. Four-check sweeps use all 24 orders. The additional pair-product redundancy sweep covers masks 3, 5 and 6 on B+C. Hybrid orders that remove already prepared rows can coincide. Coupling orders within a four-body measurement are explicit in `perm`; they are not exhaustively enumerated.',
       '- [recipes.csv](recipes.csv) records QASM hashes and regeneration parameters; [regeneration verification](regeneration.receipt.json) checks exact reconstruction before bulk removal. Retained finalists include QASM, judge metadata, and numerical receipts.', '',
       '## Best measured order per grid-free structure', '',
       '| Prefix | MB blocks | Structure | Variants | Best order | 2nd | 3rd | Total | exp(-A1) | 1e6 acceptance |',
       '|---|---|---|---:|---|---:|---:|---:|---:|---:|']
for k,rs in sorted(g.items()):
    r=min(rs,key=lambda x:x['total']);lines.append(f"| {k[0]} | {k[1] or 'none'} | {k[2]} | {len(rs)} | {''.join(map(str,r['order']))} | {r['second']:.7g} | {r['third']:.7g} | {r['total']:.7g} | {r['expA1']:.5f} | {r['check']['acceptance']:.6f} |")
lines += ['', '## Three-seed MC comparisons', '',
          'Each seed uses 1e8 shots, at seeds 0, 1000 and 2000. These are grid-free diagnostics unless explicitly marked physical. They cannot qualify as on-grid submissions.', '',
          '| Circuit | MC 0 | MC 1000 | MC 2000 | Mean | Seed-0 acceptance | Evidence |','|---|---:|---:|---:|---:|---:|---|']
for p in sorted(OUT.rglob('*.mc.json')):
    r=json.loads(p.read_text());ss=r['seeds'];lines.append(f"| {r['stem']} | {ss[0]['score']:.9g} | {ss[1]['score']:.9g} | {ss[2]['score']:.9g} | {r['mean']:.9g} | {ss[0]['acceptance']:.7f} | [{p.name}]({p.relative_to(OUT)}) |")
lines += ['', '## Placement models', '',
          '`grid.py` reserves complete lifetimes with NoOverlap2D: prefix, data transfers, preparation block qubits and reusable ancillas. It includes optional block teleports, independent code automorphisms, and movement between sequential stabilizer measurements. CP-SAT proposes compact feasible circuits; only exact loss may select a built candidate. INFEASIBLE is confined to the stated graph, hop, horizon, embedding and relabeling bounds. UNKNOWN and interrupted searches are not impossibility proofs.', '',
          '| Model | Status | Evidence |','|---|---|---|']
for p in sorted(OUT.glob('*.receipt.json')):
    if not p.name.startswith(('grid','all_embeddings')):continue
    r=json.loads(p.read_text())
    if isinstance(r,dict):lines.append(f"| {p.stem.removesuffix('.receipt')} | {r.get('status','see receipt')} | [{p.name}]({p.name}) |")
for p in sorted(OUT.glob('geometry_[0-9]*.json')):
    r=json.loads(p.read_text());lines.append(f"| {r['kinds']}, round={r['round']} | {r['status']} | [{p.name}]({p.name}) |")
lines += ['', '## Mechanisms and current conclusions', '',
          '- The preparation frame is entirely classical. A\'s Z-check detector XORs its preparation result. B\'s final X-check detector XORs both B and C preparation results, since C\'s Z frame propagates backward through B→C. C\'s Z-readout checks have no preparation-frame terms. No conditional gate is used.',
          '- An error absorbed into a measured preparation frame is harmless. An erroneous preparation record, or a phase error after the corresponding check, can instead cancel the final detector syndrome of a data Z error. Redundancy checks reject many of those record errors. They do not detect the X-hook errors that commute with the preparation X checks.',
          '- Bare MB-A is worse than the separate unitary reference. Its target-ancilla Z faults propagate into multi-qubit Z on A, and interact with pre-round data Z faults. Flag brackets substantially reduce this cost; cats can introduce harmful preparation faults before any data coupling.',
          '- MB-B and MB-C have nearly equal single-block costs. A fourth redundant stabilizer suppresses much of the cost associated with preparation records masking the data syndrome. B+C costs are not additive: joint experiments measure additional cross terms.',
          '- Direct three-generator stars, and the original partial star encoders plus remaining bare measurements, fail the standalone grid embedding model. A 2+2 split at every two-member cat also fails. Allowing 1+3 cat splits makes a single block embeddable; this does not prove that an entire round fits.',
          '- The five-CX partial tree `0→4, 1→5, 0→6, 1→6, 6→2` prepares the first two stabilizers from pivots 0 and 1; one measurement prepares the third. Unlike the original star hybrids, its support graph embeds. Its A version has an expensive initial phase fault: this is measured in `tree2_ABC_v22`, and keeps the unitary-A / MB-B+C version as the stronger grid candidate.',
          '- Redundant four-check two-member cats are also INFEASIBLE for one stationary block, even allowing helper reuse and 1+3 splits ([geometry_14.json](geometry_14.json)). Three-member cats can reuse one path of three helper cells, but the two-block preparation adds long exposure and has matching weight-two X-hook pairs in B and C. Each such reset-fault pair contributes 5e-7 at second order. The physical bridge diagnostic verifies all detectors but fails acceptance by orders of magnitude; it is not a competitive placement.',
          '- Both redundancy types were checked geometrically: a four-record dependency and a three-record dependency ([geometry_16.json](geometry_16.json)). Their two code-automorphism classes cover the 35 four-stabilizer sets: 7 and 28 respectively ([certificate](algebra_geometry_certificate.json)). The fixed-cell two-member-cat obstruction covers both classes; moving block qubits between checks is outside it.',
          '- The explicit reused three-helper B+C recipe has seed-0 1e6 acceptance 0.498116–0.500172 over all 24 orders at R33, and 0.446484–0.447463 at R45. Every tested order misses the practical 0.505 floor before physical routing. The [hook-pair receipt](hook_pair.json) measures eight accepted fault pairs, conditional loss 0.5 each, contributing 4e-6 in total at second order.',
          '- Tree-hybrid A exposes a specific dangerous phase hook: the initial Z fault on its shared parity wire becomes a two-qubit Z pattern. With the pre-round data Z idle at logical index 3, one measured pair alone contributes 5.28033e-6 in `tree2_ABC_v22`. This explains why the same partial tree is much less attractive for A than for B/C.',
          '- On `v22_BC_redundant_201`, total=5.205006e-5. No preparation-ancilla noise: 5.142945e-5; no pre-round data idles: 3.468781e-5. The reductions overlap and must not be added. [Region-pair and ablation receipt](runs/v22_BC_redundant_201.analysis.json).',
          '- A layout failure only closes that model. Other partial encoders, cat trees, internal gate orders, and wider movement models are not globally ruled out.', '',
          '## Verified versus inferred / unfinished', '',
          'Measured: every numerical circuit row, every retained MC mean, exact/accelerated evaluator agreement, Stim detector determinism, actual non-Clifford judge correctness, and the stated bounded solver statuses. Algebraically checked: the 28 generator bases, 35 redundant-check sets, and all 48 prefix embeddings grouped into six D4 classes.', '',
          'Inference: the noise-competitive MB constructions could help if their preparation fits with sufficiently little exposure. No eligible full-grid winner was constructed. The only newly built physical diagnostic fails acceptance. Searches with block motion and independent code relabeling timed out without incumbents; their broad feasibility remains unresolved. Consequently no physical finalist qualified for the requested MAIN/spec/mc3.py ranking. The MC table is explicitly a grid-free comparison, not a substitute for that missing physical result.', '',
          '## Every measured variant', '',
          'The full machine-readable table is [results.csv](results.csv). `GF PASS/FAIL` refers to the explicitly relaxed grid-free judge. No 1e6-shot score is used for ranking. Regeneration: `.venv/bin/python work/lanes/MBP/mbp.py <name> --blocks <blocks> --kind <structure> --R <R> --pre <prefix> --order <order> --perm <perm> --procs N`.', '',
          '| Variant / file stem | Structure | CX | R | c1 | 2nd | 3rd | Exact total | exp(-A1) | Check / MC |',
          '|---|---|---:|---:|---:|---:|---:|---:|---:|---|']
for r in rows:
    fmt=lambda x:f'{x:.7g}' if x is not None else '—'
    ch=r['check'];check=('GF ' if r.get('grid_free') else '')+('PASS' if ch['passed'] else 'FAIL')+f"; acc {ch['acceptance']:.6f}"
    stem=r['name'];target=OUT/(stem+'.qasm');label=f'[{stem}]({stem}.qasm) · [JSON]({stem}.json) · [receipt]({stem}.result.json)' if target.exists() else f'`{stem}` (regenerate)'
    mcp=OUT/(stem+'.mc.json');mc=f"; MC mean {json.loads(mcp.read_text())['mean']:.7g}" if mcp.exists() else '; MC not run'
    structure=r['kind']+(f" mask={r['red_mask']}" if r.get('red_mask',7)!=7 else '')
    lines.append(f"| {label} | {r.get('blocks','')} {structure} | {r['cx']} | {r['R']} | {fmt(r['c1'])} | {fmt(r['second'])} | {fmt(r['third'])} | {fmt(r['total'])} | {r['expA1']:.5f} | {check}{mc} |")
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(len(rows),'measured variants; report refreshed')
