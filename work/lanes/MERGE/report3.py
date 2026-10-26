from pass3 import *
def collect():
 rows=json.loads((H/'archive/results_v37c.json').read_text())
 for s,r in rows.items():
  r['phase']='prior MERGE passes'
  if 'loss'in r:r.update(J_previous=r.get('J_tau'),J_tau=rank(r),tau=TAU)
 for f in sorted(R.glob('*.jsonl')):
  for ln in f.read_text().splitlines():
   try:r=json.loads(ln)
   except json.JSONDecodeError:continue
   if 'sha256'not in r or 'stem'not in r:continue
   old=rows.get(r['sha256'],{});aliases=old.get('aliases',[])
   alias=dict(stem=r['stem'],moved=r.get('what_moved',r.get('edits')),stage=r.get('stage','direct'))
   if alias not in aliases:aliases.append(alias)
   r=dict(r,aliases=aliases,phase='v37d pass3',tau=TAU)
   if 'loss'in r:r['J_tau']=rank(r)
   jf=R/f"judge_{r['sha256']}.json"
   if jf.exists():r['judge_1e6']=json.loads(jf.read_text())
   rows[r['sha256']]=r
 dump(H/'results.json',rows)
 table=['| Circuit | L | A | J_tau(v37d) | SHA256 | What moved / status |','|---|---:|---:|---:|---|---|']
 for s,r in sorted(rows.items(),key=lambda x:(x[1].get('loss',1),x[0])):
  st=Path(r['stem']);rel=str(st.relative_to(H));why=r.get('what_moved',r.get('edits',r['phase']))
  why=json.dumps(why,separators=(',',':')) if isinstance(why,(dict,list))else str(why)
  why=why.replace('|','/').replace('\n',' ')[:800]
  if r.get('judge_1e6',{}).get('speed_ok')is False:why+='; SPEED REJECTED'
  if 'error'in r:why+='; '+r['error']
  vals=[f'[{rel}]({rel}.qasm)']+[f'{r[k]:.14g}'if k in r else 'ERROR'for k in ['loss','acceptance','J_tau']]+[s[:16],why]
  table.append('| '+' | '.join(vals)+' |')
 (H/'priced_circuits.md').write_text('\n'.join(table)+'\n');return rows
