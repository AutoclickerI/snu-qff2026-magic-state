"""Use original Engine.batch_tables on active projectors with exact rejection.

The full model and every detector constraint are retained. Identity projector
bits are checked as Python integers before forming the engine's signed-int64
batch. This only changes lane-local batching, not EVAL or its scalar table().
"""
from build import *
import numpy as np

def prepare(ev):
 original=ev.e;small=copy.copy(original)
 active=[i for i,p in enumerate(original.projs)if p!=(0,0,1+0j)]
 inactive=[i for i in range(len(original.projs))if i not in active]
 assert len(active)<63
 small.projs=[original.projs[i]for i in active];small.v=original.v[active]
 reject_mask=sum(1<<i for i in inactive)
 expected=sum(int(original.v[i])<<i for i in inactive)
 old_batch=small.batch_tables
 def batch(S,D):
  A=np.zeros(len(S));E=np.zeros((len(S),len(original.keys)))
  live=[j for j,d in enumerate(D)if(int(d)&reject_mask)==expected]
  if live:
   ss=[int(S[j])for j in live]
   dd=[sum(((int(D[j])>>i)&1)<<k for k,i in enumerate(active))for j in live]
   aa,ee=old_batch(ss,dd);A[live]=aa;E[live]=ee
  return A,E
 original.batch_tables=batch
 return ev

def evaluate(ev):return mom.evaluate(prepare(ev))

if __name__=='__main__':
 for name in sys.argv[1:]:
  st=V/name;c=json.loads(st.with_suffix('.plan.json').read_text());ev=exact2.Eval(st.with_suffix('.qasm').read_text(),c['meta']['data_qubits'])
  old=mom.evaluate(ev)if name=='guard_joint_2'else None
  r=evaluate(ev);r['batching']='exact identity-projector rejection, original active-projector Engine.batch_tables'
  if old:
   assert max(abs(r[k]-old[k])for k in ['c1','second','third','total','exp_minus_A1'])<1e-16
   r['comparison_to_unmodified_lane_moments']=old
  st.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print(name,json.dumps(r),flush=True)
