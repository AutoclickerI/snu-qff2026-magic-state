"""Publish current standalone prices for ST2 without writing outside this lane."""
import json,collections,hashlib
from v35_build import H,V,ROOT,BASE,BASE_SHA,L0,A0,fa,lines,DATA

def circuit(p):
 oo,dd=fa.parse_current(p.with_suffix('.qasm').read_text())
 return dict(ops=[dict(kind=o.kind,qs=list(o.qs),t=o.time,bit=o.bit)for o in oo],dets=[sorted(d)for d in dd])
def patch(c):
 def key(o):return(o['t'],o['kind'],tuple(o['qs']),o['bit'])
 aa={key(o):o for o in BASE['ops']};bb={key(o):o for o in c['ops']}
 return dict(remove=[dict(t=aa[k]['t'],lines=lines(aa[k]))for k in aa.keys()-bb.keys()],add=[dict(t=bb[k]['t'],lines=lines(bb[k]))for k in bb.keys()-aa.keys()],detector_remove=['// DETECTOR '+' '.join(f'c[{b}]'for b in r)for r in BASE['dets']if r not in c['dets']],detector_add=['// DETECTOR '+' '.join(f'c[{b}]'for b in r)for r in c['dets']if r not in BASE['dets']])
def main():
 entries=[]
 for p in sorted(V.glob('*.score.json')):
  r=json.loads(p.read_text());st=V/r['stem']
  if r.get('description',{}).get('family')in('combination','baseline'):continue
  item=dict(gadget=r['stem'],source='WAITPROT',stem=str(st.relative_to(ROOT)),description=r['description'],ok=r['ok'])
  if r['ok']:
   cost=A0-r['acceptance'];gain=L0-r['loss']
   item.update(loss=r['loss'],acceptance=r['acceptance'],loss_gain=gain,acceptance_cost=cost,gain_per_acceptance=gain/cost if cost>0 else None,eligible=r['acceptance']>=.5005,c1=r['c1'],lines=patch(circuit(st)),sha256=r['sha256'])
  else:item['error']=r['error']
  entries.append(item)
 for group in ['additions','fasttrack']:
  for p in sorted((ROOT/'work/lanes/ST2/v35'/group).glob('*.score.json')):
   r=json.loads(p.read_text())
   if group=='fasttrack'and not p.name.startswith('guard_'):continue
   if not r.get('ok')or'loss'not in r:continue
   st=p.with_name(p.name.removesuffix('.score.json'));cost=A0-r['acceptance'];gain=L0-r['loss']
   entries.append(dict(gadget='ST2/'+st.name,source='ST2 imported, not rerun',stem=str(st.relative_to(ROOT)),description=r['description'],ok=True,loss=r['loss'],acceptance=r['acceptance'],loss_gain=gain,acceptance_cost=cost,gain_per_acceptance=gain/cost if cost>0 else None,eligible=r['acceptance']>=.5005,lines=patch(circuit(st)),sha256=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()))
 out=dict(base='work/lanes/MAIN/v35a',base_snapshot='work/lanes/WAITPROT/v35/base',base_sha256=BASE_SHA,data_qubits=DATA,base_loss=L0,base_acceptance=A0,acceptance_floor=.5005,semantics='Each price is the complete circuit after that one listed edit to v35a. lines contains native-tick additions/removals and detector changes. Reassign new record bits when composing. Joint effects require complete-circuit repricing.',entries=entries)
 (H/'menu_v35a.json').write_text(json.dumps(out,indent=2)+'\n')
 finals=[]
 for p in sorted(V.glob('*.gates.json')):
  g=json.loads(p.read_text());r=json.loads((V/(g['stem']+'.score.json')).read_text())
  if g['passed']and g.get('speed',{}).get('classification')=='FAST'and r.get('loss',1)<L0 and r['acceptance']>=.5005:finals.append((r,g))
 finals.sort(key=lambda x:x[0]['loss'])
 out=['# WAITPROT — v35a acceptance-efficient protection','']
 if finals:
  rr,gg=finals[0];stem=rr['stem'];md=json.loads((V/(stem+'.json')).read_text())
  out += [f'Best verified all-orders candidate: **{stem}**, **{rr["loss"]:.12e}** ({100*(1-rr["loss"]/L0):.4f}% below v35a), acceptance **{rr["acceptance"]:.9f}**, {md["cx"]} CX, R44, depth47. Official 1e6 PASS and XTIM FAST.', '',
          'Artifacts: [v35_best.qasm](v35_best.qasm), [v35_best.json](v35_best.json), [v35_best.metrics.json](v35_best.metrics.json).','']
  for suffix in ('.qasm','.json'):(H/('v35_best'+suffix)).write_bytes((V/(stem+suffix)).read_bytes())
  metrics=dict(source_stem='v35/'+stem,score=rr,gate=gg)
  for suffix,key in [('.mc.json','mc'),('.audit.json','audit')]:
   p=V/(stem+suffix)
   if p.exists():metrics[key]=json.loads(p.read_text())
  (H/'v35_best.metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
 completed=[]
 for rr,gg in finals:
  p=V/(rr['stem']+'.mc.json')
  if p.exists():completed.append((rr,gg,json.loads(p.read_text())))
 if completed:
  rr,gg,mc=min(completed,key=lambda x:x[2]['seeds'][0]['score']);stem=rr['stem'];s0=mc['seeds'][0]
  out += [f'Best measured seed-0 key among completed finalists: **{s0["score"]:.6e}**, acceptance **{s0["acceptance"]:.5f}**, `{stem}`. Its all-orders loss is {rr["loss"]:.12e}; MC3 mean {mc["mean"]:.9e}. [QASM](v35_seed0_best.qasm) · [JSON](v35_seed0_best.json).','']
  for suffix in ('.qasm','.json'):(H/('v35_seed0_best'+suffix)).write_bytes((V/(stem+suffix)).read_bytes())
  (H/'v35_seed0_best.metrics.json').write_text(json.dumps(dict(source_stem='v35/'+stem,score=rr,gate=gg,mc=mc),indent=2)+'\n')
 out+=['| Finalist | All-orders loss | Acceptance | Judge 1e6 | FAST s/1e6 | MC3: seed0 / mean |','|---|---:|---:|---|---:|---|']
 for r,g in finals:
  p=V/(g['stem']+'.mc.json');mc=json.loads(p.read_text())if p.exists()else{}
  out.append(f'| [v35/{r["stem"]}](v35/{r["stem"]}.qasm) | {r["loss"]:.12e} | {r["acceptance"]:.9f} | PASS {g["score"]:.7e}, acc {g["acceptance"]:.6f} | {g["speed"]["median_seconds_per_1e6"]:.3f} | '+(f'{mc["seeds"][0]["score"]:.6e} / {mc["mean"]:.9e}'if'mean'in mc else'pending')+' |')
 out+=['',f'Base v35a: **{L0:.12e}**, acceptance **{A0:.12f}**. Required candidate budget: ≥0.5005. The parsed source has native ticks0–46 (47 layers), despite the briefing’s depth48; all original schedules are preserved unless an edit explicitly retimes an operation.','',f'[menu_v35a.json](menu_v35a.json): {sum(r["ok"]for r in entries)} numerical standalone prices and {sum(not r["ok"]for r in entries)} noiseless rejections, including ST2 receipts imported to avoid duplicate work. [v35/windows.json](v35/windows.json) maps data paths, idle runs and released helpers.','',
 'Current scope: guard initialization/parity changes, shortened windows, guard duals, shared helpers, readout folded into an existing check, and newly released helper windows. ST2 owns the broad detector/physical-removal knapsack; this lane prices complementary gadgets and complete combinations.','',
 '| Standalone edit | All-orders loss | Acceptance | Loss gain | Acceptance cost |','|---|---:|---:|---:|---:|']
 for r in sorted((x for x in entries if x['ok']),key=lambda x:x['loss']):out.append(f'| {r["gadget"]} | {r["loss"]:.10e} | {r["acceptance"]:.9f} | {r["loss_gain"]:+.5e} | {r["acceptance_cost"]:+.7f} |')
 out+=['','Negative acceptance cost means recovered acceptance. These marginal prices guide proposals; no joint loss is inferred by addition.','',
 'Previous v30f campaign and its completed evidence: [REPORT_v30f.md](REPORT_v30f.md). No submissions, commits, pushes or credentials.']
 notes=V/'research_notes.md'
 if notes.exists():out+=['',notes.read_text()]
 (H/'REPORT.md').write_text('\n'.join(out)+'\n');print('PUBLISHED',len(entries),'finalists',len(finals))
if __name__=='__main__':main()
