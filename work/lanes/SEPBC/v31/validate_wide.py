from build import *
import wide_moments,numpy as np,random
rows=[]
for name in ['guard_joint_2','guard5_timing_1']:
 st=V/name;c=json.loads(st.with_suffix('.plan.json').read_text());ev=exact2.Eval(st.with_suffix('.qasm').read_text(),c['meta']['data_qubits'])
 old=mom.evaluate(ev)if name=='guard_joint_2'else None
 active=[i for i,p in enumerate(ev.e.projs)if p!=(0,0,1+0j)];inactive=[i for i in range(len(ev.e.projs))if i not in active];rng=random.Random(0);req=[]
 for k in range(128):
  mask=rng.randrange(1<<len(active));d=sum(((mask>>j)&1)<<i for j,i in enumerate(active));s=rng.choice([0]+ev.fs)
  req.append((s,d))
  if inactive:req.append((s,d^(1<<rng.choice(inactive))))
 ref=[]
 for s,d in req:
  row=ev.e.table(s,d);ref.append((0.,np.zeros(len(ev.e.keys)))if row is None else row)
 wide_moments.prepare(ev);aa,ee=ev.e.batch_tables([s for s,d in req],[d for s,d in req]);err=max(max(abs(a-aa[j]),float(np.max(np.abs(e-ee[j]))))for j,(a,e)in enumerate(ref));assert err<1e-12,err
 now=mom.evaluate(ev)
 if old:assert max(abs(old[k]-now[k])for k in ['second','third','total'])<1e-16
 row=dict(stem=name,active_projector_indices=active,identity_projector_count=len(inactive),scalar_cases=len(req),max_scalar_difference=err,unmodified_moments_match=old is not None,qasm_sha256=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest());rows.append(row);print(row,flush=True)
(V/'wide_validation.json').write_text(json.dumps(rows,indent=2))
