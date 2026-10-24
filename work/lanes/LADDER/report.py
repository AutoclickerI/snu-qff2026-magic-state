"""Render the measured ladder from completed exact2 receipts; no invented scores."""
import json,math,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
F=['f00_base','f01_sepBC','a_order210','order210/f03_nohops','order210/f04_prefix32_R45','order210/f05_R42','order210/f05_R39','order210/f05_R36','order210/f05_R33','order210/f06_sep33_v23','order210/f07_sep33_old','f07_sep33_old']
LABELS=['v23h_c2c9; R45','Separate B/C, 9+9 CX; R45','Best tested standard A, order210; R45','Remove hops and guards; R45','Only compact prefix to end32; R45','Only advance suffix to R42','Only advance suffix to R39','Only advance suffix to R36','Only advance suffix to R33','Direct readout; v23 prefix, R33','Older prefix; retain A210, R33','Restore reference A012; published sep33']
def read(n):
 r=json.loads((H/(n+'.price.json')).read_text());assert r['status']=='PASS',n;return r

def table(names,labels,reference=None):
 rows=['| Rung / output | Change | Exact 2nd | 3rd correction | Total through 3rd | Delta | exp(-A1) | CX |','|---|---|---:|---:|---:|---:|---:|---:|'];prev=reference
 for n,l in zip(names,labels):
  r=read(n);d=r['total']-prev if prev is not None else 0
  rows.append(f'| [{n}]({n}.exact.txt) | {l} | {r["second"]:.8e} | {r["third"]:.8e} | **{r["total"]:.8e}** | {d:+.8e} | {r["exp_minus_A1"]:.7f} | {r["CX"]} |')
  if reference is None:prev=r['total']
 return '\n'.join(rows)

