import json,math,re
from pathlib import Path
H=Path(__file__).resolve().parent
def read(p,default=None):
    return json.loads(p.read_text()) if p.exists() else default
rows=read(H/'manifest.json',[])+read(H/'bcfb_manifest.json',[])
results=[]
for r in rows:
    n=r['stem'];s=read(H/(n+'.screen.json'),{});e=read(H/(n+'.exact.json'),{});g=read(H/(n+'.gate.json'),{});a=read(H/(n+'.allorders.json'),{})
    mc={}
    p=H/(n+'.mc.log')
    if p.exists():
        txt=p.read_text();m=re.search(r' mean (\S+)',txt)
        if m:mc['mean']=float(m[1])
        mc['seeds']={int(m[1]):dict(loss=float(m[2]),acceptance=float(m[3])) for m in re.finditer(r' (0|1000|2000) (\S+) ± .* acc (\S+)',txt)}
        m=re.search(r' check (True|False)',txt)
        if m:mc['check']=m[1]=='True'
    results.append(dict(r,screen=s,exact=e,gate=g,allorders=a,mc=mc))
def eligible(r):
    return r['gate'].get('passed') and r['screen'].get('exp_minus_A1',0)>=.5002
ranked=sorted([r for r in results if eligible(r) and r['allorders'].get('validated')],key=lambda r:r['allorders']['loss'])
mc_ranked=sorted([r for r in results if eligible(r) and 'mean' in r['mc'] and len(r['mc'].get('seeds',{}))==3],key=lambda r:r['mc']['mean'])
best=ranked[0] if ranked else mc_ranked[0] if mc_ranked else None
screened=sorted([r for r in results if eligible(r)],key=lambda r:r['screen'].get('total',1))
lines=['# COMP29','', '**Status: RUNNING.** Complete native subset enumeration and reference verification are in progress. No submission, commit, push, credential access, or subagent use.','',
'Goal: lowest verified true-mean conditional 1−F among the composed v29c edits, with acceptance ≥0.5 and FAST execution. No additivity assumption is used.', '',
f"Built {len(results)} candidates; {sum(bool(r['screen']) for r in results)} Fourier third-order screens; {sum(bool(r['exact']) for r in results)} unchanged exact2 CLI receipts; {sum(bool(r['gate']) for r in results)} speed/judge receipts; {sum(r['gate'].get('passed',False) for r in results)} full 1e6 passes; {sum(bool(r['allorders']) for r in results)} all-orders results; {sum('mean' in r['mc'] for r in results)} complete MC means.", '',
'## Methods and scope','',
'The nine elementary choices are copy4, timing10, late q1 commute, extra early q19 X check, BC q11 reset→measure, final 14→15 readout edge, the two ST1 feedback timing moves, and known-zero q5 measurements at t37/t38. All 512 subsets are emitted, including both q5 measurements together. Copy4 is reviewer #1 itself, not a second independent edit. q19 already has an early check in v29c; the LNS2 extra repeated check is nevertheless priced independently.', '',
'Native units, per-wire precedence, nearest-neighbour assertions, terminal measurement identity, detector parities and fresh-helper barrier coverage are checked at emission. Every build is fully repriced; no marginal scores are added. `manifest.json` contains provenance and QASM hashes. `build_errors.json` records structural failures. SEPBC t37/t38 singleton prices reproduce its supplied native ports.', '',
'The LNS normalizer’s hardcoded c[256] register cannot hold v29c records through c[263]; the local adapter sizes the classical register from actual records. The corrected native copy4 rewrite repairs every detector containing the old terminal q25 record and moves q29/q28 readings after the copy layer. ST2’s older review_copy import is not used. ST1 feedback changes CX9→15 at t29→30 and MX9 at t30→31.', '',
'`screen.json` uses BCPOL’s existing exact categorical-channel Fourier contraction. `exact.json` is a separate unchanged `work/lanes/EVAL/exact2.py --third` CLI run (the task’s `work/EVAL/exact2.py` path does not exist). Full-precision screen values are shown below; a CLI receipt is explicitly marked. New CLI receipts retain the original CLI printed precision. The baseline independent CLI agrees within 3.2e-18.', '',
'All-orders ranking uses the unchanged BCPOL five-projector evaluator, copied byte-for-byte into COMP29 to keep owl dependencies/cache writes local. Its per-circuit validation checks rotation axes, decoder observables, categorical channel multisets, 1,024 projector sectors, and a nonzero-error three-channel enumeration. Rejected width/contract checks are recorded, not interpreted as scores. Speed uses the unchanged XTIM predictor; the full 1e6 gate uses fast_check. Three 1e8 MC seeds use the unchanged MAIN/spec/mc3.py.', '',
'BCFB’s rank-6 clean preparations replace v29c’s rank-5 endpoint through the B→C boundary; their complete output contract and detector frame are rebuilt. The original ±2 exterior timing window was infeasible. A ±12 window permits retiming the q4 release and yields native R48 candidates. The full judge, rather than the local preparation contract alone, decides validity. BCFB init checks preserve basis and record-frame parity. Mutually exclusive preparation replacements are not combined with each other. q5 checks are added only where symbolic CSS propagation proves the same known-zero opportunity.', '',
'## Results','',
'Third order is conditional 1−F through cubic order. `A` is exp(−A1); threshold 0.5002. `CLI` means the unchanged exact2 reference has completed. “screen only” is not an independent CLI claim. Judge acceptance is the actual 1e6 seed-0 measurement. MC columns list the three-seed mean when complete; individual seeds remain in the adjacent log. Speed is the XTIM prediction in seconds per 1e6, followed by actual judge wall time. Pending fields are unfinished, not passes.', '',
'| Stem | Edits | Third order | A | Reference | Judge / acc | Speed | All-orders | MC mean |',
'|---|---|---:|---:|---|---|---|---:|---:|']
for r in sorted(results,key=lambda r:(r['screen'].get('total',1),r['stem'])):
    s,e,g,a,mc=(r[k] for k in ['screen','exact','gate','allorders','mc'])
    fmt=lambda x:f'{x:.10g}' if x is not None else 'pending'
    judge=('PASS' if g.get('passed') else 'FAIL')+f" / {g.get('acceptance',0):.6f}" if 'passed' in g else g.get('error','pending')
    sp=g.get('speed',{});speed=f"{sp['classification']} {sp['median_seconds_per_1e6']:.2f}" if sp else 'pending'
    if 'judge_seconds' in g:speed+=f" / {g['judge_seconds']:.2f}"
    lines.append('| `%s` | %s | %s | %s | %s | %s | %s | %s | %s |'%(r['stem'],' + '.join(r['edits']) or 'v29c control',fmt(s.get('total')),fmt(s.get('exp_minus_A1')),'CLI' if e.get('unchanged_cli') else 'screen only',judge,speed,fmt(a.get('loss')),fmt(mc.get('mean'))))
