"""Compose LNS2 speed-safe edits and verified prep seeds into ST2."""
import copy, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "work/lanes/LNS2"))
import core as C
import moves as M
import review_copy
C.OUT = OUT
C.xtim.cache_dir = str(OUT / ".xtim_cache_deep")
M.OUT = OUT

def norm(c):
    return C.normalize(c)

def save(c, name, desc):
    c = norm(c)
    md = dict(c["meta"])
    md.update({"data_qubits": C.D, "source": str(c.get("source", "")),
               "method": desc, "st2_compose": desc,
               "cx": sum(u.name == "CX" for u in c["u"]),
               "native_depth": max(c["t"]) + 1})
    (OUT / f"{name}.qasm").write_text(C.textof(c))
    (OUT / f"{name}.json").write_text(json.dumps(md, indent=2) + "\n")
    return c

def find_one(gen, pred):
    for c, d in gen:
        if pred(d): return c, d
    return None, None

def edit(c, kind):
    if kind == "timing10":
        return find_one(M.timing_moves(c, True), lambda d: d.get("op") == ["cx q[10],q[4];"] and d.get("new") == 10)[0]
    if kind == "commute_q1":
        return find_one(M.commute_moves(c), lambda d: d.get("ops") == [["cx q[1],q[0];"], ["cx q[1],q[7];"]])[0]
    if kind == "q19check":
        return find_one(M.init_moves(c), lambda d: d.get("move") == "check_rx" and d.get("q") == 19)[0]
    if kind == "q11measure":
        return find_one(M.init_moves(c), lambda d: d.get("move") == "reset_to_measure" and d.get("q") == 11)[0]
    if kind == "edge14to15":
        return find_one(M.readout_moves(c), lambda d: d.get("move") == "add_edge" and d.get("edge") == [14,15])[0]
    raise KeyError(kind)

def compose(base, kinds):
    c = C.clone(base)
    applied=[]
    for k in kinds:
        x = edit(c, k)
        if x is None: return None
        c = x; applied.append(k)
    return c

def main():
    # Copy4 is generated with LNS2's corrected helper/barrier/detector port.
    v27 = ROOT / "work/lanes/MAIN/v27x"
    revstem = OUT / "rev_v27x_copy4"
    try:
        review_copy.copy4(str(v27), str(revstem), 230, True)
    except Exception as e:
        print("copy4 failed", repr(e))
    seeds = {
        "v27x": v27,
        "v26n": ROOT / "work/lanes/MAIN/v26n",
        "bcpol_v25_endpoint": OUT / "prep_bcpol",
        "bcfb_clean": OUT / "prep_bcfb",
        "rev_v27x_copy4": revstem,
    }
    bases={}
    for name,p in seeds.items():
        if p.with_suffix(".qasm").exists():
            try: bases[name]=norm(C.read(p))
            except Exception as e: print("seed failed",name,repr(e))
    manifest=[]
    edits=["timing10","commute_q1","q19check","q11measure","edge14to15"]
    # Singleton and all prefixes on v27x; prefixes expose interactions without
    # assuming that marginal prices add.
    for bname,base in bases.items():
        save(base, f"deep_{bname}_base", f"seed:{bname}")
        manifest.append({"name":f"deep_{bname}_base","seed":bname,"edits":[]})
        for k in edits:
            c=compose(base,[k])
            if c is not None:
                n=f"deep_{bname}_{k}";save(c,n,f"seed:{bname}+{k}");manifest.append({"name":n,"seed":bname,"edits":[k]})
        # Ordered combinations, retaining temporarily worse intermediates.
        for mask in range(1,1<<len(edits)):
            ks=[k for i,k in enumerate(edits) if mask>>i&1]
            if len(ks)<2: continue
            c=compose(base,ks)
            if c is not None:
                n=f"deep_{bname}_"+"_".join(ks);save(c,n,f"seed:{bname}+"+"+".join(ks));manifest.append({"name":n,"seed":bname,"edits":ks})
    (OUT/"deep_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"seeds":list(bases),"candidates":len(manifest)}))

if __name__ == "__main__": main()
