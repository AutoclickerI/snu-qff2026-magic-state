"""Resource and measurement-endpoint CSS contracts, with independent X-fault audit."""
import os,sys,json,itertools,collections
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import ft,stim
import sat30 as S
B,C,ROWS=ft.B,ft.C,ft.ROWS

def span(vs):
    out={0}
    for v in vs:out|={a^v for a in list(out)}
    return out

def independent(vs):
    out=[];ss={0}
    for v in vs:
        if v not in ss:out.append(v);ss|={a^v for a in list(ss)}
    return out

def nullchecks(vs,n=7):return independent(v for v in range(1,1<<n) if all((v&w).bit_count()%2==0 for w in vs))
def rows(block):return [sum(1<<block[i] for i in r) for r in ROWS]
def xmap(ops,mask):
    for layer in ops:
        for a,b in layer:
            if mask>>a&1:mask^=1<<b
    return mask

def spec(family,value=0,helpers=()):
    bg,cg=rows(B),rows(C);cells=B+C+list(helpers);bell=family.startswith('bell')
    if family=='rank4':
        line=0
        for j,g in enumerate(cg):
            if value>>j&1:line^=g
        gs=[a^b for a,b in zip(bg,cg)]+[line];cspace=[sum(((line>>q)&1)<<i for i,q in enumerate(C))];stage='pre';allowed=[0]+list(range(9,16))
    elif family in ('policy','helper','helpermx'):
        gs=[a^b for a,b in zip(bg,cg)];cspace=[];stage='pre';allowed=[0]+([value] if family=='policy' and value else [])
    elif family=='c6':
        gs=[a^(b&~(1<<C[value])) for a,b in zip(bg,cg)];cspace=[];stage='pre';allowed=[0,9+value]
    elif bell:
        gs=bg+([] if family=='bell4' else cg)+[sum(1<<q for q in B+C)]
        cspace=([127] if family=='bell4' else [sum(1<<i for i in r) for r in ROWS]+[127]);stage='post';allowed=[0]+list(range(9,16))
    else:raise ValueError(family)
    check_masks=nullchecks(cspace)
    if family=='c6':check_masks=[1<<i for i in range(7) if i!=value]
    sig={}
    for q in cells:
        sb=ft.sig({q},B)
        if bell and q in C:sb^=8
        cc=sum(((q in {C[i] for i in range(7) if m>>i&1}) ^ (stage=='pre' and q in {B[i] for i in range(7) if m>>i&1}))<<(4+j) for j,m in enumerate(check_masks))
        sig[q]=sb|cc
    return dict(family=family,value=value,kind='c6' if family=='c6' else 'endpoint',endpoint_rank=len(gs),extra_check=True,stage=stage,generators=gs,signature_rows=sig,allowed=allowed,cspace=cspace,cells=cells,helpers=list(helpers),helper_x=False,bell=bell)

def checks(d):
    masks=([1<<i for i in range(7) if i!=d['value']] if d['family']=='c6' else nullchecks(d.get('cspace',[])))
    return [{C[i] for i in range(7) if m>>i&1} for m in masks]

def verify(d):
    gs=d['generators'];cells=d['cells'];measured=([C[d['value']]] if d['family']=='c6' else d.get('helpers',[])) if d.get('helper_x') else [];outs=[q for q in cells if q not in measured]
    xs=[xmap(d['ops'],1<<q)&sum(1<<q for q in outs) for q in d['pivots']]
    target=span(xs)==span(gs)
    # This is a complete CSS-state equality for this R/H/CX construction.
    circ=stim.Circuit()
    for q in cells:circ.append('R',[q])
    for q in d['pivots']:circ.append('H',[q])
    for layer in d['ops']:
        used=set()
        for a,b in layer:
            assert b in S.nb(a) and not ({a,b}&used);used|={a,b};circ.append('CX',[a,b])
    sim=stim.TableauSimulator();sim.do(circ)
    for q in measured:sim.postselect_x(q,desired_value=False)
    for g in gs:
        p=stim.PauliString(36)
        for q in cells:
            if g>>q&1:p[q]='X'
        target=target and sim.peek_observable_expectation(p)==1
    sig={int(q):v for q,v in d['signature_rows'].items()};bad=[];res=collections.Counter()
    for src in ft.sources(d,cells):
        err=ft.propagate(d['ops'],src);v=0
        for q in err:v^=sig[q]
        if v>>4==0:
            res[v&15]+=1
            if (v&15) not in d['allowed']:bad.append(src)
    return dict(stim_target_pass=bool(target),policy_pass=not bad,policy_faults=len(bad),residual_classes=dict(res),cx=sum(map(len,d['ops'])),depth=len(d['ops']))

def joint(d):
    if d['stage']=='post' or d['family']=='c6':return d
    d=json.loads(json.dumps(d));d['pre_verification']=verify(d);last=[list(e) for e in zip(B,C)]
    d['ops'].append(last);d['generators']=[xmap([last],g) for g in d['generators']]
    d['signature_rows']={q:ft.sig({q},B)|sum(int(q in zs)<<(4+j) for j,zs in enumerate(checks(d))) for q in d['cells']}
    d['allowed']=[0]+list(range(9,16));d['stage']='post';return d

class Model(S.Model):
    def __init__(self,D,cap,seed,contract,helper_x=False):
        contract={k:v for k,v in contract.items() if k not in ('ops','pivots','verification','pre_verification')};contract['signature_rows']={int(q):v for q,v in contract['signature_rows'].items()};self.contract=dict(contract,helper_x=helper_x);gs=contract['generators'];tar={q:sum(((g>>q)&1)<<j for j,g in enumerate(gs)) for q in contract['cells']}
        super().__init__(D,cap,seed,helpers=contract['helpers'],target_rows=tar,signature_rows=contract['signature_rows'],n_pivots=len(gs),free_target_x=([C[contract['value']]] if contract['family']=='c6' else contract['helpers']) if helper_x else [],helper_x=helper_x)
    def cut(self,source):
        if source in self.added:return
        self.added.add(source);t,qs=source;hs=list(self.h[t][qs[0]]);guard=[]
        if len(qs)==2:hs=[self.xor(a,b) for a,b in zip(hs,self.h[t][qs[1]])];guard=[-self.sel[t-1][qs]]
        for v in range(16):
            if v not in self.contract['allowed']:self.add(guard+hs[4:]+[-z if v>>i&1 else z for i,z in enumerate(hs[:4])])
    def candidate(self):return {**super().candidate(),**self.contract}