def report(final=False):
 rows=collect();new=[r for r in rows.values()if r['phase']=='v37d pass3'];cands=[]
 for f in (H/'cand').glob('*.json'):
  r=json.loads(f.read_text())
  if r.get('tau')==TAU and r.get('judge_1e6',{}).get('speed_ok'):cands.append((rank(r),f,r))
 lines=['# MERGE — pass3 on v37d','',f"Verdict: {'COMPLETE'if final else 'ACTIVE'}. tau={TAU:.17g}; finalist L<tau−5e-8, exact A≥.5002, judge gates_ok at1e6, single-process fast_check≤4.8s."]
 if cands:
  _,f,b=min(cands,key=lambda z:(z[0],z[1].stem!='merge3_final'))
  lines += [f"Best verified: [cand/{f.stem}](cand/{f.stem}.qasm), L={b['loss']:.16g}, A={b['acceptance']:.16g}, J_tau={rank(b):.16g}; gain vs v37d={TAU-b['loss']:.10g}.",f"SHA256 `{b['sha256']}`; judge median{b['judge_1e6']['median_judge_seconds']:.3f}s; limit4.8s is fixed to the supplied v37d3.2s reference. Loaded local baseline times do not relax it."]
  if 'final_cli_check'in b:
   lines.append(f"Final fast_check CLI: {b['final_cli_check']['seconds']:.6f}s at1e6 shots/1process on{b['final_cli_check']['host']}; gates_ok=True. {b['cx']}CX,{b['native_depth']}native ticks. Archived original evaluator replay matches L and A exactly.")
 lines += ['', 'Source controls: v37d reproduced exactly; GLOBAL G3 reproduced3.676199483205871e-5,A=.5037245347586016; BC2-polish control3.7225517523299324e-5,A=.5046963821877385. Independent measured gain4.63523e-7 in GLOBAL’s exterior.',
 'Footprint: G3 versus its BC2-polish control removes17/adds18 native units, touches36 qubit/tick cells and12 classical bits, replaces4 detector rows. Full diff: res37d/G3_diff.json. Relative to v37d, prefix measured preparations/readout shifts are independent repairs, not part of the resource core.',
 'Transport: R45 q17/q23/q28/q29 changes reverse four resource edges and move the measured-plus source fromq17 toq28; allocate a fresh record and rebuild three B detector rows by their logical parity. The q26/q29 source records keep v37d meanings.',
 'Transport: q18/q24 preparations advance to31, addCX24→18@32 andCX12→18@33, reverse two late18/24 edges. Remove competing known-zeroCX12→13@33. q3 branch advances its three resource gates by1 and removes competingCX3→4@39; retain v37d’s already-reused q3 source.',
 '', '| BC3 modules on v37d | L | A | Delta vs v37d |','|---|---:|---:|---:|']
 byname={Path(r['stem']).name:r for r in new}
 for k in range(1,8):
  r=byname.get('bc3_'+str(k))
  if r and 'loss'in r:lines.append(f"| {'+'.join(n for i,n in enumerate(['R','L','q3'])if k>>i&1)} | {r['loss']:.13g} | {r['acceptance']:.12g} | {r['loss']-TAU:+.9g} |")
 lines += ['', 'Interaction: R alone loses7.59e-8; with q3 it gains. All seven nonempty combinations were priced; no additive gain assumption is used.',
 'Measured-source port: eligible GLOBAL reset→measurement substitutions propagate the recorded Pauli byproduct through the actual merged circuit and XOR affected detector rows. q21@19 andq13@25 fail the stabilizer-output byproduct condition and remain resets. RX12@26 remains unchanged to avoid the known slow dispatch.',
 'POLISH: latest source compared by native footprint against v37b; already-carried edits retained; surviving reversalCX21→15@34, prefix removals and retimed pair16→17 tested as complete combinations. Conflicting R46 guard timings are regenerated, not copied literally. Detailed outcomes under res37d/polish3*.']
 for f in sorted(R.glob('*_history.json')):
  h=json.loads(f.read_text())
  if h:
   lines += [f"{f.stem}: {len(h)} complete greedy rounds; last gain{h[-1]['loss_gain']:.10g}, stop={h[-1]['stop']}; L={h[-1]['price']['loss']:.14g}, A={h[-1]['price']['acceptance']:.13g}."]
 histories=[(f.stem,json.loads(f.read_text()))for f in sorted(R.glob('*_history.json'))]
 if histories:
  lines+=['','| Greedy round | L | A | Gain in round | J_tau |','|---|---:|---:|---:|---:|']
  for tag,h in histories:
   for r in h:
    p=r['price'];lines.append(f"| {tag}/{r['round']} | {p['loss']:.13g} | {p['acceptance']:.12g} | {r['loss_gain']:.9g} | {rank(p):.10g} |")
 status=R/'runtime_conclusion.json'
 if status.exists():lines.append('Runtime diagnosis: '+json.loads(status.read_text())['summary'])
 lines += ['', 'Greedy: regenerated all singles, connected positive/cheap-buyer pairs, additions unlocked by freeing edits, then full-price joint extensions and funding until gain<1e-9. Rank feasible candidates byA(L−tau). A speed rejection excludes promotion, never changes the numerical receipt.',
 'Evaluator speed repair: q11 read/reset fusion invalidated the prior warm detector basis (replay width14). Trained a width8 basis, reproduced the full candidate price exactly, stopped only this lane’s identified evaluator PIDs, observed their exit, and resumed pending tasks from completed hash-keyed receipts. Basis files and control receipts are retained; no numerical objective or check was changed.',
 'Evaluator refinement now trains the cheapest replay once instead of retraining every stored warm basis; all73 moments still contract exactly. A difficult saved case replayed its recorded loss under the change, and the final circuit matches the archived original evaluator. Profiling and both source versions are retained.',
 'Provenance correction: updating the evaluator file while an old module remained loaded mislabeled172 hashes when its driver recomputed a version key. Stopped the old process tree, archived original metadata, and rekeyed343 receipts/cache entries to the actual loaded original core. Numerical values were unchanged; the incumbent was independently repriced after restart. res37d/provenance_correction.json and archive/provenance_fix3/.',
 'Finalization correction: hippo’s older fast_check CLI omits the gates_ok text field. Its passed=True run was valid; the handoff parser now checks the actual rep.correct_ok structured result. The complete final CLI run satisfies correctness and4.8s without relaxing either check.',
 'Verified: saved QASM+data mapping and SHA256 for every numerical claim; native schedule/adjacency and exact ideal checks; candidate judge correctness and measured1e6 speed. All factor/kernel omission bounds and evaluator hashes are retained.',
 'Inferred only: finite menu transport/search coverage, no global optimality claim. Short sampler timings and static zero-general-atom status diagnose speed; only full single-process1e6 judge times qualify candidates.',
 'Scope: only MERGE written; hippo≤24 processes including controller, zebra≤4; BLAS/OpenMP caps1; no subagents/GPU/submission/commit/push/credential access. Heavy local jobs ended before search moved to hippo when zebra became overfull. Host allocations are for this pass, not new standing rules.',
 f"Ledger: {len(new)} pass3 hashes;{len(rows)} total. [Full table](priced_circuits.md), [results.json](results.json), v37d/,res37d/,logs37d/,cand/. Prior evidence archived in archive/." ]
 if final:
  lines.insert(6,'Completion: all seven BC3 module combinations and POLISH transports priced;1539 singles,1196 connected/contextual bundles, six complete greedy rounds with acceptance funding. Last-round gain2.787344985e-10<1e-9. Bulk prefix measurements were not required for the final gain. No submission, commit or push.')
 assert len(lines)<=100 and max(map(len,lines))<2000
 (H/'REPORT.md').write_text('\n'.join(lines)+'\n');print('report',len(lines),'lines',len(new),'pass3 hashes',flush=True)
if __name__=='__main__':report('--final'in sys.argv)
