import json,math
from pathlib import Path
H=Path(__file__).resolve().parent;D=H/'blue'
def report():
 bases={b:json.loads((D/'finalists'/b).with_suffix('.screen.json').read_text()) for b in ['v25k','v26n']}
 rows=[]
 for f in (D/'finalists').glob('*.screen.json'):
  r=json.loads(f.read_text());tag=f.name[:-12];v=f.with_name(tag+'.verify.json')
  if v.exists():r.update(json.loads(v.read_text()));rows.append(r)
 rows.sort(key=lambda r:r.get('total',1))
 lines=['# BCFB','', 'Status: RUNNING — blue-context ports, speed gates and exact-loss feedback. Prior completed campaign: [REPORT_v23.md](REPORT_v23.md). No submission, commit or push.','', 'Hard gates: full judge PASS, seed-0 acceptance ≥0.5 and zebra 1e6-shot single-process command ≤20 seconds. Rank by 1-F; close finalists require ≥100 seed-0 re-draws.','', '| Base | Exact second | Cubic | Exact total | exp(-A1) |','|---|---:|---:|---:|---:|']
 for b,r in bases.items():lines.append(f"| {b} | {r['second']:.12g} | {r['third']:.12g} | {r['total']:.12g} | {r['exp_minus_A1']:.9f} |")
 if (D/'base_redraws.json').exists():
  lines+=['','MAIN re-draw references (v26n remains in progress):']
  for b,r in json.loads((D/'base_redraws.json').read_text()).items():lines.append(f"- {b}: {r['draws']} draws; {r['mean']:.12g} ± {r['sem']:.3g} SEM; all passed={r['all_passed']}.")
 lines+=['','Delta columns are candidate minus base. A1 = -log(exp(-A1)); negative is better acceptance.','', '| Stem (`blue/finalists/`) | Exact | Δ1-F v25k / v26n | ΔA1 v25k / v26n | exp(-A1) | Zebra s | Judge acc | Exact CLI |','|---|---:|---:|---:|---:|---:|---:|---|']
 for r in rows:
  delta=' / '.join(f"{r['total']-b['total']:+.5g}" for b in bases.values());da=' / '.join(f"{math.log(b['exp_minus_A1']/r['exp_minus_A1']):+.5g}" for b in bases.values())
  lines.append(f"| `{r['tag']}` | {r['total']:.12g} | {delta} | {da} | {r['exp_minus_A1']:.9f} | {r.get('speed_seconds',0):.3f} {'PASS' if r.get('speed_pass') else 'FAIL'} | {r.get('acceptance','—')} {'PASS' if r.get('judge_pass') else 'FAIL'} | {r.get('exact_verified',False)} |")
 if (D/'checkpoint_candidates.json').exists():
  lines+=['','Current feedback checkpoint (screened until its Exact CLI column passes):']
  for context,r in json.loads((D/'checkpoint_candidates.json').read_text()).items():
   md=json.loads((D/'finalists'/r['tag']).with_suffix('.json').read_text());lines.append(f"- {context}: `{r['tag']}`, {r['total']:.12g}, prep {md['verification']['cx']} CX, R={md['R']}, exterior native timing changes `{md['non_BC_time_changes']}`.")
 verified=[r for r in rows if r.get('exact_verified') and r.get('gates_pass')]
 if verified:
  r=verified[0];md=json.loads((D/'finalists'/r['tag']).with_suffix('.json').read_text())
  lines+=['',f"Best independently confirmed exact: `{r['tag']}`; c1={r['c1']:.12g}, second={r['second']:.12g}, cubic={r['third']:.12g}, total={r['total']:.12g}, exp(-A1)={r['exp_minus_A1']:.12g}. MC ranking pending.",f"Diff: prep {md.get('verification',{}).get('cx','base')} CX; round {md['R']}; options `{json.dumps(md.get('options',{}),sort_keys=True)}`; exterior timing changes `{json.dumps(md.get('non_BC_time_changes',{}))}`."]
 lines+=['','| Feedback seed | Context / D / cap | Budget s | Status | Witnesses | Best screened exact |','|---|---|---:|---|---:|---:|']
 for f in sorted((D/'runs').glob('blue_s*.process.json')):
  stem=f.name[:-13];pr=json.loads(f.read_text());cmd=pr['cmd'];val=lambda k:cmd[cmd.index(k)+1];log=f.with_name(stem+'.log');prices=[]
  for line in log.read_text().splitlines() if log.exists() else []:
   try:r=json.loads(line)
   except ValueError:continue
   if 'kind' in r:prices.append(r)
  rc=f.with_name(stem+'.exit.json');status=('FINISHED' if json.loads(rc.read_text())['exit_code']==0 else 'FAILED') if rc.exists() else 'RUNNING';best=min([r.get('total',1) for r in prices],default=1)
  lines.append(f"| {stem} | {val('--context')} / {val('--depth')} / {val('--cap')} | {val('--seconds')} | {status} | {len(prices)} | {best:.12g} |")
 for f in sorted((D/'runs').glob('neighbor_*.receipt.json')):
  r=json.loads(f.read_text());lines.append(f"| {f.stem} | init toggles and init checks, radius ≤2 | finite | {r['status']} | {r['prices']} | {r['best_eligible']:.12g} |")
 if (D/'round_receipt.json').exists():
  r=json.loads((D/'round_receipt.json').read_text());lines.append(f"| Round shifts R45–R50, windows 4/12 | four leading preps | finite | {r['status']} | {r['prices']} | {r['best']:.12g} |")
 if (D/'retry_receipt.json').exists():
  r=json.loads((D/'retry_receipt.json').read_text());lines.append(f"| Failed schedules retried at window 4 | both contexts | finite | {r['status']} | {r['prices']} | {r['best']:.12g} |")
 lines+=['','Counts above are recorded proposals, including repeats across seeds and rejected schedules.','', '| MAIN mc3 stem | Seed 0 | Seed 1000 | Seed 2000 | Mean | Seed-0 acceptance |','|---|---:|---:|---:|---:|---:|']
 for f in sorted((D/'finalists').glob('*.mc.json')):
  r=json.loads(f.read_text());v=r['seeds'];lines.append(f"| `{r['stem']}` | {v[0]['score']:.9g} | {v[1]['score']:.9g} | {v[2]['score']:.9g} | {r['mean']:.9g} | {v[0]['acceptance']:.5f} |")
 lines+=['','| Re-draw stem | Completed draws | Mean 1-F | SEM | ΔMC v25k / v26n | Minimum acceptance |','|---|---:|---:|---:|---:|---:|']
 from blue_redraw_summary import summarize
 for stem,r in summarize().items():
  refs=json.loads((D/'base_redraws.json').read_text()) if (D/'base_redraws.json').exists() else {}
  delta=' / '.join(f"{r['mean']-refs[b]['mean']:+.5g}" if b in refs else '—' for b in ['v25k','v26n'])
  lines.append(f"| `{stem}` | {r['draws']} {'COMPLETE100' if r['complete100'] else 'provisional'} | {r['mean']:.12g} | {(r['sem'] or 0):.3g} | {delta} | {r['min_acceptance']:.8f} |")
 if (D/'ablation.json').exists():
  lines+=['','Screened mechanism ablation (validated Fourier evaluator, no independent CLI claim for these rejected variants):']
  for r in json.loads((D/'ablation.json').read_text()):lines.append(f"- `{r['tag']}`: {r.get('total',float('nan')):.12g}, exp(-A1)={r.get('exp_minus_A1',float('nan')):.9f}.")
  lines+=['Applying the five exterior timing moves to the original 82-CX prep worsens loss by about 2.07e-7 on either base. The clean replacement network produces the net gain despite that cost.']
 if (D/'network_ablation.json').exists():
  lines+=['','Network/timing ablation:']
  for r in json.loads((D/'network_ablation.json').read_text()):lines.append(f"- {r['context']} 86-CX network with the old 88-CX port’s five timing moves: {r['retimed_score']['total']:.12g}. Removed/added CX multiplicities: `{r['removed']}` / `{r['added']}`. Full Clifford-map equality with the 88-CX network: {r['same_full_clifford_map']}.")
  lines+=['The new networks fit the unchanged exterior timing. Applying the old port’s timing moves to them adds about 2.04e-7 loss. This explains the context-dependent optimum. R48 is a lower bound for the retained native wire order, through the chain ending at CX 1→2; it is not a global architectural bound. See `blue/critical_path.json`.']
 lines+=['','Mechanisms and verification: the original 82-CX preparation replays both bases with exact loss agreement <1e-15. All exterior operations and detector definitions are retained, with the old BC frame corrections replaced by the new ones. The q19 speed repair is retained as reset+H when q19 is a pivot, or Z reset when the new prep makes it a nonpivot. Depth-15 ports need retiming in the new blue context; this is measured separately. The Fourier screen uses the unchanged exact2 model/decoder; independent unmodified CLI confirmations are recorded per row. Speed is measured on zebra with the exact requested command. Screened values alone are not verified improvements.','', 'XTIM’s completed [report](../XTIM/REPORT.md) independently supports retaining q19 reset+H and measuring runtime: moving the q19 MX across one T gate remains slow, while generic MX timing/counts do not predict the path. This campaign has not run XTIM’s code or modified its directory. Cache incident: the initial sampler inherited xtim’s default repository `.xtim_cache` path; the twirl environment variable did not redirect the separate reference cache. It was stopped by verified host PID, completed draws were preserved, and resumed with `xtim.cache_dir` under BCFB. Speed/MC subprocesses now also run from the lane directory. Shared cache entries were not deleted. See `blue/cache_restart.json` and `blue/cache_audit.json`. Re-draw comparisons remain in progress; partial means are provisional. No global optimality claim. Early-MX timing is not used as an admissibility proxy: measured speed is the hard gate. The original global-after-last-T probe proved overly restrictive because native T-dagger operations remain at steps 35, 36 and 47 in these bases; those failed schedules do not imply a speed failure.']
 (H/'REPORT.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':report()
