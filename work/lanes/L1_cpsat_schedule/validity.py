"""Symbolic CSS Pauli propagation through the scheduled Clifford circuit.

Require final data stabilizers/logicals to pull back to themselves up to prepared
ancilla stabilizers, and check readouts to pull back to their intended data check.
This is a nondemolition-cycle model, stronger than the supplied parity conditions.
Stim remains the oracle for accepted schedules.
"""
from common import *

def specifications(sc):
    data={k[1] for k in sc.keys if isinstance(k[1],tuple)}
    out=[]
    for B in 'XZ':
        for t,(_,ds) in enumerate(g2.TILES): out.append((B,f'data{t}',set(ds),set(ds)))
        out.append((B,'logical',data,data))
        for t,(m,ds) in enumerate(g2.TILES): out.append((B,t,None,set(ds)))
    return out

def check_numeric(a,o):
    from cpsat import Schedule
    # Only the static key/specification data are used; avoid constructing a CP model.
    class Static: pass
    sc=Static(); sc.keys=g2.Model(EXTRAS).keys
    m=g2.Model(EXTRAS); allq={q for k in m.keys for q in m.qubits_of(k,o)}
    bad=[]
    for B,name,start,target in specifications(sc):
        if start is None:
            ax,az=g2.g1.readers(name,o); start={ax if B=='X' else az}
            if B=='X': start|={q for t,q,_,_ in m.extras if t==name}
        vec=set(start)
        def cx(control,targ):
            source,dest=(control,targ) if B=='X' else (targ,control)
            if source in vec: vec.symmetric_difference_update({dest})
        for k in sorted(m.keys,key=a.__getitem__,reverse=True):
            t,d,typ=k
            if d=='U': control,targ=g2.g1.readers(t,o)
            elif d=='A': control,targ=m.qubits_of(k,o)
            elif typ=='X': control,targ=m.anc(t,d,typ),d
            else: control,targ=d,m.anc(t,d,typ)
            cx(control,targ)
        for mm,_ in g2.TILES: cx(mm,(mm[0]+1,mm[1]))
        data={k[1] for k in m.keys if isinstance(k[1],tuple)}
        permitted={mm for mm,_ in g2.TILES} if B=='X' else {(mm[0]+1,mm[1]) for mm,_ in g2.TILES}|{q for _,q,_,_ in m.extras}
        expected=[target]
        if B=='Z':
            expected=[]
            for mask in range(8):
                support=set(data) if name=='logical' else set()
                for t,(_,ds) in enumerate(g2.TILES):
                    if mask>>t&1: support.symmetric_difference_update(ds)
                expected.append(support)
        if vec&data not in expected or (vec-data)-permitted: bad.append((B,name,str(vec)))
    return bad

def install(sc):
    c=sc.model; m=sc.g; allq=sorted(sc.perq); data={k[1] for k in sc.keys if isinstance(k[1],tuple)}
    arcs={L:[] for L in range(2,sc.lmax+1)}
    def conjunction(bs,name):
        b=c.new_bool_var(name)
        c.add_bool_and(bs).only_enforce_if(b); c.add_bool_or([~x for x in bs]).only_enforce_if(~b)
        return b
    for L in arcs:
        for k in sc.keys:
            t,d,typ=k; on=sc.on[k,L]
            if d=='U':
                mm=g2.TILES[t][0]; nn=(mm[0]+1,mm[1])
                arcs[L].append((mm,nn,conjunction([on,~sc.o[t]],f'u{t}a{L}')))
                arcs[L].append((nn,mm,conjunction([on,sc.o[t]],f'u{t}b{L}')))
            else:
                if d=='A': control,targ=m.qubits_of(k,[0,0,0])
                elif typ=='X': control,targ=m.anc(t,d,typ),d
                else: control,targ=d,m.anc(t,d,typ)
                arcs[L].append((control,targ,on))
    for B,name,start,target in specifications(sc):
        label=f'{B}{name}'; vec={q:c.new_bool_var(f'{label}_end{q}') for q in allq}
        if start is None:
            mm=g2.TILES[name][0]; nn=(mm[0]+1,mm[1])
            extras={q for t,q,_,_ in m.extras if t==name and B=='X'}
            for q,b in vec.items():
                if q==mm: c.add(b==1-sc.o[name] if B=='X' else b==sc.o[name])
                elif q==nn: c.add(b==sc.o[name] if B=='X' else b==1-sc.o[name])
                else: c.add(b==int(q in extras))
        else:
            for q,b in vec.items(): c.add(b==int(q in start))
        for L in range(sc.lmax,1,-1):
            toggles={q:[] for q in allq}
            for control,targ,on in arcs[L]:
                source,dest=(control,targ) if B=='X' else (targ,control)
                toggles[dest].append(conjunction([on,vec[source]],f'{label}_{L}_{control}_{targ}'))
            prev={}
            for q in allq:
                if not toggles[q]: prev[q]=vec[q]; continue
                toggle=c.new_bool_var(f'{label}_{L}_toggle{q}'); c.add(toggle==sum(toggles[q]))
                prev[q]=c.new_bool_var(f'{label}_{L}_value{q}'); c.add_bool_xor([vec[q],toggle,~prev[q]])
            vec=prev
        # The fixed Bell preparation at layer1 also conjugates the observable.
        for mm,_ in g2.TILES:
            nn=(mm[0]+1,mm[1]); source,dest=(mm,nn) if B=='X' else (nn,mm)
            val=c.new_bool_var(f'{label}_bell{dest}'); c.add_bool_xor([vec[source],vec[dest],~val]); vec[dest]=val
        permitted={mm for mm,_ in g2.TILES} if B=='X' else {(mm[0]+1,mm[1]) for mm,_ in g2.TILES}|{q for _,q,_,_ in m.extras}
        if B=='Z':
            rows=[]
            for mask in range(8):
                support=set(data) if name=='logical' else set()
                for t,(_,ds) in enumerate(g2.TILES):
                    if mask>>t&1: support.symmetric_difference_update(ds)
                rows.append([int(q in support) for q in sorted(data)])
            c.add_allowed_assignments([vec[q] for q in sorted(data)],rows)
        for q,b in vec.items():
            if q in data:
                if B=='X': c.add(b==int(q in target))
            elif q not in permitted: c.add(b==0)
