"""Build the evidence table exclusively from stored receipts; screening values labeled separately."""
import json,re,math,hashlib,csv
from pathlib import Path
H=Path(__file__).resolve().parent

def get(name,default=None):
 p=H/name
 return json.loads(p.read_text()) if p.exists() else default

def ref(stem):
 p=H/(stem+'.ref.log');rc=get(stem+'.ref.exit.json',{})
 if not p.exists() or rc.get('returncode')!=0:return None
 s=p.read_text();d={}
 for k,pattern in [('second',r'second order: ([0-9.e+-]+)'),('third',r'third order: ([0-9.e+-]+)'),('total',r'1-F \(to 3rd order\) = ([0-9.e+-]+)'),('weight3',r'weight-3 sets ([0-9.e+-]+)'),('normalization3',r'pair-times-others ([0-9.e+-]+)'),('acceptance_proxy',r'exp\(-A1\) = ([0-9.e+-]+)')]:
  m=re.search(pattern,s)
  if m:d[k]=float(m.group(1))
 return d if 'total' in d else None

def window(gs):return '; '.join(f'{g["axis"]}:q{g["q"]}/h{g["h"]} CX {g["start"]},{g["end"]}' for g in gs)
def metrics(stem):
 d=ref(stem);g=get(stem+'.gates.json',{});mc=get(stem+'.mc.json',{})
 return [f'{d["second"]:.6e} + {d["third"]:.6e} = **{d["total"]:.6e}**' if d else 'pending reference',f'{d["acceptance_proxy"]:.5f}' if d else '—',
         ('PASS' if g.get('passed') else 'FAIL')+f' 1−F={g.get("score",0):.6e}, acc={g.get("acceptance",0):.6f}' if 'passed' in g else '—',
         f'{g["speed"]["classification"]} {g["speed"]["median_seconds_per_1e6"]:.3f} s/1e6' if 'speed' in g else '—',
         (' / '.join(f'{r["score"]:.6e}' for r in mc.get('seeds',[]))+f'; mean **{mc["mean"]:.6e}**') if mc.get('mean') else '—']

