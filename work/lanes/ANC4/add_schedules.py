import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
import stim
from generate import build,PRE_DATA,PAR
HERE=Path(__file__).resolve().parent
for depth in [6,7,8]:
 j=json.loads((HERE/f'checker_d{depth}.json').read_text());lay=j['layers'];c=stim.Circuit()
 for l in lay:
  for e in l:c.append('CX',e)
 tab=stim.Tableau.from_circuit(c).inverse()
 assert [[i for i in range(7) if tab.z_output(7+k)[i]==3] for k in range(4)]==PAR
 for R in [33,39]:
  text=build('anc4',R,layers=lay);p=HERE/'gf'/f'opt{depth}_{R}'
  p.with_suffix('.qasm').write_text(text);p.with_suffix('.json').write_text(json.dumps(dict(data_qubits=PRE_DATA,grid_free=True,variant=f'opt{depth}',R=R,cx=text.count('\ncx '))))
print('All three optimized checkers have the correct Stim pullbacks.')
