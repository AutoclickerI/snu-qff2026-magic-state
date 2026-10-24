from core import *
import tprep,collections
def main():
 audit=[]
 for f in OUT.glob('*results.jsonl'):
  rows=[json.loads(l)for l in f.read_text().splitlines()]
  for r in rows:
   stem=OUT/r['stem']
   if 'error'in r:
    meta=json.loads(stem.with_suffix('.json').read_text())
    if stem.with_suffix('.check.json').exists():ck=json.loads(stem.with_suffix('.check.json').read_text())
    else:
     rep=tprep.check(stem.with_suffix('.qasm').read_text(),meta['data_qubits'],shots=10**6,seed=0)
     ck=dict(passed=rep.passed,acceptance=rep.acceptance,repr=str(rep));stem.with_suffix('.check.json').write_text(json.dumps(ck,indent=2)+'\n')
    r.update(check=ck['passed'],check_acceptance=ck['acceptance'],CX=meta['cx'],R=meta['R']);audit.append(dict(stem=r['stem'],**ck))
  f.write_text(''.join(json.dumps(r)+'\n'for r in rows))
 # Existing exact receipts must match the delivered circuit bytes.
 for nm in ['base','partial_1_x_129','partial_x_enc21_joint_d7_rigid','enc25_rigid','enc21_joint_d7_rigid','partial_x_enc21_joint_d7_rigid_budget_1_none','blue_xz_e21_r1_u0_budget_0_both','blue_xz_e21_r0_u0_budget_1_low_c2','blue_xz_e21_r1_u0_budget_0_low_c2']:
  stem=OUT/nm;row=json.loads(stem.with_suffix('.exact.json').read_text());text=stem.with_suffix('.qasm').read_text()
  assert hashlib.sha256(text.encode()).hexdigest()==row['sha256']
  c=read(stem);assert c['meta']['native_depth']==max(c['t'])+1
  for u in c['u']:
   if u.name=='CX':
    a,b=u.qs;assert abs(a//6-b//6)+abs(a%6-b%6)==1
  audit.append(dict(stem=nm,sha256=row['sha256'],exact_matches_bytes=True,native_depth=c['meta']['native_depth'],R=c['meta']['R'],CX=c['meta']['cx'],adjacency=True))
 (OUT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 print('audit complete',len(audit),flush=True)
if __name__=='__main__':main()
