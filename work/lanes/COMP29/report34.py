"""Current v34m receipts and fully gated finalists; no inherited verdicts."""
import json,re,hashlib,shutil,os
from pathlib import Path
H=Path(__file__).resolve().parent
def read(p,default=None):return json.loads(p.read_text()) if p.exists() else default
def atomic(p,text):
    tmp=p.with_name(p.name+f'.tmp.{os.getpid()}');tmp.write_text(text);os.replace(tmp,p)
def refresh():
    manifests=['v34_manifest.json','v34_bell.json','v34_bell2.json','v34_bridge.json','v34_combinations.json','v34_other.json','v34_readout.json','v34_echo.json','v34_echo_drop.json','v34_drop43.json']
    rows={}
    for mf in manifests:
        for row in read(H/mf,[]):rows[row['stem']]=dict(row)
    for n,r in rows.items():
        r['allorders']=read(H/(n+'.allorders.json'),{});r['gate']=read(H/(n+'.gate.json'),{})
        p=H/(n+'.mc.log');r['mc']={}
        if p.exists():
            text=p.read_text();m=re.search(r' mean (\S+)',text)
            if m:r['mc']['mean']=float(m[1])
            r['mc']['seeds']={int(m[1]):dict(loss=float(m[2]),acceptance=float(m[3])) for m in re.finditer(r' (0|1000|2000) (\S+) ± .* acc (\S+)',text)}
    base=read(H/'g_base.allorders.json');candidates=[]
    for r in rows.values():
        a,g,m=r['allorders'],r['gate'],r['mc']
        if a.get('loss',1)<base['loss'] and a.get('acceptance',0)>=.5005 and g.get('passed') and g.get('speed',{}).get('classification')=='FAST' and 'mean' in m and set(m.get('seeds',{}))=={0,1000,2000} and m['seeds'][0]['acceptance']>=.5:
            sha=hashlib.sha256((H/(r['stem']+'.qasm')).read_bytes()).hexdigest();assert sha==a['source_sha256']==r['sha256'];candidates.append(r)
    candidates.sort(key=lambda r:r['allorders']['loss'])
    status=read(H/'v34_status.json',{'state':'RUNNING'})['state']
    lines=['# COMP29 — v34m terminal decoder search','',f'**Status: {status}.** All-orders acceptance floor: **0.5005**. Ranking uses the unchanged MAIN sparse evaluator, relocated into this lane so every output stays here.','',
    '## Finalists beating v34m','', '| Stem | All-orders 1−F | Improvement | All-orders acceptance | Judge / measured acceptance | XTIM | MC seed 0 / 1000 / 2000 | MC mean |','|---|---:|---:|---:|---|---|---|---:|']
    for r in candidates:
        n=r['stem'];a,g,m=r['allorders'],r['gate'],r['mc'];improvement=100*(1-a['loss']/base['loss'])
        host='jerry' if n=='g_edge_28_29' else 'tom'
        lines.append(f"| [{n}]({n}.qasm) | {a['loss']:.12g} | {improvement:.6g}% | {a['acceptance']:.12g} | PASS / {g['acceptance']:.6f} | FAST; {g['judge_seconds']:.2f} s/1e6 on {host} | "+' / '.join(f"{m['seeds'][s]['loss']:.8g}" for s in [0,1000,2000])+f" | {m['mean']:.8g} |")
    if not candidates:lines+=['','No completed beating finalist yet.']
    if candidates:
        best=candidates[0];n=best['stem']
        for ext in ['.qasm','.json']:
            text=(H/(n+ext)).read_text();target=H/('best'+ext)
            if not target.exists() or target.read_text()!=text:atomic(target,text)
        atomic(H/'best.verification.json',json.dumps(best,indent=2)+'\n')
        lines+=['',f"Delivery: [best.qasm](best.qasm) / [best.json](best.json) = **{n}**."]
    lines+=['','## Baseline and scope','',f"Frozen v34m (`g_base`): **{base['loss']:.12g}**, acceptance **{base['acceptance']:.12g}**, 207 CX, native depth 48. This was independently reproduced by the sparse evaluator. The baseline’s inherited JSON includes older A-only counts; all new candidate metadata uses its actual emitted circuit counts and no inherited verification verdicts.",'',
    'B geometric obstruction: retaining its three X-check rows requires a new B Z flag to have B support in the orthogonal code. Every nonzero such support spans at least five grid edges, even if every grid cell can be a helper. A new terminal single-qubit flag pulled back through at most three nearest-neighbor CXs cannot have that support. `v34_B_geometry_certificate.json` records all 15 nonzero codewords. This excludes the terminal 1–3-CX form, not earlier instruments or rewrites that borrow existing gates.','',
    'The complete connected search on the 21 existing terminal readout cells covered 44 one-CX, 268 two-CX and 2,364 three-CX networks. Twelve expose an independent A flag; none exposes a B flag. C’s current detector restrictions span all seven Z readouts, so their re-encoding can change noisy rejection but adds no independent ideal Z information. Every old detector row is conjugated through each decoder and re-expressed; a proposed extra flag is added only on a column absent from every retained row. The sparse frontend checks noiseless determinism and ideal loss before evaluating all 73 moments.','',
    'The alternative B/C endpoint search commutes or reverses the existing Bell readout so its parity check can occur after B→data. Retiming fixes the prefix through t40 and preserves native wire precedence inside depth 48. Variants also test removal of the two existing readout edges with exact detector repair. Infeasible schedules and blocked CX cancellations have explicit build-error receipts.','',
    'Removing the intermediate q16 Z check at t28 (c43) preserves the first checked projection at t27 (c270) and the final one at t30 (c266). Between them q16 has no interaction with another qubit. Its intervening noise is therefore an independent scalar acceptance factor; the final post-measurement state and conditional data state are unchanged. The exact predicted acceptance multiplier is **1.0010018919641532**. Four independent all-orders runs reproduce that multiplier and preserve loss within 2.3e-16 (`v34_drop43_validation.json`). This recovers about 0.000502 acceptance without claiming a fidelity gain. It pays for both useful readout edges, whose joint score is evaluated directly.','',
    'The best delivery is v34m + CX14→15 and CX28→29 at t46, their Z readouts at t47 with detector-row repair, and removal of c43 with c266’s parity simplified. It has **209 CX, native depth 48**, and 66 detectors. The full 243-case product of five readout-edge choices covers keeping/removing/reversing the existing edges and both orientations of each added edge. The unscreened joint winner originally had acceptance 0.50040069; removing c43 raises it above the requested floor.','',
    'Longer B logical-Z decoders were also built for the B6/B13/B26 representative, including cancellation against existing gates. Their ideal checks pass, but even the best tested longer decoder has loss about 3.62e-4 and acceptance below 0.5. The delayed B/C endpoint checks also worsen loss. The reversed final blue Bell readout reproduces the baseline exactly. Seven echo-readout helper copies, acceptance-recovery variants, and combinations with the leading readout pair are fully priced; none provides a better eligible result.','',
    'Independent model audit on v34m, the A14→A15 finalist and the combined delivery matches every categorical noise-channel signature, rotation axis and decoder observable against the actual judge-based EVAL model. Thirty-two quantum-table cross-checks per circuit have zero discrepancy. The unchanged sparse evaluator’s source hashes are recorded in `v34_evaluator_hashes.json`; its cutoff omission bound for the winner is 1.24e-14, excluding ordinary floating-point roundoff. The all-orders difference between finalists is much smaller than single-seed Monte Carlo noise, so the specified all-orders ranking decides.','',
    f"Receipts: {len(rows)} built candidate stems; {sum('loss' in r['allorders'] for r in rows.values())} complete all-orders prices; {sum(bool(r['allorders'].get('byte_identical_reference')) for r in rows.values())} prices reuse a byte-identical QASM receipt. Build failures are retained separately. Preliminary endpoint-scheduling errors used an overbroad repeated-gate selector; the occurrence-specific builder in v34_bell2 corrects it, and those earlier infeasibility messages are not used as exclusions.",'',
    '## Candidate prices','', '| Stem | Edits | CX | All-orders 1−F | All-orders acceptance | Judge | Speed | MC mean |','|---|---|---:|---:|---:|---|---|---:|']
    for r in sorted(rows.values(),key=lambda r:r['allorders'].get('loss',1)):
        a,g,m=r['allorders'],r['gate'],r['mc'];sp=g.get('speed',{});missing='—' if status=='COMPLETE' else 'pending';fmt=lambda x:f'{x:.12g}' if x is not None else missing
        judge=('PASS' if g['passed'] else 'FAIL') if 'passed' in g else a.get('error','not a finalist' if status=='COMPLETE' else 'pending')
        lines.append('| `%s` | %s | %s | %s | %s | %s | %s | %s |'%(r['stem'],json.dumps(r.get('edits',[])),r.get('cx',''),fmt(a.get('loss')),fmt(a.get('acceptance')),judge,sp.get('classification',missing),fmt(m.get('mean'))))
    lines+=['','Older campaigns are superseded and preserved in `REPORT_v29c.md` and `REPORT_v30f.md`. Their cancelled jobs are not confirmations. No credentials, submission, commit, push or agent delegation were used.','',f"Best finalist: **{candidates[0]['stem']}**." if candidates else 'Best finalist: **none yet; baseline v34m retained**.']
    atomic(H/'REPORT.md','\n'.join(lines)+'\n');atomic(H/'v34_results.json',json.dumps(list(rows.values()),indent=2)+'\n')
    return dict(candidates=len(rows),priced=sum('loss' in r['allorders'] for r in rows.values()),finalists=[r['stem'] for r in candidates])
if __name__=='__main__':print(refresh())
