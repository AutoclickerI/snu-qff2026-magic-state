"""Recheck the finite commuting-T phase-support family on current v32p+A.

This certifies ideal signed phase identities and phase-axis fault protection,
not grid implementations or arbitrary full-circuit fault protection of new
unsynthesized forms. Derived from pinned TREP/enumerate.py.
"""
from pathlib import Path
import collections, hashlib, itertools, json, math, sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'audit/reaudit_evaluation/portable'))
import frontend as f

stem=HERE/'v32p_a_decode'
f.DATA=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
ops,dets=f.parse_current(stem.with_suffix('.qasm').read_text())
m=f.make_model(ops,dets);e=f.Engine(m)
b=f.Basis();full=f.Basis()
n=max((x|z).bit_length()for x,z,*_ in m.rots+m.proj_m+list(m.Q.values()))
for x,z,*_ in m.rots:b.add(x);full.add(x|(z<<n))
assert len(b.vecs)==5
assert all(f.comm(a,c)==0 for a,c in itertools.combinations(m.rots,2))
assert all((z&v).bit_count()%2==0 for x,z,*_ in m.rots for v in b.vecs)
axes=[dict(coordinate=b.express(x),coefficient=int(round(-theta/(math.pi/8)*co.real)))
      for x,z,co,theta,_ in m.rots]
support={a['coordinate']for a in axes}
assert len(support)==15
phase=[sum(a['coefficient']*((a['coordinate']&y).bit_count()%2)for a in axes)%8 for y in range(32)]
target=next(x for x in range(1,32)if phase==[(x&y).bit_count()%2 for y in range(32)])
signature=f.Basis();rows=[]
for degree in(1,2,3):
 for subset in itertools.combinations(range(5),degree):
  mask=sum(1<<k for k in subset)
  row=sum(int(x&mask==mask)<<(x-1)for x in range(1,32))
  rows.append(row);signature.add(row)
assert len(signature.vecs)==25
sig=list(m.gen_m)+[m.Q['X',0,0],f.mul(m.Q['X',0,0],m.Q['Y',0,0]),(0,0,1),(0,0,1)]
faults={}
for c in range(32):
 x=0
 for j,v in enumerate(b.vecs):
  if c>>j&1:x^=v
 d=sum(f.comm((x,0),p)<<j for j,p in enumerate(m.proj_m))
 esig=sum(f.comm((x,0),p)<<j for j,p in enumerate(sig))
 a,nt=e.ntable(0,d)
 faults[c]=dict(acceptance=a,loss=0 if nt is None else float(nt[esig]))
forms=[]
for a in range(32):
 for c in range(2):
  supp=sorted(support^{x for x in range(1,32)if((a&x).bit_count()%2)^c})
  word=sum((((a&x).bit_count()%2)^c)<<(x-1)for x in range(1,32))
  assert all((word&row).bit_count()%2==0 for row in rows)
  row=dict(id=f'f{a:02d}_{c}',support=supp,T=len(supp),
           bad_singles=[x for x in supp if faults[x]['loss']>1e-10],
           bad_pairs=[(x,y)for x,y in itertools.combinations(supp,2)if faults[x^y]['loss']>1e-10])
  if len(supp)==15:
   signed=[]
   for sign in range(32):
    coefficients=[(-1)**((sign&x).bit_count()%2)for x in supp]
    if[sum(k*((x&y).bit_count()%2)for x,k in zip(supp,coefficients))%8 for y in range(32)]==phase:
     signed.append(dict(sign_character=sign,coefficients=coefficients))
   assert signed and not row['bad_singles']and not row['bad_pairs']
   row['signed_representations']=signed
  forms.append(row)
out=dict(scope=__doc__,source_commit='f843cb2a2a7e23e53cb2ba54b891d42943bfedfe',
         qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),
         rank_state=len(b.vecs),rank_pauli=len(full.vecs),commuting=True,
         phase_signature_rank=len(signature.vecs),kernel_dimension=6,target=target,
         axes=axes,phase=phase,counts=dict(collections.Counter(r['T']for r in forms)),
         allforms=forms,phase_axis_faults=faults)
(HERE/'phase_forms_current.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k not in ['allforms','phase_axis_faults','axes','phase']},indent=2))
