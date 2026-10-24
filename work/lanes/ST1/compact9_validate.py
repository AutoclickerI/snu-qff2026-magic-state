from common import *
import stim
cells=[1,8,2,6,0,12,7];mid=13;end=14
rows=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
receipts=[]
for plus in[False,True]:
 for a in[0,1]:
  for b in[0,1]:
   s=stim.TableauSimulator();s.reset(*cells)
   for i,q in enumerate(cells):
    if (i in[0,1,3])!=plus:s.h(q)
   def cx(i,j):
    u,v=cells[i],cells[j]
    s.cx(v,u)if plus else s.cx(u,v)
   for i,j in[(0,2),(1,6),(3,5),(0,4),(1,2),(3,6)]:cx(i,j)
   old=cells[5];s.reset(mid)
   if plus:s.h(mid);s.cx(mid,old);s.postselect_z(old,desired_value=bool(a))
   else:s.cx(old,mid);s.postselect_x(old,desired_value=bool(a))
   cells[5]=mid;s.reset(end)
   if plus:s.h(end);s.cx(end,mid);s.postselect_z(mid,desired_value=bool(b))
   else:s.cx(mid,end);s.postselect_x(mid,desired_value=bool(b))
   cells[5]=end
   # Apply the exact resulting Pauli frame before the remaining encoder CXs.
   if a^b:
    s.x(end)if plus else s.z(end)
   for i,j in[(0,6),(3,4),(1,5)]:cx(i,j)
   expectations=[]
   for basis in'XZ':
    for row in rows+([list(range(7))]if (basis=='X')==plus else[]):
     p=stim.PauliString(36)
     for i in row:p[cells[i]]=basis
     expectations.append(s.peek_observable_expectation(p))
   assert all(v==1 for v in expectations),(plus,a,b,expectations)
   receipts.append(dict(plus=plus,outcomes=[a,b],expectations=expectations));cells=[1,8,2,6,0,12,7]
(H/'compact9_validation.json').write_text(json.dumps(receipts,indent=2));print('PASS',len(receipts),'complete CSS/ logical targets, every teleport outcome')
