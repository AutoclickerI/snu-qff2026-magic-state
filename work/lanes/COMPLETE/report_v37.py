"""Audited, current report including the preserved v36k experiment cohort."""
import json,hashlib,html,re
from pathlib import Path
H=Path(__file__).resolve().parent
TAU=3.761821654835085e-5;TARGET=TAU-1e-7
def sha(st):return hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()
def run():
    rs=json.loads((H/'results.json').read_text());history=json.loads((H/'history_v36k/results.json').read_text())
    for fp in sorted((H/'logs').glob('*.price.json')):
        receipt=json.loads(fp.read_text());st=Path(receipt['stem']);digest=sha(st);assert digest==receipt['sha256'],st
        current=rs.get(digest,{})
        aliases=sorted(set(current.get('aliases',[])+receipt.get('aliases',[])+[st.name]))
        rs[digest]={**receipt,**current,'aliases':aliases}
    for digest,r in rs.items():
        st=Path(r['stem']);assert sha(st)==digest
        data=json.loads(st.with_suffix('.json').read_text())['data_qubits']
        assert data==r.get('data_qubits',data)
        for alias in r.get('aliases',[]):
            p=H/'builds'/alias;assert sha(p)==digest
            assert json.loads(p.with_suffix('.json').read_text())['data_qubits']==data
        if 'loss' in r:
            r.update(tau=TAU,J_tau=r['acceptance']*(r['loss']-TAU))
            if digest in history:r['J_v36k']=history[digest]['J_tau']
    (H/'results.json').write_text(json.dumps(rs,indent=2)+'\n')
    numeric=[r for r in rs.values() if 'loss' in r];bad=[r for r in rs.values() if 'error' in r]
    names={n:r for r in rs.values() for n in [Path(r['stem']).name]+r.get('aliases',[])}
    current=[r for r in numeric if Path(r['stem']).name.startswith('v37')]
    eligible=[r for r in current if r['acceptance']>=.5002]
    best=min(eligible,key=lambda r:r['J_tau']);assert best['loss']<TARGET,best
    finals=json.loads((H/'finalists_v37.json').read_text());cert=next(r for r in finals if r.get('sha256')==best['sha256'] and r.get('eligible'))
    assert cert['judge']['gates_ok'] and cert['judge']['seconds']<=20
    assert sha(Path(cert['candidate']))==best['sha256']
    archive=json.loads((H/'archive_v37.json').read_text());assert len(archive['profiles'])>=20
    for p in archive['profiles']:
        assert p['ideal'] and sha(H/'builds'/p['stem'])==p['sha256']
        assert p['stem'] in names and 'loss' in names[p['stem']]
    manifests=['v37_joint_names.json','v37_handoff_names.json','v37_handoff_best_names.json','v37_neighbor_names.json','v37_prefix_finish_names.json','v37_read14_names.json']
    for f in manifests:
        for name in json.loads((H/f).read_text()):assert name in names,(f,name)
    md=json.loads(Path(best['stem']).with_suffix('.json').read_text());candrel=Path(cert['candidate']).relative_to(H)
    readcells=', '.join('q'+str(q) for q in sorted(z['q'] for z in md.get('handoffs',[])))
    base=names['v37a_roundtrip'];oldbase=names['roundtrip']
    improvement=TAU-best['loss'];margin=TARGET-best['loss']
    text=['# COMPLETE','',
      '**Verdict: VERIFIED FINALIST; the completion contract is met for the tested families and final completion-repair neighborhood.**',
      f'Best: [{candrel.name}]({candrel}.qasm), L={best["loss"]:.16g}, A={best["acceptance"]:.16g}, Jτ={best["J_tau"]:.15g}; SHA256 `{best["sha256"]}`. {md["cx"]}CX, {md["native_depth"]} native ticks.',
      f'Improvement over v37a={improvement:.12g}; target margin={margin:.12g}. Exact A≥.5002. Judge1e6 gates_ok={cert["judge"]["gates_ok"]}, passed={cert["judge"]["passed"]}, {cert["judge"]["seconds"]:.3f}s; sampled acceptance={cert["judge"]["sampled_acceptance"]:.6f}. Exact all-orders values determine ranking; the noisy run checks gates/runtime.',
      f'What moved: reverse the blue check’s final CX and exchange its X/Z readout ports (q1/q2), then reuse q2’s measured-Z state directly for the data hop. Direct source Z-read handoffs on {readcells} replace their following resets. The existing A encoder,65-CX correlated resource and both on-grid A-flag-gap helpers run at R45, one tick earlier. Readout bits keep their logical meanings; independent Pauli propagation verifies the same XX/ZZ observables and c64 lies in the detector span (`bell_certificate.json`).',
      f'Current control: byte-identical v37a, L={base["loss"]:.16g}, A={base["acceptance"]:.16g}, Jτ=0, SHA `{base["sha256"][:12]}`. Fixed model OPTIMAL:557 native operations, explicit roles/lifetimes/records, both helpers, A11 and all65 resource CXs.',
      '',
      'Decisions: the strict pre28 five-wire completions were already CNOT-minimal or lost after routing. Following the performance priority, completion was extended through the immediately following blue check at34–36 and its source handoffs. GLOBAL’s B/C synthesis and late-X work and POLISH’s general greedy campaign were left to those lanes; this lane only retimes the carried resource and repairs the changed completion interface.',
      f'Current archive: {len(archive["profiles"])} distinct actual native source-record cell/release vectors, each saved, ideal-checked and exactly priced before selection. Complete downstream families include phase-check roots q9/q7/q14, Bell-port exchange and R45 coherent handoffs. B/C’s65 gates are retained rather than replaced by an independent-encoder model.',
      'Repair coverage: all32 subsets of five individually feasible guard restorations were modeled and every emitted circuit priced. Source Z-read/reset handoffs were composed and repriced; the final neighborhood covers all32 guard choices at the best tested handoff mask and all16 handoff masks on the leading guard profile, plus the additional leading profiles. All eight subsets of three opened cancelling prefix pairs were tested on the q11 direct-read branch. The final guard/source-handoff pass found no further improvement over the retained winner. This is a finite completion neighborhood; no global layout/Clifford optimum is claimed.',
      '',
      '| Complete family / matched change | L | A | Measured cost or gain |',
      '|---|---:|---:|---|']
    family_rows=[
      ('v37_root9_r1_R46','Phase-check readout/reset on q9','Same depth; below acceptance floor'),
      ('v37_root9_pair8_7_fund351','q9 root, vacated-slot repair + acceptance purchase','One init-check trade funds acceptance'),
      ('v37_root7_fixed_R47','Phase-check root q7','Requires a later round in this fixed-block model'),
      ('v37_root14_fixed_R47','Phase-check root q14','Requires a later round in this fixed-block model'),
      ('v37_bell_R46','Bell-port exchange, current R46','Essentially neutral until the interface is used'),
      ('v37_early_f3_bc1','R45 by dropping three source checks','Source-check loss consumes the shorter wait'),
      ('v37_bell8_f0_R45','R45 Bell handoff, all source checks retained','Initial guard-removal cost exceeds waiting gain'),
      ('v37_R45_joint11','R45 plus three restored guards','First judge-verified numerical finalist'),
      ('v37_R45_joint27','Four-guard profile before source-read reuse','Retained despite worse fixed-interface score'),
      ('v37_handoff_k27_m6','Four-guard profile with q3/q13 Z-read reuse','Reverses the guard-profile ranking')]
    for name,label,why in family_rows:
        r=names[name];text.append(f'| {label} | {r["loss"]:.13g} | {r["acceptance"]:.11f} | ΔL={(r["loss"]-TAU)/1e-6:+.6f}µ; {why}. |')
    if 'v37_handoff27_6_R46' in names and 'loss' in names['v37_handoff27_6_R46']:
        r=names['v37_handoff27_6_R46'];rr=names['v37_handoff_k27_m6']
        text.append(f'| Matched direct-read recipe moved back to R46 | {r["loss"]:.13g} | {r["acceptance"]:.11f} | Complete R45 counterpart gains {(r["loss"]-rr["loss"])/1e-6:.6f}µ; this includes the re-scheduled handoff/readout noise. |')
    flagcost=names['v37_bell8_f1_R45']['loss']-names['v37_bell8_f0_R45']['loss']
    text += ['',
      f'µ=1e-6 loss. Deleting sourceM15/c322 from the matched R45 Bell build costs {flagcost/1e-6:.6f}µ. The successful read/port completion keeps that check. Pairwise build differences include their full retiming and noise interaction; they are not additive channel allocations.',
      f'Preserved v36k measurements: baseline L={oldbase["loss"]:.16g}, A={oldbase["acceptance"]:.16g}. History has144 numerically priced distinct QASMs,27 rejected attempts,120 independently verified output-permutation completions and30 release profiles. Best relocated tested circuit after repair: L=.00015785851733506653, A=.4598734973759598, judge gates_ok=True but acceptance fails. Restoration-family gate-noise removal saved .208/.775/1.539µ; pre-round-idle removal saved121.821/51.786/120.036µ (overlapping counterfactuals). Full original-cohort report: [history_v36k/REPORT.md](history_v36k/REPORT.md).',
      'Verified: every priced QASM hash and ordered data mapping, exact baseline reproduction, ideal checks for all archived profiles, all numerical finalists promoted to cand through independent judge1e6 and runtime checks. v37a and the q3/q13 direct-read winner have roundoff-zero first-order loss (2.79e-19), so the measured gains are higher-order. The sparse-kernel omission bounds remain in results.json.',
      'Scope/inference: scheduling feasibility or infeasibility applies only to the declared native model; timing objectives do not prove noisy global optimality. Unbuilt larger windows, different output geometries and new resource/check families remain open. Raw SLOW dispatch was confirmed for q9-measurement reuse without reset, but no long noisy run was spent on that losing case.',
      'Implementation corrections retained as evidence: v36k strict per-wire ordering inserted a false extra tick; exact commuting dependencies fixed it. A extraction now follows original operation identity through interleaved D→A couplings. Removing a measurement eliminates its detector column rather than dropping its term (c275^c282 is deterministic, c282 alone is random). Rejected attempts have errors, never fabricated prices.',
      f'Ledger: {len(numeric)} numerically priced distinct QASMs and {len(bad)} rejected QASMs. All Jτ below use v37a; J_v36k and the historical report preserve the earlier objective. Aliases, full precision, provenance and counterfactuals are in [results.json](results.json). A<.5002 is excluded from candidate ranking.',
      'No submission, commit/push, sub-agent or GPU was used. Only COMPLETE was written; tom was read only (its race occupied22 workers). All owned jobs were observed to exit before final delivery.',
      '',
      '<table><thead><tr><th>Circuit</th><th>L</th><th>A</th><th>Jτ</th><th>SHA256 prefix</th><th>What moved</th></tr></thead><tbody>']
    rows=[]
    for r in sorted(numeric,key=lambda x:(not Path(x['stem']).name.startswith('v37'),Path(x['stem']).name)):
        n=Path(r['stem']).name
        if n.startswith('v37_handoff') and n.endswith('_R46'):desc='Direct-read handoff; matched R46 control'
        elif n.startswith(('v37_neighbor','v37_handoff','v37_read14')):desc='R45 source Z-read/prep handoffs and guard choices'
        elif n.startswith('v37_R45'):desc='R45 Bell completion; guard restoration'
        elif n.startswith('v37_prefix'):desc='Opened prefix-pair completion'
        elif n.startswith('v37_arch'):desc='Archived source-cell release profile'
        elif n.startswith('v37_bell'):desc='Bell readout ports and earlier handoff'
        elif n.startswith('v37_early'):desc='Earlier round with source-check removals'
        elif n.startswith('v37_root'):desc='Phase-check readout/reset placement'
        elif n.startswith('v37a'):desc='v37a exact round trip'
        elif re.search(r'_a\d+',n):desc='v36k history: A resynthesis'
        elif re.search(r'_g\d+',n):desc='v36k history: new data guard'
        elif 'restore' in n:desc='v36k history: relocated completion, locality restored'
        elif 'rb2' in n or 'rebind' in n:desc='v36k history: relocated completion, A rebound'
        elif 'funded' in n:desc='v36k history: acceptance purchase'
        else:desc='v36k history: control or completion route'
        al=len(r.get('aliases',[]));label=n+(f' (+{al-1} aliases)' if al>1 else '')
        rows.append(f'<tr><td><a href="builds/{n}.qasm">{html.escape(label)}</a></td><td>{r["loss"]:.13g}</td><td>{r["acceptance"]:.12g}</td><td>{r["J_tau"]:.10g}</td><td>{r["sha256"][:12]}</td><td>{desc}</td></tr>')
    text += [''.join(rows[i:i+12]) for i in range(0,len(rows),12)]
    text += ['</tbody></table>','','Files: `cand/`, `results.json`, `finalists_v37.json`, `model_v37a.json`, `archive_v37.json`, `v37_joint_schedules.json`, `v37.py`, `handoff_v37.py`, `prefix_finish_v37.py`, `logs/`, `history_v36k/`.']
    assert len(text)<=100,len(text)
    (H/'REPORT.md').write_text('\n'.join(text)+'\n')
    audit=dict(priced=len(numeric),rejected=len(bad),v37_prices=len(current),report_lines=len(text),archive_profiles=len(archive['profiles']),best=best,verified_candidate=cert,all_hashes_verified=True)
    (H/'audit_v37.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k not in ('best','verified_candidate')}))
if __name__=='__main__':run()
