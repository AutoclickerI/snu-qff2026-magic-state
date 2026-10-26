import re
import schedule_local as S
from tprep.qasm import convert
from tprep.noise import STANDARD,schedule

def native_times(text,units):
    stim,labels,errors=convert(text,36,STANDARD)
    assert not errors,errors
    prog,steps,gaps=schedule(stim)
    qmap=S.native_qasm_index(text)
    raw_to_unit={k:i for i,u in enumerate(units) for k in u.raw_indices}
    times=[None]*len(units)
    for ins,ss in zip(prog,steps):
        if not ss:continue
        lab=labels[ins.line_no-1];mt=re.match(r'instruction (\d+)',lab)
        if mt and int(mt.group(1)) in qmap:
            i=raw_to_unit[qmap[int(mt.group(1))]]
            t=min(t for q,t in ss)
            times[i]=t if times[i] is None else min(times[i],t)
    assert all(t is not None for t in times),[(i,u.lines)for i,u in enumerate(units)if times[i] is None]
    return times
