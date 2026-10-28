"""Combine independently tested early scheduling and late physical heralds."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'work/tools'),str(ROOT/'work/lanes/END2_20261027'),str(ROOT/'work/lanes/EXPAND2_20261027')]
import frontend_axis as f
from joint import emit
from axis_echo import exact
from qtools import write_stem
from qtools.validity import raw_check

early=HERE/'schedule/lateprep_0_25_11_61195e875ba71064_d6_20_19_10_2_22_16'
late=ROOT/'work/lanes/SOTA_DETECT_20261028/heralds/h13t34_33t39_14t35_b35c099d591c3662_d6_20_19_10_2_22_16'
eo,_=f.parse_current(early.with_suffix('.qasm').read_text())
lo,dets=f.parse_current(late.with_suffix('.qasm').read_text())
ops=[o for o in eo if o.time<=25]+[o for o in lo if o.time>25]
ops.sort(key=lambda o:o.time)
seen=set()
for o in ops:
    for q in o.qs:
        key=(o.time,q);assert key not in seen;seen.add(key)
text=emit(ops,dets)
data=json.loads(early.with_suffix('.json').read_text())['data_qubits']
info=dict(early_parent=str(early.relative_to(ROOT)),late_parent=str(late.relative_to(ROOT)),
          raw=raw_check(text,data),cx=sum(o.kind=='CX' for o in ops),ticks=max(o.time for o in ops)+1,
          scope='Complete native circuit; this combines small changes and is not an architecture/SOTA claim.')
assert info['raw']['ok'],info
stem=write_stem(text,data,HERE/'native_best','schedule_heralds',source=info)
info.update(stem=str(stem),exact=exact(stem))
stem.with_suffix('.result.json').write_text(json.dumps(info,indent=2)+'\n')
print(json.dumps(info),flush=True)
