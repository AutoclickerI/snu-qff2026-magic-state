"""Guard removal profiles that also release B/C cells for earlier synthesis."""
from core35 import *
def generate():
    base=load(V/'inputs/fresh_timing');groups={6:(273,(6,0)),11:(276,(10,11)),5:(277,(4,5)),13:(275,(7,13)),19:(274,(20,19))};refs=[]
    for qs in [[6],[11],[5,11],[5,6,11,13,19]]:
        c=copy.deepcopy(base);drop=set();bits=set()
        for q in qs:
            b,e=groups[q];mi=next(i for i,u in enumerate(c['us']) if u.name in ('MEASURE','MX') and bit(u)==b);end=c['ts'][mi]
            gates=[i for i,u in enumerate(c['us']) if u.name=='CX' and edge(u)==e and c['ts'][i]<end][-2:];assert len(gates)==2
            begin=min(c['ts'][i] for i in gates);ri=max((i for i,u in enumerate(c['us']) if u.qs==(q,) and u.name in ('RESET','RX') and c['ts'][i]<begin),key=lambda i:c['ts'][i]);drop|={mi,ri,*gates};bits.add(b)
        c['us']=[u for i,u in enumerate(c['us']) if i not in drop];c['ts']=[t for i,t in enumerate(c['ts']) if i not in drop];c['tail']=[l for l in c['tail'] if not(set(map(int,re.findall(r'c\[(\d+)\]',l)))&bits)]
        name='flex_noguard_'+'_'.join(map(str,qs));emit(c,V/'inputs'/name,dict(source='FRESH timing',removed_guard_helpers=qs));refs.append(name)
    (V/'guard.references.json').write_text(json.dumps(refs,indent=2));print(json.dumps(refs))
if __name__=='__main__':generate()
