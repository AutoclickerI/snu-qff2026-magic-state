from a30_common import *
import collections,hashlib
text,md,h,us,ts,tail,init,owned,clean=source();release={q:max(ts[i] for i in range(init[q]) if q in us[i].qs) for q in A}
def sig(u,t):return (u.name,edge(u) if u.name=='CX' else u.qs,bit(u) if u.name in ('MEASURE','MX') else None,t)
base_out=collections.Counter(sig(u,t) for i,(u,t) in enumerate(zip(us,ts)) if i not in owned)
for name in ['a30_fb_s810_00837','a30_fbn_00549','a30_fastpick_feedback_neighbors_05085','a30_fastpick_feedback_neighbors_05061']:
 p=D/'finalists'/name
 if not p.with_suffix('.qasm').exists():continue
 tx=p.with_suffix('.qasm').read_text();_,raw,tl=S.qasm_ops(tx);uu=S.fold_units(raw);tt=native_times(tx,uu)
 own={i for i,(u,t) in enumerate(zip(uu,tt)) if t<48 and set(u.qs)<=set(A) and all(t>release[q] for q in u.qs)}
 out=collections.Counter(sig(u,t) for i,(u,t) in enumerate(zip(uu,tt)) if i not in own);assert out==base_out,(name,out-base_out,base_out-out)
 olddet={bit(us[i]) for i in owned if us[i].name in ('MX','MEASURE')};newdet={bit(uu[i]) for i in own if uu[i].name in ('MX','MEASURE')}
 stable=lambda tail,bits:collections.Counter(l for l in tail if not(set(map(int,BITS.findall(l)))&bits))
 assert stable(tail,olddet)==stable(tl,newdet)
 r=dict(stem=name,base='v30f',outside_A_native_units_and_times_equal=True,other_detector_rows_equal=True,old_owned=len(owned),new_owned=len(own),old_A=[dict(t=ts[i],name=us[i].name,qs=us[i].qs,lines=us[i].lines) for i in sorted(owned)],new_A=[dict(t=tt[i],name=uu[i].name,qs=uu[i].qs,lines=uu[i].lines) for i in sorted(own)],qasm_sha256=hashlib.sha256(tx.encode()).hexdigest(),note='Native MX identity includes retained X output; q14 H restoration is explicit in QASM and folded into the existing prefix MX, with the same bit and time.')
 Path(str(p)+'.diff.json').write_text(json.dumps(r,indent=2));print(name,'PASS',len(owned),len(own))
