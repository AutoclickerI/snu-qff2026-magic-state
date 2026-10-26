from pass5 import *
from wide5 import fund,choose,frontier
j=json.loads((R/'xor_current_summary.json').read_text());current=j['base'];p=R/'xor_current_menu.json';singles=[json.loads(l)for l in (R/'wide_r2_singles.jsonl').read_text().splitlines()]
E.configure(R/('basis_'+sha(C/'base')+'.json'),12)
rows=j['rows'];funded=fund(current['stem'],p,rows,singles,current,'xor_current',1);rows+=funded
best=choose(rows,current);dump(R/'xor_current_funded_outcome.json',dict(base=current,price=best,gain=current['loss']-best['loss'],count=len(rows),pareto=frontier(rows+[current]),menu=str(p)))
print(json.dumps(dict(event='xor_funding_complete',loss=best['loss'],acceptance=best['acceptance'],gain=current['loss']-best['loss'],count=len(rows))),flush=True)
