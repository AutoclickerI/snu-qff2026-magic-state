"""Measured-codeword reuse to replace the last data idle with a physical CX.

Only adjacency is relaxed. The actual measurement-reuse depolarization, final
CX noise and affine logical frame are included in the lane-local evaluator.
"""
import hashlib,json,sys
from pathlib import Path
import cross
s=cross.s
sys.path.insert(0,str(cross.ROOT/'work/lanes/FRAME20261027'))
import frame_tools as ft
ft.OUT=cross.HERE/'cand'


def raw_abstract(text,data):
    from tprep.exact import run,verify
    ops,dets=s.f.parse_current(text)
    native,_=s.f.native_text(ops)
    bits=[o.bit for o in ops if o.bit is not None]
    pos={b:i for i,b in enumerate(bits)}
    native+='\n'+'\n'.join('DETECTOR '+' '.join(f'rec[-{len(bits)-pos[b]}]'for b in sorted(row))for row in dets)
    frames={P:(c,[pos[b]for b in sorted(bs)])for P,(c,bs)in ft.parse_frames(text).items()}
    result=verify(native,data,frame=frames)
    state,inverse,_,_,wires=run(native,36)
    values=[]
    for P in 'XZ':
        for support in s.f.SUPPORTS:
            obs=state.stim.PauliString(state.n)
            for i in support:obs[wires[data[i]]]=P
            values.append(state.expectation(obs,inverse))
    result.pop('detector_values',None)
    result.update(ok=not result['errors']and all(abs(v-1)<1e-9 for v in values),six_stabilizers=values,
                  scope='Official raw exact checker including affine logical frame, before ideal syndrome decoding. Only physical adjacency validation is bypassed.')
    return result


ft.raw_check=raw_abstract


def build(variant):
    _,meta,ops,_=cross.source('bell2','reuse_seed_'+variant)
    r=meta['tail_start']
    frames={'X':(0,set()),'Z':(0,set())}
    if variant.startswith('dual'):
        new=[]
        for o in ops:
            t=o.time;qs=set(o.qs)
            if qs<=set(s.B+s.C) and t>9:
                t-=1
            if o.time>9 and o.kind=='CX' and qs&set(s.B)and qs&set(s.D):
                t-=1
            if o.time>9 and o.kind=='CX' and qs&set(s.A)and qs&set(s.D):
                t+=1
            if o.kind=='M'and o.qs[0]in s.A and t>9:t+=1
            new.append(s.f.Op(o.kind,o.qs,t,o.bit))
        ops=new
        if variant=='dual_reuse_B':
            ops += [s.f.Op('CX',(d,b),r+2)for d,b in zip(s.D,s.B)]
            frames['Z']=(0,set(range(114,121)))
    elif variant=='reuse_A':
        ops += [s.f.Op('CX',(a,d),r+2)for a,d in zip(s.A,s.D)]
        frames['X']=(0,set(range(107,114)))
    elif variant!='control':raise ValueError(variant)
    ops.sort(key=lambda o:o.time)
    used=set()
    for o in ops:
        keys={(o.time,q)for q in o.qs};assert not used&keys,(o,used&keys);used|=keys
    s.f.DATA=s.D
    contract=s.record_contract.complete(s.f.make_model(ops,[]),[])
    assert all(not row['reference']for row in contract['missing'])
    dets=[set(row['bits'])for row in contract['missing']]
    metadata=dict(variant=variant,source='Bell2',roles=meta['roles'],tail_start=r,
                  frames={P:(c,sorted(bs))for P,(c,bs)in frames.items()},grid_valid=False,
                  diagnostic_only=True,scope=__doc__,ticks=max(o.time for o in ops)+1,
                  record_contract=contract)
    return ft.emit('terminal_'+variant,ops,dets,s.D,frames,metadata)


def main():
    rows=[]
    for variant in ('control','reuse_A','dual_control','dual_reuse_B'):
        try:
            stem=build(variant)
            result=ft.price(stem)
            if result['raw']['ok']:
                singles=ft.singles(stem)
                result['singles']={k:v for k,v in singles.items()if k!='harmful'}
                stem.with_suffix('.singles.json').write_text(json.dumps(singles,indent=2)+'\n')
            result.update(variant=variant,diagnostic_only=True,grid_valid=False)
            stem.with_suffix('.reuse_result.json').write_text(json.dumps(result,indent=2)+'\n')
        except Exception as exc:
            import traceback
            result=dict(variant=variant,error=str(exc),traceback=traceback.format_exc())
        rows.append(result)
        print(json.dumps(result),flush=True)
        (cross.HERE/'reuse_results.json').write_text(json.dumps(dict(completed=False,rows=rows),indent=2)+'\n')
    (cross.HERE/'reuse_results.json').write_text(json.dumps(dict(completed=True,rows=rows),indent=2)+'\n')


if __name__=='__main__':main()
