"""Optional b45-source noise experiment with a q19->q25 identity pair at20/21.

The late pair cannot preserve its original order after CX13->19@27 and still
release q25 by29. Moving the entire adjacent identity pair before that source
operation preserves the exact ideal instrument, but changes the noisy channel.
"""
import json
import os
import sys
from pathlib import Path

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
from qtools import write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit


def main():
    bpath=HERE.parent/'PREFIX2_20261027/retimed/b45_alap_b_module.json'
    parent=Path(json.loads(bpath.read_text())['prefix_stem'])
    ops,dets=f.parse_current(parent.with_suffix('.qasm').read_text())
    original=list(ops)
    for tick in (20,21):
        assert not any(op.time==tick and set(op.qs)&{19,25} for op in ops)
    pair=[f.Op('CX',(19,25),tick) for tick in (20,21)]
    ops.extend(pair);ops.sort(key=lambda op:op.time)
    # Erasing the consecutive same-CX pair recovers every original operation
    # and its timestamp. No other operation touches either pair wire between.
    assert [op for op in ops if op not in pair]==original
    for q in (19,25):
        sequence=[op for op in ops if q in op.qs]
        assert sequence.index(pair[1])==sequence.index(pair[0])+1
    release=max(op.time+1 for op in ops if 25 in op.qs)
    assert release<=29,release
    data=[6,20,19,10,2,22,16]
    text=emit(ops,dets);raw=raw_check(text,data);assert raw['ok'],raw
    meta=dict(parent=str(parent),added=[dict(kind='CX',qs=[19,25],time=t) for t in (20,21)],
              source_rest_unchanged=True,ideal_identity_pair=True,q25_release=release,raw=raw,
              scope='Physical noisy source experiment; full native single/pair audit and exact price are separate.')
    stem=write_stem(text,data,HERE/'boundary','source_b45_restore25_early_pair',source=meta)
    result=dict(stem=str(stem),cx=sum(op.kind=='CX' for op in ops),**meta)
    (HERE/'restore25_early_pair.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
