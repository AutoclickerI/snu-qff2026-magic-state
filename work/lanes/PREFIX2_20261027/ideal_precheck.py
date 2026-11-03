"""Counterfactual ideal Steane prechecks, preserving every original noise channel.

These are diagnostic models, NOT legal/native candidate circuits. Ideal meters
are noiseless and add no waiting exposure: original channel blocks are copied
verbatim by source instruction identity. This isolates which precheck type can
remove accepted source+tail pairs before implementing its native circuit.
"""
import os,sys,json,time,copy
from pathlib import Path
from collections import defaultdict
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'EXPAND2_20261027'))
import analytic_price as ap
from qtools.evaluator import frontend as fa,sparse_walsh as sw
A=[1,14,8,9,2,16,15]

def run(stem,bases,cut):
    st=Path(stem);text=st.with_suffix('.qasm').read_text()
    data=json.loads(st.with_suffix('.json').read_text())['data_qubits'];fa.DATA=data
    ops,dets=fa.parse_current(text);original=list(ops)
    nt,labels=fa.native_text(original);old_noise=fa.noise_blocks
    original_prog,original_blocks=old_noise(nt,.001,first_order=False)
    lookup={o.line:(ins.text,block) for o,ins,block in zip(labels,original_prog,original_blocks)}
    new=copy.deepcopy(ops);bits=max(o.bit for o in new if o.bit is not None)+1
    physical=A if cut<=17 else data
    extra=[];extra_dets=[];t=cut
    for basis in bases:
        for support in fa.SUPPORTS:
            extra.append(fa.Op('RX' if basis=='X' else 'R',(24,),t,line=-len(extra)-1));t+=1
            for i in sorted(support):
                qs=(24,physical[i]) if basis=='X' else (physical[i],24)
                extra.append(fa.Op('CX',qs,t,line=-len(extra)-1));t+=1
            extra.append(fa.Op('MX' if basis=='X' else 'M',(24,),t,bit=bits,line=-len(extra)-1));t+=1
            extra_dets.append({bits});bits+=1
    for o in new:
        if o.time>=cut:o.time+=t-cut
    new=sorted(new+extra,key=lambda o:o.time);all_dets=dets+extra_dets
    new_text,newlabels=fa.native_text(new)
    def copied_noise(text,p,first_order=True):
        prog,blocks=old_noise(text,p,first_order=first_order)
        assert len(prog)==len(newlabels)
        ans=[]
        for ins,o in zip(prog,newlabels):
            if o.line in lookup:
                name,block=lookup[o.line];assert name==ins.text
                ans.append(block)
            else:ans.append([ins.text])
        return prog,ans
    try:
        fa.noise_blocks=copied_noise;m=fa.make_model(new,all_dets)
    finally:fa.noise_blocks=old_noise
    eng=fa.Engine(m);sw.canonicalize_detector_rows(m,eng);eng=fa.Engine(m)
    active=[i for i,p in enumerate(eng.projs) if p[:2]!=(0,0)]
    assert all(p[0]==0 for p in eng.projs)
    nd=len(all_dets);ks=tuple(active+list(range(nd,nd+len(eng.rot))))
    groups=defaultdict(list)
    for f in m.faults:groups[f['chan']].append(f)
    assert len(m.chans)==sum(len(b)-1 for b in original_blocks) or len(m.chans)>0
    compiled,elim=sw.compile_best(m,eng,groups,nd,ks,save=False)
    values=[]
    try:
        for key in [None]+eng.keys:
            states,weights,_=ap.kernel(eng,active,key)
            vec,peak=sw.contract_quotient(compiled,states,0 if key is None else sw.emask_for(key),elim['order'])
            values.append(float(weights@vec/(1<<len(ks))))
    finally:sw.COLUMNS.clear()
    acc=values[0];obs=sum(w*b*v for w,b,v in zip(eng.W,eng.beta,values[1:]))
    return dict(diagnostic_only=True,stem=str(stem),perfect_checks=bases,cut=cut,
                loss=float((acc-obs)/(2*acc)),acceptance=acc,channels=len(m.chans),
                width=elim['width'],rotations=len(eng.rot))

if __name__=='__main__':
    base=sys.argv[1];out=[]
    for cut in [17,20]:
        for b in ['','X','Z','XZ']:
            start=time.time();r=run(base,b,cut);r['seconds']=time.time()-start
            print(json.dumps(r),flush=True);out.append(r)
            (H/'ideal_prechecks.json').write_text(json.dumps(out,indent=2)+'\n')
