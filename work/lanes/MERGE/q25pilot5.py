from pass5 import *
from judge5 import verify
es=json.loads((R/'wide_r2_menu.json').read_text());e=es['herald:RESET25@32:v1']
E.configure(R/('basis_'+sha(C/'base')+'.json'),12)
cases=[('fast_1c4',H/'cand/merge5_live_1c4b23e89b48',[e]),('fast_ee3',H/'cand/merge5_live_ee3c93a6dab9',[e])]
hist=json.loads((R/'wide_history.json').read_text());current=hist[-1]['price'];cases.append(('funded_current',Path(current['stem']),[e,es['pair:16_17@25']]))
rows=[]
for name,base,edits in cases:
 c,txt=apply(M.read(base),edits);st=E.write_stem(txt,c['meta']['data_qubits']);r=price(st,dict(pilot=name,base=str(base),edits=[x['id']for x in edits]),TAU);r['pilot']=name;r['edits']=[x['id']for x in edits];rows.append(r)
 if feasible(r)and r['loss']<TAU-3e-8:publish(r)
dump(R/'q25_pilot_outcome.json',rows)
print(json.dumps(dict(event='q25_pilot_complete',prices=[dict(name=r['pilot'],loss=r.get('loss'),A=r.get('acceptance'),sha256=r.get('sha256'))for r in rows])),flush=True)
