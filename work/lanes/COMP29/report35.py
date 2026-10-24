"""Live v35b report, including acceptance-only handoff before MC completes."""
import json,re,os,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
def read(p,default=None):return json.loads(p.read_text()) if p.exists() else default
def atomic(p,s):
    tmp=p.with_name(p.name+f'.tmp.{os.getpid()}');tmp.write_text(s);os.replace(tmp,p)
def moment_delta(a,b):
    if not a.get('results') or not b.get('results'):return None
    assert [x['key'] for x in a['results']]==[x['key'] for x in b['results']]
    return max(abs(x['value']/a['acceptance']-y['value']/b['acceptance']) for x,y in zip(a['results'],b['results']))
def refresh():
    manifests=['v35_checks.json','v35_prep_timing.json','v35_ports.json','v35_readouts.json','v35_independent_joint.json','v35_combinations.json','v35_guard_exchange.json','v35_tailguards.json','v35_prep_guards.json']
    rows={}
    for mf in manifests:
        for r in read(H/mf,[]):rows[r['stem']]=dict(r)
    base=read(H/'h_base.allorders.json',{});threshold=read(H/'h_v35a.allorders.json',{}).get('loss',4.393527676042078e-5)
    scalar=[];finalists=[]
    for n,r in rows.items():
        a=r['allorders']=read(H/(n+'.allorders.json'),{});g=r['gate']=read(H/(n+'.gate.json'),{});m=r['mc']={};p=H/(n+'.mc.log')
        if p.exists():
            s=p.read_text();match=re.search(r' mean (\S+)',s)
            if match:m['mean']=float(match[1])
            m['seeds']={int(z[1]):dict(loss=float(z[2]),acceptance=float(z[3])) for z in re.finditer(r' (0|1000|2000) (\S+) ± .* acc (\S+)',s)}
        if 'loss' in a and 'loss' in base:
            r['loss_delta']=a['loss']-base['loss'];r['acceptance_delta']=a['acceptance']-base['acceptance'];r['max_normalized_moment_delta']=moment_delta(a,base)
            if abs(r['loss_delta'])<=1e-15 and (r['max_normalized_moment_delta'] is not None and r['max_normalized_moment_delta']<=3e-13) and r['acceptance_delta']>1e-9 and r.get('family') in ('detector','omit','reset','prep_timing','independent_joint'):scalar.append(r)
        if a.get('loss',1)<threshold and a.get('acceptance',0)>=.5005 and g.get('passed') and g.get('speed',{}).get('classification')=='FAST' and 'mean' in m and set(m.get('seeds',{}))=={0,1000,2000} and m['seeds'][0]['acceptance']>=.5:finalists.append(r)
    finalists.sort(key=lambda r:r['allorders']['loss']);scalar.sort(key=lambda r:-r['acceptance_delta']);status=read(H/'v35_status.json',{'state':'RUNNING'})['state']
    lines=['# COMP29 — v35b acceptance recovery and composition','',f'**Status: {status}.** Acceptance floor: **0.5005**. Finalist threshold: v35a, **{threshold:.12g}**. Source of v35b is ST2’s `restore_181_182_188`; the supplied v35b QASM is frozen as `h_base`.','',
    '## Finalists below v35a','', '| Stem | All-orders 1−F | Acceptance | Judge | Speed | MC seed 0 / 1000 / 2000 | MC mean |','|---|---:|---:|---|---|---|---:|']
    for r in finalists:
        a,g,m=r['allorders'],r['gate'],r['mc'];lines.append(f"| [{r['stem']}]({r['stem']}.qasm) | {a['loss']:.12g} | {a['acceptance']:.12g} | PASS / {g['acceptance']:.6f} | FAST / {g['judge_seconds']:.2f}s per 1e6 | "+' / '.join(f"{m['seeds'][s]['loss']:.8g}" for s in [0,1000,2000])+f" | {m['mean']:.8g} |")
    if not finalists:lines+=['','No new fully gated finalist yet.']
    if finalists:
        r=finalists[0];n=r['stem'];assert hashlib.sha256((H/(n+'.qasm')).read_bytes()).hexdigest()==r['sha256']==r['allorders']['source_sha256']
        for ext in ['.qasm','.json']:atomic(H/('best'+ext),(H/(n+ext)).read_text())
        atomic(H/'best.verification.json',json.dumps(r,indent=2)+'\n')
    lines+=['','## Acceptance-only handoff for ST2','',
    'Rows below preserve all-orders conditional loss within 1e-15 and every normalized acceptance/decoder moment within 3e-13. Detector/check removals are distinguished from reset timing. Numerical singleton neutrality is not assumed to compose: every exported joint is repriced. Physical factorization certificates are recorded separately where established.','',
    '| Stem | Method | Removed check / timing | Loss delta | Acceptance recovered | Final acceptance | Max normalized moment delta |','|---|---|---|---:|---:|---:|---:|']
    for r in scalar:lines.append(f"| [{r['stem']}]({r['stem']}.qasm) | {r.get('family','')} | {json.dumps(r.get('edits',[]))} | {r['loss_delta']:.3g} | {r['acceptance_delta']:.12g} | {r['allorders']['acceptance']:.12g} | {r['max_normalized_moment_delta']:.3g} |")
    if not scalar:lines+=['','No acceptance-only v35b change has completed its full comparison yet.']
    if base:lines+=['',f"Reproduced v35b: **{base['loss']:.12g}**, acceptance **{base['acceptance']:.12g}**, 210 CX, native depth **47** (actual source schedule). Its available acceptance over the floor is {base['acceptance']-.5005:.8f}."]
    lines+=['','## Candidate prices','',f"{len(rows)} built stems; {sum('loss' in r['allorders'] for r in rows.values())} completed prices. Sparse code is copied unchanged from MAIN, with output confined to this lane. No gain additivity is assumed.",'',
    '| Stem | Family / edit | CX | All-orders 1−F | Acceptance | Judge / speed | MC mean |','|---|---|---:|---:|---:|---|---:|']
    missing='—' if status=='COMPLETE' else 'pending';fmt=lambda x:f'{x:.12g}' if x is not None else missing
    for r in sorted(rows.values(),key=lambda r:r['allorders'].get('loss',1)):
        a,g,m=r['allorders'],r['gate'],r['mc'];judge=('PASS / '+g['speed']['classification']) if g.get('passed') else a.get('error','not selected' if status=='COMPLETE' else 'pending')
        lines.append('| `%s` | %s | %s | %s | %s | %s | %s |'%(r['stem'],r.get('family',json.dumps(r.get('edits',[]))),r.get('cx',''),fmt(a.get('loss')),fmt(a.get('acceptance')),judge,fmt(m.get('mean'))))
    notes=H/'NOTES_v35.md'
    if notes.exists():lines+=['',notes.read_text()]
    lines+=['','Earlier rounds are archived in REPORT_v34m.md, REPORT_v30f.md and REPORT_v29c.md. No credentials, submissions, commits, pushes or collaboration tools are used.','',f"Best finalist: **{finalists[0]['stem']}**." if finalists else 'Best finalist: pending; v35b retained as control.']
    atomic(H/'REPORT.md','\n'.join(lines)+'\n');atomic(H/'v35_results.json',json.dumps(list(rows.values()),indent=2)+'\n');atomic(H/'v35_acceptance_only.json',json.dumps(scalar,indent=2)+'\n')
    return dict(candidates=len(rows),priced=sum('loss' in r['allorders'] for r in rows.values()),scalar=[r['stem'] for r in scalar],finalists=[r['stem'] for r in finalists])
if __name__=='__main__':print(refresh())
