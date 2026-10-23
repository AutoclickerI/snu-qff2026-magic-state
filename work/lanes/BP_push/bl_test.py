import json, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/me_layout")
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/BP_push")
import gmodel2 as G
import run_moves as R
from verify import load_assign
cost, a, o, seed, name = json.load(open("../me_layout/res_A1_9b_1792752451.json"))[0]
m = R.variant(name)
m.__class__ = G.GModel
A = load_assign(a)
print(m.proxy(A, o))
for bl in [{0:2},{1:2},{2:2},{0:2,1:2},{0:2,1:2,2:2},{2:3},{0:3},{1:3}]:
    m.bell_layer = bl
    try: print(bl, m.proxy(A, o))
    except Exception as e: print(bl, 'err', e)
