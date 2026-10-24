"""Exact clean/dirty-bus identities and measured replacements in the BC resource."""
from evaluator import *
from build30 import S,native_times,bit
from contract30 import B,C
from moments_batch import evaluate
import re,copy,itertools

def certificates():
    rows=[]
    for k,l in [(1,1),(2,1),(1,2),(2,2)]:
        n=k+l;h=n;N=1<<n;errors=[]
        for m in [0,1]:
            K=np.zeros((N,N));U=np.zeros_like(K)
            for x in range(N):
                y=x
                for a,b in [(a,h) for a in range(k)]+[(h,b) for b in range(k,n)]:
                    if y>>a&1:y^=1<<b
                K[y&(N-1),x]=(-1)**(m*((y>>h)&1))/math.sqrt(2)
                z=x
                for a,b in itertools.product(range(k),range(k,n)):
                    if z>>a&1:z^=1<<b
                U[z,x]=(-1)**(m*(x&((1<<k)-1)).bit_count())/math.sqrt(2)
            errors.append(float(abs(K-U).max()));assert max(errors)<1e-14
        rows.append(dict(k=k,l=l,errors=errors))
    for d in [2,3,4]:
        edges=[(i,i+1) for i in range(d)]+[(i,i+1) for i in reversed(range(d-1))]+[(i,i+1) for i in range(1,d)]+[(i,i+1) for i in reversed(range(1,d-1))]
        for x in range(1<<(d+1)):
            y=x
            for a,b in edges:
                if y>>a&1:y^=1<<b
            assert y==x^(((x>>0)&1)<<d)
        rows.append(dict(dirty_distance=d,cx=len(edges),arbitrary_helper_states=True))
    (V/'bus.certificates.json').write_text(json.dumps(rows,indent=2));return rows

def run():
    certificates();stem=V/'inputs/v30f';md=json.loads(stem.with_suffix('.json').read_text());txt=stem.with_suffix('.qasm').read_text();head,raw,tail=S.qasm_ops(txt);us=S.fold_units(raw);ts=native_times(txt,us);R=md['R'];cells=set(B+C)
    # State rows are exact on the initialized R/H/CX preparation.
    rows={q:None for q in cells};before={};piv=md['prep']['pivots'];init={int(q):t for q,t in md['init_times'].items()}
    for i,(u,t) in enumerate(zip(us,ts)):
        before[i]=rows.copy()
        if len(u.qs)==1 and u.qs[0] in cells and t==init[u.qs[0]]:rows[u.qs[0]]=(1<<piv.index(u.qs[0])) if u.qs[0] in piv else 0
        elif u.name=='CX' and set(u.qs)<=cells:
            a,b=map(int,re.findall(r'q\[(\d+)\]',u.lines[0]));rows[b]=None if rows[a] is None or rows[b] is None else rows[a]^rows[b]
    candidates=[];seen=set()
    for i,u in enumerate(us):
        if u.name!='CX' or ts[i]>=R or not set(u.qs)<=cells:continue
        a,h=map(int,re.findall(r'q\[(\d+)\]',u.lines[0]))
        if before[i][h]!=0:continue
        # Candidate buses use only gates incident on h, with no interleaved use
        # of any endpoint inside the proposed instrument.
        incident=[j for j in range(i,len(us)) if h in us[j].qs and ts[j]<R]
        for k in range(1,4):
            for l in range(1,4):
                ids=incident[:2*k+l]
                if len(ids)!=2*k+l or any(us[j].name!='CX' for j in ids):continue
                edges=[tuple(map(int,re.findall(r'q\[(\d+)\]',us[j].lines[0]))) for j in ids]
                ctr=[a for a,b in edges[:k] if b==h];tgt=[b for a,b in edges[k:k+l] if a==h]
                if len(set(ctr))!=k or len(set(tgt))!=l or set(ctr)&set(tgt):continue
                if set(edges[k+l:])!={(a,h) for a in ctr}:continue
                footprint=set(ctr+tgt+[h]);touch=[j for j in range(ids[0],ids[-1]+1) if set(us[j].qs)&footprint]
                if touch!=ids:continue
                key=tuple(ids)
                if key in seen:continue
                seen.add(key);candidates.append(dict(ids=ids,helper=h,controls=ctr,targets=tgt,k=k,l=l))
    output=[];nb=int(re.search(r'creg c\[(\d+)\]',txt)[1])
    for ci,c in enumerate(candidates):
        end=c['ids'][-1];when=ts[end];h=c['helper'];later=[ts[j] for j in range(end+1,len(us)) if h in us[j].qs]
        if later and min(later)<=when+1:output.append(dict(candidate=c,status='RESET_SLOT_UNAVAILABLE'));continue
        removed=set(c['ids'][c['k']+c['l']:]);new=[];nt=[]
        for j,(u,t) in enumerate(zip(us,ts)):
            if j not in removed:new.append(u);nt.append(t)
        new.extend([S.Unit([f'h q[{h}];',f'measure q[{h}] -> c[{nb}];'],[]),S.Unit([f'reset q[{h}];'],[])]);nt.extend([when,when+1])
        z=set(c['controls']);flips=set()
        for j in range(end+1,len(us)):
            u=us[j]
            if u.name in ('RESET','RX'):z-=set(u.qs)
            elif u.name=='CX':
                a,b=map(int,re.findall(r'q\[(\d+)\]',u.lines[0]))
                if b in z:z.symmetric_difference_update([a])
            elif u.name=='MX' and u.qs[0] in z:flips.add(bit(u));z.remove(u.qs[0])
            elif u.name=='MEASURE':z-=set(u.qs)
            elif u.name not in ('H','MX') and set(u.qs)&z:raise AssertionError(('non-Clifford byproduct',u.lines))
        assert not z&set(md['data_qubits'])
        tail2=[]
        for line in tail:
            if line.startswith('// DETECTOR') and len(set(map(int,re.findall(r'c\[(\d+)\]',line)))&flips)%2:line+=f' c[{nb}]'
            tail2.append(line)
        head2=[re.sub(r'creg c\[\d+\]',f'creg c[{nb+1}]',line) for line in head];order=sorted(range(len(new)),key=lambda j:(nt[j],j));new=[new[j] for j in order];nt=[nt[j] for j in order];text=S.emit(head2,new,nt,tail2)
        tag=f'bus_measured_{ci:03d}';s=V/'finalists'/tag;meta=copy.deepcopy(md);meta.pop('prep',None);meta.pop('verification',None);meta.update(method='measured clean parity bus',bus=c,CX=md['CX']-c['k'],boundary_step=R+1)
        s.with_suffix('.qasm').write_text(text);s.with_suffix('.json').write_text(json.dumps(meta,indent=2))
        try:
            ev=exact2.Eval(text,md['data_qubits']);c1=float(ev.fp@ev.n_single);r=evaluate(ev) if abs(c1)<1e-12 else dict(c1=c1,invalid_cubic=True)
            r.update(tag=tag,bus=c);s.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));output.append(r)
        except (ValueError,AssertionError) as ex:output.append(dict(tag=tag,candidate=c,error=str(ex)))
    (V/'bus.portfolio.json').write_text(json.dumps(dict(found=len(candidates),rows=output),indent=2));print(json.dumps(dict(found=len(candidates),rows=output)),flush=True)

if __name__=='__main__':run()
