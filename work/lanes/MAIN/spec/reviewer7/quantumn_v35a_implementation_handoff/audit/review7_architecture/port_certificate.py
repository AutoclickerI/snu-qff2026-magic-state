"""Exact detector-parity and Pauli certificate for the fresh A decoder ports."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'audit/reaudit_evaluation/portable'))
import frontend as f
cases=[]
for name in['v32p']:
 old=ROOT/'quantumn_review7/work/lanes/MAIN'/name;new=HERE/(name+'_a_decode')
 ops,od=f.parse_current(old.with_suffix('.qasm').read_text());newops,nd=f.parse_current(new.with_suffix('.qasm').read_text())
 meta=json.loads(new.with_suffix('.json').read_text());R=meta['R']
 expected=[set(row)for row in od]
 for cb,tb in[(17,20),(16,17)]:
  for row in expected:
   if tb in row:row.symmetric_difference_update({cb})
 assert all(16 not in row for row in expected)
 expected.append({16});assert expected==nd
 gates=[(9,15),(8,9)];readout=[o.qs for o in ops if o.kind=='CX'and o.time>=R+1]
 assert all(c!=v and t!=u for c,t in gates for u,v in readout)
 flag={8}
 for c,t in reversed(gates):
  if c in flag:flag.symmetric_difference_update({t})
 assert flag=={8,9,15}
 supports=[{1,8,2,15},{14,8,16,15},{9,2,16,15}]
 assert all(len(flag&s)%2==0 for s in supports)
 cases.append(dict(source=name,source_sha256=hashlib.sha256(old.with_suffix('.qasm').read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(new.with_suffix('.qasm').read_bytes()).hexdigest(),all_detector_row_transformations_exact=True,existing_terminal_CX_commute_with_inserted_decoder=True,rewritten_A_detector_rows=[sorted(s)for s in nd[14:17]],additional_detector=[16],pulled_back_X_flag=sorted(flag),logical_code_indices=[2,3,6],arbitrary_input_flag_determinism='X_A flag commutes with every D->A CX and is +1 on ideal |+L>; no assumption about the data state is required.',all_old_readout_edges_preserved=all(any(o.kind=='CX'and o.qs==pair for o in newops)for pair in readout)))
out=dict(source_commit='f843cb2a2a7e23e53cb2ba54b891d42943bfedfe',scope=__doc__,cases=cases)
(HERE/'port_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
