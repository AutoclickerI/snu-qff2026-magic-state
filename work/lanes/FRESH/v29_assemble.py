"""Correlated-resource transplant onto COMP29's v29c prefix.

This is the BCPOL emitter with only its historical 96-operation assertion
relaxed: v29c has two fewer old B/C operations after its local edits.  The
replacement resource, detector propagation, and endpoint checks are unchanged.
"""
import json, pathlib, re, sys
import argparse
ROOT = pathlib.Path(__file__).resolve().parents[3]
FRESH = ROOT / "work/lanes/FRESH"
sys.path.insert(0, str(ROOT / "work/lanes/BCPOL"))
import build as bc
import schedule as S
from util import native_times

bc.H = FRESH

def source_v29(kind="policy", value=9, base="v29c"):
    text = (bc.H / "inputs" / f"{base}.qasm").read_text()
    md = json.loads((bc.H / "inputs" / f"{base}.json").read_text())
    head, raw, tail = S.qasm_ops(text); us = S.fold_units(raw); ts = native_times(text, us); R = md["R"]
    init = {q: max(i for i,u in enumerate(us) if u.qs == (q,) and ts[i] < R and u.name in ("RESET","RX","MEASURE","MX")) for q in bc.B + bc.C}
    rem = set(init.values()) | {i for i,u in enumerate(us) if ts[i] < R and u.name == "CX" and set(u.qs) <= set(bc.B + bc.C) and all(i > init[q] for q in u.qs)}
    if kind == "endpoint":
        rem |= {i for i,u in enumerate(us) if ts[i] == R and u.name == "CX" and set(u.qs) <= set(bc.B + bc.C)}
    if kind == "c6":
        raise ValueError("v29c c6 is outside this transplant")
    mxold = {bc.bit(us[i]) for i in init.values() if us[i].name == "MX"}
    zold = {bc.bit(us[i]) for i in init.values() if us[i].name == "MEASURE"}
    clean = []
    for line in tail:
        if line.startswith("// DETECTOR"):
            bs = set(map(int, bc.BITS.findall(line)))
            if bs & zold:
                if len(bs) == 1: continue
                raise AssertionError(("unexpected init detector", line))
            bs -= mxold
            if not bs: continue
            line = "// DETECTOR " + " ".join(f"c[{b}]" for b in sorted(bs))
        else:
            if set(map(int, bc.BITS.findall(line))) & (mxold | zold): continue
        clean.append(line)
    return md, head, us, ts, clean, init, rem

def main():
    ap0 = argparse.ArgumentParser(add_help=False); ap0.add_argument('--input-json'); ap0.add_argument('--name', default='corr_d11_k57_s35_002'); known, _ = ap0.parse_known_args()
    if known.input_json:
        src = json.loads(pathlib.Path(known.input_json).read_text()); prep = src.get('prep', src.get('meta', {}).get('prep', src))
    else:
        plan = json.loads((FRESH / "corr_d11_k57_s35_002_freshbase_w0_fast_zlast.plan.json").read_text()); prep = plan["meta"]["prep"]
    prep.update(kind="endpoint", value=0, endpoint_rank=3, extra_check=True, helper_x=False)
    bc.source = source_v29
    ap = argparse.ArgumentParser(); ap.add_argument('--window', type=int, default=0); ap.add_argument('--init', choices=['reset','fast'], default='reset'); ap.add_argument('--timing', choices=['alap','asap','project'], default='alap'); ap.add_argument('--round-shift', type=int, default=0); ap.add_argument('--input-json'); ap.add_argument('--name', default=known.name); a = ap.parse_args()
    options = dict(base="v29c", retime_window=a.window, endpoint_parity=True, timing=a.timing, round_shift=a.round_shift)
    if a.init == 'fast': options['mx'] = [q for q in prep['pivots'] if q != 19]
    text, md = bc.build(prep, options)
    stem = FRESH / f"{a.name}_v29c_w{a.window}_{a.init}_{a.timing}_rs{a.round_shift}"
    stem.with_suffix(".qasm").write_text(text)
    stem.with_suffix(".json").write_text(json.dumps(md, indent=2) + "\n")
    print(stem)

if __name__ == "__main__": main()
