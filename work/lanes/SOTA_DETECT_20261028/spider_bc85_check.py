import stim,json
c=stim.Circuit(open('work/lanes/SOTA_DETECT_20261028/spider_bc85.log').read());s=stim.TableauSimulator()
for op in c:
 if op.name=='DETECTOR':continue
 if op.name in ('M','MX'):
  for q in op.targets_copy():
   getattr(s,'postselect_z' if op.name=='M' else 'postselect_x')(q.value,desired_value=False)
 else:s.do(op)
rows=[[((m>>i)&1) for i in range(7)]*2 for m in [85,102,120]]+[[0]*7+[(m>>i)&1 for i in range(7)] for m in [85,2,8,32]]
ans=[]
for row in rows:
 p=stim.PauliString(18)
 for j,v in enumerate(row):
  if v:p[j]='X'
 ans.append(s.peek_observable_expectation(p))
print('desired X-generator expectations',ans)
masks=[sum(v<<i for i,v in enumerate(row)) for row in rows]
null=[v for v in range(1<<14) if all((v&m).bit_count()%2==0 for m in masks)]
zexpect=[]
for v in null:
 p=stim.PauliString(18)
 for j in range(14):
  if v>>j&1:p[j]='Z'
 zexpect.append(s.peek_observable_expectation(p))
print('orthogonal Z products',len(null),'all +1',all(v==1 for v in zexpect))
