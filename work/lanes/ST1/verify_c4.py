from common import *
import stim,itertools
checks=[[0,1,2],[0,3,4],[0,5,6],[1,3,5]];std=[(0,2),(1,6),(3,5),(0,4),(1,2),(3,6),(0,6),(1,5),(3,4)]
rows=[sum(1<<i for i in r)for r in checks];span={0}
for r in rows:span|={v^r for v in list(span)}
expected={0}
for inds in [[0,2,4,6],[1,2,5,6],[3,4,5,6],list(range(7))]:
 r=sum(1<<i for i in inds);expected|={v^r for v in list(expected)}
assert span==expected and len(span)==16
s=stim.TableauSimulator();s.set_num_qubits(37)
for k,off in [('d',0),('a',7),('b',14)]:
 piv=[i for i in range(7)if i not in[0,1,3]]if k=='a'else[0,1,3]
 for i in piv:s.h(off+i)
 for u,v in std:s.cx(off+v,off+u)if k=='a'else s.cx(off+u,off+v)
s.h(36)
for i in range(7):s.cx(36,i)
for i in range(7):s.cx(i,7+i)
ops=[(j,i)for j,r in enumerate(checks)for i in r];last={i:max(k for k,(j,l)in enumerate(ops)if l==i)for i in range(7)};bread={};cread={}
for k,(j,i)in enumerate(ops):
 s.cx(14+i,21+j)
 if k==max(z for z,(jj,ii)in enumerate(ops)if jj==j):cread[j]=s.measure(21+j)
 if last[i]==k:s.cx(14+i,i);bread[i]=s.measure_observable(stim.PauliString('I'*(14+i)+'X'))
aread={i:s.measure(7+i)for i in range(7)}
assert not any(cread.values())
for r in [[0,2,4,6],[1,2,5,6],[3,4,5,6]]:
 assert sum(aread[i]for i in r)%2==0 and sum(bread[i]for i in r)%2==0
 for pa in 'XZ':
  obs=stim.PauliString(37)
  for i in r:obs[i]=pa
  assert s.peek_observable_expectation(obs)==1
for pa in'XZ':
 obs=stim.PauliString(37);obs[36]=pa
 for i in range(7):obs[i]=pa
 assert s.peek_observable_expectation(obs)==1
out=dict(passed=True,checks=checks,z_group_rank=4,cx_verification=12,c_ancillas=4,logical_bell_and_six_output_stabilizers=True,scope='Adjacency-free Clifford instrument check; B_i couples immediately after its final checker CX; no physical or fault-performance claim.')
(H/'c4_instrument_validation.json').write_text(json.dumps(out,indent=2));append_result('c4_instrument',out,out['scope']);print(json.dumps(out))
