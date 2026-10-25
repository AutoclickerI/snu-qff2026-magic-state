"""Rebuild protection on released cells, with the actual A and r3 retained.

Enumerate every idle known-state/data edge and every immediately earlier legal
preparation. Rank new slots by time/data exposure, evaluate up to twelve, then
re-price the joint accepted portfolio. All measurements are on saved circuits.
"""
import copy,json,sys,hashlib
from model import *
from completion import evolve,member
from ideal import check
from price import price,TAU

def menu(c,baseline=None):
    known=[(0,1<<q,0) for q in range(36)];out=[];ns=nodes(c)
    for t,seg in enumerate(c.segs):
        busy=c.qubits_at(t)
        if 29<=t<=44:
            for d in D:
                if d in busy:continue
                for h in range(36):
                    if h==d or h in busy or abs(h//6-d//6)+abs(h%6-d%6)!=1:continue
                    for basis in ('Z','X'):
                        if not member(known,(0,1<<h,0) if basis=='Z' else (1<<h,0,0)):continue
                        a,b=(h,d) if basis=='Z' else (d,h)
                        cc=copy.deepcopy(c);cc.segs[t].append([f'cx q[{a}],q[{b}];'])
                        if baseline is not None and t not in changed_times(c,baseline,h,d):continue
                        out.append((dict(t=t,h=h,d=d,basis=basis,kind='known',edge=[a,b]),cc))
        for o in [x for x in ns if x['t']==t]:known=evolve(known,o)
    # Advance a preparation into a newly vacated cell, then use its old tick.
    for o in ns:
        if o['kind'] not in ('R','RX') or not 29<=o['t']<=43:continue
        t=o['t'];h=o['qs'][0]
        if h in c.qubits_at(t-1):continue
        for d in D:
            if d in c.qubits_at(t) or d==h or abs(h//6-d//6)+abs(h%6-d%6)!=1:continue
            cc=copy.deepcopy(c);cc.segs[t].remove(o['lines']);cc.segs[t-1].append(o['lines'])
            a,b=(h,d) if o['kind']=='R' else (d,h)
            cc.segs[t].append([f'cx q[{a}],q[{b}];'])
            out.append((dict(t=t,h=h,d=d,basis='Z' if o['kind']=='R' else 'X',kind='advance_init',edge=[a,b],init=o['lines']),cc))
    return out

def changed_times(c,base,h,d):
    # Include the interval between each changed operation and its old position.
    aa=[(t,tuple(g)) for t,seg in enumerate(c.segs) for g in seg if set(classify(g)[1])&{h,d}]
    bb=[(t,tuple(g)) for t,seg in enumerate(base.segs) for g in seg if set(classify(g)[1])&{h,d}]
    diff=set(aa)^set(bb)
    if not diff:return set()
    ts=[t for t,g in diff];return set(range(min(ts),max(ts)+2))

def apply(c,s):
    t=s['t'];h=s['h'];a,b=s['edge']
    if s['kind']=='advance_init':
        if s['init'] not in c.segs[t] or h in c.qubits_at(t-1):return None
        c.segs[t].remove(s['init']);c.segs[t-1].append(s['init'])
    if {a,b}&c.qubits_at(t):return None
    c.segs[t].append([f'cx q[{a}],q[{b}];'])
    return c

def run(name,budget=10):
    p=HERE/'builds'/name;c=Circ(p.with_suffix('.qasm').read_text())
    baseline=Circ((HERE/'builds/v36h.qasm').read_text());rows=menu(c,baseline)
    # Later data exposure is more valuable; tie-break toward flag data 10/21.
    rows.sort(key=lambda z:-(z[0]['t']+(2 if z[0]['d'] in (10,21) else 0)))
    seen=set();retained=[]
    for spec,cc in rows:
        key=cc.text()
        if key in seen:continue
        seen.add(key);retained.append((spec,cc))
    (HERE/'inputs'/f'{name}_menu.json').write_text(json.dumps([s for s,c in retained],indent=2))
    ledger=json.loads((HERE/'results.json').read_text());fp=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest();base=ledger[fp]
    tested=[]
    for j,(spec,cc) in enumerate(retained[:budget]):
        stem=save(cc,f'{name}_g{j}',dict(family='downstream_guard',interface=name,slot=spec))
        z=price(stem,workers=2)
        if z:tested.append((z['loss']-base['loss'],j,spec,z))
    cur=c;best=base;accepted=[]
    for delta,j,spec,z in sorted(tested):
        if delta>=-1e-10:continue
        cc=apply(copy.deepcopy(cur),spec)
        if cc is None:continue
        if not accepted:trial=z;stem=HERE/'builds'/f'{name}_g{j}'
        else:
            stem=save(cc,f'{name}_join{len(accepted)+1}',dict(family='downstream_joint',interface=name,slots=accepted+[spec]));trial=price(stem,workers=2)
        if trial and trial['acceptance']>=.5002 and trial['loss']<best['loss']-1e-10:
            cur=cc;best=trial;accepted.append(spec)
            if best['loss']<TAU-3e-7:break
    final=save(cur,f'{name}_downstream',dict(family='complete_downstream',interface=name,slots=accepted))
    cert=check(final);assert cert['ok'],cert
    fp=hashlib.sha256(final.with_suffix('.qasm').read_bytes()).hexdigest()
    assert fp==best['sha256']
    result=dict(interface=name,base=base,best=best,final=str(final),ideal=cert,accepted=accepted,menu_count=len(retained),tested=len(tested))
    (HERE/'logs'/f'{name}_downstream.json').write_text(json.dumps(result,indent=2)+'\n')
    print('COMPLETE',json.dumps(result),flush=True)
    return result

if __name__=='__main__':
    for name in sys.argv[1:]:
        r=run(name)
        if r['best']['loss']<TAU-3e-7:break
