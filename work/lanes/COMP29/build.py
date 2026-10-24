from common import *
import itertools, math

def finish(c):
    order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i))
    c['u']=[c['u'][i] for i in order];c['t']=[c['t'][i] for i in order]
    pred,succ=C.S.build_dag(c['u'])
    assert all(c['t'][j]>c['t'][i] for j,ps in enumerate(pred) for i in ps),'wire collision'
    return C.normalize(c)

def replace_parity(c,target,control):
    for j,line in enumerate(c['tail']):
        if line.startswith('// DETECTOR'):
            bs=set(map(int,re.findall(r'c\[(\d+)\]',line)))
            if target in bs:bs^={control}
            c['tail'][j]='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bs))

def edit(c,kind):
    c=C.clone(c);us=c['u'];ts=c['t'];R=c['meta']['R']
    def add(lines,t):us.append(C.Unit(lines));ts.append(t)
    if kind=='copy4':
        i=max(i for i,u in enumerate(us) if u.lines==['cx q[19],q[25];'])
        t=ts[i];assert t>R
        del us[i];del ts[i]
        read={q:next(i for i,u in enumerate(us) if u.lines==[f'measure q[{q}] -> c[{b}];']) for q,b in [(19,23),(25,22),(29,26),(28,27)]}
        start=C.bit(c)
        replace_parity(c,22,23)
        for k,(q,h,b) in enumerate([(19,18,23),(25,31,22),(29,35,26),(28,34,27)]):
            assert not any(h in u.qs for u in us),'helper not fresh'
            ts[read[q]]=max(ts[read[q]],t+1)
            add([f'reset q[{h}];'],t-1)
            add([f'cx q[{q}],q[{h}];'],t)
            add([f'measure q[{h}] -> c[{start+k}];'],max(ts[read[q]],max(ts)))
            c['tail'].append(f'// DETECTOR c[{b}] c[{start+k}]')
    elif kind=='timing10':
        ids=[i for i,u in enumerate(us) if u.lines==['cx q[10],q[4];']]
        i=ids[1];assert ts[i]==12;ts[i]=10
    elif kind=='commute1':
        i=max(i for i,u in enumerate(us) if u.lines==['cx q[1],q[0];'] and ts[i]<R)
        j=max(i for i,u in enumerate(us) if u.lines==['cx q[1],q[7];'] and ts[i]<R)
        assert C.commute(us[i],us[j])
        assert all(C.commute(us[i],u) and C.commute(us[j],u) for u in us[i+1:j])
        ts[i],ts[j]=ts[j],ts[i]
    elif kind=='q19check':
        i=next(i for i,u in enumerate(us) if u.name=='RX' and u.qs==(19,))
        assert ts[i]==2;ts[i]=1;b=C.bit(c)
        add(['h q[19];',f'measure q[19] -> c[{b}];','h q[19];'],2)
        c['tail'].append(f'// DETECTOR c[{b}]')
    elif kind=='q11measure':
        i=next(i for i,u in enumerate(us) if u.name=='RESET' and u.qs==(11,))
        b=C.bit(c);us[i]=C.Unit([f'measure q[11] -> c[{b}];'])
        c['tail'].append(f'// DETECTOR c[{b}]')
    elif kind=='edge14to15':
        ids=[next(i for i,u in enumerate(us) if u.lines==[f'measure q[{q}] -> c[{b}];']) for q,b in [(14,15),(15,20)]]
        assert ts[ids[0]]==ts[ids[1]];t=ts[ids[0]]
        for i in ids:ts[i]=t+1
        add(['cx q[14],q[15];'],t);replace_parity(c,20,15)
    elif kind=='feedback':
        i=next(i for i,u in enumerate(us) if u.lines==['h q[9];','measure q[9] -> c[9];'])
        assert ts[i]==30;ts[i]=31
        ids=[i for i,u in enumerate(us) if u.lines==['cx q[9],q[15];']]
        i=ids[2];assert ts[i]==29;ts[i]=30
    elif kind in ('q5t37','q5t38'):
        t=int(kind[-2:]);b=C.bit(c)
        add([f'measure q[5] -> c[{b}];'],t)
        c['tail'].append(f'// DETECTOR c[{b}]')
    else:raise KeyError(kind)
    return finish(c)

def main():
    base=C.read(ROOT/'work/lanes/MAIN/v29c')
    kinds=['copy4','timing10','commute1','q19check','q11measure','edge14to15','feedback','q5t37','q5t38']
    manifest=[];errors=[];seen={}
    for n in range(len(kinds)+1):
        for ks in itertools.combinations(kinds,n):
            c=C.clone(base)
            try:
                for k in ks:c=edit(c,k)
                name='v29c' if not ks else 'c'+format(sum(1<<kinds.index(k) for k in ks),'03x')
                row=save(c,name,list(ks))
                if row['sha256'] in seen:row['duplicate_of']=seen[row['sha256']]
                else:seen[row['sha256']]=name
                manifest.append(row)
            except Exception as e:errors.append(dict(edits=ks,error=repr(e)))
    (H/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (H/'build_errors.json').write_text(json.dumps(errors,indent=2)+'\n')
    print(json.dumps(dict(candidates=len(manifest),unique=len(seen),errors=errors[:15])))
if __name__=='__main__':main()
