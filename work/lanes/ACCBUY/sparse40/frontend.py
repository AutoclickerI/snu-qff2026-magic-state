"""Independent zero-frame circuit frontend for the checked v23/v29 family.
Integer Pauli propagation; official native-X folding and noise scheduling.
Basis/Engine are extracted from pinned repository EVAL code.
"""
from __future__ import annotations
import json, math, re
from dataclasses import dataclass
from types import SimpleNamespace
from collections import defaultdict
import numpy as np
from judge_subset.noise import noise_blocks, schedule
from judge_subset.qasm import _x_readouts, _x_preparations
SQ2=math.sqrt(2)
DATA=[]
SUPPORTS=({0,2,4,6},{1,2,5,6},{3,4,5,6})
@dataclass
class Op:
    kind: str
    qs: tuple
    time: int
    bit: int | None=None
    line: int=0
class Basis:
    """GF(2) span of the rotations' X parts; coordinates c <-> basis state b(c)."""

    def __init__(self):
        self.vecs = []
        self.piv = {}

    def express(self, x):
        combo = 0
        while x:
            h = x.bit_length() - 1
            if h not in self.piv:
                return None
            v, c = self.piv[h]
            x ^= v
            combo ^= c
        return combo

    def add(self, x):
        combo = 0
        orig = x
        while x:
            h = x.bit_length() - 1
            if h not in self.piv:
                idx = len(self.vecs)
                self.vecs.append(orig)
                self.piv[h] = (x, combo ^ (1 << idx))
                return 1 << idx
            v, c = self.piv[h]
            x ^= v
            combo ^= c
        return combo
class Engine:
    def __init__(self, model: Model):
        m = self.m = model
        B = self.B = Basis()
        for r in m.rots:
            B.add(r[0])
        self.rank_rot = len(B.vecs)
        # make sure every x-part we will touch lies in the span (exact, otherwise extend)
        for x, z, c in m.proj_m + [(q[0], q[1], q[2]) for q in m.Q.values()]:
            B.add(x)
        self.r = len(B.vecs)
        N = self.N = 1 << self.r
        self.idx = np.arange(N, dtype=np.uint64)
        self.rot = []
        for (x, z, coef, theta, _ins) in m.rots:
            self.rot.append((B.express(x), self._w(z), coef, theta))
        self.projs = [(B.express(x), self._w(z), c) for x, z, c in m.proj_m]
        self.sign_cache = {}
        self.Qs = {k: (B.express(v[0]), self._w(v[1]), v[2]) for k, v in m.Q.items()}
        # decode weights W[T][(a,b)]
        W = {"X": {}, "Y": {}}
        syn = np.arange(64)
        sx = (syn & 7) != 0
        sz = ((syn >> 3) & 7) != 0
        sgn = {"X": np.where(sx, -1.0, 1.0), "Y": np.where(sx ^ sz, -1.0, 1.0)}
        for T in "XY":
            for a in range(8):
                for b in range(8):
                    ch = np.array([(-1) ** (bin((s & 7) & a).count("1") + bin(((s >> 3) & 7) & b).count("1")) for s in range(64)])
                    W[T][(a, b)] = float((sgn[T] * ch).sum() / 64)
        self.keys = [k for k in m.Q if abs(W[k[0]][(k[1], k[2])]) > 1e-15]
        self.W = np.array([W[k[0]][(k[1], k[2])] for k in self.keys])
        self.beta = np.array([(1 / SQ2) * (-1) ** m.cz if k[0] == "X" else -(1 / SQ2) * (-1) ** m.cxz for k in self.keys])
        # sign table over e (10 bits): bit mask of each Q key
        # e bits: 0..5 stabs, 6 X7, 7 Z7, 8 parZ, 9 parXZ
        masks_ = []
        for (T, a, b) in self.keys:
            msk = a | (b << 3)
            if T == "X":
                msk |= (1 << 6) | (1 << 8)
            else:
                msk |= (1 << 6) | (1 << 7) | (1 << 9)
            masks_.append(msk)
        e = np.arange(1024)
        par = np.zeros((1024, len(self.keys)))
        for k, msk in enumerate(masks_):
            par[:, k] = 1 - 2 * (np.bitwise_count(e & msk).astype(np.int64) & 1)
        self.SG = par * (self.W * self.beta)[None, :]      # (1024, nq)
        # detector reference values: from the noiseless state
        self.v = list(m.proj_v)
        self._ref()

    def _w(self, z):
        w = 0
        for i, b in enumerate(self.B.vecs):
            w |= ((b & z).bit_count() & 1) << i
        return w

    def sgn(self, w):
        s = self.sign_cache.get(w)
        if s is None:
            s = 1.0 - 2.0 * (np.bitwise_count(self.idx & np.uint64(w)) & 1).astype(np.float64)
            self.sign_cache[w] = s
        return s

    def phi(self, s):
        a = np.zeros(self.N, dtype=complex)
        a[0] = 1.0
        for j, (mj, wj, coef, theta) in enumerate(self.rot):
            th = -theta if (s >> j) & 1 else theta
            sg = self.sgn(wj)
            sn = 1j * math.sin(th) * coef
            a = math.cos(th) * a + sn * (sg * a)[self.idx ^ np.uint64(mj)]
        return a

    def apply(self, a, pm):
        mj, wj, coef = pm
        return coef * (self.sgn(wj) * a)[self.idx ^ np.uint64(mj)]

    def expect(self, a, pm):
        mj, wj, coef = pm
        return float((np.conj(a[self.idx ^ np.uint64(mj)]) * coef * self.sgn(wj) * a).sum().real)

    def _ref(self):
        a = self.phi(0)
        # postselect conditions first
        for k in range(self.m.n_post):
            sg = (-1) ** self.v[k]
            a = (a + sg * self.apply(a, self.projs[k])) / 2
        A0 = float(np.vdot(a, a).real)
        for k in range(self.m.n_post, len(self.projs)):
            val = self.expect(a, self.projs[k]) / A0
            assert abs(abs(val) - 1) < 1e-9, f"detector {k} not deterministic: {val}"
            self.v[k] = 0 if val > 0 else 1
        self.A0 = A0
        self.v = np.array(self.v)

    def table(self, s, d):
        """(A/A0, E vector of <acc|Q|acc>/A0 over self.keys) for flipped rotations s and detector flips d,
        or None if the acceptance vanishes."""
        a = self.phi(s)
        for k, pm in enumerate(self.projs):
            sg = 1 - 2 * (int(self.v[k]) ^ ((d >> k) & 1))
            a = (a + sg * self.apply(a, pm)) / 2
            if k % 4 == 3 and float(np.vdot(a, a).real) < 1e-22:
                return None
        A = float(np.vdot(a, a).real)
        if A < 1e-18:
            return None
        E = np.array([self.expect(a, self.Qs[k]) for k in self.keys])
        return A / self.A0, E / self.A0

    def ntable(self, s, d):
        """(a, n over all 1024 e) : n = a - 0.5 * sum_q beta W sgn(e) E, in units of 1/A0."""
        t = self.table(s, d)
        if t is None:
            return 0.0, None
        A, E = t
        n = 0.5 * (A - self.SG @ E)
        return A, n
