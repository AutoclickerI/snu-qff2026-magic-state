import json, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/DR"); sys.path.insert(0, ".")
import merge
from steane_full import LAYOUTS, MOVES
def make(stem, gad, A="../DR/prepA_L5_s7307.json", bc="../ST_BC/sat6_14_400_305.json"):
    preps = {"a": json.load(open(A)), "bc": json.load(open(bc))}
    text, data, R, pre = merge.build(preps, ["a", "bc"], LAYOUTS["L5"], MOVES["L5"], gad)
    open(stem + ".qasm", "w").write(text)
    json.dump({"data_qubits": data}, open(stem + ".json", "w"))
    return R
if __name__ == "__main__":
    # ceiling: adjacency ignored, M={2,4,5}, cat 33-34-35, checks at R+1, A measured R+2
    gad = dict(timing="late", M=[2, 4, 5], anc=[33, 34, 35], tree=[(33, 34), (33, 35)],
               checks=[(33, 8, 1), (34, 2, 1), (35, 16, 1)], mx=2)
    print(make("cb_ceil_late", gad))
    print(make("cb_base", None))
