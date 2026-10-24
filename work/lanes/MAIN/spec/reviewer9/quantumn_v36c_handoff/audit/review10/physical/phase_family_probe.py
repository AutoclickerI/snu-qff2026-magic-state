"""Phase-axis-only all-orders channel comparison on v36c's exact ideal exterior.

This is a relaxed diagnostic, NOT a physical grid candidate. Only one Pauli
component (the commuting phase axis) of each hypothetical T-gate noise is
retained, at probability p/3. Clifford correction, synthesis gates, other
Pauli components, preparations, measurements and idles are noiseless here.
"""
import sys,json,itertools,collections,math
from pathlib import Path
from fractions import Fraction
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'evaluator'))
import frontend as fa
BASE=ROOT.parents[2]/'quantumn_review10/work/lanes/MAIN/v36c'
fa.DATA=json.loads(BASE.with_suffix('.json').read_text())['data_qubits']
ops,dets=fa.parse_current(BASE.with_suffix('.qasm').read_text())
m=fa.make_model(ops,dets);eng=fa.Engine(m)
b=fa.Basis()
for x,z,*_ in m.rots:b.add(x)
assert len(b.vecs)==5
assert all(fa.comm(a,c)==0 for a,c in itertools.combinations(m.rots,2))
assert all((z&v).bit_count()%2==0 for x,z,*_ in m.rots for v in b.vecs)
axes=[{'coordinate':b.express(x),'coefficient':int(round(-theta*float(c.real)/(math.pi/8)))} for x,z,c,theta,ii in m.rots]
support={a['coordinate'] for a in axes};assert len(support)==15
phase=[sum(a['coefficient']*((a['coordinate']&y).bit_count()%2) for a in axes)%8 for y in range(32)]
target=next(x for x in range(1,32) if phase==[(x&y).bit_count()%2 for y in range(32)])
sig=list(m.gen_m)+[m.Q['X',0,0],fa.mul(m.Q['X',0,0],m.Q['Y',0,0]),(0,0,1),(0,0,1)]
response=[]
for c in range(32):
 x=0
 for j,v in enumerate(b.vecs):
  if c>>j&1:x^=v
 F=(x,0)
 d=sum(fa.comm(F,q)<<j for j,q in enumerate(m.proj_m))
 e=sum(fa.comm(F,q)<<j for j,q in enumerate(sig))
 a,nt=eng.ntable(0,d)
 response.append({'axis':c,'detector_signature':str(d),'output_signature':e,'A':a,'N':0. if nt is None else float(nt[e])})
forms=[];p=.001;q=p/3
def gf2_rank(xs):
 piv={}
 for x in xs:
  while x:
   k=x.bit_length()-1
   if k not in piv:piv[k]=x;break
   x^=piv[k]
 return len(piv)
for aa in range(32):
 for cc in range(2):
  supp=sorted(support^{x for x in range(1,32) if ((aa&x).bit_count()%2)^cc})
  dist=np.zeros(32);dist[0]=1.
  for ax in supp:dist=(1-q)*dist+q*dist[np.arange(32)^ax]
  A=sum(pr*r['A'] for pr,r in zip(dist,response));N=sum(pr*r['N'] for pr,r in zip(dist,response))
  row={'id':f'f{aa:02d}_{cc}','T':len(supp),'support':supp,'phase_coordinate_rank':gf2_rank(supp),'A':A,'N':N,'L':N/A,'bad_singles':[x for x in supp if response[x]['N']>1e-10],'bad_pairs':[(x,y) for x,y in itertools.combinations(supp,2) if response[x^y]['N']>1e-10]}
  if len(supp)==14:
   # Construct a valid ideal phase: +T on the listed support, plus the
   # exact residual diagonal Clifford on the five abstract variables.
   vals=[(phase[y]-sum((x&y).bit_count()%2 for x in supp))%8 for y in range(32)]
   coeff=vals[:]
   for bit in range(5):
    for mask in range(32):
     if mask>>bit&1:coeff[mask]=(coeff[mask]-coeff[mask^(1<<bit)])%8
   assert coeff[0]==0
   assert all(not a or (i.bit_count()==1 and a%2==0) or (i.bit_count()==2 and a%4==0) for i,a in enumerate(coeff))
   row['residual_clifford']=[{'monomial_mask':i,'phase_mod8':a} for i,a in enumerate(coeff) if a]
  forms.append(row)
result={'baseline_source':str(BASE),'p':p,'phase_axis_probability':q,'scope':__doc__,'rank':5,'target_axis':target,'base_axes':axes,'response':response,'forms':forms,'count_by_T':dict(collections.Counter(r['T'] for r in forms))}
q_exact=Fraction(1,3000);r_exact=1-2*q_exact
A_exact=(1+7*r_exact**8)/8;N_exact=(1+7*r_exact**8-8*r_exact**7)/16
assert max(abs(f['L']-float(N_exact/A_exact)) for f in forms if f['T']==14)<1e-15
result['fourteen_T_formula']={'q':'p/3','r':'1-2*q','A':'(1+7*r**8)/8','N':'(1+7*r**8-8*r**7)/16','A_at_p001':str(A_exact),'N_at_p001':str(N_exact),'L_at_p001':str(N_exact/A_exact),'L_float':float(N_exact/A_exact)}
(ROOT/'phase_family_certificate.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'target':target,'response_nonzero':[r for r in response if r['A']>1e-10],'counts':result['count_by_T'],'group_results':{t:{'count':len(rs),'L_min':min(r['L'] for r in rs),'L_max':max(r['L'] for r in rs),'A_min':min(r['A'] for r in rs),'A_max':max(r['A'] for r in rs),'bad_single_counts':sorted(set(len(r['bad_singles']) for r in rs)),'bad_pair_counts':sorted(set(len(r['bad_pairs']) for r in rs))} for t in sorted({r['T'] for r in forms}) for rs in [[r for r in forms if r['T']==t]]}},indent=2))