def mul(a,b):
    return (a[0]^b[0],a[1]^b[1],a[2]*b[2]*(-1)**((a[1]&b[0]).bit_count()))

def comm(a,b):return ((a[0]&b[1]).bit_count()+(a[1]&b[0]).bit_count())&1

def native_text(ops):
    lines=[];labels=[];lasttime=None
    for op in ops:
        name={'TDG':'T_DAG','ID':'I'}.get(op.kind,op.kind)
        line=name+' '+' '.join(map(str,op.qs))
        if op.time!=lasttime:
            line+=' # barrier '+' '.join(map(str,range(40)))
            lasttime=op.time
        lines.append(line);labels.append(op)
    return '\n'.join(lines),labels

def make_model(ops,dets):
    text,labels=native_text(ops)
    prog,blocks=noise_blocks(text,.001,first_order=True)
    _,steps,gaps=schedule(text)
    n=40+sum(len(ins.qubits) for ins in prog if ins.name in ('R','RX','M','MX'))
    xs=[(1<<i,0,1) for i in range(n)];zs=[(0,1<<i,1) for i in range(n)]
    wire=list(range(40));nxt=40;records={};rots=[];faults=[];chans=[]
    def cx(c,t):
        xs[c]=mul(xs[c],xs[t]);zs[t]=mul(zs[c],zs[t])
    def pull(P):
        x,z,coef=P;out=(0,0,coef)
        while x:
            bit=x&-x;x^=bit;out=mul(out,xs[bit.bit_length()-1])
        while z:
            bit=z&-z;z^=bit;out=mul(out,zs[bit.bit_length()-1])
        return out
    def physical(qs,pauli):
        x=z=0;co=1
        for q,P in zip(qs,pauli):
            if P in 'XY':x|=1<<wire[q]
            if P in 'YZ':z|=1<<wire[q]
            if P=='Y':co*=1j
        return x,z,co
    def channel(line,ii,jl):
        if '(' not in line:return
        head,rest=line.split(')',1);name,pr=head.split('(');pr=float(pr)
        qs=list(map(int,rest.split()));arity=2 if name=='DEPOLARIZE2' else 1
        comps={'X_ERROR':['X'],'Z_ERROR':['Z'],'DEPOLARIZE1':list('XYZ'),'DEPOLARIZE2':[a+b for a in 'IXYZ' for b in 'IXYZ' if a+b!='II']}[name]
        for k in range(0,len(qs),arity):
            grp=qs[k:k+arity];cid=len(chans)
            chans.append(dict(name=name,p=pr,qs=grp,ins=ii,jl=jl))
            for pauli in comps:
                x,z,co=pull(physical(grp,pauli))
                faults.append(dict(x=x,z=z,p=pr/len(comps),m=len(rots),chan=cid,pauli=pauli,qs=grp,ins=ii,jl=jl,label=f'{name} {pauli}@{grp} after/before native#{ii} srcL{labels[ii].line}'))
    for ii,(ins,block) in enumerate(zip(prog,blocks)):
        k=block.index(ins.text)
        for jl,line in enumerate(block[:k]):channel(line,ii,jl)
        name=ins.name;qs=ins.qubits
        if name in ('R','RX'):
            for q in qs:
                wire[q]=nxt;nxt+=1
                if name=='RX':xs[wire[q]],zs[wire[q]]=zs[wire[q]],xs[wire[q]]
        elif name in ('M','MX'):
            assert len(qs)==1
            q=qs[0];w=nxt;nxt+=1
            if name=='MX':xs[wire[q]],zs[wire[q]]=zs[wire[q]],xs[wire[q]]
            cx(wire[q],w)
            if name=='MX':xs[wire[q]],zs[wire[q]]=zs[wire[q]],xs[wire[q]]
            records[labels[ii].bit]=w
        elif name=='CX':cx(*[wire[q] for q in qs])
        elif name=='H':
            for q in qs:xs[wire[q]],zs[wire[q]]=zs[wire[q]],xs[wire[q]]
        elif name in ('T','T_DAG'):
            for q in qs:
                x,z,co=zs[wire[q]]
                rots.append((x,z,co,(-1 if name=='T' else 1)*math.pi/8,ii))
        elif name!='I':raise ValueError(name)
        for jl in range(k+1,len(block)):channel(block[jl],ii,jl)
    assert nxt==n
    def par(bits):
        z=0
        for bit in bits:z^=1<<records[bit]
        return 0,z,1
    proj=[pull(par(row)) for row in dets]
    gens=[physical([DATA[i] for i in sorted(S)],P*len(S)) for P in 'XZ' for S in SUPPORTS]
    X7=physical(DATA,'X'*7);Z7=physical(DATA,'Z'*7);Y7=physical(DATA,'Y'*7)
    sig=[pull(g) for g in gens]+[pull(X7),pull(Z7),(0,0,1),(0,0,1)]
    Q={}
    for T,L in [('X',X7),('Y',Y7)]:
        for a in range(8):
            for b in range(8):
                if T=='X' and b:continue
                ps=(0,0,1)
                for i,g in enumerate(gens):
                    if (a|(b<<3))>>i&1:ps=mul(ps,g)
                Q[T,a,b]=pull(mul(ps,L))
    record_ps={bit:pull((0,1<<w,1)) for bit,w in records.items()}
    # comm(F,P) is linear in F: column cx[w] (cz[w]) holds the targets anticommuting with X (Z) on wire w.
    targets=[r[:3] for r in rots]+proj+sig+list(record_ps.values())
    cx=[0]*n;cz=[0]*n
    for j,(x,z,_) in enumerate(targets):
        while z:b=z&-z;cx[b.bit_length()-1]|=1<<j;z^=b
        while x:b=x&-x;cz[b.bit_length()-1]|=1<<j;x^=b
    nr,nd,ne=len(rots),len(proj),len(sig);bits=list(record_ps)
    for f in faults:
        x,z,a=f['x'],f['z'],0
        while x:b=x&-x;a^=cx[b.bit_length()-1];x^=b
        while z:b=z&-z;a^=cz[b.bit_length()-1];z^=b
        f['s']=a&((1<<nr)-1)&~((1<<f['m'])-1)
        f['d']=(a>>nr)&((1<<nd)-1)
        f['e']=(a>>(nr+nd))&((1<<ne)-1)
        a>>=nr+nd+ne;f['record_flips']=[]
        while a:b=a&-a;f['record_flips'].append(bits[b.bit_length()-1]);a^=b
    model=SimpleNamespace(rots=rots,proj_m=proj,Q=Q,cz=0,cxz=0,proj_v=[None]*len(proj),n_post=0,faults=faults,chans=chans)
    model.gen_m=[pull(g) for g in gens];model.native=text;model.steps=steps;model.labels=labels;model.dets=dets
    model.record_ps=record_ps
    return model
def parse_current(src):
    ops=[];dets=[];time=0
    for li,raw in enumerate(src.splitlines(),1):
        if raw.startswith('barrier'):time+=1;continue
        if raw.startswith('// DETECTOR'):
            dets.append(set(map(int,re.findall(r'c\[(\d+)\]',raw))))
        if not raw or raw.startswith(('//','OPENQASM','include','qreg','creg')):continue
        qs=tuple(map(int,re.findall(r'q\[(\d+)\]',raw)))
        bits=list(map(int,re.findall(r'c\[(\d+)\]',raw)))
        kind={'reset':'R','measure':'M','tdg':'T_DAG'}.get(raw.split()[0],raw.split()[0].upper())
        ops.append(Op(kind,qs,time,bits[0] if bits else None,li))
    lines=[op.kind+' '+' '.join(map(str,op.qs)) for op in ops]
    _x_readouts(lines,drop_h=True);_x_preparations(lines)
    ans=[]
    for op,line in zip(ops,lines):
        if line is None:continue
        op.kind={'T_DAG':'TDG'}.get(line.split()[0],line.split()[0]);ans.append(op)
    return ans,dets
