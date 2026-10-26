import itertools, json
import numpy as np

n=3; dim=8
def symp(a,b):
    return (((a&7)*(0)) + ((a&7)&(b>>3)).bit_count()+((a>>3)&(b&7)).bit_count())&1

def generated(gs):
    s={0}
    for g in gs:s|={x^g for x in list(s)}
    return s

def pmat(g):
    x=g&7;z=g>>3;M=np.zeros((8,8),complex)
    for b in range(8):M[b^x,b]=(1j)**((x&z).bit_count())*(-1)**((z&b).bit_count())
    return M
P={g:pmat(g) for g in range(64)}
groups={}
for gs in itertools.combinations(range(1,64),3):
    if any(symp(a,b) for a,b in itertools.combinations(gs,2)):continue
    span=generated(gs)
    if len(span)==8:groups.setdefault(tuple(sorted(span)),gs)
assert len(groups)==135

def is_css(span):
    return generated([g for g in span if not g&7 or not g>>3])==set(span)
def is_product(span):
    return generated([g for g in span if ((g&7)|(g>>3)).bit_count()==1])==set(span)
assert sum(is_css(s) for s in groups)==16
assert sum(is_product(s) for s in groups)==27

def pname(g):
    return ''.join('IXZY'[((g>>i)&1)+2*((g>>(i+3))&1)] for i in range(3))

# Actual square logical Clifford; D=0,A=1,B=2,C=3, least significant D.
perm=[]
for b in range(16):
    z=b
    for a,c in [(0,1),(2,3),(2,0),(3,1)]:z^=((z>>a)&1)<<c
    perm.append(z)
H=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
def hgate(st,q):
    out=st.copy()
    for b in range(16):
        if b>>q&1:continue
        a,bv=st[b],st[b|(1<<q)]
        out[b]=(a+bv)/np.sqrt(2);out[b|(1<<q)]=(a-bv)/np.sqrt(2)
    return out
ps=[np.eye(2),np.array([[0,1],[1,0]]),np.diag([1,-1]),np.array([[0,-1],[1,0]])]
tv=np.array([1,np.exp(1j*np.pi/4)])/np.sqrt(2)
targetproj=np.outer(tv,tv.conj())
def affine_solutions(vals):
    return [u for u in range(16) if all(v is None or (((u&1)^((u>>1)&m).bit_count())&1)==v for m,v in enumerate(vals))]

def kraus(resource,bases):
    K=np.zeros((8,2,2),complex)
    for d in range(2):
        st=np.zeros(16,complex)
        for r in range(8):st[perm[2*r+d]]=resource[r]
        for i,b in enumerate(bases,1):
            if b=='X':st=hgate(st,i)
        K[:,:,d]=st.reshape(8,2)
    return K

valid=[];tested=0
for span,gs in groups.items():
    for signs in itertools.product((1,-1),repeat=3):
        projector=np.eye(8,dtype=complex)
        for g,sgn in zip(gs,signs):projector=projector@(np.eye(8)+sgn*P[g])/2
        col=max(range(8),key=lambda i:np.linalg.norm(projector[:,i]))
        state=projector[:,col].copy();state/=np.linalg.norm(state)
        assert np.max(np.abs(np.outer(state,state.conj())-projector))<1e-12
        for bases in itertools.product('XZ',repeat=3):
            tested+=1;K=kraus(state,bases);vals=[];ok=True
            for m in range(8):
                v=K[m]@tv;prob=np.vdot(v,v).real
                if prob<1e-20:vals.append(None);continue
                fits=[p for p in range(4) if np.linalg.norm((np.eye(2)-targetproj)@ps[p]@v)<1e-10]
                if len(fits)!=1:ok=False;break
                vals.append(fits[0])
            if not ok:continue
            fx=affine_solutions([None if p is None else p&1 for p in vals])
            fz=affine_solutions([None if p is None else (p>>1)&1 for p in vals])
            if not fx or not fz:continue
            identity=True
            for m,k in enumerate(K):
                if vals[m] is None:continue
                k=ps[vals[m]]@k
                if np.linalg.norm(k-np.trace(k)*np.eye(2)/2)>1e-10:identity=False
            valid.append(dict(generators=[('+' if s==1 else '-')+pname(g) for g,s in zip(gs,signs)],
                readout=''.join(bases),css=is_css(span),product=is_product(span),genuine_tripartite=not any(((g&7)|(g>>3)).bit_count()==1 for g in span if g),identity=identity,fx=fx[0],fz=fz[0],
                branch_prob=[float(np.vdot(k@tv,k@tv).real) for k in K]))

