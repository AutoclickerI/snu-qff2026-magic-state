"""Regenerate the lane report from receipts; no inferred proofs or MC ranks."""
import os,sys,json,re,math,sqlite3
from pathlib import Path
H=Path(__file__).resolve().parent;BASE=6.92210398227877e-5

def report(status='RUNNING: long-budget feedback and expanded screens; no stopping on a win.'):
 rows=[]
 for f in (H/'finalists').glob('*.screen.json'):
  r=json.loads(f.read_text());stem=f.name[:-len('.screen.json')];elog=f.with_name(stem+'.exact.log')
  if elog.exists():
   txt=elog.read_text();mt=re.search(r'1-F \(to 3rd order\) = (\S+)',txt)
   if mt:
    r['exact_cli']=float(mt[1]);r['exact_agrees']=abs(r['total']-float(mt[1]))<=5.1e-11
    assert r['exact_agrees'],(stem,r['total'],mt[1])
  mlog=f.with_name(stem+'.mc.log')
  if mlog.exists():
   txt=mlog.read_text();mm={int(s):(float(v),float(a)) for s,v,a in re.findall(r' (0|1000|2000) ([\deE+.-]+) .*?acc ([\deE+.-]+)',txt)}
   if len(mm)==3:r['mc']=[mm[s][0] for s in (0,1000,2000)];r['mc_mean']=sum(r['mc'])/3;r['mc_acceptance']=mm[0][1]
  rows.append(r)
 verified=sorted([r for r in rows if r.get('exact_agrees') and r.get('check',{}).get('passed') and r['check']['acceptance']>=.505 and r['total']<BASE],key=lambda r:r['total'])
 best=verified[0] if verified else None
 lines=['# BCFB','',f'Status: {status}','',f'Baseline `../MAIN/v23h_c2c9`: c1 = 2.92358729818e-19, second = 5.24923143353e-5, cubic = 1.67287254875e-5, total = **{BASE:.12g}**, exp(-A1) = 0.540859577712. Independently replayed to 7e-19 in total; both 1e6-shot judge checks PASS.','']
 if best:
  md=json.loads((H/'finalists'/f'{best["tag"]}.json').read_text());lines += [f'Best verified exact circuit: **`finalists/{best["tag"]}`**, exact **{best["total"]:.12g}** ({100*(best["total"]/BASE-1):+.3f}%), exp(-A1) **{best["exp_minus_A1"]:.9f}**. MC '+(f'mean {best["mc_mean"]:.9g}, seed-0 acceptance {best["mc_acceptance"]:.5f}.' if 'mc_mean' in best else 'pending; no statistical ranking claim.'),'',f'Difference from v23h_c2c9: {md.get("CX")} total CX; BC prep {md.get("verification",{}).get("cx")} CX, solver depth {md.get("verification",{}).get("depth")}; initialization / timing options `{json.dumps(md.get("options",{}),sort_keys=True)}`. R={md["R"]}; non-BC time edits `{json.dumps(md.get("non_BC_time_changes",{}))}`; retained preceding X states `{md.get("retained_previous_X_states",[])}`. Repeated BC init checks `{md.get("init_checks",[])}`; bounded-retiming changes `{md.get("non_BC_check_retime",[])}`. Hop and A gate edits are retained.','']
  (H/'BEST.json').write_text(json.dumps(best,indent=2))
 else:lines += ['No improvement has yet completed the unmodified exact confirmation. Fourier-screen candidates are provisional.','']
 lines += ['| Verified improvement stem (under finalists/) | c1 | Second | Cubic | Exact total | exp(-A1) | Judge acc, 1e6 | MC mean / seed-0 acc |','|---|---:|---:|---:|---:|---:|---:|---|']
 for r in verified:
  mc=f'{r["mc_mean"]:.9g} / {r["mc_acceptance"]:.5f}' if 'mc_mean' in r else 'pending'
  lines.append(f'| `{r["tag"]}` | {r["c1"]:.4g} | {r["second"]:.12g} | {r["third"]:.12g} | {r["total"]:.12g} | {r["exp_minus_A1"]:.9f} | {r["check"]["acceptance"]:.6f} | {mc} |')
 if (H/'base_redraw_reference.json').exists():
  br=json.loads((H/'base_redraw_reference.json').read_text());lines += ['',f'Completed baseline re-draw reference: {br["draws"]} draws, mean **{br["mean"]:.12g}**, SEM {br["sem"]:.3g}, read from MAIN logs (rounded printed scores).']
 if (H/'redraw_summary.json').exists():
  rd=json.loads((H/'redraw_summary.json').read_text());lines += ['','Re-draw counts below include only completed 1e8-shot seed-0 samples. Fewer than 100 draws remain provisional.','', '| Circuit | Completed draws | Mean | SEM | Minimum acceptance | ≥100 complete |','|---|---:|---:|---:|---:|---|']
  for tag,r in sorted(rd.items(),key=lambda kv:kv[1]['mean']):
   sem=f'{r["sem"]:.3g}' if r['sem'] is not None else '—'
   lines.append(f'| `{tag}` | {r["draws"]} | {r["mean"]:.12g} | {sem} | {r["min_acceptance"]:.8f} | {r["complete100"]} |')
 lines += ['','| Formulation | Budget | Status | Witnesses | Best in-situ exact screen |','|---|---|---|---:|---:|']
 completed=list((H/'runs').glob('fast_s*.receipt.json'))
 lines.append(f'| Exact feedback SAT, clean BC2, depth 14/15, caps 82/90/98/105 | 20 seeds × 7200 s fresh budget, plus initial runs; host-capacity pauses recorded separately | {len(completed)}/20 budgets completed | database counts below | database minimum below |')
 if (H/'search.sqlite').exists():
  with sqlite3.connect(H/'search.sqlite') as db:
   for kind,n,b in db.execute("select kind,count(*),min(value) from prices where kind!='prior_evidence' group by kind"):lines.append(f'| {kind} | see per-run receipts | running/completed per receipt | {n} | {b if b is not None else "—"} |')
 for f in sorted((H/'runs').glob('*.receipt.json')):
  r=json.loads(f.read_text());lines.append(f'| `{f.stem}` | {r.get("seconds",r.get("prices","—"))} | {r.get("status")} | {r.get("priced",r.get("masks","—"))} | {r.get("best","—")} |')
 lines += ['| Cell automorphisms | complete induced-graph enumeration | 2 graph automorphisms, only identity preserves target and clean predicate | 1 valid | base |','',
 'Mechanisms: SAT repair prices full-circuit X/Z correlations and idle exposure, with complete BC2-clean single-fault constraints. Depth 14/15 and CX caps 82/90/98/105 diversify the search; CX count is not a ranking objective. The transplant removes owned old initialization bits, then propagates replacement MX frames into the existing detector span. Native timing is checked after emission; strict builds retain all non-BC times, while explicitly tagged retime_window variants minimize retained-unit displacement with R fixed. Initialization masks and prep timing remain independent dimensions. In the first 207-CX winner, removing either of its added canceling CX pairs raises loss (6.89704e-5 or 6.91092e-5); removing both yields 6.93103e-5. This directly shows a benefit from the identities under the noisy schedule. The inferred mechanism is replacing idle channels with less harmful joint gate channels.', '',
 'The strongest confirmed SAT network lowers loss by 1.02979e-6 relative to the base; the q11/q19 initialization checks add a 5.40798e-8 reduction. Thus about 95% of the confirmed exact gain comes from the prep network and 5% from those checks. The network uses 88 CX instead of 82 without delaying the round. These are arithmetic differences of the verified exact values, not an independent fault attribution.', '',
 'R45 was initially held as a scheduling choice, then explicitly widened. The 72-case R42–R47 screen found no gain, and 1500 uniformly sampled distinct failed feedback representatives priced at R46/R47 had best 7.26302449692e-5. The fixed-order dependency path through the prefix and A encoder independently requires R45 (critical_path.json); this is not a bound on other operation orders or architectures. No extra round-time hard gate is imposed on eligibility.', '',
 'Verified: deterministic full stabilizer targets; BC2 clean predicate including actual-CX XX faults; matching baseline Fourier arithmetic; native grid/timing assertions; unmodified exact2 --third for rows above (|c1|<1e-12); 1e6-shot judge and, when shown, MAIN/spec/mc3.py at 1e8 shots, seeds 0/1000/2000. Owl lacks the MAIN/spec path, so its byte-identical copy inputs/mc3.py is used (SHA-256 in mc3_provenance.log). Batched exact decoder tables agree with the original Fourier evaluator within 8e-19 on five circuits (batch_validation.json), cutting contraction ~4.9 s to .7–1.2 s. The absolute precision of CLI totals is 5.1e-11; full-precision components in the table are Fourier results cross-checked against that CLI.', '',
 'Inferred/limits: third-order arithmetic is a screen, not the all-orders MC mean. No global optimum or UNSAT claim follows from a bounded search. The BCSYN2 feedback logs were absent locally and on owl, then recovered from tom and read in full (201 lines, 106 JSON records; hashes in prior_feedback_audit.json). Complete original text is preserved in the compressed witness archive. The winning old seed-401 circuit appeared after 447.0 s; the logs contain no exhaustion certificate. The initial 501–508 batch exposed a copied Unit parser bug on a single H; its errors/stops are preserved, and the corrected long batch starts at 511. Search witnesses are stored compressed in the lane database while workers run, then packaged into one tar.xz; bulk QASM files are not retained. No submission, credentials, commits or pushes; no other lane files edited.']
 (H/'REPORT.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps(dict(verified=len(verified),best=best['tag'] if best else None)))
if __name__=='__main__':report(sys.argv[1] if len(sys.argv)>1 else 'RUNNING: long-budget feedback and expanded screens; no stopping on a win.')
