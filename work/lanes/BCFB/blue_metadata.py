"""Keep candidate metadata self-consistent; source index arrays belong to source."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;D=H/'blue'
KEYS={'data_qubits','source','method','R','prep','verification','options','CX','native_depth','non_BC_time_changes','retained_previous_X_states','unfolded_previous_MX','init_checks','init_check_retime','non_BC_check_retime','source_qasm_sha256','source_metadata'}
def clean(md):
 if not md.get('options',{}).get('context'):return md
 context=md['options']['context'];p=D/'inputs'/context
 out={k:v for k,v in md.items() if k in KEYS};out['source_metadata']=str(p.with_suffix('.json').relative_to(H));out['source_qasm_sha256']=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest();return out
def main():
 n=0
 for f in (D/'finalists').glob('*.json'):
  if f.name.endswith(('.screen.json','.verify.json','.exact.json','.mc.json')):continue
  md=json.loads(f.read_text());new=clean(md)
  assert new.get('data_qubits')==md.get('data_qubits')
  if new!=md:f.write_text(json.dumps(new,indent=2));n+=1
 print('metadata normalized',n,flush=True)
if __name__=='__main__':main()
