"""Verify content-addressed receipts and render the bounded lane report."""
import hashlib,json
from pathlib import Path
from model import HERE
from price import TAU

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.loads((HERE/'results.json').read_text())
aliases={}
for p in (HERE/'builds').glob('*.qasm'):aliases.setdefault(sha(p),[]).append(str(p.relative_to(HERE)))
for fp,r in rows.items():
    assert sha(HERE/r['path'])==fp==r['sha256']
    result=json.loads((HERE/r['log']).read_text().splitlines()[-1])
    assert result['loss']==r['loss'] and result['acceptance']==r['acceptance']
    assert r['J_tau']==r['acceptance']*(r['loss']-TAU)
    assert json.loads((HERE/r['path']).with_suffix('.json').read_text())['data_qubits']==r['data_qubits']
    for f,h in r['evaluator'].items():assert sha(HERE/'sparse'/f)==h
    r['aliases']=sorted(aliases[fp])
fp=sha(HERE/'builds/del_echo14.qasm')
rows[fp]['fast_check']=dict(shots=1000000,seed=0,passed=True,loss=4.889272935180194e-5,sem=8.64e-6,
    acceptance=.501097,seconds=12.7,procs=1,qasm_sha256=fp,receipt='logs/del_echo14.fast_check.txt')
(HERE/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
down=[json.loads((HERE/'logs'/f'{n}_downstream.json').read_text()) for n in ('if_d','if_hde','if_hdej')]
assert all(r['best']['loss']>TAU for r in down)
best=min((r for r in rows.values() if r['path']!='builds/v36h.qasm'),key=lambda r:r['J_tau'])

lines=[
'# IFACE',
'',
'**Verdict: no finalist. Three downstream builds are priced and all lose to τ; stop rule reached for the tested interface family.**',
f'Baseline reproduced exactly: L={TAU}, A=0.5016415049479505, SHA `c8e8a44e104a`. The fixed-variable model reproduces all 503 native operations, 77 lifetimes, classical records, guards, and all 56 r3 CXs; byte-identical QASM and an independent judge-schedule comparison pass.',
f'Best modified circuit: [{best["path"]}]({best["path"]}), L={best["loss"]}, A={best["acceptance"]}, Jτ={best["J_tau"]}; removes the known-state CX13→14 at 32. Judge 1e6 seed0 PASS: sampled loss 4.889272935180194e-5 ±8.64e-6, A=.501097, 12.7 s. It is above τ, so `cand/` is empty.',
'',
'Decisions: use exact prepared-subspace equivalence for local completion, preserve the correlated r3 and actual records, and retain release diversity before selecting downstream builds. Selected the cheapest meaningful hop interface (`if_d`), both-hop release (`if_hde`), and earliest q4 release (`if_hdej`); selection beyond Jτ used distinct release opportunities, not a claim of global optimality.',
'Archive: 24 distinct occupied-cell schedules, but only eight listed source-release vectors. All have ideal correctness verified, fixed D=[0,20,7,10,3,22,21], R44, and q15 released at 40. This does **not** supply 20 different output geometries. The four-to-six-wire completion scan found only guard/pair shortcuts; none replaces the D6 8→9→15→21 spine.',
'The downstream builds retain the A encoder and r3 and rebuild available known-state guards/initialization times. Menus screened: 7/7, 10/13, 10/20 slots, followed by joint pricing; this is a ranked greedy search, not an exhaustive suffix synthesis.',
'',
'| Downstream interface | Final L | A | Jτ | Remaining loss above τ | Protection recovered |',
'|---|---:|---:|---:|---:|---:|']
for r in down:
    b=r['best'];lines.append(f'| [{r["interface"]}](builds/{r["interface"]}_downstream.qasm) | {b["loss"]:.15e} | {b["acceptance"]:.12f} | {b["J_tau"]:.9e} | {b["loss"]-TAU:.9e} | {r["base"]["loss"]-b["loss"]:.9e} |')
lines += [
'',
'Measured blockers by approach: deleting the q10 hop completion costs +5.9137411e-8; deleting the extra q15→16 completion costs +5.2555363e-8; commuting the blue c64 readout from 37 to 35 costs +5.5974658e-8. Their joint earlier-release builds recover protection as shown above, but retain the limiting q15 release. These are finite circuit comparisons, not additive channel decompositions.',
'Verified: every table price is an unchanged all-orders evaluation of a saved circuit; all QASM hashes, ordered outputs, evaluator hashes and log totals were checked. All archive members and completed downstream circuits pass the independent ideal checker. Only the best changed circuit received judge1e6; the three losing downstream builds have no noisy judge receipt.',
'Inferred/open: q15 is the obstruction for this retained spine, not a bound on different completions. Different final data placements, a genuinely different phase-routing completion, and re-synthesized A/r3 on new cells remain unbuilt. Therefore this report closes the tested guard/completion/retiming family, **not the wider geometry-changing brief**. No claim that all prefix-interface approaches are exhausted.',
'Files: [PREFIX.md](PREFIX.md) (timeline/interpretation), [model.json](model.json), [archive.json](archive.json), [results.json](results.json), `inputs/completions.json`, `inputs/native_roundtrip.json`, `builds/`, `logs/`; builders `model.py`, `completion.py`, `archive.py`, `downstream.py`, `price.py`. Work ran on zebra with thread caps and ≤3 evaluation workers; hippo was not used. No submission, commit, push, or write outside IFACE.',
'',
'Every distinct priced circuit follows (aliases and full precision in `results.json`). h=remove CX15→16@33; d=remove CX10→4@34; e=remove CX13→14@32 and CX20→26@29,30; j=remove CX11→10@30–32. `if_*` also retimes the prefix; blue advances c64. Jτ=A(L−τ).',
'',
'| Circuit | L | A | Jτ | SHA256 prefix | What changed |',
'|---|---:|---:|---:|---|---|']
for r in rows.values():
    m=r['moved']
    if isinstance(m,dict):
        if m['family']=='state_specific_completion':desc=m['cut']+('; early blue' if m['early_blue'] else '')
        elif 'slot' in m:
            s=m['slot'];desc=f'{m["interface"]}: {s["kind"]} {s["edge"][0]}→{s["edge"][1]}@{s["t"]}'
        else:desc=m.get('interface','')+': joint '+', '.join(f'{s["edge"][0]}→{s["edge"][1]}@{s["t"]}' for s in m.get('slots',[]))
    else:desc=m
    name=Path(r['path']).stem
    lines.append(f'| [{name}]({r["path"]}) | {r["loss"]:.12e} | {r["acceptance"]:.12f} | {r["J_tau"]:.8e} | `{r["sha256"][:12]}` | {desc} |')
assert len(lines)<=100,len(lines)
(HERE/'REPORT.md').write_text('\n'.join(lines)+'\n')
(HERE/'inputs/receipt_audit.json').write_text(json.dumps(dict(ok=True,unique_priced_qasms=len(rows),report_lines=len(lines),
    baseline_sha256=sha(HERE/'builds/v36h.qasm'),best_modified_sha256=fp,
    downstream=[dict(interface=r['interface'],sha256=r['best']['sha256'],loss=r['best']['loss'],acceptance=r['best']['acceptance']) for r in down]),indent=2)+'\n')
print(json.dumps(dict(prices=len(rows),report_lines=len(lines),best_modified=best['path'],best_loss=best['loss'])))