def main():
 rs=[read(n) for n in F];gap=rs[0]['total']-rs[-1]['total'];base=rs[8]['total']
 rev=['order210/r_BC','r_A','order210/f04_prefix32_R45'];rr=[read(n) for n in rev]
 rh0=read('order210/r_hops_nohop');rh1=read('order210/r_hops_hop_alap')
 std=read('f06_sep33_v23');old=rs[-1]
 lines=['Status: **COMPLETE** — matched forward ladder and reverse one-at-a-time prices measured; impossible fixed-R33 restorations identified. No submission, commit, or push.','',
 f'**The measured {gap:.8e} gap is chiefly B+C preparation (+{rs[0]["total"]-rs[1]["total"]:.8e} recovered), A preparation (+{rs[1]["total"]-rs[2]["total"]:.8e}), and advancing the round (+{rs[4]["total"]-rs[8]["total"]:.8e}).** Prefix compaction is a prerequisite for the early round but costs {rs[4]["total"]-rs[3]["total"]:.8e} at fixed R45. Removing hops also costs {rs[3]["total"]-rs[2]["total"]:.8e} on this matched path. Neither is a positive recoverable grid tax.','',
 'All losses use STANDARD p=1e-3 and condition on every detector passing. “Exact” means the exact fault sum **through the stated order**, not an all-orders score. Third is the signed third-order correction, not the larger positive raw weight-3 sum. Delta means current minus previous row; negative improves. exp(-A1) is an acceptance proxy. Deltas and percentages below are arithmetic derived from measured receipts.','',
 '## Forward ladder','',table(F,LABELS),'',
 'The A210 choice is the lowest measured total among all six orders of the standard encoder’s three commuting CX layers at the R45 A-replacement rung. It is held fixed through the timing ladder; no global optimum over all encoders or relabellings is claimed. The last row changes A210→A012 separately so the endpoint is exactly the published sep33, without mixing an encoder-order change into the prefix comparison.','',
 '### Why these are matched','',
 '- Native provenance gives **75 prefix + 82 B+C prep + 11 A prep + 12 hop + 23 round/readout CX = 203**. `build.py` matches all 129 prefix native units against v20 provenance by statement and occurrence. The boundary-based 78/83/13/6/23 counts in GAP mix these regions; the QASM and its score agree. See [build.log](build.log) and per-rung JSON unit records.',
 '- B+C replacement changes only its preparation package: 82→18 CX, all blocks finished at44. The existing 7-CX B→C check remains at45. Initialization basis/policy and internal preparation timing belong to this replacement; the measured gain is **not** a price per deleted CX.',
 '- A replacement changes only its encoder/initialization/check package, 11→9 CX, still ending at44. The old MX initialization checks cannot simply be kept verbatim when the encoder’s input bases change.',
 '- Removing hops removes their 12 CX, destination preparations, and vacated-source guards. Reset-prepared A/B/C lifetimes are relabelled onto the 21 cells unused by the prefix. This avoids overwriting unmoved data; STANDARD noise is independent of cell numbers. Other gates and their native times are preserved.',
 '- v23’s prefix contains late couplings/readouts and four terminal T† gates through44. `f04` moves only prefix units to their latest feasible times at or before32, preserving per-cell order. The R42/R39/R36/R33 rungs then shift **only** A/B/C preparation and the round, keeping this compact prefix fixed.',
 '- The original readout includes parity CXs 19→25 and 17→16. `f06` removes only these readout gadgets, advances the affected A/C measurements by one step, and updates detector XORs. Omitting this control would conflate readout and prefix differences.',
 '- Empty scheduled layers are kept by unconditioned Z measurements on an already discarded prefix wire. They keep native time from collapsing; that disconnected wire cannot affect acceptance or logical loss. No noise rates are changed.','',
 '## Reverse one-at-a-time controls','',
 'All deltas in the next table are versus the same A210 R33 circuit (`order210/f05_R33`), not versus the preceding reverse row. A/B+C restore the original grid-derived preparation circuits and their offsets from R on prefix-free ancilla cells. They restore the encoder packages, **not** the original physical layout or release constraints. The original A footprint includes live unmoved data cells8/15; B includes live cell4. Those footprints cannot be restored independently of movement.','',
 table(rev,['Restore 82-CX joint B+C preparation','Restore 11-CX grid A preparation/checks','Restore R45 suffix timing; compact prefix fixed'],base),'',
 f'The early-context B+C cost is {rr[0]["total"]-base:.8e}, versus {rs[0]["total"]-rs[1]["total"]:.8e} on the forward path. The early-context A cost is {rr[1]["total"]-base:.8e}, versus {rs[1]["total"]-rs[2]["total"]:.8e} forward. These interactions make a unique order-independent additive attribution impossible.','',
 '**Fixed-R33 reverse hops: infeasible for the original routes and this unchanged prefix.** q8 has T† at30, followed by three two-CX transfers: six sequential CX slots require destination readiness at37 or later. [reverse_hops_feasibility.json](order210/reverse_hops_feasibility.json) records the ASAP dependency schedule. This is a bound for those paths, not a bound on redesigned routing or a modified prefix.','',
 'The matched feasible R37 control below restores the paths while placing fresh destination initialization immediately before first use. The first ASAP construction initialized fresh destinations at0 and charged gratuitous waiting; that version is retained as `order210/r_hops_hop` but is excluded from constraint attribution. Both versions pass correctness.','',
 table(['order210/r_hops_nohop','order210/r_hops_hop_alap'],['No-hop control at R37','Restore hops; destination init immediately before use']), '',
 f'At R37 the restored hops improve total loss by {- (rh1["total"]-rh0["total"]):.8e}; second-order loss is unchanged to numerical precision, and the difference is third order. This agrees in sign with the R45 removal rung. The reduced acceptance proxy is measured; this is not a free noisy operation.','',
 '**Original prefix timing at R33: infeasible.** Its terminal T† at44 cannot precede R33. At matched R45, restoring the delayed prefix (`f04`→`f03`) improves loss by '+f'{rs[4]["total"]-rs[3]["total"]:.8e}'+'. Readout restoration at R33 is the inverse of `f05_R33`→`f06`, costing '+f'{rs[8]["total"]-rs[9]["total"]:.8e}'+'.','',
 '## Attribution of the endpoint gap','',
 f'{rs[0]["total"]:.10e} − {rs[-1]["total"]:.10e} = **{gap:.10e}**. Positive entries are loss recovered by relaxing the named constraint/package; negative entries worsen it. They telescope exactly along the forward path.','',
 '| Change | Recovered 1−F | Fraction of gap | What recovery would require on the grid (inference) |','|---|---:|---:|---|']
 gains=[('Joint B+C preparation package',0,1,'A smaller/cleaner preparation preserving rejection of dangerous B faults, with its finish time and acceptance maintained. Fewer CX alone is not sufficient.'),('Grid A preparation package → standard A210',1,2,'A short, clean Steane logical plus encoder or economical verification that removes its dangerous Z-hook interactions without delaying the round.'),('Remove data hops/guards',2,3,'No gain on this path. A no-hop layout must improve timing or another package to compensate; deleting the transfers alone loses.'),('Compact delayed prefix',3,4,'No standalone gain at fixed R. Earlier releases must be paired with an earlier round; delayed checks otherwise protect part of the wait.'),('Advance suffix R45→R33',4,8,'Ancillas ready immediately after the compact prefix on genuinely available cells; this couples placement, release times, encoder depth, and movement.'),('Direct readout instead of two parity gadgets',8,9,'Equivalent detector information with direct A/C measurement. The measured benefit is small.'),('v23 prefix → older prefix, matched A210',9,10,'Recover the older prefix’s better early-round fault distribution; the six additional prefix CX do not prevent it from winning here.'),('Reference A-order bridge A210→A012',10,11,'An ordering detail of the reference, not a grid-imposed constraint.')]
 for lab,a,b,need in gains:
  g=rs[a]['total']-rs[b]['total'];lines.append(f'| {lab} | {g:+.8e} | {100*g/gap:+.3f}% | {need} |')
 lines+=['',f'Prefix compaction plus round advancement together recover **{rs[3]["total"]-rs[8]["total"]:.8e} ({100*(rs[3]["total"]-rs[8]["total"])/gap:.3f}% of the gap)**. Quoting only the R45→R33 gain would overstate the benefit of the complete scheduling change.','',
 '### Direct sep33 prefix control','',
 table(['f06_sep33_v23','f07_sep33_old'],['Published A012/B/C/round rebuilt on compact v23 prefix','Published older prefix, identical suffix']), '',
 f'With the literal reference A012 encoder, v23’s prefix costs **{std["total"]-old["total"]:.8e}**: second-order difference {std["second"]-old["second"]:.8e}, third-order difference {std["third"]-old["third"]:.8e}. The A210 matched-prefix difference is {rs[9]["total"]-rs[10]["total"]:.8e}. Thus the prefix price itself depends on the ancillary encoder.','',
 '## Mechanisms','',
 'Each row’s `.exact.txt` contains exact2 `--top 40` fault pairs and the largest triple sets; `.price.json` contains aggregate pair classes, examples, raw weight-3 sum, normalization correction, and retained triple classes. Regions follow unit provenance. `data_cell_idle` follows suffix data-token movement and includes long runs beginning before32; it is deliberately broader than a post32 waiting window.','',
 '| Transition | Largest pair-class deltas, current minus previous | Third-order delta |','|---|---|---:|']
 for i in range(1,len(rs)):
  a,b=rs[i-1],rs[i];pc={k:b['pair_classes'].get(k,0)-a['pair_classes'].get(k,0) for k in a['pair_classes'].keys()|b['pair_classes'].keys()};top=sorted(pc,key=lambda k:abs(pc[k]),reverse=True)[:3]
  desc='All pair-class sums unchanged (within 1e-18)' if max(map(abs,pc.values()),default=0)<1e-18 else '; '.join(f'{k}: {pc[k]:+.6e}' for k in top)
  lines.append(f'| {i-1}→{i}: {LABELS[i]} | '+desc+f' | {b["third"]-a["third"]:+.8e} |')
 lines+=['','The second-order round×round contribution stays **2.88400e-5** throughout the matched ladder, including direct readout. The direct-readout benefit here comes from cross-region faults, not lowering that tail. At R33 the remaining largest triples involve prefix idle faults and a final readout fault rather than three long post-prefix data waits.','',
 '| Rung | Largest retained weight-3 set | Contribution |','|---|---|---:|']
 for n,l,r in zip(F,LABELS,rs):
  v,*labs=r['top_triples'][0];lines.append(f'| {l} | '+ ' + '.join(labs)+f' | {v:.8e} |')
 lines+=['','| Transition | Delta raw weight-3 sum | Delta pair-times-others correction | Largest retained triple-class deltas (partial sums) |','|---|---:|---:|---|']
 for i in range(1,len(rs)):
  a,b=rs[i-1],rs[i];tc={k:b['triple_classes_kept'].get(k,0)-a['triple_classes_kept'].get(k,0) for k in a['triple_classes_kept'].keys()|b['triple_classes_kept'].keys()};top=sorted(tc,key=lambda k:abs(tc[k]),reverse=True)[:2]
  lines.append(f'| {i-1}→{i} | {b["weight3"]-a["weight3"]:+.8e} | {b["pair_times_others"]-a["pair_times_others"]:+.8e} | '+'; '.join(f'{k}: {tc[k]:+.6e}' for k in top)+' |')
 lines+=['','The full third-order correction includes **all** weight-3 contributions and the signed pair-times-others correction. Individual triple examples are retained only above exact2’s threshold, so retained triple-class totals are partial and are never substituted for the exact total.','',
 '## A-encoder order control','',table(['f02_stdA','a_order021','a_order102','a_order120','a_order201','a_order210'],['012','021','102','120','201','210'],read('f02_stdA')['total']),'',
 'These six rows differ only in A’s three layer order, with every other operation and native time fixed. Delta is versus012. This establishes the chosen standard encoder order for the forward rung, not a global synthesis optimum.','',
 '## Verification, execution, and limitations','',
 '- **Measured:** every reported rung passes exact2’s real noiseless judge path, has noiseless acceptance ≈1, and c1 below1e-12. Native times and per-layer cell exclusivity are checked by `build.py` against `tprep.noise.schedule`, not just requested metadata. `.command.json` records the command, process exit, environment, and launch load. The original v23 control is also measured by unmodified exact2 in [f00_base.exact.txt](f00_base.exact.txt).',
 '- **Exact evaluator:** the task brief’s statement that exact2 ignores adjacency is false for this checkout: Model calls the adjacency-checking QASM converter. `price.py` applies the existing grid-free override from MAIN/gf/exact_gf.py. Noise, correctness, conditional acceptance, decoder, and error probabilities remain unchanged.',
 '- **Performance change:** `filtered_price.py` uses dependent detector-projector identities to remove classes with mathematically zero postselected amplitude, then runs exact2’s original surviving fault enumeration and third-order normalization. It does not threshold surviving contributions. [pruning_validation.json](pruning_validation.json) shows zero difference in second, third, total, raw weight3, normalization, and exp(-A1) against unmodified exact2 on both v23 and the no-hop control. The exact2 function source hash is printed in pruned receipts.',
 '- **Execution:** initial unpruned B+C/A jobs on zebra were terminated by PID and rerun to completion on sunfish. Zebra’s capacity guard rejected subsequent launches when shared usage rose; those required runs were routed to sunfish. All reported values have successful completed receipts. The early-initialized reverse-hop construction is retained and explicitly excluded as described above. No worker is intentionally left running.',
 '- **Inferred:** proposed grid changes are implications of counterfactual prices. No new on-grid circuit, static/dynamic embedding feasibility claim, global lower bound, or measured noisy-judge Monte Carlo score is supplied. Original cell-release constraints couple the encoders and hops, so these independent package savings cannot simply be pasted into a grid circuit.',
 '- **Scope:** writes are confined to this lane; Other lanes were read only; submission credentials were never read. No submission, commit, push, or sub-agent was used.','',
 '## Reproduction','',
 'From the repository root, use Python `.venv/bin/python` and set `PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1` for every invocation.','',
 '1. `work/lanes/LADDER/build.py` builds the standard012 controls; `work/lanes/LADDER/build_best.py` builds the selected A210 family; `work/lanes/LADDER/fix_hop_init.py` makes the corrected R37 reverse-hop comparison.',
 '2. `.venv/bin/python work/lanes/LADDER/price.py work/lanes/LADDER/<stem>.qasm --third --top 40 --procs 1 --json work/lanes/LADDER/<stem>.sens.json > work/lanes/LADDER/<stem>.exact.txt` writes the exact receipt and `.price.json`. Set `LADDER_PRUNE=0` for unmodified exact2 enumeration; it is slower but gives the same numbers.',
 '3. `run.py <stem> ...` runs a finite batch, checks host headroom before every launch, and waits on process exit. Use `LADDER_JOBS` within the task’s host limits. All exact commands used are in adjacent `.command.json` files.',
 '4. `report.py` regenerates this report only from passing completed receipts. [source_receipts.json](source_receipts.json) records original source hashes; rung JSON contains all native units and their provenance.']
 (H/'REPORT.md').write_text('\n'.join(lines)+'\n')
 summary=dict(gap=gap,forward=[dict(stem=n,**{k:r[k] for k in ['second','third','total','exp_minus_A1','CX','R']}) for n,r in zip(F,rs)],attribution=[dict(change=lab,recovered=rs[a]['total']-rs[b]['total']) for lab,a,b,need in gains],reverse=[dict(stem=n,total=r['total'],delta=r['total']-base) for n,r in zip(rev,rr)],reverse_hops=dict(R=37,delta=rh1['total']-rh0['total']))
 (H/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print('REPORT complete',len(F),'forward rungs; gap',gap)
if __name__=='__main__':main()