fresh=[x for x in valid if not x['css'] and not x['product']]
full_rank_fresh=[x for x in fresh if x['readout'][0]=='Z' and x['readout'][1]=='X']
genuine_fresh=[x for x in full_rank_fresh if x['genuine_tripartite']]
product_valid=sum(x['product'] for x in valid)
assert product_valid==1072 # Reproduces reviewer15 / WHOLEEND's small control.
witness=genuine_fresh[0]
name_to_g={pname(g):g for g in range(64)}
projector=np.eye(8,dtype=complex)
for name in witness['generators']:
    projector=projector@(np.eye(8)+(1 if name[0]=='+' else -1)*P[name_to_g[name[1:]]])/2
col=max(range(8),key=lambda i:np.linalg.norm(projector[:,i]))
state=projector[:,col].copy();state/=np.linalg.norm(state)
K=kraus(state,witness['readout'])
W=np.array([[0,1-1j],[1+1j,0]])/np.sqrt(2)
errors=[];scales=[]
for m,k in enumerate(K):
    x=((witness['fx']&1)^((witness['fx']>>1)&m).bit_count())&1
    z=((witness['fz']&1)^((witness['fz']>>1)&m).bit_count())&1
    kc=ps[x+2*z]@k;c=np.trace(W.conj().T@kc)/2
    errors.append(float(np.max(np.abs(kc-c*W))));scales.append([float(c.real),float(c.imag)])
witness={**witness,'corrected_K_is_W':True,'max_abs_K_minus_scale_W':max(errors),'scales':scales,
    'frame_x':'1 xor m_C','frame_z':'1 xor m_A',
    'meaning':'A/B/C are 3 encoded logical qubits, not the 3 syndrome gauge qubits in reviewer15\u2019s 18-stabilizer physical contract.'}
assert max(errors)<1e-12
fault_response={}
for qi,block in enumerate('ABC'):
    for name,x,z in [('X',1,0),('Y',1,1),('Z',0,1)]:
        faulty=P[(x<<qi)|(z<<(qi+3))]@state
        fk=kraus(faulty,witness['readout']);loss=0;acceptance=0
        for m,k in enumerate(fk):
            xx=((witness['fx']&1)^((witness['fx']>>1)&m).bit_count())&1
            zz=((witness['fz']&1)^((witness['fz']>>1)&m).bit_count())&1
            v=ps[xx+2*zz]@k@tv;prob=float(np.vdot(v,v).real)
            acceptance+=prob;loss+=prob-abs(np.vdot(tv,v))**2
        fault_response[block+name]={'acceptance':acceptance,'loss':float(loss/acceptance)}
witness['logical_resource_fault_response']=fault_response
print(json.dumps(dict(unsigned_groups=len(groups),css_groups=sum(is_css(s) for s in groups),
    product_groups=sum(is_product(s) for s in groups),tested=tested,valid=len(valid),product_valid_control=product_valid,
    entangled_non_css_valid=len(fresh),entangled_non_css_identity=sum(x['identity'] for x in fresh),
    full_rank_incoming_entangled_non_css=len(full_rank_fresh),
    genuine_tripartite_full_rank_non_css=len(genuine_fresh),
    witness=witness,examples=genuine_fresh[:2]),indent=2))
