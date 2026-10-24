"""Extra diagnostic outside clean-single policy; preserve the exact rank-three endpoint."""
import argparse,json,time
from synth_resource import configure,F,endpoint,H
rows=json.loads((H/'labelled_regions.json').read_text());row=rows[2];B=row['final']['b'];C=row['final']['c'];configure(B,C)
start=time.monotonic();m=F.Model(10,42,51,clean=False);m.warm(json.loads((H/'r2_d11_k56.prep.json').read_text()))
for t in range(11):
 for q in B+C:m.cut((t,(q,)))
status='UNKNOWN';n=0
while time.monotonic()-start<90:
 m.s.conf_budget(5000);ok=m.s.solve_limited()
 if ok is False:status='UNSAT';break
 if ok is None:continue
 n+=1;d=m.candidate();v=F.verify(d,clean=False);assert v['target_ok']
 if not v['bad']:
  e=endpoint(d,B,C);out=dict(d,B=B,C=C,row_index=2,clean=False,verification=v,endpoint=e,note='Outside clean policy: allows accepted B X errors in weight-one correction classes; full physical first-order and loss still required.');(H/'r2_correctable_d10_k42.prep.json').write_text(json.dumps(out,indent=2));status='SAT';break
 for src in v['bad']:m.cut(src)
 m.warm(d)
(H/'r2_correctable_d10_k42.receipt.json').write_text(json.dumps(dict(status=status,seconds=time.monotonic()-start,models=n,clean=False,cap=42,depth=10,scope='fixed row2 labels/cells, no helper, proper rank-three endpoint; correctable-single rather than clean-single fault policy'),indent=2));print(status,n,time.monotonic()-start,flush=True)
