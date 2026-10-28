import stim,itertools
c=stim.Circuit('''RX 0
R 1 2 3
RX 4
R 5
RX 6
R 7
CX 0 7 7 3 0 2
R 8
CX 4 8
R 9
CX 6 9 7 1 8 2 4 5 9 3 8 1 9 2 6 5 0 7
M 7
CX 4 8
M 8
CX 6 9
M 9''')
s=stim.TableauSimulator()
for op in c:
 if op.name=='M':
  for q in op.targets_copy():s.postselect_z(q.value,desired_value=False)
 else:s.do(op)
SUP=[{0,2,4,6},{1,2,5,6},{3,4,5,6}]
for perm in itertools.permutations(range(7)):
 if all(s.peek_observable_expectation(stim.PauliString(''.join(('X' if i in [perm[j] for j in S] else '_')for i in range(10))))==1 for S in SUP) and all(s.peek_observable_expectation(stim.PauliString(''.join(('Z' if i in [perm[j] for j in S] else '_')for i in range(10))))==1 for S in SUP+[{0,1,2,3,4,5,6}]):
  print(perm);break
