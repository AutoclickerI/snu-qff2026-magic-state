"""Joint counterfactual for exactly the incumbent operations replaced by joint.py."""
from joint import *
from qtools.evaluator import sparse_walsh as sw

if __name__=='__main__':
    old=split_base()[2];keys={(o.time,o.kind,o.qs) for o in old}
    m,e,groups,nd,ks,psi,where,_=sw.prepare(BASE,True)
    removed=[]
    for cid,ch in enumerate(m.chans):
        o=m.labels[ch['ins']]
        if (o.time,o.kind,o.qs) in keys:
            ch['p']=0
            for ff in groups[cid]:ff['p']=0
            removed.append(cid)
    compiled,elim=sw.compile_best(m,e,groups,nd,ks,save=False)
    sw._CTX.update(eng=e,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
    rows=[sw._row(k) for k in [None]+e.keys]
    A=rows[0]['value'];obs=sum(w*b*r['value'] for w,b,r in zip(e.W,e.beta,rows[1:]))
    out={'baseline':str(BASE.relative_to(ROOT)),'removed_ops':[dict(t=o.time,kind=o.kind,qubits=o.qs,bit=o.bit) for o in old],
         'removed_cx':sum(o.kind=='CX' for o in old),'removed_channels':len(removed),'total_channels':len(m.chans),
         'convention':'All selected operation channels and attached following-idle channels are ideal jointly; nonadditive counterfactual.',
         'loss':(A-obs)/(2*A),'acceptance':A}
    (HERE/'evidence/resource_counterfactual.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='removed_ops'},indent=2))
