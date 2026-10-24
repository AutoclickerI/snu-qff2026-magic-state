from common import *
import argparse,collections
p=argparse.ArgumentParser();p.add_argument('stem');a=p.parse_args();stem=Path(a.stem);c=json.loads(stem.with_suffix('.plan.json').read_text());txt=stem.with_suffix('.qasm').read_text();h,raw,tail=S.qasm_ops(txt);units=S.fold_units(raw)
qmap=S.native_qasm_index(txt);rawunit={j:i for i,u in enumerate(units)for j in u.raw_indices};ev=exact2.Eval(txt,c['meta']['data_qubits']);fp=ev.fp.copy();tags=[]
for ch in ev.m.chans:
 lab=ev.m.labels[ev.m.prog[ch['ins']].line_no-1];k=int(re.match(r'instruction (\d+)',lab)[1]);tags.append(c['ops'][rawunit[qmap[k]]]['tag'])
R=c['meta']['R'];rows=[]
def idle(ch):return ch['gap']is not None and ch['gap'][1]+ch['gap'][2]<=R
def before(ch):
 if ch['gap']is not None:return idle(ch)
 steps=ev.m.steps[ch['ins']];return bool(steps)and steps[0][1]<R
specs=[('all',lambda ch,k:False),('no_pre_round_idle',lambda ch,k:idle(ch)),('no_prefix_operation_noise',lambda ch,k:ch['gap']is None and k=='prefix'),('no_encoder_operation_noise',lambda ch,k:ch['gap']is None and(k.startswith('encoder_')or k=='prep_init')),('no_move_operation_noise',lambda ch,k:ch['gap']is None and k in('move_init','move_cx','data_cx','data_watch','tele_m')),('no_pre_idle_or_moves',lambda ch,k:idle(ch)or(ch['gap']is None and k in('move_init','move_cx','data_cx','data_watch','tele_m'))),('round_only',lambda ch,k:before(ch))]
for label,pred in specs:
 selected={i for i,(ch,k)in enumerate(zip(ev.m.chans,tags))if pred(ch,k)};ev.fp=fp.copy()
 for j,ch in enumerate(ev.fch):
  if ch in selected:ev.fp[j]=0
 r=mom.evaluate(ev);row=dict(label=label,channels_removed=len(selected),**r);rows.append(row);print(json.dumps(row),flush=True);append_result(stem.name+':'+label,r,'Counterfactual channel removal; overlapping comparisons, not additive physical gains. Complete-circuit exact numerator/denominator coefficients recomputed.')
(H/(stem.name+'.ablation.json')).write_text(json.dumps(rows,indent=2))
