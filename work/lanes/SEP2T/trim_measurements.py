"""Advance terminal/reset-followed measurements while keeping preparations ALAP."""
from reschedule import *
import hashlib

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);a=p.parse_args();src=HERE/a.stem;meta=json.loads(src.with_suffix('.json').read_text());txt=src.with_suffix('.qasm').read_text();head,raw,dets=S.qasm_ops(txt);units=S.fold_units(raw);old=native_times(txt,units);ts=old[:];per={};pred={};succ={}
 for i,u in enumerate(units):
  for q in u.qs:per.setdefault(q,[]).append(i)
 for q,seq in per.items():
  for i,j in zip(seq,seq[1:]):pred[j]=i;succ[i]=j
 changed=[]
 for i,u in enumerate(units):
  if u.name not in ('MX','MEASURE'):continue
  if i in succ and units[succ[i]].name not in ('RESET','RX'):continue
  t=ts[pred[i]]+1 if i in pred else 0
  if t<ts[i]:changed.append(dict(unit=i,lines=u.lines,old=ts[i],new=t));ts[i]=t
 text=S.emit(head,units,ts,dets);h,rr,tail=S.qasm_ops(text);nu=S.fold_units(rr);nt=native_times(text,nu);order=sorted(range(len(units)),key=lambda i:(ts[i],i));comp={t:i for i,t in enumerate(sorted(set(ts)))}
 assert [units[i].lines for i in order]==[u.lines for u in nu]
 assert [comp[ts[i]] for i in order]==nt
 provenance=json.loads(src.with_suffix('.units.json').read_text());assert [o['lines'] for o in provenance]==[u.lines for u in units]
 updated=[dict(provenance[i],t=t) for i,t in zip(order,nt)]
 out=HERE/a.out;meta.update(source=a.stem,measurement_timing='ASAP before reset or terminal',advanced_measurements=changed,R_native=min(u['t'] for u in updated if u['region']=='round'),R_A_native=min((u['t'] for u in updated if u['region']=='round_a'),default=min(u['t'] for u in updated if u['region']=='round')),native_depth=max(nt)+1,units_file=out.with_suffix('.units.json').name)
 out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(meta,indent=1));out.with_suffix('.units.json').write_text(json.dumps(updated,indent=1));print(dict(out=a.out,advanced=len(changed),idle_steps_removed=sum(x['old']-x['new'] for x in changed),R=meta['R_native']),flush=True)
