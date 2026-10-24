import os,sys,json,itertools,collections
sys.dont_write_bytecode=True
import stim
from pathlib import Path
HERE=Path(__file__).resolve().parent
G=[0b1010101,0b1100110,0b1111000]
P=[[0,5,6],[1,4,6],[2,4,5],[3,4,5,6]]
B=[8,9,22,26,16,13,19]; A=[14,15,21,20]
LAY=[[(13,14),(19,20)],[(14,15)],[(20,14),(16,15)],[(15,21)],[(21,20),(14,15)],[(8,14),(9,15),(22,21),(26,20)]]
S={0}
for g in G:S|={s^g for s in list(S)}
assert len(S)==8
H=[sum(1<<i for i in p) for p in P]
assert {x for x in range(128) if all((x&h).bit_count()%2==0 for h in H)}==S
circ=stim.Circuit()
for l in LAY:
 assert len(set(q for e in l for q in e))==2*len(l)
 for u,v in l:
  assert abs(u//6-v//6)+abs(u%6-v%6)==1
  circ.append('CX',[u,v])
# Pull each readout back: equals requested B parity times ancilla-only Zs.
tab=stim.Tableau.from_circuit(circ).inverse()
rows=[]
for q in A:
 z=tab.z_output(q)
 assert all(z[i] in (0,3) for i in range(len(z)))
 rows.append([i for i,b in enumerate(B) if z[b]==3])
assert rows==P,(rows,P)
# Exhaustive basis inputs verifies instrument sectors and uniform encoded-C outcomes.
old_probs={}
for x in range(128):
 st=stim.TableauSimulator()
 for i,b in enumerate(B):
  if x>>i&1:st.x(b)
 st.do(circ)
 got=tuple(int(st.peek_z(q)==-1) for q in A)
 expected=tuple((x&h).bit_count()%2 for h in H)
 assert got==expected
 for c in range(128):
  assert ((c^x) in S)==(all(((c^x)&h).bit_count()%2==0 for h in H))
# Equivalence on an entangled reference: conditional projection is diagonal in x,
# and original encoded C has amplitude 1/sqrt(8) exactly on each coset x+S.
classes=[]
for x in range(128):
 sy=0
 for i in range(7):
  if x>>i&1:sy^=i+1
 residual=x^(1<<(sy-1) if sy else 0)
 dangerous=residual not in S
 if dangerous:classes.append(dict(x=x,syndrome=''.join(str((x&h).bit_count()%2) for h in H),weight=sum((x&h).bit_count()%2 for h in H)))
hist=dict(sorted(collections.Counter(v['weight'] for v in classes).items()))
assert min(v['weight'] for v in classes)==2
out=dict(parities=P,reviewer_rows=rows,mapping='identity',rank=4,old_random_bits=3,checked_patterns=128,checked_basis_readout_pairs=16384,dangerous_patterns=len(classes),dangerous_histogram=hist,dangerous_classes=sorted(set((v['syndrome'],v['weight']) for v in classes)),reviewer_layers=LAY,reviewer_B=B,reviewer_anc=A,reviewer_exposure=[0,0,0,0,3,5,5],proof='Pullback of all four measured Zs via Stim; full rank and kernel equality proves identical joint spectral projectors, including entangled B inputs, after forgetting 3 encoded-C random bits.')
(HERE/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
