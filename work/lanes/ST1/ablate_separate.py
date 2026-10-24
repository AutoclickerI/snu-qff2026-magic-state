from common import *
import argparse,collections
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--source',required=True);a=p.parse_args();stem=Path(a.stem);source=json.loads(Path(a.source).with_suffix('.plan.json').read_text());txt=stem.with_suffix('.qasm').read_text();md=json.loads(stem.with_suffix('.json').read_text());h,raw,tail=S.qasm_ops(txt);units=S.fold_units(raw)
queues=collections.defaultdict(list)
for op in sorted(source['ops'],key=lambda o:o['t']):queues[tuple(op['lines'])].append(op.get('tag','unknown'))
tags=[]
for u in units:tags.append(queues[tuple(u.lines)].pop(0))
qmap=S.native_qasm_index(txt);rawunit={j:i for i,u in enumerate(units)for j in u.raw_indices};ev=exact2.Eval(txt,md['data_qubits']);fp=ev.fp.copy();owners=[]
for ch in ev.m.chans:
 lab=ev.m.labels[ev.m.prog[ch['ins']].line_no-1];match=re.match(r'instruction (\d+)',lab);owners.append(tags[rawunit[qmap[int(match[1])]]]if match and int(match[1])in qmap else'unknown')
R=md['R'];rows=[]
def idle(ch):return ch['gap']is not None and ch['gap'][1]+ch['gap'][2]<=R
for label,pred in [('all',lambda ch,k:False),('no_pre_round_idle',lambda ch,k:idle(ch)),('no_teleport_operation_noise',lambda ch,k:ch['gap']is None and k.startswith('tele_')),('no_encoder_operation_noise',lambda ch,k:ch['gap']is None and k in('bc_init','bc_encoder')),('no_idle_or_teleport',lambda ch,k:idle(ch)or(ch['gap']is None and k.startswith('tele_')))]:
 selected={i for i,(ch,k)in enumerate(zip(ev.m.chans,owners))if pred(ch,k)};ev.fp=fp.copy()
 for j,ch in enumerate(ev.fch):
  if ch in selected:ev.fp[j]=0
 r=mom.evaluate(ev);rows.append(dict(label=label,channels_removed=len(selected),**r));print(rows[-1],flush=True);append_result(stem.name+':'+label,r,'Counterfactual noise removal, not attainable bound; ownership from exact native operation provenance.')
(H/(stem.name+'.ablation.json')).write_text(json.dumps(rows,indent=2))
