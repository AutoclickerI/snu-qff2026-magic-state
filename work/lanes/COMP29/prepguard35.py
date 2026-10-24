"""Use otherwise isolated checked X preparations to herald neighbour idles."""
from core35 import *
def build_guard(base,opt,rtime,assignments):
    c=C.clone(base);q=opt['qubit'];i=next(i for i,u in enumerate(c['u']) if u.name=='RX' and u.qs==(q,) and c['t'][i]==opt['new']);c['t'][i]=rtime
    for t,d in assignments:
        if d is None:continue
        assert not any(tt==t and ({q,d}&set(u.qs)) for u,tt in zip(c['u'],c['t']))
        c['u'].append(C.Unit([f'cx q[{d}],q[{q}];']));c['t'].append(t)
    order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));c['u']=[c['u'][i] for i in order];c['t']=[c['t'][i] for i in order];return c
if __name__=='__main__':
    base=C.read(H/'h_star_111_joint_122_103');opts=json.loads((H/'v35_prep_options.json').read_text());rows=[];n=0
    for opt in opts:
        q=opt['qubit'];neighbours=[d for d in C.D if abs(q//6-d//6)+abs(q%6-d%6)==1]
        for rt in range(opt['old'],opt['new']):
            times=list(range(rt+1,opt['check_time']));choices=[]
            for t in times:
                choices.append([None]+[d for d in neighbours if not any(tt==t and d in u.qs for u,tt in zip(base['u'],base['t']))])
            for ds in itertools.product(*choices):
                if all(d is None for d in ds):continue
                assignments=list(zip(times,ds));name=f'h_pguard_{n:03d}';n+=1
                c=build_guard(base,opt,rt,assignments);r=save(c,name,['h_star_111_joint_122_103','preparation check used as idle flag',dict(helper=q,reset_time=rt,interactions=assignments,check_time=opt['check_time'],check_bit=opt['bit'])]);r.update(family='preparation_guard',helper=q,reset_time=rt,assignments=assignments);rows.append(r)
    (H/'v35_prep_guards.json').write_text(json.dumps(rows,indent=2)+'\n');print(dict(candidates=len(rows),helpers={q:sum(r['helper']==q for r in rows) for q in [1,4,6]}))
