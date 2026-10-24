"""Move the last data20 T-dagger across its idle-only interval; price, do not assume."""
from a30_search import *
p=Path(sys.argv[1]).resolve();text=p.with_suffix('.qasm').read_text();md=json.loads(p.with_suffix('.json').read_text());h,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us)
i=next(i for i,u in enumerate(us) if u.name=='TDG' and u.qs==(20,));before=max(ts[j] for j in range(i) if 20 in us[j].qs);old=ts[i];ts[i]=before+1
# Move this disjoint operation first within its new layer, ahead of same-tick MX.
u=us.pop(i);t=ts.pop(i);us.insert(0,u);ts.insert(0,t)
new,meta=finish(h,us,ts,tail,md,dict(kind='T20_speed',parent=p.name,original_options=md['options'],T20_before=old,T20_after=t,R=48))
out=p.with_name(p.name+'_t40');out.with_suffix('.qasm').write_text(new);out.with_suffix('.json').write_text(json.dumps(meta,indent=2));ev=exact2.Eval(new,DATA);assert abs(float(ev.fp@ev.n_single))<1e-12;r=evaluate(ev);r['status']='SCREENED';out.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print(out.name,json.dumps(r),flush=True)
