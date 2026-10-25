"""Complete real-grid coherent output handoff with a one-tick longer round."""
import copy,json,re
from borrow import HERE,D,B,save
from qedit import load,QRE

base=load(str(HERE/'builds/v36h'))
for lateflag in [False,True]:
    c=copy.deepcopy(base)
    c.segs.insert(45,[])
    if lateflag:
        for d,a in [(10,9),(21,15)]:
            g=[f'cx q[{d}],q[{a}];'];c.segs[43].remove(g);c.segs[44].append(g)
        g=['cx q[9],q[15];'];c.segs[44].remove(g);c.segs[45].append(g)
    desc=dict(family='full coherent output handoff',extra_tick=45,late_flag=lateflag)
    save(c,'fullhand'+str(int(lateflag))+'_control',desc)
    for d,b in zip(D,B):c.segs[45].append([f'cx q[{d}],q[{b}];'])
    mapping=dict(zip(D,B))|dict(zip(B,D))
    for t in range(47,len(c.segs)):
        c.segs[t]=[[QRE.sub(lambda mt:f'q[{mapping.get(int(mt[1]),int(mt[1]))}]',ln) for ln in g] for g in c.segs[t]]
    stem=save(c,'fullhand'+str(int(lateflag)),desc)
    meta=json.loads(stem.with_suffix('.json').read_text());meta['data_qubits']=B
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
