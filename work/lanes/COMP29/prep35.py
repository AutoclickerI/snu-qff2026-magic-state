"""Remove only idle noise before an isolated checked preparation measurement."""
from core35 import *
def options(base):
    out=[]
    for q in range(36):
        seq=[(i,u,t) for i,(u,t) in enumerate(zip(base['u'],base['t'])) if q in u.qs]
        for a,b in zip(seq,seq[1:]):
            i,u,t=a;j,v,tm=b
            if u.name not in ('RESET','RX') or v.name not in ('MX','MEASURE') or tm<=t+1:continue
            bit=int(re.search(r'c\[(\d+)\]',' '.join(v.lines))[1])
            if (u.name=='RX')!=(v.name=='MX') or not known_zero(base,bit):continue
            out.append(dict(index=i,qubit=q,old=t,new=tm-1,check_time=tm,bit=bit,basis=v.name,idles_removed=tm-t-1))
    return out
def apply(base,selected):
    c=C.clone(base)
    for r in selected:c['t'][r['index']]=r['new']
    order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));c['u']=[c['u'][i] for i in order];c['t']=[c['t'][i] for i in order];return c
if __name__=='__main__':
    base=C.read(H/'h_base');opts=options(base);rows=[];p=.001
    for r in opts:
        r['predicted_acceptance_ratio']=(1+(1-2*p)**2)/(1+(1-2*p)**2*(1-4*p/3)**r['idles_removed'])
    for mask in range(1,1<<len(opts)):
        selected=[r for i,r in enumerate(opts) if mask>>i&1];n=f'h_prep_{mask:02x}';r=save(apply(base,selected),n,['delay isolated preparation resets',selected]);r.update(family='prep_timing',selected=selected,predicted_ratio=__import__('math').prod(x['predicted_acceptance_ratio'] for x in selected));rows.append(r)
    (H/'v35_prep_options.json').write_text(json.dumps(opts,indent=2)+'\n');(H/'v35_prep_timing.json').write_text(json.dumps(rows,indent=2)+'\n');print(opts)