lines+=['','## Selection and limits','']
if best:
    metric='all-orders' if best['allorders'] else '3-seed MC'
    val=best['allorders'].get('loss',best['mc'].get('mean'))
    lines += [f"Current ranked candidate: **{best['stem']}**, {metric} **{val:.12g}**. Final designation requires its complete CLI and MC receipts and completion of the relevant comparisons."]
else:lines+=['True-mean finalist ranking is pending.']
if screened:lines+=[f"Best completed 1e6-passing third-order screen: `{screened[0]['stem']}`, {screened[0]['screen']['total']:.12g}."]
lines+=['','The first c167 and c1e7 serializations fail the 1e6 acceptance draw despite passing the proxy; those failures are retained. No failed gate is relabeled as a pass. Conditional-error performance and acceptance are ranked separately. Server execution has not been tested. This finite composition search is not a global optimum proof.','',f"Best finalist: **{best['stem']} (provisional while the sweep is running)**." if best else 'Best finalist: **pending true-mean verification**.']
(H/'REPORT.md').write_text('\n'.join(lines)+'\n')
(H/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(dict(candidates=len(results),screens=sum(bool(r['screen']) for r in results),exact=sum(bool(r['exact']) for r in results),gates=sum(bool(r['gate']) for r in results),best=None if best is None else best['stem']))
