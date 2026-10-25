import os,sys,json,hashlib,html,math
from pathlib import Path
H=Path(__file__).resolve().parent
TAU=3.789826092701952e-5
def sha(st):return hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()
def run():
    rs=json.loads((H/'results.json').read_text())
    # Recover every alias, including pre-lock legacy receipts; the saved circuit
    # hash and ordered outputs must match before a receipt is used.
    for fp in sorted((H/'logs').glob('*.price.json')):
        r=json.loads(fp.read_text());st=Path(r['stem']);assert sha(st)==r['sha256'],st
        old=rs.get(r['sha256'],{});al=sorted(set(old.get('aliases',[])+r.get('aliases',[])+[st.name]))
        rs[r['sha256']]={**r,**old,'aliases':al}
    valid=[r for r in rs.values() if 'loss' in r];invalid=[r for r in rs.values() if 'error' in r]
    for r in rs.values():
        st=Path(r['stem']);assert sha(st)==r['sha256']
        assert json.loads(st.with_suffix('.json').read_text())['data_qubits']==r.get('data_qubits',[0,20,7,10,3,22,21])
        if 'loss' in r:assert abs(r['J_tau']-r['acceptance']*(r['loss']-TAU))<1e-18
    (H/'results.json').write_text(json.dumps(rs,indent=2)+'\n')
    eligible=[r for r in valid if r['acceptance']>=.5002]
    best=min(eligible,key=lambda r:r['J_tau']);assert best['loss']>=TAU-1e-13,best
    byname={n:r for r in rs.values() for n in [Path(r['stem']).name]+r.get('aliases',[])}
    arc=json.loads((H/'archive.json').read_text());cert=json.loads((H/'archive_certificate.json').read_text())
    assert len(arc['profiles'])==30 and all(r['ideal'] for r in cert['rows'])
    comp=json.loads((H/'completions.json').read_text());cc=json.loads((H/'completion_certificate.json').read_text());assert cc['checked']==120
    catalog=json.loads((H/'a_catalog_fixed.json').read_text());guards=json.loads((H/'guards.json').read_text())
    assert all(r['stem'] in byname and 'loss' in byname[r['stem']] for fam in catalog.values() for r in fam)
    assert all(n in byname for fam in guards.values() for n in fam)
    assert all('single_fault' in byname[n] for n in ['roundtrip','swap8_2_restore','swap8_14_restore','swap8_9_restore'])
    control=byname['swap8_8_commute_funded'];base=byname['roundtrip'];nofund=byname['swap8_8_commute']
    lines=['# COMPLETE','',
      '**Verdict: no finalist in the declared five-wire completion family. Three release profiles were rebuilt and priced; the incumbent remains best.**',
      f'Best admissible circuit is the unchanged [v36k round trip](builds/roundtrip.qasm): L={base["loss"]:.16g}, A={base["acceptance"]:.16g}, Jτ=0, SHA `{base["sha256"][:12]}`.',
      f'Best feasible opened-window control: [swap8_8_commute_funded](builds/swap8_8_commute_funded.qasm), L={control["loss"]:.16g}, A={control["acceptance"]:.16g}, Jτ={control["J_tau"]:.12g}; it keeps output placement and removes six window guards plus the early q25 echo. Target L<3.759826092701952e-5 was not reached; `cand/` is empty.',
      '',
      'The fixed-variable model reproduces byte-identical QASM, all546 native operations, roles, records, lifetimes, guards, the A encoder and all56 r3 CXs. Fixed solve: OPTIMAL; baseline all-orders numbers match the requested values exactly.',
      'Window: cells [2,7,8,9,14], ticks24–26, actual incoming constraint X8 X9=+1. Exact BFS searches the prepared-subspace isometry with all120 output permutations; independent signed nine-wire purified tableaux verify every endpoint. Minimum CX: original placement3, 8↔2 four, 8↔14 five, 8↔9 six. The star graph serializes these CXs. This is a finite CNOT grammar, not a global Clifford optimum.',
      'Archive:30 distinct **actual native source-record release vectors**, each with a complete saved routed circuit, QASM hash and passing ideal check. `completion_end_archive.json` separately retains the earlier last-completion-use vectors; those were not sufficient evidence of physical cell release. Profiles are retained before suffix-score selection.',
      'Downstream methods: exact dirty-ancilla routing; on-demand placement restoration; absorbing 8→9 into the relocated data hop; independent A-role rebinding after source records; all20 verified EXENC A encoders per selected family, release-aware scheduling; the actual correlated r3 retained throughout. All35 incumbent polish edits are inherited except the explicitly opened window/A blocks. Fresh data-guard slots receive a T-aware known-state screen followed by exact validity/pricing (36/17/26 singles). All valid single-guard trials fail A≥.5002; no new guard conjunction was selected. This is not exhaustive arbitrary bundle optimization.',
      '',
      '| Relocated output | Best tested L (acceptance-failing diagnostic) | A | Restoration L | Native depth | Measured cost mechanism |',
      '|---|---:|---:|---:|---:|---|']
    for fam,label in [('swap8_2','8↔2'),('swap8_14','8↔14'),('swap8_9','8↔9')]:
        vals=[r for n,r in byname.items() if n.startswith(fam) and 'loss' in r]
        rr=min(vals,key=lambda r:r['loss']);rest=byname[fam+'_restore']
        di=rest['diagnostics'];gate=rest['loss']-di['completion_route_gates']['loss'];idle=rest['loss']-di['preround_idle']['loss']
        lines.append(f'| {label} | {rr["loss"]:.12g} | {rr["acceptance"]:.10f} | {rest["loss"]:.12g} | {rest["depth"]} | Completion+restore gate-noise removal saves {gate/1e-6:.3f}µ; pre-round-idle removal saves {idle/1e-6:.3f}µ; acceptance deficit {.5002-rest["acceptance"]:.5f}. |')
    lines += ['',
      'µ=1e-6 loss. Counterfactual differences overlap and are not additive. Gate diagnostic removes only completion/restoration operation noise; idle diagnostic removes runs on all physical cells starting at23 until depth−4. The source release/guard geometry, subsequent hops and exposure consume the gain; A catalog replacement also adds latency. These are measured costs of these rebuilds, not lower bounds on every downstream synthesis.',
      f'Opening the six guard CXs alone costs {nofund["loss"]-base["loss"]:.12g} loss and {nofund["acceptance"]-base["acceptance"]:.12g} acceptance. Removing the early q25 echo buys {control["acceptance"]-nofund["acceptance"]:.12g} acceptance for {control["loss"]-nofund["loss"]:.12g} loss. This funds the control, but cannot repair the relocated families’ much larger loss gaps.',
      'Single-fault diagnostics (not the ranking evaluator): '+ '; '.join(f'{n}: {byname[n].get("single_fault",{}).get("first_order_loss",float("nan")):.8g}' for n in ['roundtrip','swap8_2_restore','swap8_14_restore','swap8_9_restore'])+'.',
      '',
      'Verified: every numerical row below is an all-orders evaluation of the saved QASM; hashes and ordered output mappings audited. All120 synthesis endpoints and all30 archived ideal circuits pass. Independent judge1e6 gates_ok=True for the unchanged control and funded opened-window control; sampled acceptance is not used for exact ranking. Any additional best-relocated judge receipt is in `logs/`.',
      'Fixed implementation errors: the first scheduler kept an unnecessary per-wire order (one extra tick even for the no-relocation control); corrected by exact commuting dependencies. The first A extractor cut at D→A time and missed encoder gates that commute through that coupling; replaced with immutable original operation identities. Invalid A attempts remain labeled errors in results and are excluded from the physical comparison.',
      'Unverified/open: all-noisy judge runs for losing archive/A variants; a better rerouting algorithm; new B/C placements; a larger window including the q15 bottleneck, H/S or measurement-assisted completions, or a jointly redesigned blue check. The negative verdict closes this finite star-window/rebuild experiment, not the broader prefix/interface idea. No submission, commit/push, sub-agent, GPU or write outside COMPLETE; tom was read only because its race already occupied22 workers.',
      f'Ledger: {len(valid)} distinct numerically priced QASMs, {len(invalid)} rejected QASMs; aliases and failed receipts are in [results.json](results.json). Jτ=A(L−τ); admissible ranking always requires A≥.5002. Full precision and counterfactuals are keyed by the full QASM SHA256.',
      '',
      '<table><thead><tr><th>Circuit</th><th>L</th><th>A</th><th>Jτ</th><th>SHA256 prefix</th><th>What moved</th></tr></thead><tbody>']
    rows=[]
    for r in sorted(valid,key=lambda r:Path(r['stem']).name):
        n=Path(r['stem']).name
        if '_g' in n:desc='known-state data guard'
        elif '_a' in n:desc='A encoder replaced; release-aware timing'
        elif 'restore' in n:desc='phase placement + restored locality'
        elif 'rb2' in n or 'rebind' in n:desc='phase placement + fresh A roles'
        elif 'funded' in n:desc='early q25 echo removed'
        elif 'swap' in n:desc='phase completion + routed full suffix'
        else:desc='v36k control'
        al=len(r.get('aliases',[]));label=n+(f' (+{al-1} aliases)' if al>1 else '')
        rows.append(f'<tr><td><a href="builds/{n}.qasm">{html.escape(label)}</a></td><td>{r["loss"]:.13g}</td><td>{r["acceptance"]:.12g}</td><td>{r["J_tau"]:.10g}</td><td>{r["sha256"][:12]}</td><td>{desc}</td></tr>')
    lines += [''.join(rows[i:i+4]) for i in range(0,len(rows),4)]
    lines += ['</tbody></table>','','Files: `model.json`, `completion_certificate.json`, `completions.json`, `archive.json`, `archive_certificate.json`, `a_catalog_fixed.json`, `guards.json`, `results.json`, `builds/`, `logs/`; builders/evaluators are the lane’s `.py` files.']
    assert len(lines)<=100,len(lines)
    (H/'REPORT.md').write_text('\n'.join(lines)+'\n')
    audit=dict(priced=len(valid),rejected=len(invalid),archive_profiles=len(arc['profiles']),independent_completion_checks=cc['checked'],report_lines=len(lines),best_admissible=best,all_hashes_verified=True)
    (H/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k!='best_admissible'}))
if __name__=='__main__':run()
