from wide5 import *
hf=R/'wide_history.json';hist=json.loads(hf.read_text());assert len(hist)==1
rows=json.loads((R/'q25_pilot_outcome.json').read_text());r=next(r for r in rows if r['pilot']=='funded_current')
current=hist[-1]['price'];assert current['loss']-r['loss']>=1e-9
es=json.loads((R/'wide_r2_menu.json').read_text());event=select(current['stem'],es,[r],current,hist[-1]['atoms'],'wide_r2',2)
event['phase']='funded q25 herald improvement before completing expanded scan';hist.append(event);dump(hf,hist)
update_status('running',event['price'],hist,phase=event['phase']);run(10)
