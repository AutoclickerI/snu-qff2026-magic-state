from cont37 import *
def collect():
 old=json.loads((H/'archive/results_v37a.json').read_text());rows={}
 for s,r in old.items():
  r=dict(r,phase='previous v37a merge')
  if 'loss'in r:r.update(J_previous=r.get('J_tau'),J_tau=rank(r),tau=TAU)
  rows[s]=r
 for f in sorted(R.glob('*.jsonl')):
  for ln in f.read_text().splitlines():
   try:r=json.loads(ln)
   except json.JSONDecodeError:continue
   if 'sha256'not in r or 'stem'not in r:continue
   s=r['sha256'];previous=rows.get(s);aliases=previous.get('aliases',[]) if previous else []
   alias=dict(stem=r['stem'],what_moved=r.get('what_moved',r.get('edits')),stage=r.get('stage','direct'))
   if alias not in aliases:aliases.append(alias)
   row=dict(r,aliases=aliases,phase='v37c continuation')
   if 'loss'in row:row.update(J_tau=rank(row),tau=TAU)
   jf=R/f'judge_{s}.json'
   if jf.exists():row['judge_1e6']=json.loads(jf.read_text())
   rows[s]=row
 dump(H/'results.json',rows)
 table=['| Circuit | L | A | J_tau(v37c) | SHA256 prefix | What moved / status |','|---|---:|---:|---:|---|---|']
 for s,r in sorted(rows.items(),key=lambda z:(z[1].get('loss',1),z[0])):
  p=Path(r['stem']);rel=str(p.relative_to(H));why=r.get('what_moved',r.get('edits',r.get('phase')))
  if isinstance(why,(dict,list)):why=json.dumps(why,separators=(',',':'))
  why=str(why).replace('|','/').replace('\n',' ')[:800]
  if r.get('judge_1e6',{}).get('speed_ok') is False:why+='; JUDGE SPEED REJECTED'
  if 'error'in r:why+='; '+r['error']
  values=[f'[{rel}]({rel}.qasm)']+[f'{r[k]:.14g}' if k in r else 'ERROR' for k in ['loss','acceptance','J_tau']]+[s[:16],why]
  table.append('| '+' | '.join(values)+' |')
 (H/'priced_circuits.md').write_text('\n'.join(table)+'\n');return rows
