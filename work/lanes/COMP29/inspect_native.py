from common import *
for stem in ['MAIN/v29c','ST1/combined_endpoint_instrument15_alap_feedback_best','LNS2/safe_best']:
    c=C.read(ROOT/'work/lanes'/stem)
    print(stem, {k:c['meta'].get(k) for k in ['data_qubits','R','cx','st1_feedback','options']})
    for i,(u,t) in enumerate(zip(c['u'],c['t'])):
        if (u.qs==(19,) and u.name in ('RX','MX')) or (u.qs==(11,) and u.name in ('RESET','MEASURE')) or u.lines in [['cx q[10],q[4];'],['cx q[1],q[0];'],['cx q[1],q[7];']] or t>=48:
            print(i,t,u.name,u.lines)
    if stem=='MAIN/v29c':
        print('prep',c['meta'].get('prep'))
        print('tail',c['tail'])
a=C.read(ROOT/'work/lanes/MAIN/v29c');b=C.read(ROOT/'work/lanes/ST1/combined_endpoint_instrument15_alap_feedback_best')
def keyed(c):
    seen={}; out={}
    for u,t in zip(c['u'],c['t']):
        key=tuple(u.lines);n=seen.get(key,0);seen[key]=n+1;out[key,n]=t
    return out
aa=keyed(a);bb=keyed(b)
print('feedback structural change',aa.keys()^bb.keys())
print('feedback times',[(k,aa[k],bb[k]) for k in aa.keys()&bb.keys() if aa[k]!=bb[k]])
