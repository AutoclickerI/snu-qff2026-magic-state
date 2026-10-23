"""python prep.py layout_json_file out_json : synthesize A,B,C for a layout dict."""
import sys, json
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/DR")
from synth import synth_cells, dangerous_z, layers
HAM = [[0,2,4,6],[1,2,5,6],[3,4,5,6]]
def rows_for(cells, plus):
    r = [{cells[i] for i in s} for s in HAM]
    if plus: r.append({cells[i] for i in (0,1,2)})
    return r
def best(cells, avail, plus, secs, wk, seeds, dmin=3, dmax=9):
    rows = rows_for(cells, plus); out = None
    for d in range(dmin, dmax+1):
        res = []
        for sd in seeds:
            r = synth_cells(rows, avail, d, secs, wk, seed=sd)
            if r: res.append(r)
            if r and not plus: break
        if res:
            for ops, piv, st in res:
                L = layers([e for l in ops for e in l]) if False else ops
                cx = sum(len(l) for l in ops)
                dz = dangerous_z(L, piv, cells, avail) if plus else None
                cand = (cx, dz if dz is not None else 0, {"ops": ops, "pivots": piv, "danger": dz, "cx": cx, "layers": len(ops), "status": st})
                if out is None or cand[:2] < out[:2]: out = cand
            return out[2]
    return None
def run(lay, secs=20, wk=4, seeds=(0,1,2,3,4,5)):
    res = {}
    for k, role, plus in (("a","a",True),("b","b",False),("c","c",False)):
        av = lay[role] + lay["h"+k.upper()]
        res[k] = best(lay[role], av, plus, secs, wk, seeds if plus else (0,))
    return res
if __name__ == "__main__":
    lay = json.load(open(sys.argv[1])); res = run(lay)
    json.dump(res, open(sys.argv[2], "w"))
