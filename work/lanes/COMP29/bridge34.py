"""B logical-Z flags beyond the three-CX bound, with borrowed-gate cancellation."""
from decoder34 import *
def bridge(path):
    edges=list(zip(path,path[1:]));return edges+list(reversed(edges[:-1]))
if __name__=='__main__':
    base=C.read(H/'g_base');rows=[];errors=[]
    left=bridge([6,12,13]);right=bridge([26,25,19,13])
    variants=[(13,left+right),(13,right+left),(6,right+bridge([13,12,6])),(26,left+bridge([13,19,25,26]))]
    for i,(root,net) in enumerate(variants):
        for simplified in [False,True]:
            n=f'g_Bflag_{i}_{int(simplified)}'
            try:
                c=build(base,net,axes={root:'Z'},flags=[root])
                if simplified:c=cancel_added(c)
                r=save(c,n,['B logical-Z partial decoder',dict(root=root,network=net,cancel_existing=simplified)]);rows.append(r)
            except Exception as e:errors.append(dict(stem=n,error=repr(e)))
    (H/'v34_bridge.json').write_text(json.dumps(rows,indent=2)+'\n');(H/'v34_bridge_errors.json').write_text(json.dumps(errors,indent=2)+'\n');print(rows);print(errors)
