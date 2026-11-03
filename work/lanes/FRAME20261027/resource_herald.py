"""Verify fresh phase seeds and trade other resource detectors jointly."""
from frame_tools import *
import itertools,traceback
SOURCES=[(26,31),(28,31),(29,30)]
SOURCE_FLAGS=[364,365,371,372,375,362,297,351]
def make(mask,drop=()):
    ops,dets,md=load(OUT/'btele_fresh')
    for j,(q,t) in enumerate(SOURCES):
        if not(mask>>j&1):continue
        source=next(o for o in ops if o.kind=='RX' and o.qs==(q,) and o.time==t)
        assert not any(q in o.qs and o.time==t-1 for o in ops)
        source.time=t-1
        ops.append(f.Op('MX',(q,),t,420+j))
        dets.append({420+j})
    dets=[row for row in dets if row not in [{v} for v in drop]]
    return emit('herald'+str(mask)+'_drop'+'_'.join(map(str,drop)),ops,dets,md['data_qubits'],
                parse_frames((OUT/'btele_fresh.qasm').read_text()),
                {'herald_seeds':[SOURCES[j][0] for j in range(3) if mask>>j&1],'dropped_singleton_detectors':drop})
if __name__=='__main__':
    specs=[(i,()) for i in (1,2,4,7)]
    specs += [(7,tuple(SOURCE_FLAGS[:n])) for n in (3,5,8)]
    specs += [(i,tuple(SOURCE_FLAGS[:3])) for i in (1,2,4)]
    for mask,drop in specs:
        s=make(mask,drop)
        try:print(json.dumps(price(s)),flush=True)
        except Exception:traceback.print_exc()

