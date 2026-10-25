"""Collect immutable exact receipts by QASM SHA256; emit the <=100-line handoff."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
TAU=3.761821654835085e-5
rr=[json.loads(p.read_text()) for p in sorted((H/'logs').glob('*.receipt.json'))]
records={};by={}
for r in rr:
    name=r['stem'].split('/')[-1];by[name]=r
    assert hashlib.sha256((H/(r['stem']+'.qasm')).read_bytes()).hexdigest()==r['sha256']
    entry=records.setdefault(r['sha256'],dict(paths=[],experiments={}))
    entry['paths'].append(r['stem']);entry['experiments'][name]=r
(H/'results.json').write_text(json.dumps(records,indent=2)+'\n')
v=json.loads((H/'verification.json').read_text())
best=by[v['best_first_order_safe_grid'].split('/')[-1]]
baseline=by['v37a'];sq=by['suffix_square_R44'];std=by['suffix_standard_R44']
g=best['stem'].split('/')[-1]
pp,pw,pb,ro,ceil=[by[g+'_'+s] for s in ('perfectprep','perfectwait','perfectboth','roundonly','accept_ceiling')]
def fmt(x):return f'{x:.12g}'
def label(n):
    for old,new in [('grid_grid_compact_fenced_s34','fenced34'),('grid_grid_compact_s18','compact18'),('grid_grid_square_s27','square27'),
                    ('grid_compact_fenced_s34','fenced34'),('grid_compact_s18','compact18'),('grid_square_s27','square27'),
                    ('grid_routesimp_s27','square27_simplified')]:
        if n.startswith(old):n=new+n[len(old):];break
    for s in ('_s27','_s18','_s34'):n=n.replace(s,'')
    return n
def moved(n):
    if n=='v37a':return 'incumbent, full noise'
    if n=='v37a_round':return 'actual round; perfect preparation/prefix'
    if n.startswith('round_'):return 'perfect resources; every round channel noisy'
    if n.startswith('suffix_'):return 'same retained prefix; real grid-free suffix'
    if n.endswith('perfectprep'):return 'resource-operation/idle noise off before round'
    if n.endswith('perfectwait'):return 'data idle noise off from44 to round'
    if n.endswith('perfectboth'):return 'both preceding regions perfect'
    if n.endswith('roundonly'):return 'noise from round start only'
    if n.endswith('accept_ceiling'):return 'all pre-round detectors removed; diagnostic'
    if 'routesimp' in n:return 'state-identity CX removal; full retiming'
    words=['7-hop layout' if 'compact' in n else '1-hop layout']
    if 'fenced' in n:words.append('B-preparation/verification barrier')
    if '_alap_' in n or '_both_' in n:words.append('late preparation')
    if '_guards_' in n or '_both_' in n:words.append('continuous guards')
    return '; '.join(words)
lines=[
'# SQUARE',
'Verdict: **no finalist. Gates 1–2 pass; the built and exactly priced grid families lose and fail acceptance.**',
'Stopped under the step-3 “best >= tau” branch. This closes these implementations, not the square family or all layouts.',
f'tau={TAU:.16g}; target L<tau-1e-7, A>=0.5002; J_tau=A*(L-tau). Rank only feasible builds by J_tau.',
f'Incumbent reproduced exactly: L={baseline["loss"]:.16g}, A={baseline["acceptance"]:.16g}, SHA256 {baseline["sha256"]}.',
f'Best first-order-safe grid: `{best["stem"]}.{{qasm,json}}`; L={fmt(best["loss"])}, A={fmt(best["acceptance"])}, J={fmt(best["J_tau"])}.',
f'Best grid-free square: `{sq["stem"]}.{{qasm,json}}`; L={fmt(sq["loss"])}, A={fmt(sq["acceptance"])}, J={fmt(sq["J_tau"])}. Not grid-valid.',
'',
'Gate 1: standard 28.84 p² / 2.8713361272995983e-5; square 25.6666666667 p² / 2.5558431235817117e-5;',
'eraser 25.6666666667 p² / 2.5584641585513234e-5. All three have single-fault loss <9e-19. Reviewer numbers reproduced.',
'Main-doc correction: the FINDINGS claim that every Steane-type round pays 28.84 p² is too broad; the square is a measured counterexample.',
'The actual v37a round counterfactual is 2.903230601583247e-5 at A=0.9471249113533862; early D->A at 45, other round ops>=46, waits>=45.',
f'Gate 2: the square improves the matched standard suffix by {std["loss"]-sq["loss"]:.12g} (>1e-6); eraser also passes but loses to square.',
'The common prefix is the backwards causal cone of v37a data through tick 43 plus every completed prefix detector; native MX reuse is preserved.',
'Both grid-free suffixes use 9-CX CSS encoders and all waits. Square adds an explicit three-CX logical-Z check of B; R=44.',
'',
'Grid decisions and scope:',
'',
'- Retain that prefix and move data from 44; allow up to 2 hops in the first CP layouts and 3 in the connection-length search.',
'- Standalone connected A+connected BC, and connected A+connected remaining resource space, were INFEASIBLE in the tested 2-hop/R<=60 models.',
'- A seven-square layout exists with one extra hop 22->28. Its preparation requires shared routing space; this is not an impossibility proof for other schedules.',
'- Built 64 reverse-routed CSS preparations, 64 local GF(2) preparations, and 128 state-identity simplifications; shortest routed R94, simplified R91.',
'- A connection-length CP layout uses seven hops. Its 64 routed builds reach R85 best; 64 B-fenced routes reach R92 best.',
'- The decoder-safe X/Z joint CSS CP model returned UNKNOWN after 180 s, with no solution; it provides no infeasibility certificate.',
'- Exact repair tests: delaying preparations, continuous known-state guards, their combination, and state-identity gate deletion. Kept the lowest-loss first-order-safe grid build.',
'- The faster seven-hop route has c1*p=2e-4; fencing B preparation/verification leaves 1e-4. Rejected, even though the best repaired loss is 6.646605601606709e-4.',
'- Fault witnesses have zero detector flips, X syndrome 1 and even X parity: an accepted decoder-uncorrectable X residue. A logical-Z check alone does not reject every correlated resource fault.',
'',
'Measured cost on the best first-order-safe grid (same QASM and schedule; these are overlapping counterfactuals, not redesign bounds):',
'',
f'- Full L={fmt(best["loss"])}; perfect preparation L={fmt(pp["loss"])}, A={fmt(pp["acceptance"])}; perfect data waits L={fmt(pw["loss"])}.',
f'- Both perfect L={fmt(pb["loss"])}, A={fmt(pb["acceptance"])}; round-only L={fmt(ro["loss"])}.',
f'- Relative to both-perfect: preparation alone adds {pw["loss"]-pb["loss"]:.12g}; waits alone add {pp["loss"]-pb["loss"]:.12g}; interaction {best["loss"]-pp["loss"]-pw["loss"]+pb["loss"]:.12g}.',
f'- Removing every pre-round detector gives A={fmt(ceil["acceptance"])}. This upper-bounds detector-deletion acceptance buys while retaining the fixed full square checks; it is still below 0.5002.',
'Preparation/routing and waiting consume the gain. B verification is included in preparation; its independent marginal was not isolated. No acceptance-feasible grid build exists here.',
'',
'Every exact price (L and A include all orders at p=1e-3; duplicate hashes are distinct noise experiments):',
'',
'| Saved circuit | L | A | J_tau | SHA256 prefix | What moved |',
'|---|---:|---:|---:|---|---|',
]
order=sorted(by,key=lambda n:(0 if n=='v37a' else 1 if n.startswith('round_') else 2 if n=='v37a_round' else 3 if n.startswith('suffix_') else 4,n))
for n in order:
    r=by[n];lines.append(f'| [{label(n)}]({r["stem"]}.qasm) | {fmt(r["loss"])} | {fmt(r["acceptance"])} | {fmt(r["J_tau"])} | {r["sha256"][:12]} | {moved(n)} |')
lines += ['',
'Verified: every priced QASM SHA256 and every barrier-labelled native tick checked again; exact ideal acceptance 1/loss 0 checked by the evaluator.',
f'Official fast_check at 1e6 on best first-order-safe grid: format/class/correctness all true, gates_ok=true; acceptance={v["judge"]["acceptance"]}, passed=false. MC L={v["judge"]["loss"]:.12g}, SEM={v["judge"]["sem"]:.6g}.',
'The MC acceptance does not decide eligibility; exact A does. No finalist exists, so cand/ is empty. No submissions, commits, pushes, other-lane writes or sub-agents.',
'Inferred/unverified: more economical shared-resource synthesis, prefix/layout co-design and dynamic squares may preserve the grid-free gain; this run neither demonstrates nor excludes them.',
'Files: results.json (full SHA256 keys, all experiments); builds/; logs/*.receipt.json and *.coefficients.json; verification.json; fault_witnesses.json;',
'build_rounds.py, build_suffix.py, price.py, layout_model.py, find_layout.py, route_grid.py, synthesize_grid.py, cp_prep.py, simplify_prep.py, repair_grid.py, ablate_grid.py, acceptance_ceiling.py.',
]
assert len(lines)<=100,len(lines)
(H/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(report_lines=len(lines),exact_experiments=len(rr),qasm_hashes=len(records),best_first_order_safe_grid=best['stem'],best_grid_free=sq['stem'])))
