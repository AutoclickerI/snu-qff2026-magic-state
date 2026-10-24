"""Enumerate every compatible cat-readout/preparation fusion at fixed slots."""
from build30 import *

def pairs(c):
    last={};out={}
    for i,(u,t) in enumerate(zip(c['u'],c['t'])):
        if u.name=='RESET' and u.qs[0] in last:
            q=u.qs[0];j=last[q];v=c['u'][j]
            if v.name=='MX':
                b=int(re.search(r'c\[(\d+)\]',' '.join(v.lines))[1])
                if f'// DETECTOR c[{b}]' in c['tail']:
                    assert sum(b in set(map(int,re.findall(r'c\[(\d+)\]',l))) for l in c['tail'])==1
                    out[q]=(j,i,b)
        for q in u.qs:last[q]=i
    return out

def unfold_set(base,qs):
    c=C.clone(base);pp=pairs(c)
    for q in qs:
        j,i,b=pp[q];c['u'][j]=C.Unit([f'h q[{q}];']);c['u'][i]=C.Unit([f'measure q[{q}] -> c[{b}];'])
    return finish(c)

def run():
    base=C.read(H/'f_timing_mz_5_12');pp=pairs(base);qs=sorted(pp);rows=[]
    for mask in range(1<<len(qs)):
        subset=[q for i,q in enumerate(qs) if mask>>i&1]
        name='f_unfold_'+('_'.join(map(str,subset)) if subset else 'none')
        if not subset:name='f_timing_mz_5_12'
        elif subset==[4]:name='f_unfold4'
        try:
            if name in ('f_timing_mz_5_12','f_unfold4'):
                r=dict(stem=name,edits=['unfold '+str(subset)]);r.update(json.loads((H/(name+'.screen.json')).read_text()))
            else:r=save(unfold_set(base,subset),name,['f_timing_mz_5_12','unfold '+str(subset)]);r.update(screen(name))
            rows.append(r);print(name,r['total'],r['exp_minus_A1'],flush=True)
        except Exception as e:
            rows.append(dict(stem=name,edits=['unfold '+str(subset)],error=repr(e)));print(name,repr(e),flush=True)
        (H/'v30_unfold_family.json').write_text(json.dumps(rows,indent=2)+'\n')
    return dict(candidates=len(rows),valid=sum('total' in r for r in rows))

if __name__=='__main__':print(run())

def extensions():
    rows=json.loads((H/'v30_unfold_family.json').read_text())
    for r in rows:
        if r['stem']=='f_unfold4' and 'error' in r:
            del r['error'];r.update(screen('f_unfold4'))
    (H/'v30_unfold_family.json').write_text(json.dumps(rows,indent=2)+'\n')
    rows=[]
    for source in ['f_frame_group','f_frame13']:
        for qs in [[1,4,14],[1,4,9,14]]:
            name=source+'_unfold_'+'_'.join(map(str,qs))
            try:
                r=save(unfold_set(C.read(H/source),qs),name,[source,'unfold '+str(qs)]);r.update(screen(name));rows.append(r)
            except Exception as e:rows.append(dict(stem=name,edits=[source,str(qs)],error=repr(e)))
            print(json.dumps(rows[-1]),flush=True)
    (H/'v30_unfold_extensions.json').write_text(json.dumps(rows,indent=2)+'\n')
    return dict(candidates=len(rows),valid=sum('total' in r for r in rows))
