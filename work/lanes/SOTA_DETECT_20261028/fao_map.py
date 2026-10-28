import stim,itertools
c=stim.Circuit('''H 6 8 9
CX 6 0 8 1 9 2 6 5 6 4 9 5 6 3 9 7 6 0 9 3 8 7
M 0
CX 9 2 8 5
M 2
CX 8 4 8 1
M 1''')
s=stim.TableauSimulator()
for op in c:
 if op.name=='M':
  for q in op.targets_copy():s.postselect_z(q.value,desired_value=False)
 else:s.do(op)
SUP=[{0,2,4,6},{1,2,5,6},{3,4,5,6}]
for perm in itertools.permutations(range(3,10)):
 if all(s.peek_observable_expectation(stim.PauliString(''.join(('X' if i in [perm[j] for j in S] else '_')for i in range(10))))==1 for S in SUP) and all(s.peek_observable_expectation(stim.PauliString(''.join(('Z' if i in [perm[j] for j in S] else '_')for i in range(10))))==1 for S in SUP+[{0,1,2,3,4,5,6}]):
  print(perm);break
