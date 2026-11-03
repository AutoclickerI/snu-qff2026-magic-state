# Derived from work Copyright IBM 2025, Apache License 2.0.
# Modified for this task: native d=3 extraction and T seed; see REPORT.md.
"""Extract d=3 lattice from coordinate conditions in IBM utils.py.
Reference: https://github.com/IBM/gauging_clifford_measurement/blob/main/utils.py
This is an independent transcription of the geometry rules; see source Apache 2.0.
"""
import json
from pathlib import Path
d=3
Q=[];A=[]
for col in range(1,3*d):
 if 3*d-4>col>=-2.5:
  if col%6 in (1,3):Q.append((-1,col))
  if col%6 in (0,2,4):A.append((-1,col))
for row in range(int(3*(d-1)/2)+1):
 for col in range(1,3*d-1):
  if 3*d-row-1+(row%3==2)-(row%3==0)>col>=row-0.5-1-(row%3==0)+(row%3==1):
   if (col%6 in (0,4) and row%2==0) or (col%6 in (1,3) and row%2==1):Q.append((row,col))
   if (row%2==0 and col%6 in (1,2,3,5)) or (row%2==1 and col%6 in (0,2,4,5)):A.append((row,col))
flags=[c for c in A if (c[0]%2==0 and c[1]%6==2) or (c[0]%2==1 and c[1]%6==5)]
boundary=[c for c in Q if (c[0]<0 and c!=(-1,1)) or c[1]>3*d-2-c[0] or c[1]<c[0]-1]
data=[c for c in Q if c not in boundary]
links=[]
for r,c in A:
 if (r%2==0 and c%6==3) or (r%2==1 and c%6==0):
  right=(r+1,c);above=(r,c+1);left=(r-1,c);f=(r,c-1)
  links.append(((above,right) if above in Q else (right,left),(r,c),f))
 if (r%2==0 and c%6==1) or (r%2==1 and c%6==4):
  right=(r+1,c);below=(r,c-1);left=(r-1,c);f=(r,c+1)
  links.append(((right,below) if below in Q else (right,left),(r,c),f))
 if (r%2==1 and c%6==2) or (r%2==0 and c%6==5):links.append((((r,c-1),(r,c+1)),(r,c),(r+1,c)))
plaq=[]
for r,c in flags:
 vs=[(r+dx,c+dy) for dx,dy in [(1,-1),(0,-2),(-1,-1),(1,1),(0,2),(-1,1)]]
 plaq.append({'flag':(r,c),'support':[x for x in vs if x in data],'ancillas':[(r,c-1),(r,c+1)]})
doc={'source':'https://github.com/IBM/gauging_clifford_measurement/blob/main/utils.py','d':d,'all_data_vertices':Q,'code_data':data,'boundary_vertices':boundary,'ancillas':A,'flags':flags,'links':[{'vertices':v,'edge':a,'flag':f} for v,a,f in links],'plaquettes':plaq}
Path(__file__).with_suffix('.json').write_text(json.dumps(doc,indent=2)+'\n');print(json.dumps(doc,indent=2))