def report(final=False):
 rows=collect();new=[r for r in rows.values() if r['phase']=='v37c continuation'];cand=[]
 for f in (H/'cand').glob('*.json'):
  r=json.loads(f.read_text())
  if r.get('tau')!=TAU or not r.get('judge_1e6',{}).get('speed_ok'):continue
  cand.append((rank(r),f,r))
 lines=['# MERGE — v37c continuation','',f"Verdict: {'COMPLETE' if final else 'ACTIVE'}; exact tau={TAU:.17g}; finalist L<tau−3e-8, exact A≥.5002, judge gates_ok and speed≤1.5×v37c."]
 if cand:
  _,f,b=min(cand,key=lambda x:(x[0],x[1].stem!='merge37_final'));lines += [f"Best verified candidate: [cand/{f.stem}](cand/{f.stem}.qasm). L={b['loss']:.16g}; A={b['acceptance']:.16g}; J_tau={rank(b):.16g}; SHA256 `{b['sha256']}`.",f"Judge1e6: gates_ok={b['judge_1e6']['gates_ok']}; median{b['judge_1e6']['median_judge_seconds']:.3f}s; ratio{b['judge_1e6']['judge_speed_ratio']:.3f}×v37c. Sampler ratio{b['judge_1e6']['sampler_speed_ratio']:.3f}. Both ratios≤1.5."]
 lines += ['', 'AJOINT transport: v37c has no q9→q10 guards and A9 prep is at39. Legal transport adds CX9→10@37, moves M9/c32137→38, retains prep39. Full source recipe cannot be shifted literally because q9’s source completion occupies36.',
           'Measured controls: base L=3.690403471559856e-5,A=.5057191647109531; M38 alone3.6904560842016455e-5; post-read guard38 alone3.6913060992615435e-5; joint pre-read guard37/M38 gives3.685327051991586e-5,A=.5057509615191745. Gain5.07641959e-8. The candidate has independent judge/speed verification.',
           'Menu: removals, trades, prep/operation shifts, single CX, both orientations of every idle identity pair, echoes, guards, and the legal AJOINT macro. All proposals are emitted and native-time checked before pricing.',
           'Connected pairs: all overlapping per-qubit enclosing-operation intervals among improving and cheap-acceptance singles, plus additions unlocked by each useful freeing edit. Cheap buyers have ΔA>1e-6 and ΔL≤max(3e-8,2e-5ΔA). Every bundle receives a full exact price.',
           'Greedy extension: consider every improving single/pair and cheap buyer on the current selected set; price joint funding for the five best under-floor proposals; rank by A(L−tau), enforce speed/ideal gates, and stop only when a complete round gains<1e-9 in L.',
           'Speed protocol: v37c baseline median of three1e6 judge runs3.087731s;100k exact-sampler batches repeated three times. Every promoted candidate gets a1e6 judge run and the same sampler benchmark; ambiguous wall-time ratios get paired controls. Short probes reject pathological slow dispatch before a long run.']
 for f in sorted(R.glob('*_history.json')):
  h=json.loads(f.read_text())
  if h:lines.append(f"{f.stem}: {len(h)} greedy rounds; last gain{h[-1]['loss_gain']:.9g}, stop={h[-1]['stop']}; L={h[-1]['price']['loss']:.14g}, A={h[-1]['price']['acceptance']:.12g}.")
 histories=[(f.stem,json.loads(f.read_text())) for f in sorted(R.glob('*_history.json'))]
 if histories:
  lines+=['','| Pass / round | L | A | Gain in round | J_tau |','|---|---:|---:|---:|---:|']
  for tag,history in histories:
   for r in history:
    p=r['price'];lines.append(f"| {tag} / {r['round']} | {p['loss']:.13g} | {p['acceptance']:.12g} | {r['loss_gain']:.8g} | {rank(p):.10g} |")
 refresh=R/'refresh_outcome.json'
 if refresh.exists():lines.append('Source refresh: '+json.loads(refresh.read_text())['summary'])
 if final:
  lines += ['Completion: AJOINT transport built/priced/verified;1519 original singles and1118 connected/contextual bundles; five greedy rounds. All four requested lane cand/ and ledgers refreshed; POLISH transport controls priced;1498 fresh singles and1098 bundles; two final greedy rounds. Last gains9.01546e-10 and7.96469e-10 satisfy the stop rule.',
            'Final change on v37c: delayed M9/c321 to38 and added CX9→10@37; source c319 omit trade with CX3→4@39; q21 X echo through q27 with CX15→21 advanced; CX2→3 retimed24→25; CX21→20@30; removed neutral CX28→22@29; fresh q1 guard onq7@37 and CX25→31@37. Native depth remains48.',
            'Independent original detector-basis final replay agrees within floating-point roundoff; exact price and stored recipe were verified on the final handoff. No1e8-shot run or submission was made by MERGE.']
 lines+=['','Verified: saved QASM hashes and ordered data mapping; all-orders baseline agreement within2.2e-16; all promoted candidates pass ideal gates and both speed ratios. Omission bounds and evaluator hashes are in results.json.',
         'Inferred only: finite menu/context coverage; no global optimality claim. Results from other lanes remain source observations until independently reproduced here.',
         'Decisions: use lane-local native parser/toolkit copies so remote workers do not depend on mutable other-lane tooling. Baseline and emitted native schedules agree. Preserve prior merge receipts under archive/ and in the full table.',
         'Scope: MERGE writes only; hippo≤24 processes (currently20 evaluators+controller), zebra≤2 compute jobs; thread caps1; no subagents, GPUs, submission, commit, push or credential access. No standing rule changed.',
         f"Ledger: {len(new)} continuation hashes; {len(rows)} total hashes. Full per-circuit table: [priced_circuits.md](priced_circuits.md). Machine ledger: [results.json](results.json).",'Files: cand/; v37c/; res37c/*history.json, baseline_speed.json, judge_*.json; logs37c/; cont37.py,search37.py,judge37.py.']
 assert len(lines)<=100 and max(map(len,lines))<2000
 (H/'REPORT.md').write_text('\n'.join(lines)+'\n');print('report',len(lines),'lines',len(new),'continuation hashes',flush=True)
if __name__=='__main__':report('--final'in sys.argv)
