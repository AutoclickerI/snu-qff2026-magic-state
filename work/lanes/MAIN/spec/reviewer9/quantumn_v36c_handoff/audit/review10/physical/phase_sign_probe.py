"""Enumerate +/- T signs for each 14-axis support and price residual virtual Clifford.
The Clifford count is on five abstract variables; NOT a grid circuit cost.
"""
from pathlib import Path
import json
import numpy as np
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'phase_family_certificate.json').read_text())
t=r['target_axis'];target=np.array([(t&y).bit_count()%2 for y in range(32)],dtype=np.int16)
rows=[]
for f in r['forms']:
 if f['T']!=14:continue
 supp=f['support'];sgn=1-2*((np.arange(1<<14)[:,None]>>np.arange(14)[None,:])&1)
 P=np.array([[(x&y).bit_count()%2 for y in range(32)] for x in supp],dtype=np.int16)
 vals=(target[None,:]-sgn@P)%8;coeff=vals.copy()
 for bit in range(5):
  ids=np.array([m for m in range(32) if m>>bit&1])
  coeff[:,ids]=(coeff[:,ids]-coeff[:,ids^(1<<bit)])%8
 bad=[i for i in range(32) if i==0 or i.bit_count()>2]
 assert np.max(coeff[:,bad])==0
 lin=[1<<i for i in range(5)];quad=[i for i in range(32) if i.bit_count()==2]
 assert np.max(coeff[:,lin]%2)==0 and np.max(coeff[:,quad]%4)==0
 counts=np.count_nonzero(coeff,axis=1);k=int(np.argmin(counts))
 rows.append({'id':f['id'],'minimum_virtual_clifford_terms':int(counts[k]),'number_of_minimizers':int(sum(counts==counts[k])),'support':supp,'T_coefficients':sgn[k].tolist(),'residual_clifford':[{'monomial_mask':i,'phase_mod8':int(a)}for i,a in enumerate(coeff[k]) if a]})
(ROOT/'phase_sign_certificate.json').write_text(json.dumps({'scope':__doc__,'forms':rows},indent=2))
print(json.dumps(rows,indent=2))