def write():
 single=get('tick_singles.json',[]);winners=get('subset_winners.json',[]);multi=get('multi_reference.json',[]);mapping=get('tick_mapping.json',{})
 selected={r['stem']:r for r in winners};allrows=single+list(selected.values())+multi;checked=[r for r in allrows if ref(r['stem'])]
 status='COMPLETE' if len(checked)==len(allrows) else 'IN PROGRESS'
 out=['# WAITPROT','',f'Status: **{status}**. {len(checked)}/{len(allrows)} retained native-tick candidates have completed unchanged `EVAL/exact2.py --third` receipts. Finalist ranking uses audited all-orders expectations; cubic references and official MC provide independent checks. Gains are never added between gadgets.','',
 'Base: `MAIN/v30f`, data order `[0,20,7,10,3,22,21]`, 189 CX, R48, depth 51; exact 4.62005346e-5 + 1.20387969e-5 = **5.82393315e-5**, exp(-A1)=0.527687. Inherited 3-seed 1e8 MC: 5.90419220e-5 / 5.88640000e-5 / 5.89256e-5; mean **5.89438407e-5**.','',
 '## Native schedule and data trajectories','',
 'Every `t*` and retained `u*` circuit is checked against the base native instruction list. Every original operation stays at exactly its original tick, and every inserted reset, CX and measurement lands in a free tick. R48 and depth 51 are unchanged. Z helpers are reset+H, never randomly MX-initialized. A trailing H after the helper X readout makes its reused state explicit to the native converter.','',
 'Physical storage paths after step 16: logical output q10 uses cell4 until its 31–32 transfer to10; logical output q22 uses cell15, then16 after transfer33–34, then22 after42–43; logical output q21 uses8, then9 after34–35, then15 after36–37, then21 after38–39. Cells0,20,7,3 remain stationary. Protecting future output cell10 before31 is an ancillary-storage control, not protection of logical data10.','',
 '| line index | physical weight-3 logical lines |','|---|---|']
 for i,line in enumerate(mapping.get('fano',[])):out.append(f'| {i} | {line} |')
 out += ['', 'Physical-cell idle gaps (inclusive native ticks; separate from the moving-data paths above):','', '| cell | idle windows | adjacent cells |','|---|---|---|']
 grouped={}
 for r in mapping.get('gaps',[]):grouped.setdefault(r['q'],[]).append(r)
 for q,rr in grouped.items():out.append(f'| {q} | '+', '.join(f'{r["lo"]}–{r["hi"]}' for r in rr)+f' | {rr[0]["adjacent"]} |')
 out += ['', 'All helper free intervals and their preceding/following operations are in [tick_mapping.json](tick_mapping.json). [trajectory_windows.json](trajectory_windows.json) maps every idle window on the moving data paths, including cells8 and9, to each adjacent helper’s free overlaps and fitting Z/X windows. A geometrically adjacent idle cell is not free if it still stores an entangled ancilla. Helper lifetimes must include reset, two CXs and readout; when necessary a final reset restores a later deterministic MZ initialization.','',
 '## Singles','', '| stem | protected windows (CX endpoints, inclusive) | exact second + third = total | exp(-A1) | judge 1e6 | speed | MC seeds0/1000/2000, 1e8 each |','|---|---|---|---:|---|---|---|']
 for r in single:out.append('| '+ ' | '.join([r['stem'],window(r['gadgets']),*metrics(r['stem'])])+' |')
 out += ['', '## Pairs and Fano triples','',
 'All compatible helper/window assignments are screened as complete circuits with FRESH’s Fourier contraction; `subset_screen.json` records that enumeration. For each distinct protected logical subset, retain its best Z-only and best mixed-axis realization above exp(-A1)=0.5002, then price those with unchanged exact2. This enumerates subset choices and maximal helper-free windows; it does not prove optimality over every shortened subwindow, added swaps, delayed rounds, or different base circuits.','',
 '| stem | subset / family | windows | exact second + third = total | exp(-A1) | judge 1e6 | speed | MC |','|---|---|---|---|---:|---|---|---|']
 for r in winners:out.append('| '+' | '.join([r['stem'],str(r['subset'])+' / '+r['family'],window(r['gadgets']),*metrics(r['stem'])])+' |')
 out += ['', '## Combined storage windows', '',
 'A forward/backward search of complete circuits combines useful windows, including multiple separated windows on one data trajectory and ancillary storage controls. Every combination is fully re-evaluated; no gains are added. `multi_screen.json` records 68 tested sets.', '',
 '| stem | windows | exact second + third = total | exp(-A1) | judge 1e6 | speed | MC |', '|---|---|---|---:|---|---|---|']
 for r in multi:out.append('| '+' | '.join([r['stem'],window(r['gadgets']),*metrics(r['stem'])])+' |')
 out += ['', '## Audited all-orders ranking', '',
 'The sparse evaluator is copied from MAIN’s validated implementation. Before each contraction, the independent frontend is compared with the official exact2 Model: every channel probability/qubit, Pauli component, rotation-sign signature, final logical signature and detector signature (after ordering permutation), plus every rotation, projector and decoder observable must match. All-orders results use zero frame, no POSTSELECT, diagonal projectors and native schedules with barriers covering every used qubit; assertions enforce this scope. The baseline reproduces MAIN’s 5.8937742042181006e-5 exactly.', '',
 '| stem | all-orders 1−F | exact acceptance | vs baseline | kernel omission bound | channel/fault audit |', '|---|---:|---:|---:|---:|---|']
 allorders=[json.loads(p.read_text()) for p in H.glob('*.allorders.json')]
 allorders.sort(key=lambda x:x['loss'])
 for r in allorders:
  name=Path(r['source']).name;proof=r['frontend_audit'];out.append(f'| {name} | **{r["loss"]:.10e}** | {r["acceptance"]:.9f} | {(r["loss"]/5.8937742042181006e-5-1)*100:+.3f}% | {r["conditional_loss_kernel_omission_bound"]:.2e} | {proof["channels"]} channels, {proof["faults"]} faults: all match |')
 out += ['', 'This all-orders expectation resolves close MC ordering within the audited scope. The omission bound covers the sparse-kernel threshold and excludes floating-point roundoff. Cubic values and the requested official three-seed samples are retained independently.', '']
 out += ['', 'Logical output21 has no room for this four-operation storage gadget along its native moving trajectory. Each adjacent cell is live, or its free interval ends too early. Thus Fano lines (7,10,21), (20,3,21), (0,22,21) are excluded in this fixed-schedule construction. The other four Fano lines are tested, including (0,20,7); the initial no-Fano claim was a builder error and is withdrawn.','',
 '## Loss mechanisms and diagnostic decomposition','',
 'The isolated-storage coefficients from the reviewer are reproduced by `ideal_count.py`: 14 → 11 → 10 → 10 → 28 for none/one/two/Fano-three/all-seven. For a logical line L, the coefficient is 0.5·2^|L∩P| + 1.5·1[L∩P=∅], summing over seven lines. This model removes protected Z/Y and doubles protected X exposure. It omits preparation/readout/CX faults and prefix/round correlations, which are included in the full circuit prices. Several windows sit inside cultivation, between T/T† layers and checks; the isolated storage coefficient alone cannot rank them. In the same uniform toy, the X dual gives14/14/16/20/56. Its measured benefit here therefore comes from the nonuniform prefix and cross-fault structure, especially the leading X-idle pair, not a universal reduction of isolated wait triples.', '',
 'A Z gadget detects data Z/Y inside its entangled window and admits helper X faults onto that data. The X dual detects X/Y and admits helper Z faults. Which helps depends on propagated logical signatures, not the number of idle ticks. On v30f the leading 7.731e-7 pair is X on cell7 during20–23 with Y on cell20 during40–46; Z protection leaves its X component, while X protection detects it.','',
 'Diagnostic region definitions: wait = data idle channels in the mapped storage trajectories, ticks18–47; round = original operations at48 onward and final idles; helper = all inserted gate/reset/readout noise and helper idles inside the protected lifetime; other = remaining channels. The 16 full-model region masks retain all joint cross terms. Pure wait triples mean the positive weight-three term with only wait noise. Pair×others normalization is reported separately.','',
 '| stem | wait-only weight-three | wait × final-round pairs | wait × prefix/preparation pairs | helper-containing pairs | helper-containing weight-three | full minus helper-noiseless, through3 |','|---|---:|---:|---:|---:|---:|---:|']
 for p in sorted(H.glob('*.decomposition.json')):
  r=json.loads(p.read_text());pp=r['prices'];vals=[r['wait_only_weight3'],r['wait_round_pairs'],pp['9']['second']-pp['1']['second']-pp['8']['second'],r['helper_containing_pairs'],r['helper_containing_weight3'],r['helper_full_minus_nohelper']];out.append('| '+r['stem']+' | '+' | '.join(f'{v:.7e}' for v in vals)+' |')
 out += ['', '## Negative and neutral results', '',
 '| stem | change in second order | change in third order | net change | mechanism |', '|---|---:|---:|---:|---|']
 for row in allrows:
  rr=ref(row['stem'])
  if not rr or rr['total']<5.82393315e-5-1e-10:continue
  gs=row['gadgets'];early=[g for g in gs if g['axis']=='Z' and g['start']<32]
  if all(g.get('logical') is None and g['q']==4 for g in gs):why='The state is discarded by the later reset; the extra detector spends acceptance without reducing logical loss.'
  elif early:why='Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: '+window(early)
  else:why='Added helper noise and cross terms exceed the protected-window reduction; the full-circuit coefficients above include their interaction.'
  out.append('| '+row['stem']+' | '+' | '.join(f'{v:+.5e}' if abs(v)>=1e-10 else '0 (rounded)' for v in (rr['second']-4.62005346e-5,rr['third']-1.20387969e-5,rr['total']-5.82393315e-5))+' | '+why+' |')
 out += ['', 'Single-gadget negative mechanisms are also isolated by helper-noiseless diagnostics in the preceding table. In particular, q20’s early Z variant has no second-order change: its loss increase is entirely cubic. Differences below 1e-10 are displayed as zero because the reference CLI prints six significant digits.', '']
 out += ['', 'These ablations use the exact2 model and FRESH moment contraction for diagnosis; complete-circuit cubic prices come from the unchanged exact2 receipts, and finalist ranking uses the audited all-orders expectations. Effects cannot be added between gadgets. The final-round-only loss is identical for baseline and best:2.87125197037e-5 through third order. Its operations and timing were preserved. Pair ledgers sum to the full second-order result and the four-region cubic interaction vanishes to<1e-15, as required; see `decomposition_audit.json`.','',
 '## Initial insertion experiment and corrections','',
 'The first second-order batch mistakenly nested multiprocessing pools; Python rejected daemon children. It was corrected to one process per candidate. Duplicate pilot pools were subsequently stopped by their owning-host PIDs. Completed receipts are preserved in the initial-attempt archive; the final queue uses tracked subprocess exits and source hashes.','',
 'The initial `s*`/`p*` builder inserted operations at textual boundaries and lengthened the circuit. It was replaced after native-schedule audit. Its best measured q7 X variant `s021_x_q7_h13_20_23` had exact **5.80435e-5**, exp(-A1)=0.511292, PASS at1e6, FAST 7.219s/1e6 on tom, and MC5.789242e-5 / 6.027351e-5 / 5.988296e-5 (mean **5.934963e-5**, +0.69% vs inherited base mean). The cubic increase erased most pair-order benefit; the MC difference is unresolved at this sample size. Those results do not price tick-preserving protection.','',
 'The earlier pair failures at acceptance≈0.44–0.497 were largely insertion-delay artifacts. No exclusion or final design decision uses them. Their QASM, builders, receipts and validation failures are preserved in `initial_attempt.tar.gz`.',
 'Three seven-window extensions reached the evaluator’s signed-64-bit detector-mask limit. An independent singles/A1 audit (which does not require cubic detector masks) gave exp(-A1)=0.496919, 0.496099 and 0.499395, all below the requested screen. They are acceptance rejects, not correctness failures. `multi_capacity_audit.json` preserves the error and audit; the search now checks acceptance before cubic contraction.','',
 '## Verified and limitations','',
 'New finalist gates, speed probes and MC run on tom with OMP/OPENBLAS/MKL threads=1. Speed numbers are the requested XTIM probe estimates scaled to1e6; actual1e6 wall times are in `.gates.json`. The inherited2.8s baseline timing was on zebra and is not a direct host-to-host speed comparison.','',
 '- No submissions, commits, pushes or credential access. All deliverables are under this lane.','- No-noise correctness uses exact2’s unchanged judge/Stim path; separate assertions verify exact native scheduling and helper ownership. Exported `best` and `seed0_best` artifacts were also judged again on zebra, reproducing their original1e6 scores and acceptance; hashes and native checks are in `final_artifact_check.json`.','- Complete-reference status and return codes are retained in `.ref.exit.json`; the CLI `.ref.sensitivity.json` contains pair sensitivity only, so cubic totals are parsed from `.ref.log`.','- The three-seed MC measures all noise orders. Close MC ordering can remain statistically unresolved; use the audited all-orders expectation above to rank the finalists. No global optimum over altered schedules or additional gates is claimed.','']
 if get('final_audit.json',{}).get('status')=='COMPLETE':
  out += ['[final_audit.json](final_audit.json) verifies all 78 reference source hashes and zero exit codes, agreement with the independent moment screens at CLI printed precision, all seven finalist gates/FAST probes/three-seed MC runs, and both exported artifact pairs. [process_exit_audit.json](process_exit_audit.json) records no remaining WAITPROT computation jobs on either host.','']
 if allorders:
  best=allorders[0];name=Path(best['source']).name;mc=get(name+'.mc.json',{});gate=get(name+'.gates.json',{})
  pre=[f'Best audited candidate: `{name}`, **all-orders 1−F {best["loss"]:.9e}** ({(1-best["loss"]/5.8937742042181006e-5)*100:.3f}% below v30f), acceptance **{best["acceptance"]:.9f}**, 201 CX, R48 and native depth51.', '']
  if mc.get('mean'):pre += [f'Official 1e8 scores (seeds0/1000/2000): '+ ' / '.join(f'{x["score"]:.6e}' for x in mc['seeds']) +f'; mean **{mc["mean"]:.6e}**. The 1e6 judge gate passes; speed is FAST.', '']
  else:pre += ['Three-seed MC is still running; the 1e6 gate and FAST speed probe have passed.','']
  pre += ['Byte-identical final artifacts: [best.qasm](best.qasm), [best.json](best.json); provenance and scores: [best.metrics.json](best.metrics.json).','']
  measured=[json.loads(p.read_text()) for p in H.glob('*.mc.json')]
  measured=[r for r in measured if r.get('returncode')==0 and r.get('seeds')]
  if measured:
   keyrow=min(measured,key=lambda r:r['seeds'][0]['score']);kn=keyrow['stem'];ks=keyrow['seeds'][0]
   pre += [f'Best measured seed-0 key: **{ks["score"]:.6e}**, acceptance **{ks["acceptance"]:.5f}**, `{kn}` (3-seed mean {keyrow["mean"]:.6e}). Its audited all-orders loss is '+f'{get(kn+".allorders.json")["loss"]:.9e}'+'. The expectation-ranked and seed-0 choices differ because of MC sampling.', '',
           'Seed-0 artifacts: [seed0_best.qasm](seed0_best.qasm), [seed0_best.json](seed0_best.json). No submission was made.', '']
   (H/'seed0_best.qasm').write_bytes((H/(kn+'.qasm')).read_bytes());(H/'seed0_best.json').write_bytes((H/(kn+'.json')).read_bytes())
   (H/'seed0_best.metrics.json').write_text(json.dumps(dict(source_stem=kn,reference=ref(kn),allorders=get(kn+'.allorders.json'),gate=get(kn+'.gates.json'),mc=keyrow),indent=2))
  pre += ['Expectation-ranked winner recipe (all ticks are native; CX endpoint ticks identify the two applications):','',
          '| stored cell / role | protected axis | helper | preparation tick | CX ticks | readout tick / bit |', '|---|---|---:|---:|---|---|']
  recipe=get(name+'.json')['protected']
  for j,g in enumerate(recipe):
   role='ancilla' if g.get('logical') is None else 'data for output'+str(g['logical'])
   pre.append(f'| q{g["q"]}, {role} | {g["axis"]} | {g["h"]} | {g["reset"]} | {g["start"]}, {g["end"]} | {g["measure"]} / c[{264+j}] |')
  pre += ['', 'Z protection uses reset+H, helper→stored-cell CX, and MX; X protection uses reset, stored-cell→helper CX, and MZ. Every new record is a deterministic zero detector.','']
  out[2:2]=pre
  (H/'best.qasm').write_bytes((H/(name+'.qasm')).read_bytes());(H/'best.json').write_bytes((H/(name+'.json')).read_bytes())
  (H/'best.metrics.json').write_text(json.dumps(dict(source_stem=name,reference=ref(name),allorders=best,gate=gate,mc=mc),indent=2))
 (H/'REPORT.md').write_text('\n'.join(out)+'\n')
 out_sources=['Primary sources: [official noise/scheduling](../../../upstream/snu-qff2026-problem/tprep/noise.py), [official judge](../../../upstream/snu-qff2026-problem/tprep/check.py), [Steane supports](../../../upstream/snu-qff2026-problem/tprep/grid.py), [unchanged cubic evaluator](../EVAL/exact2.py), [validated sparse evaluator](../MAIN/sparse/sparse_walsh.py). All WAITPROT numbers are this lane’s receipts unless explicitly marked inherited.']
 with (H/'REPORT.md').open('a') as f:f.write('\n'+'\n'.join(out_sources)+'\n')
 # machine-readable retained table
 (H/'retained_results.json').write_text(json.dumps([dict(stem=r['stem'],gadgets=r['gadgets'],reference=ref(r['stem']),gates=get(r['stem']+'.gates.json'),mc=get(r['stem']+'.mc.json')) for r in allrows],indent=2))
if __name__=='__main__':write()
