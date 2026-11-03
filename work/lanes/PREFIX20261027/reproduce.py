"""Rebuild and validate the best native rank-five experiment, not a finalist.

From the repository root:
  PYTHONPATH=work/tools:upstream/snu-qff2026-problem .venv/bin/python \
      work/lanes/PREFIX20261027/reproduce.py

The checked-in QASM remains the canonical artifact. This script verifies the
integer phase identity, replays every parity location, rebuilds byte-identical
QASM, and recomputes its exact noisy score through the shared evaluator.
"""
import hashlib,json
from pathlib import Path
import synth
from qtools import price

H=Path(__file__).resolve().parent
STEM=H/'cand/final_phase_random_1'

def rank(vs):
    p={}
    for v in vs:
        while v:
            b=v.bit_length()-1
            if b not in p:p[b]=v;break
            v^=p[b]
    return len(p)

def main():
    meta=json.loads(STEM.with_suffix('.json').read_text());r=meta['synthesis']
    assert r['goals']==synth.goals(r['functional'])
    for z in range(32):
        phase=-sum((g&z).bit_count()%2 for g in r['goals'])
        assert (phase-((synth.LOGICAL&z).bit_count()%2))%8==0
    rows=list(synth.INIT);states=[list(rows)]
    for a,b in r['path']:
        assert synth.adjacent(synth.CELLS[a],synth.CELLS[b])
        rows[b]^=rows[a];states.append(list(rows))
    assert rows==r['rows'] and rank(rows)==5 and sum(v!=0 for v in rows)==5
    for gs,(k,i) in r['phase_locations'].items():assert states[k][i]==int(gs)
    assert set(map(int,r['phase_locations']))==set(r['goals'])
    rebuilt=synth.build(r,'reproduced_best')
    original=STEM.with_suffix('.qasm').read_bytes();new=rebuilt.with_suffix('.qasm').read_bytes()
    assert original==new,'rebuild differs from the scored artifact'
    ans=price(rebuilt,processes=1,use_cache=False)
    assert abs(ans['loss']-8.489600747077256e-5)<1e-13
    assert abs(ans['acceptance']-.6890119163514336)<1e-11
    out=dict(qasm_sha256=hashlib.sha256(new).hexdigest(),integer_phase_identity=True,
             rank5=True,all_cx_adjacent=True,byte_identical=True,
             loss=ans['loss'],acceptance=ans['acceptance'],raw=ans['raw'])
    (H/'reproduction.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
