"""Complete the source reads directly into known-Z initial states.

These are changes at the new R45 interface, not B/C gate synthesis: delay a
deterministic Z source read until just before first use, remove its following
reset, and restore any guard that the reset formerly displaced. Every candidate
retains the same65 B/C CXs, A encoder, parity records and terminal helpers.
"""
import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
import v37
H=v37.H
KEEPS=[(29,28,22),(40,2,8),(41,20,14),(41,22,21),(44,2,1)]
def make(keepmask,readmask):
    keep={g for i,g in enumerate(KEEPS) if keepmask>>i&1};c=v37.blue_bell()
    if readmask&1:keep.add((32,11,10))
    v37.remove(c,v37.EARLY_GUARDS-keep)
    changes=[]
    for flag,q,resettime,bit,mt in [(1,11,34,297,33),(2,3,40,319,39),(4,13,40,318,39),(8,7,40,317,39)]:
        if not readmask&flag:continue
        v37.remove(c,{(resettime,q)})
        for o in c['ops']:
            if bit in v37.lib.bits_of(o):o['t']=mt
        changes.append(dict(q=q,record=bit,measure_time=mt,remove_reset_at=resettime))
    c['meta'].update(source=f'v37a R45 Bell/source completion; guardmask={keepmask}; direct Z-read handoffs {changes}',handoffs=changes,keepmask=keepmask,readmask=readmask)
    return c
if __name__=='__main__':
    out=[]
    for keepmask in [27,31]:
        for readmask in range(1,8):
            n=f'v37_handoff_k{keepmask}_m{readmask}';st,info=v37.schedule(make(keepmask,readmask),n,-1,seconds=5)
            print(n,info['status'],flush=True)
            if st:out.append(n)
    (H/'v37_handoff_names.json').write_text(json.dumps(out))
