import copy,itertools,json,sys
from qedit import load,QRE,CRE
from borrow import HERE,save

def repair(stem,name,g6=False,checks=False,guard14=False,extended=False):
    c=load(str(stem));meta=json.loads(stem.with_suffix('.json').read_text());bit=c.max_creg()+1
    enc=json.loads(open(meta['global_change']['encoder']).read())
    # The B0 preparation now starts only at 42. Remove its unprotected lifetime left by rerouting D0/D2.
    g=['reset q[6];'];c.segs[31].remove(g);c.segs[39 if g6 else 41].append(g)
    if g6:
        for t in [40,41]:c.segs[t].append(['cx q[6],q[7];'])
    if checks:
        aa=meta['global_change']['roles']['A']
        for i,(kind,t) in enumerate(enc['init']):
            if kind!=2:continue
            q=aa[i]
            assert q not in c.qubits_at(t-1),(q,t)
            g=[f'reset q[{q}];',f'h q[{q}];'];c.segs[t].remove(g);c.segs[t-1].append(g)
            c.segs[t].append([f'h q[{q}];',f'measure q[{q}] -> c[{bit}];',f'h q[{q}];']);c.dets.append(f'// DETECTOR c[{bit}]');bit+=1
    if guard14:
        g=['reset q[14];'];loc=[(t,j) for t,ss in enumerate(c.segs) for j,gg in enumerate(ss) if gg==g and t>33]
        if loc:
            (t,j),=loc;c.segs[t].pop(j);c.segs[t-1].append(g);c.segs[t].append(['cx q[14],q[20];'])
    if extended:
        g=['reset q[1];','h q[1];'];c.segs[43].remove(g);c.segs[41].append(g);c.segs[42].append(['cx q[7],q[1];'])
    c.header=[f'creg c[{bit}];' if h.startswith('creg') else h for h in c.header]
    desc=dict(base=stem.name,family='R44 repairs',g6=g6,pivot_checks=checks,guard14=guard14,extended_helper=extended)
    out=save(c,name,desc);meta['global_change']=desc;out.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n');return out

if __name__=='__main__':
    for name,flags in [('late',(0,0,0,0)),('g6',(1,0,0,0)),('checks',(0,1,0,0)),('g6checks',(1,1,0,0)),('g6checksk',(1,1,1,0)),('g6checkske',(1,1,1,1))]:
        print(repair(HERE/'builds/r44_a0_h',f'r44_a0_{name}',*flags))
