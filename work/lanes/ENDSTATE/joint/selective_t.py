"""Transport only label3's terminal Tdg, the hop-release bottleneck."""
import json,re
from pathlib import Path
from retime import run
H=Path(__file__).resolve().parent
p=json.loads((H/'region2_k56_A2_safe_dest.plan.json').read_text());ops=p['ops'];found=[o for o in ops if o['name']=='TDG'and o['qs']==[16]];assert len(found)==1
found[0].update(qs=[22],lines=['tdg q[22];'],t=p['meta']['R']-1)
resets=[o for o in ops if o['name']=='RESET'and o['region']=='data_hops'and o['qs']==[15]];assert len(resets)==1
r=resets[0];prev=max((o for o in ops if 15 in o['qs']and o['t']<r['t']),key=lambda o:o['t']);assert prev['name']=='MX'and prev['lines']==['h q[15];','measure q[15] -> c[9];']
assert '// DETECTOR c[9]'in p['tail'];ops.remove(r);p['meta']['selective_terminal_transport']=dict(label=3,source=16,destination=22);p['meta']['physical_zero_destination15']=dict(record=9,time=prev['t'])
temp=H/'region2_selectiveT_ordered';temp.with_suffix('.plan.json').write_text(json.dumps(p,indent=1));run(temp,'region2_selectiveT')
