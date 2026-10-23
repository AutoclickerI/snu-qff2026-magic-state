from collections import defaultdict
import re
f='work/submissions/v11_A1i_alap45.qasm'; E=set()
for line in open(f):
 m=re.match(r'cx q\[(\d+)\],q\[(\d+)\];',line)
 if m:E.add(tuple(sorted(map(int,m.groups()))))
a=defaultdict(set)
for x,y in E:a[x].add(y);a[y].add(x)
col={};bad=None
for v in a:
 if v in col:continue
 col[v]=0;st=[v]
 while st and bad is None:
  x=st.pop()
  for z in a[x]:
   if z in col:
    if col[z]==col[x]:bad=(x,z);break
   else:col[z]=1-col[x];st.append(z)
print(len(E),len(a),bad)
