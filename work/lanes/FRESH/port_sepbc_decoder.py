"""Port reviewer-6's destructive A decoder onto a SEPBC schedule.

The SEPBC schedules already use q15's terminal instrument, so q15 is retained
as the logical-X representative's destination and its measurement is moved one
tick after q8/q9. Detector rows are transformed from the actual bit IDs.
"""
import json, pathlib, sys, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3]; FRESH=ROOT/'work/lanes/FRESH'
PORT=ROOT/'work/lanes/MAIN/spec/reviewer6/quantumn_v31s_validated/audit/reaudit_evaluation/portable'
ARCH=ROOT/'work/lanes/MAIN/spec/reviewer6/quantumn_v31s_validated/audit/review6_architecture'
sys.path.insert(0,str(PORT))
sys.path.insert(0,str(ARCH))
import frontend as f
from circuit_io import emit

def build(src_name):
    src=ROOT/src_name
    text=src.with_suffix('.qasm').read_text(); ops,dets=f.parse_current(text)
    meta=json.loads(src.with_suffix('.json').read_text()); R=meta['R']
    meas={o.qs[0]:o for o in ops if o.kind in ('M','MX') and o.qs[0] in (8,9,15)}
    assert set(meas)=={8,9,15}, (src_name,meas)
    # Move the two D->A couplings earlier, freeing the decoder ticks.
    for pair in ((10,9),(21,15)):
        xs=[o for o in ops if o.kind=='CX' and o.qs==pair and o.time==R]
        assert len(xs)==1,(src_name,pair)
        xs[0].time=R-1
    tdg=[o for o in ops if o.kind=='TDG' and o.qs==(10,) and o.time==R-1]
    assert len(tdg)==1; tdg[0].time=R-2
    b8,b9,b15=meas[8].bit,meas[9].bit,meas[15].bit
    # Re-express the A rows under X9<-X9+X15 and X8<-X8+X9,
    # then add the deterministic X_A flag row.
    for row in dets:
        if b15 in row: row.symmetric_difference_update({b9})
        if b9 in row: row.symmetric_difference_update({b8})
    assert all(b8 not in row for row in dets)
    dets.append({b8})
    meas[8].kind='MX'; meas[8].time=R+2
    meas[9].kind='M';  meas[9].time=R+2
    meas[15].kind='M'; meas[15].time=R+2
    ops.extend([f.Op('CX',(9,15),R),f.Op('CX',(8,9),R+1)])
    ops.sort(key=lambda o:o.time)
    name=pathlib.Path(src_name).stem+'_a_decode'
    out=FRESH/name
    out_meta=dict(meta,source=str(src_name),variant='SEPBC A partial decoder',CX=sum(o.kind=='CX' for o in ops),cx=sum(o.kind=='CX' for o in ops),R=R,native_depth=max(o.time for o in ops)+1,decoder=dict(gates=[(9,15,R),(8,9,R+1)],bits=[b8,b9,b15],flag=[b8]))
    emit(ops,dets,out,out_meta)
    # Reparse, validate layer disjointness and nearest-neighbour geometry.
    p,dd=f.parse_current(out.with_suffix('.qasm').read_text())
    for t in range(max(o.time for o in p)+1):
        qs=[q for o in p if o.time==t for q in o.qs]; assert len(qs)==len(set(qs)),(t,qs)
    assert all(abs(a//6-b//6)+abs(a%6-b%6)==1 for o in p if o.kind=='CX' for a,b in [o.qs])
    print(json.dumps(dict(stem=str(out),R=R,CX=out_meta['CX'],detectors=len(dd),sha256=hashlib.sha256(out.with_suffix('.qasm').read_bytes()).hexdigest())),flush=True)
    return out

if __name__=='__main__':
    for s in sys.argv[1:]: build(s)
