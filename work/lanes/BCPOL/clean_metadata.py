"""Remove inherited source-unit indices/counters after a full circuit rebuild."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
H=Path(__file__).resolve().parent
from synth import verify
import json,hashlib
obsolete={'prefix_unit_indices','component_tags','schedule_objective','round_range','change','cx','edits','steps_moved','mode','reuse'};rows=[]
for p in list((H/'finalists').glob('*.json'))+list((H/'inputs').glob('*.json')):
 d=json.loads(p.read_text())
 if 'prep' not in d or 'data_qubits' not in d:continue
 removed=sorted(obsolete&d.keys())
 for k in removed:del d[k]
 if d.get('options',{}).get('endpoint_parity'):d['prep']['extra_check']=True
 v=verify(d['prep']);assert v['stim_target_pass'] and v['policy_pass'];d['verification']=v
 p.write_text(json.dumps(d,indent=2)+'\n');rows.append(dict(stem=str(p),removed=removed))
(H/'metadata_cleanup.json').write_text(json.dumps(rows,indent=2));print('metadata cleaned',len(rows))
