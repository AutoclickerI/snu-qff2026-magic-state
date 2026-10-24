import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
import stim
from generate import REVIEW,LAYERS0,PIV
HERE=Path(__file__).resolve().parent
rows=[]
for sector in range(16):
 sims=[]
 for mode in ['old_C','anc4']:
  s=stim.TableauSimulator()
  for i in range(7):s.h(i);s.cx(i,7+i)
  if mode=='old_C':
   for i in PIV:s.h(14+i)
   for l in LAYERS0:
    for u,v in l:s.cx(14+u,14+v)
   for i in range(7):s.cx(i,14+i)
   for i in range(7):s.postselect_z(14+i,desired_value=bool(sector>>i&1))
  else:
   for l in REVIEW:
    for u,v in l:s.cx(u if u<7 else u+7,v if v<7 else v+7)
   for i in range(4):s.postselect_z(14+i,desired_value=bool(sector>>i&1))
  s.set_num_qubits(14);sims.append([str(p) for p in s.canonical_stabilizers()])
  assert len(sims[-1])==14
 assert sims[0]==sims[1],(sector,sims)
 rows.append(dict(sector=sector,identical=True))
(HERE/'entangled_verification.json').write_text(json.dumps(dict(reference='7 EPR pairs between B and a reference register',sectors=rows,method='Stim postselection in all 16 sectors; discard measured C/F and compare canonical stabilizers of B+reference'),indent=2)+'\n')
print('16/16 entangled sectors: identical canonical B+reference stabilizers.')
