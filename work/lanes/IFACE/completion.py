"""Conservative stabilizer support and state-specific local CNOT completions.

At T gates retain only commuting stabilizers. Thus equivalence on the retained
subspace implies equivalence on the actual magic state; no T gate is discarded
from the saved candidate. Local synthesis uses a purification of every unknown
logical degree of freedom, rather than testing a single stabilizer input.
"""
import copy,itertools,json,random
import stim
from model import *

def mul(a,b,n=36):
    x,z,s=a;u,v,t=b
    # Hermitian Pauli signs, from i^(x.z) X^x Z^z.
    phase=((x&z).bit_count()+(u&v).bit_count()+2*(z&u).bit_count()-((x^u)&(z^v)).bit_count())%4
    assert phase%2==0
    return x^u,z^v,s^t^(phase//2)

def anti(a,b):return ((a[0]&b[1]).bit_count()+(a[1]&b[0]).bit_count())%2

def restrict(stabs,p):
    ids=[i for i,a in enumerate(stabs) if anti(a,p)]
    if not ids:return stabs[:]
    pivot=stabs[ids[0]]
    return [mul(a,pivot) if i in ids else a for i,a in enumerate(stabs) if i!=ids[0]]

def reduce_rows(stabs,mask=None):
    piv={};rest=[]
    for a in stabs:
        v=a[0]|a[1]<<36
        if mask is not None:v&=mask
        while v:
            k=v.bit_length()-1
            if k not in piv:piv[k]=a;break
            a=mul(a,piv[k]);v=a[0]|a[1]<<36
            if mask is not None:v&=mask
        if not v:rest.append(a)
    return piv,rest

def member(stabs,p):
    piv,_=reduce_rows(stabs);a=p;v=a[0]|a[1]<<36
    while v:
        k=v.bit_length()-1
        if k not in piv:return False
        a=mul(a,piv[k]);v=a[0]|a[1]<<36
    return a[2]==0

def cx_pauli(a,c,t):
    x,z,s=a
    s^=((x>>c)&1)*((z>>t)&1)*(((x>>t)^(z>>c)^1)&1)
    if x>>c&1:x^=1<<t
    if z>>t&1:z^=1<<c
    return x,z,s

def evolve(stabs,o):
    k=o['kind'];qs=o['qs'];q=qs[0]
    if k=='CX':return [cx_pauli(a,*qs) for a in stabs]
    if k in ('R','RX'):
        stabs=restrict(restrict(stabs,(1<<q,0,0)),(0,1<<q,0))
        p=(1<<q,0,0) if k=='RX' else (0,1<<q,0)
        return stabs+[p]
    if k in ('M','MX'):
        p=(1<<q,0,0) if k=='MX' else (0,1<<q,0)
        stabs=restrict(stabs,p)
        if not member(stabs,p):stabs.append(p)
        return stabs
    if k in ('T','TDG'):return restrict(stabs,(0,1<<q,0))
    raise ValueError(k)

def snapshots(c):
    stabs=[(0,1<<q,0) for q in range(36)];out={};ident=[]
    for o in nodes(c):
        out[o['id']]=stabs[:]
        if o['kind']=='CX' and (member(stabs,(0,1<<o['qs'][0],0)) or member(stabs,(1<<o['qs'][1],0,0))):ident.append(o)
        stabs=evolve(stabs,o)
    return out,ident

def local_stabs(stabs,qs):
    mask=sum(1<<q for q in qs);outside=((1<<36)-1)^mask
    _,local=reduce_rows(stabs,outside|(outside<<36))
    out=[]
    for x,z,s in local:
        if not (x|z):continue
        p=stim.PauliString(len(qs));p.sign=(-1)**s
        for i,q in enumerate(qs):p[i]= (2 if (x>>q&1) and (z>>q&1) else 1 if x>>q&1 else 3 if z>>q&1 else 0)
        out.append(p)
    return out

def canonical(stabs,n):
    # Full binary RREF including the sign column; commuting rows only.
    rows=list(stabs);j=0
    for bit in range(2*n-1,-1,-1):
        k=next((k for k in range(j,len(rows)) if ((rows[k][0]|rows[k][1]<<n)>>bit)&1),None)
        if k is None:continue
        rows[j],rows[k]=rows[k],rows[j]
        for k in range(len(rows)):
            if k!=j and ((rows[k][0]|rows[k][1]<<n)>>bit)&1:rows[k]=mul(rows[k],rows[j])
        j+=1
    return tuple(rows)

def choi(local,n):
    # Tableau encoding has the given stabilizers as its first Z outputs.
    if not local:local=[stim.PauliString(n)]
    enc=stim.Tableau.from_stabilizers(local,allow_underconstrained=True,allow_redundant=True)
    r=sum(any(p[i] for i in range(n)) for p in local);N=2*n-r
    sim=stim.TableauSimulator();sim.set_num_qubits(N)
    for j in range(r,n):sim.h(j);sim.cx(j,n+j-r)
    sim.do_tableau(enc,list(range(n)))
    rows=[]
    for p in sim.canonical_stabilizers():
        x=sum(1<<i for i in range(N) if p[i] in (1,2));z=sum(1<<i for i in range(N) if p[i] in (2,3));rows.append((x,z,int(p.sign.real<0)))
    return canonical(rows,N),N

def act(key,e,N):return canonical([cx_pauli(a,*e) for a in key],N)

def synth(qs,stabs,ops,maxhalf=3):
    start,N=choi(local_stabs(stabs,qs),len(qs));target=start
    old=[tuple(qs.index(q) for q in o['qs']) for o in ops]
    for e in old:target=act(target,e,N)
    edges=[(i,j) for i,a in enumerate(qs) for j,b in enumerate(qs) if abs(a//6-b//6)+abs(a%6-b%6)==1]
    if start==target:return [],dict(old=len(old),new=0,local_rank=2*len(qs)-N)
    fw={start:()};bw={target:()};front=[start];back=[target]
    for d in range(1,maxhalf+1):
        nf=[]
        for key in front:
            for e in edges:
                nxt=act(key,e,N)
                if nxt in fw:continue
                fw[nxt]=fw[key]+(e,);nf.append(nxt)
                if nxt in bw:
                    path=fw[nxt]+bw[nxt][::-1]
                    return [(qs[a],qs[b]) for a,b in path],dict(old=len(old),new=len(path),local_rank=2*len(qs)-N)
        front=nf;nb=[]
        for key in back:
            for e in edges:
                nxt=act(key,e,N)
                if nxt in bw:continue
                bw[nxt]=bw[key]+(e,);nb.append(nxt)
                if nxt in fw:
                    path=fw[nxt]+bw[nxt][::-1]
                    return [(qs[a],qs[b]) for a,b in path],dict(old=len(old),new=len(path),local_rank=2*len(qs)-N)
        back=nb
    return None,dict(old=len(old),states=len(fw)+len(bw))

if __name__=='__main__':
    c=Circ((HERE/'builds/v36h.qasm').read_text());ss,identity=snapshots(c)
    (HERE/'inputs/identity_cx.json').write_text(json.dumps(identity,indent=2))
    print('known-state identities',[(x['t'],x['qs']) for x in identity if 16<=x['t']<=39])
    # Enumerate closed, 4--6-cell Clifford windows. Operations touching a
    # component cannot escape it, and no non-CX instruction occurs inside.
    ns=nodes(c);seen=set();found=[]
    for width in range(2,7):
      for t0 in range(22,38-width+1):
        sub=[x for x in ns if t0<=x['t']<t0+width];comps=[{q} for q in range(36)]
        for x in sub:
          if x['kind']=='CX':
            c1=next(z for z in comps if x['qs'][0] in z);c2=next(z for z in comps if x['qs'][1] in z)
            if c1 is not c2:c1.update(c2);comps.remove(c2)
        for cells in comps:
          if not 4<=len(cells)<=6:continue
          ops=[x for x in sub if set(x['qs'])&cells]
          if any(x['kind']!='CX' for x in ops):continue
          ids=tuple(x['id'] for x in ops)
          if ids in seen:continue
          seen.add(ids);qs=sorted(cells)
          path,info=synth(qs,ss[ops[0]['id']],ops,maxhalf=min(2,len(ops)//2))
          print(t0,width,qs,info,flush=True)
          if path is not None and len(path)<len(ops):found.append(dict(t0=t0,width=width,cells=qs,ids=ids,path=path,**info))
    (HERE/'inputs/completions.json').write_text(json.dumps(found,indent=2)+'\n')
    print('shorter completions',len(found),flush=True)
