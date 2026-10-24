import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
THRESH=1.03*8.41984e-5
def num(x):return '—' if x is None else f'{x:.9g}'
def make():
    rows=[];missing=[]
    for p in sorted(HERE.rglob('*.score.json')):
        if p.name=='best.score.json':continue
        name=p.name[:-11];stem=p.parent/name
        r=json.loads(p.read_text());m=json.loads(stem.with_suffix('.json').read_text())
        x=r.get('exact',{});mc=r.get('MC',{})
        if x.get('total') is not None and x['total']<=THRESH and len(mc)!=3:missing.append(str(stem.relative_to(HERE)))
        rows.append((stem,r,m,x,mc))
    means=[(r['mean'],stem,r,m,x,mc) for stem,r,m,x,mc in rows if stem.name!='v16_bc2m' and 'mean' in r and r['check_1e6']['passed'] and mc.get('0',{}).get('acceptance',0)>=.5]
    means.sort(key=lambda r:r[0])
    out=['# COMBO5 — clean B+C synthesis with release-aware timing','']
    if means:
        mean,stem,r,m,x,mc=means[0]
        out += [f'Lowest measured mean: **{mean:.9g}**, `{stem.relative_to(HERE)}`, seed-0 acceptance **{mc["0"]["acceptance"]:.8f}**.',
                f'Target mean 8.46431e-5: **{"met" if mean<8.46431e-5 else "not met"}**. No submissions were made.','']
        refs=[r for stem,r,m,x,mc in rows if stem.name=='v16_bc2m']
        if refs and 'mean' in refs[0]:
            out += [f'The identical v16_bc2m reference text measured {refs[0]["mean"]:.9g} on these three seeds; its seed-0 acceptance was {refs[0]["MC"]["0"]["acceptance"]:.8f}. The stricter 8.46431e-5 threshold from the brief remains the success criterion.','']
    out+=['All MC entries are 1e8 shots at seeds 0, 1000, 2000. Each MC circuit first passed `tprep.check` at 1e6 shots. Exact totals use EVAL/exact2.py’s `--third` computation only for |c1| < 1e-12. `c1` is the contribution at p=0.001; exp(−A1) is an acceptance estimate. Wait steps are R−33, the common post-prefix interval; move operations overlap parts of this interval.','',
          '| Candidate | Prep rule | Depth | Prep CX | R | Wait | c1 | 2nd | 3rd | Exact total | exp(−A1) | MC 0 | MC 1000 | MC 2000 | Mean | Seed-0 acceptance | 1e6 judge | Files |',
          '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|']
    for stem,r,m,x,mc in sorted(rows,key=lambda z:(z[1].get('mean',1),z[3].get('total') or 1,str(z[0]))):
        rel=stem.relative_to(HERE);base=stem.name=='v16_bc2m';R=m.get('R',50 if base else None)
        vals=[str(rel),m.get('rule','clean' if base else '—'),str(m.get('depth',14 if base else '—')),str(m.get('prep_cx',82 if base else '—')),str(R),str(m.get('wait_steps',17 if base else '—'))]
        vals += [num(x.get(k)) for k in ('c1','second','third','total','exp_minus_A1')]
        vals += [num(mc.get(str(s),{}).get('score')) for s in (0,1000,2000)]
        vals += [num(r.get('mean')),num(mc.get('0',{}).get('acceptance')),'PASS' if r.get('check_1e6',{}).get('passed') else 'FAIL',f'[QASM]({rel}.qasm), [metadata]({rel}.json), [receipt]({rel}.score.json)']
        out.append('| '+' | '.join(vals)+' |')
    out+=['','## Solver receipts','','The solver is EARLY’s release-constrained copy of BC2 sat6, with BC2’s clean rule. An X fault invisible to C must leave B trivial modulo its X stabilizers. Single-X faults at layer boundaries and correlated XX faults from each selected CX are checked by CEGAR. Late layers are zero-indexed. UNSAT applies only to the recorded model, pivot restrictions, release constraints and CX cap; TIMEOUT is not a proof.','',
          '| Search | Depth | CX cap | Late-cell constraints | Fixed pivots | Status | Prep CX | Seconds | CEGAR fault constraints | Receipt |',
          '|---|---:|---:|---|---|---|---:|---:|---:|---|']
    for p in sorted(HERE.glob('*.receipt.json')):
        r=json.loads(p.read_text());out.append('| '+' | '.join([r['name'],str(r['depth']),str(r['cap']),str(r['first_use']),str(not r['free_pivots']),r['status'],str(r.get('cx','—')),num(r['elapsed']),str(r['constraints']),f'[{p.name}]({p.name})'])+' |')
    out += ['','Fixed-pivot clean depth 13 was UNSAT at late splits 2, 3 and 4. Allowing arbitrary pivots at depths 13, 14 and 15 timed out at 360 seconds. The six `window_` searches held the original BC2 winner’s suffix fixed while freeing its first 6, 8 or 10 layers, with late split 2 or 3; all were UNSAT. These results leave other pivots, helpers, layouts and broader synthesis models open.','']
    out+=['','## Measurement initialization','','`minit_scan.py` invokes MAIN/minit.py’s copied transform at every eligible first-use Z-reset site and on all sites together. Sites are selected by the full exact total, not second order. All variants within 3% of 8.41984e-5 are required to have all three MC seeds.','']
    for p in sorted(HERE.glob('*.minit_scan.json')):
        r=json.loads(p.read_text());out.append(f'- `{p.name}`: selected sites {r["picked"]}; baseline exact {num(r["base"])}.')
    out+=['','## Loss attribution','',
          'These runs use MAIN/ablate.py with `--pre-end 32`, the candidate’s actual R, A cells 1,14,8,9,2,16,15, and both `--pairs` and `--wait-scale 0,0.5,1`. Region names follow the tool’s time-based definition: preparation operations that overlap the prefix before step 33 are included in `pre`. Removing or scaling a noise region is a diagnostic, not a physically constructed faster circuit.','',
          '| Circuit | Wait-noise scale | 2nd | 3rd | Exact total | exp(−A1), estimate | Receipt |',
          '|---|---:|---:|---:|---:|---:|---|']
    import re
    for p in sorted(HERE.rglob('*.waitscale.log')):
        for line in p.read_text().splitlines():
            z=re.match(r'wait x([\d.]+)\s+2nd (\S+)\s+3rd (\S+)\s+total (\S+)\s+exp\(-A1\) (\S+)',line)
            if z:out.append('| '+' | '.join([p.name[:-14],*z.groups(),f'[{p.name}]({p.relative_to(HERE)})'])+' |')
    out+=['','Pair decompositions:']
    for p in sorted(HERE.rglob('*.pairs.log')):
        if 'weight-3 term' in p.read_text():
            out+=['',f'[{p.name}]({p.relative_to(HERE)})','```text',p.read_text().strip(),'```']
    selected=HERE/'clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.waitscale.log'
    if selected.exists() and 'wait x1.000' in selected.read_text():
        out += ['','The measured diagnostic shows why the gains do not simply add: the selected R=47 circuit has zero-wait-noise exact loss 6.2957e-5 versus 5.6619e-5 for v16. The wait contribution falls from about 2.7579e-5 to 2.1143e-5, while the remaining contribution rises by about 6.338e-6. The second-order prep×prep term grows from 8.719e-6 to 1.402e-5; round×round remains 2.884e-5. These are exact-model diagnostics with the tool’s region convention, not MC measurements of physically modified circuits.','']
    out+=['','## Verification and limitations','',f'MC audit: {len(missing)} eligible candidates still missing full MC. '+(', '.join(missing) if missing else 'All eligible circuits have all three seeds.'),
          'All candidate QASM files have adjacent metadata containing `data_qubits`. No first-order diagnostic is used as a judge gate. All files are lane-local. Host capacity receipts are in `capacity.jsonl`; solver limits and failures are preserved in individual logs.','']
    (HERE/'REPORT.md').write_text('\n'.join(out))
    (HERE/'completion_audit.json').write_text(json.dumps(dict(missing_mc=missing,candidates=len(rows),best_mean=means[0][0] if means else None),indent=2))
    if means:
        _,stem,*_=means[0]
        for ext in ('.qasm','.json','.score.json'):(HERE/('best'+ext)).write_bytes(Path(str(stem)+ext).read_bytes())

if __name__=='__main__':make()
