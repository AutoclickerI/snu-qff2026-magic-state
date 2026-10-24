from build import *

def zero_at(c,q,t):
    R=c['meta']['R']
    init={q:max(i for i,(u,tt) in enumerate(zip(c['u'],c['t'])) if u.qs==(q,) and tt<R and u.name in ('RX','RESET','MX','MEASURE')) for q in C.B+C.C}
    it={q:c['t'][i] for q,i in init.items()}
    vals={};n=0
    for u,tt in zip(c['u'],c['t']):
        if tt>=t:break
        for z in u.qs:
            if z in it and tt==it[z] and len(u.qs)==1:
                vals[z]=1<<n if u.name in ('RX','MX') else 0
                n+=u.name in ('RX','MX')
        if u.name=='CX' and set(u.qs)<=vals.keys():
            a,b=map(int,C.S.QRE.findall(u.lines[0]));vals[b]^=vals[a]
    return vals.get(q,-1)==0 and not any(tt==t and q in u.qs for u,tt in zip(c['u'],c['t']))

if __name__=='__main__':
    rows=[];errors=[];known=[]
    for b in json.loads((H/'bcfb_ports.json').read_text()):
        if 'stem' not in b:continue
        base=C.read(H/b['stem'])
        kinds=['copy4','timing10','commute1','q19check','q11measure','edge14to15','feedback']
        for t in (37,38):
            z=zero_at(base,5,t);known.append(dict(stem=b['stem'],q=5,t=t,known_zero=z))
            if z:kinds.append(f'q5t{t}')
        for n in range(len(kinds)+1):
            for ks in itertools.combinations(kinds,n):
                try:
                    c=C.clone(base)
                    for k in ks:c=edit(c,k)
                    mask=sum(1<<kinds.index(k) for k in ks)
                    name=b['stem'] if not ks else b['stem']+'_'+format(mask,'03x')
                    rows.append(save(c,name,b['edits']+list(ks)))
                except Exception as e:errors.append(dict(base=b['stem'],edits=ks,error=repr(e)))
    (H/'bcfb_manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
    (H/'bcfb_combination_errors.json').write_text(json.dumps(errors,indent=2)+'\n')
    (H/'bcfb_known_q5.json').write_text(json.dumps(known,indent=2)+'\n')
    print(json.dumps(dict(candidates=len(rows),errors=len(errors),examples=errors[:8],known=known)),flush=True)
