import sys,json,runpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import acceptance as a,knapsack_select as k
base=a.d.normalize(a.C.read(a.OUT/'base'))
x=k.apply(base,[k.patches(base,a.C.read(a.OUT/'prices/det_62')),k.patches(base,a.C.read(a.OUT/'additional/mz_5'))]);od=a.OUT/'early';od.mkdir(exist_ok=True);st=od/'drop_Z20_mz5';a.d.save(x,st);r=a.score((str(st),dict(family='budget_exchange',removed='q20 Z detector c269',added='measured-Z init q5')));print(json.dumps(r),flush=True)
if r.get('eligible')and r['loss']<a.BASE_LOSS-1e-13:
 sys.argv=[str(a.H/'gate_budget.py'),str(st)];runpy.run_path(str(a.H/'gate_budget.py'),run_name='__main__')
