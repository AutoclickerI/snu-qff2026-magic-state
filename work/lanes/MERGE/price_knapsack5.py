from pass5 import *
from wide5 import frontier
m=json.loads((R/'global_knapsack_model.json').read_text());cur=m['base'];E.configure(R/('basis_'+cur['sha256']+'.json'),12)
rs=batch(cur['stem'],R/'global_knapsack_menu.json',json.loads((R/'global_knapsack_tasks.json').read_text()),'global_knapsack',20,cur['loss'])
best=choose(rs,cur);dump(R/'global_knapsack_outcome.json',dict(base=cur,price=best,gain=cur['loss']-best['loss'],pareto=frontier(rs+[cur]),proposals=len(rs)))
print(json.dumps(dict(event='global_knapsack_complete',loss=best['loss'],acceptance=best['acceptance'],gain=cur['loss']-best['loss'],count=len(rs))),flush=True)
