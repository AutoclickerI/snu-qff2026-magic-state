"""Remove CSS-state identity gates, then retime/rebuild the full preparation."""
import sys,json,copy
from build_rounds import H
from synthesize_grid import build

def reduce(v,vs):
    piv={}
    for x in vs:
        while x:
            b=x.bit_length()-1
            if b in piv:x^=piv[b]
            else:piv[b]=x;break
    while v:
        b=v.bit_length()-1
        if b not in piv:return v
        v^=piv[b]
    return 0

def simplify(res):
    res=copy.deepcopy(res)
    lay=json.loads((H/'layout_joint.json').read_text())
    sites=[q for q in range(36) if q not in lay['D']]
    x={q:1<<res['pivots'].index(q) if q in res['pivots'] else 0 for q in sites}
    kept=[];dropped=[]
    for a,b in res['ops']:
        if not x[a] or reduce(x[b],[x[q] for q in sites if q!=b]):dropped.append((a,b));continue
        x[b]^=x[a];kept.append((a,b))
    res['ops']=kept;res['prep_cx']=len(kept);res['state_identity_drops']=len(dropped)
    return res

if __name__=='__main__':
    rows=[]
    for r in json.loads((H/'gf2_manifest.json').read_text()):
        m=json.loads((H/'builds'/r['name']).with_suffix('.json').read_text())
        out=build(simplify(m['resource']),tag='gf2simp');rows.append(out)
    for r in json.loads((H/'route_manifest.json').read_text()):
        m=json.loads((H/'builds'/r['name']).with_suffix('.json').read_text())
        res=dict(seed=m['seed'],pivots=m['initial_plus'],ops=[(a,b) for t,a,b in m['preparation_ops']],checks=[],
            flag=m['flag'],support=m['logical_z_verification'],prep_cx=m['prep_cx'])
        out=build(simplify(res),tag='routesimp');rows.append(out)
    rows.sort(key=lambda r:(r['R'],r['prep_cx']))
    (H/'simplified_manifest.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows[:12]),flush=True)
