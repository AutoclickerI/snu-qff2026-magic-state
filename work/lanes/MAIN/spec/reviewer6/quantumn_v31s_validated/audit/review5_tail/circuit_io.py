from pathlib import Path
import json

def emit(ops,dets,stem,data,frame_x=(),frame_z=(),metadata=None):
    ops=sorted(ops,key=lambda o:o.time)
    maxbit=max(o.bit for o in ops if o.bit is not None)
    depth=max(o.time for o in ops)+1
    lines=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{maxbit+1}];']
    for t in range(depth):
        active=[]
        for o in ops:
            if o.time!=t:continue
            active+=list(o.qs);qs=','.join(f'q[{q}]' for q in o.qs)
            if o.kind in ['M','MX']:
                if o.kind=='MX':lines.append('h '+qs+';')
                lines.append(f'measure {qs} -> c[{o.bit}];')
                nxt=next((o2 for o2 in ops if o2.time>t and o.qs[0] in o2.qs),None)
                if o.kind=='MX' and nxt is not None and nxt.kind not in ['R','RX']:lines.append('h '+qs+';')
            elif o.kind in ['R','RX']:
                lines.append('reset '+qs+';')
                if o.kind=='RX':lines.append('h '+qs+';')
            else:lines.append(o.kind.lower()+' '+qs+';')
        assert len(active)==len(set(active)),(t,active)
        if t<depth-1:lines.append('barrier '+','.join(f'q[{q}]'for q in range(36))+';')
    lines.extend('// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(d))for d in dets)
    if frame_x or frame_z:
        lines.append('// FRAME_X(0) '+' '.join(f'c[{b}]'for b in frame_x))
        lines.append('// FRAME_Z(0) '+' '.join(f'c[{b}]'for b in frame_z))
    stem=Path(stem);stem.with_suffix('.qasm').write_text('\n'.join(lines)+'\n')
    md=dict(data_qubits=data,native_depth=depth,CX=sum(o.kind=='CX'for o in ops),review_status='Independent-model candidate; official judge class/speed not yet run')
    if metadata:md.update(metadata)
    stem.with_suffix('.json').write_text(json.dumps(md,indent=2)+'\n')

def certify(ops,dets,data,fa,frame_x=(),frame_z=(),frame_x_const=0,frame_z_const=0):
    fa.DATA=data;fa.FRAME_X=list(frame_x);fa.FRAME_Z=list(frame_z)
    fa.FRAME_X_CONST=frame_x_const;fa.FRAME_Z_CONST=frame_z_const
    m=fa.make_model(ops,dets);eng=fa.Engine(m);a,n=eng.ntable(0,0)
    stabs=[eng.expect(eng.phi(0),(eng.B.express(x),eng._w(z),c))for x,z,c in m.gen_m]
    single=0.;cache={}
    for f in m.faults:
        key=(f['s'],f['d'])
        if key not in cache:cache[key]=eng.ntable(*key)
        aa,nn=cache[key]
        if nn is not None:single+=f['p']*nn[f['e']]
    return dict(ideal_acceptance=a,ideal_loss=float(n[0]),stabilizers=stabs,first_order_loss=float(single),channels=len(m.chans),rank=eng.r)
