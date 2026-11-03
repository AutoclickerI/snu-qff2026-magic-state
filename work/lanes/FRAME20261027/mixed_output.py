"""Test partial encoded teleportation as a genuine change of output roles."""
from frame_tools import *
from teleport_b import D,B,C,A
import itertools,traceback
if __name__=='__main__':
    base=OUT/'btele_fresh'
    original,ds,md=load(base)
    results=[];valid=[]
    for mask in range(1,127):
        ops=copy.deepcopy(original)
        for o in ops:
            if o.time==47 and o.kind=='CX' and o.qs in list(zip(D,B)):
                j=D.index(o.qs[0])
                if not(mask>>j&1):o.qs=o.qs[::-1]
            if o.bit in range(400,407):
                j=o.bit-400
                o.qs=((D if mask>>j&1 else B)[j],)
        data=[B[j] if mask>>j&1 else D[j] for j in range(7)]
        # All seven measured X values are available for the affine logical frame.
        stem=emit(f'mixed_{mask:03}',ops,ds,data,
                  {'X':(0,set()),'Z':(0,{400+j for j in range(7) if mask>>j&1})},
                  {'teleported_code_coordinate_mask':mask})
        raw=raw_check(stem.with_suffix('.qasm').read_text(),data)
        results.append({'mask':mask,'raw':raw})
        if raw['ok']:
            valid.append(str(stem));print('VALID',mask,flush=True)
        else:
            # Keep the summary, not 126 large invalid QASMs.
            stem.with_suffix('.qasm').unlink();stem.with_suffix('.json').unlink()
    (HERE/'mixed_output_summary.json').write_text(json.dumps(results,indent=2)+'\n')
    print('VALID_COUNT',len(valid),flush=True)
    for s in valid:
        try:print(json.dumps(price(Path(s))),flush=True)
        except Exception:traceback.print_exc()

