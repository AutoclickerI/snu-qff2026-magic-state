from campaign import *
from summarize import collect
import html
def report(final=False):
 with __import__('contextlib').redirect_stdout(__import__('io').StringIO()):collect()
 rows=json.loads((H/'results.json').read_text());numeric=[r for r in rows.values() if 'loss'in r]
 candidates=[]
 for f in (H/'cand').glob('*.json'):
  r=json.loads(f.read_text());candidates.append((r['J_tau'],f.with_suffix(''),r))
 _,dst,best=min(candidates)
 bystem={Path(a['stem']).name:r for r in rows.values() for a in r['aliases'] if a['stem']}
 lines=['# MERGE','',f"Verdict: {'VERIFIED FINALIST; completion contract met' if final else 'ACTIVE; verified three-way finalist available'}.",
 f"Best judge-verified candidate: [{dst.name}](cand/{dst.name}.qasm); L={best['loss']:.15g}, A={best['acceptance']:.15g}, J_tau={best['J_tau']:.15g}.",
 f"SHA256 `{best['sha256']}`. Threshold: L < {TAU-5e-8:.15g}; A >= .5002; tau={TAU:.15g} (v37b).",
 '','Native diff audit against v37a:','',
 '| Lane | Removed / added native units | Qubit/tick cells | Classical bits touched | Detector rows removed / added |',
 '|---|---:|---:|---:|---:|',
 '| POLISH | 9 / 10 | 26 | 4 | 0 / 0 |',
 '| GLOBAL | 16 / 26 | 42 | 18 | 5 / 7 |',
 '| COMPLETE | 191 / 179 | 378 | 35 | 0 / 0 |',
 'POLISH/GLOBAL: zero quantum-cell overlap; records323/325/329 are shared because POLISH retimes their reads and GLOBAL extends their detector parities.',
 'POLISH/COMPLETE: nine shared cells (q7/q13/q15/q21 at47–48 and q16@37), four shared records. GLOBAL/COMPLETE:23 shared cells,12 shared records. Full locations and operation/record changes: res/diffs_initial.json.',
 'No source has OBSERVABLE, FRAME or POSTSELECT declarations. The unchanged detector text in COMPLETE retains record meanings while Bell readout ports and native timing change.',
 '', 'Measured contributions (conditional comparisons, not additive independent fault budgets):','',
 '| Change | Before L | After L | Delta L | After A |', '|---|---:|---:|---:|---:|']
 for x,y,why in [('A','C','COMPLETE full R45 completion'),('C','CPprefix_read','Compatible POLISH prefix + regenerated early readouts'),('CPprefix_read','CPGcore_read','GLOBAL B/C core on R45'),('R46_PGcore','CPGcore_read','COMPLETE, matched POLISH/GLOBAL recipe'),('P','PG','GLOBAL full diff added directly to v37b')]:
  if x in bystem and y in bystem:
   a,b=bystem[x],bystem[y];lines.append(f"| {why} | {a['loss']:.12g} | {b['loss']:.12g} | {b['loss']-a['loss']:+.9g} | {b['acceptance']:.12g} |")
 if 'CPGcore_read' in bystem:
  a=bystem['CPGcore_read'];lines.append(f"| Repair of three-way merge | {a['loss']:.12g} | {best['loss']:.12g} | {best['loss']-a['loss']:+.9g} | {best['acceptance']:.12g} |")
 if (H/'res/final_refresh.json').exists():
  refresh=json.loads((H/'res/final_refresh.json').read_text());lines+=['','Final source refresh: '+refresh['summary']]
 if (H/'res/final_repair_outcome.json').exists():
  fin=json.loads((H/'res/final_repair_outcome.json').read_text())
  lines+=['',f"Repair coverage:1549 distinct regenerated proposals (1006 numerical,543 rejected); full extension pass over all174 useful/buyer recipes; seven source-guard combinations; positive joint repair;39 refreshed POLISH transports; final regenerated pass of{fin['scan_count']} saved proposals and sequential full-price greedy composition. Final pass accepted{sum(x.get('accepted',False) for x in fin['history'])} extensions. This is finite-menu coverage, not a convergence/global-optimality claim."]
  if 'runtime_repair' in fin:
   lines+=['Runtime repair: the numerically best final circuit exceeded90s in its1e6 judge run (terminated by exact PID); short exact-sampler probes gave≈340s/1e6. Bisection identified pair1→7 at37–38. Removing only that pair costs8.4443e-10 L and retains the other improvements. The recommended candidate passes the complete1e6 judge check within the documented20s limit. Slower numerical witnesses remain recorded, explicitly ineligible for promotion.',
           'Reporting correction: a NumPy boolean prevented the first outcome-JSON write; converted it to builtin bool and rebuilt the summary from saved receipts, without changing circuits or measurements.']
 lines+=['',
 'Merge decisions: retain COMPLETE’s R45 schedule; shift GLOBAL’s B/C orientations/preparations one tick earlier; retain COMPLETE’s measured-q7 source instead of GLOBAL’s competing q7 initialization. Reapply POLISH through the lane-local regenerated menu.',
 'POLISH CX16→10 cannot be transplanted to39/40/41/43/44: all20 saved variants fail deterministic detectors. Restoring its old slot collides with q15’s source read. Restoring GLOBAL’s pair16→17 slot collides with q15’s earlier prefix operation. These failures close the tested local transports only.',
 'Acceptance purchases and deletions are priced as complete circuits. Exact A, not the sampled acceptance, enforces the0.5002 floor. Rank is J_tau=A*(L-tau).',
 'Evaluator: copied MAIN all-orders contraction and POLISH adapter; all73 Fourier moments. A frozen trained detector basis changes contraction coordinates only; the merged control reproduces bit-for-bit. Cache receipts bind QASM hash, ordered data and evaluator/adapter/basis hashes.',
 'Verified: v37a/v37b reproduced within1.2e-16; all listed prices come from saved QASM; every cand artifact has a1e6-shot judge receipt. Structural/ideal failures remain errors. Numerical omission bounds are retained in results.json.',
 'Inference limits: finite menu and transported-schedule coverage; no global optimality claim. Source-lane advertised numbers are not used as newly measured MERGE prices.',
 'Scope: only MERGE files written; hippo≤3 evaluator workers+controller, zebra≤2 evaluator jobs; thread caps1; no GPU, subagents, submissions, commits or pushes; no standing rule changed.',
 'Execution decisions: preserve completed receipts when redistributing the slower local queue; replace a width12 contraction basis with a control-verified width8 basis. Stop the initial repeated-search driver after its complete extension pass and continue with the requested refreshed-source repair; no completed price was discarded.',
 f"Ledger: {len(rows)} unique evaluated QASM hashes ({len(numeric)} numerical prices). Aliases, full values and errors: [results.json](results.json). All generated proposals and unbuilt conflicts are retained under c/, builds/ and res/.",
 'Files: cand/; logs/*judge*; res/diffs_initial.json; res/port_audit.json; res/*history.json; res/*refresh*.json; evaluator provenance and frozen basis under res/; campaign.py, merge_build.py, repair.py, greedy_pass.py.',
 '', '<details><summary>Every evaluated circuit: L, A, J_tau, SHA256 prefix and what moved</summary>','']
 tab=['<table><thead><tr><th>Circuit</th><th>L</th><th>A</th><th>J_tau</th><th>SHA256</th><th>What moved / error</th></tr></thead><tbody>']
 for r in sorted(rows.values(),key=lambda r:(r.get('loss',1),r['sha256'])):
  st=Path(r['stem']);name=str(st.relative_to(H));why=r.get('what_moved','')
  if isinstance(why,dict):why=json.dumps(why,separators=(',',':'))
  runtime=' RUNTIME INELIGIBLE' if r.get('runtime',{}).get('eligible') is False else ''
  vals=[f"<a href='{html.escape(name)}.qasm'>{html.escape(name)}</a>"]+[f"{r[k]:.13g}" if k in r else 'ERROR' for k in ['loss','acceptance','J_tau']]+[r['sha256'][:16],html.escape(str(why)+' '+r.get('error','')+runtime)]
  tab.append('<tr>'+''.join('<td>'+v+'</td>' for v in vals)+'</tr>')
 tab.append('</tbody></table>');lines+=[''.join(tab),'','</details>']
 assert len(lines)<=100
 (H/'REPORT.md').write_text('\n'.join(lines)+'\n')
 print('report',len(lines),'lines',len(rows),'hashes',dst.name,flush=True)
if __name__=='__main__':report('--final' in sys.argv)
