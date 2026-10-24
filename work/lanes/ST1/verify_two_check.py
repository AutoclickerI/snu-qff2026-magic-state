from common import *
import stim
x=json.loads((H/'two_check_package.json').read_text());s=stim.TableauSimulator();s.set_num_qubits(37);std=[(0,2),(1,6),(3,5),(0,4),(1,2),(3,6),(0,6),(1,5),(3,4)]
for k,off in [('d',0),('a',7),('b',14)]:
 ops=x['encoder_b']['ops']if k=='b'else std;piv=x['encoder_b']['pivots']if k=='b'else[0,1,3]
 if k=='a':piv=[i for i in range(7)if i not in piv];ops=[(v,u)for u,v in ops]
 for i in piv:s.h(off+i)
 for u,v in ops:s.cx(off+u,off+v)
s.h(36)
for i in range(7):s.cx(36,i)
for j,row in enumerate(x['check_rows']):
 for i in row:s.cx(14+i,21+j)
for i in range(7):s.cx(i,7+i)
for i in range(7):s.cx(14+i,i)
a={i:s.measure(7+i)for i in range(7)};b={i:s.measure_observable(stim.PauliString('I'*(14+i)+'X'))for i in range(7)};c=[s.measure(21+j)for j in range(2)];assert not any(c)
for row in[[0,2,4,6],[1,2,5,6],[3,4,5,6]]:
 assert sum(a[i]for i in row)%2==0 and sum(b[i]for i in row)%2==0
 for pa in'XZ':
  obs=stim.PauliString(37)
  for i in row:obs[i]=pa
  assert s.peek_observable_expectation(obs)==1
for pa in'XZ':
 obs=stim.PauliString(37);obs[36]=pa
 for i in range(7):obs[i]=pa
 assert s.peek_observable_expectation(obs)==1
r=dict(passed=True,encoded_B_cx=x['encoder_cx'],verification_cx=8,checks=x['check_rows'],logical_bell_and_all_stabilizers=True,scope='Adjacency-free full encoded Clifford instrument. Harmful B encoder X-component singles checked separately. Full circuit fault objective still required.');(H/'two_check_instrument_validation.json').write_text(json.dumps(r,indent=2));append_result('two_check_ideal_instrument',r,r['scope']);print(json.dumps(r))
