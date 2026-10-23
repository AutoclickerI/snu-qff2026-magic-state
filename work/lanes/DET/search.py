"""Detector-space search using exact2's Pauli fault signatures and Engine.

Build the complete joint detector-syndrome distribution through fault weight two.
Every subspace is then a linear filter on these sufficient statistics; there is
no circuit reparse and no Clifford replacement of the T gates.
"""
from analyze import *
import copy, itertools, collections
import numpy as np
from engine import Engine
from model import comm

def rebind(ev, records):
    out = copy.copy(ev)
    m = out.m = copy.copy(ev.m)
    assert m.n_post == 0
    m.proj_ps = [m.par(bits(d)) for d in records]
    m.proj_m = [m.pull(ps) for ps in m.proj_ps]
    m.proj_v = [None] * len(records)
    m.n_det = len(records)
    m.faults = [dict(f, d=sum(comm(f['x'],f['z'],v[0],v[1]) << j
                             for j,v in enumerate(m.proj_m))) for f in ev.m.faults]
    out.e = Engine(m)
    out.fd = [f['d'] for f in m.faults]
    groups = collections.defaultdict(list)
    for i,f in enumerate(m.faults):
        groups[(f['s'],f['d'])].append(i)
    out.gkeys = list(groups)
    out.gmem = [np.array(groups[k]) for k in out.gkeys]
    out.ga = np.zeros(len(groups))
    out.n_single = np.zeros(out.n_f)
    out.a_single = np.zeros(out.n_f)
    for g,(s,d) in enumerate(out.gkeys):
        a,n = out.e.ntable(s,d)
        out.ga[g] = a
        out.a_single[out.gmem[g]] = a
        if n is not None:
            out.n_single[out.gmem[g]] = n[out.fe[out.gmem[g]]]
    return out

def make_hist(ev, path):
    eng = ev.e
    assert all(x == 0 for x,z,c in eng.projs), 'requires diagonal record projectors'
    # Each computational basis state belongs to one joint detector eigenspace.
    sector = np.zeros(eng.N, dtype=np.int64)
    for j,pm in enumerate(eng.projs):
        x,z,c = pm
        sector |= (((c.real * eng.sgn(z)) < 0).astype(np.int64) ^ int(eng.v[j])) << j
    sectors = np.unique(sector)
    svals = sorted({a ^ b for a in set(ev.fs)|{0} for b in set(ev.fs)|{0}})
    si = {s:i for i,s in enumerate(svals)}
    A = np.zeros((len(svals),len(sectors)))
    N = np.zeros((len(svals),len(sectors),1024))
    for i,s in enumerate(svals):
        phi = eng.phi(s)
        for j,d in enumerate(sectors):
            a = phi * (sector == d)
            A[i,j] = np.vdot(a,a).real / eng.A0
            if A[i,j] < 1e-18:
                continue
            E = np.array([eng.expect(a,eng.Qs[k]) for k in eng.keys]) / eng.A0
            N[i,j] = 0.5 * (A[i,j] - eng.SG @ E)
    print('TABLE',path.name, 's',len(svals),'sectors',sectors.tolist(),flush=True)
    # Hist columns: single probability, single loss, single loss * other-channel
    # probability, unordered distinct-channel pair probability and pair loss.
    hist = collections.defaultdict(lambda: np.zeros(5))
    sf = np.array([si[s] for s in ev.fs]); fd=np.array(ev.fd,dtype=np.int64)
    Pch=np.bincount(ev.fch,weights=ev.fp); Ptotal=float(ev.fp.sum())
    def add(ds, vals, col):
        u,ix=np.unique(ds,return_inverse=True)
        summed=np.bincount(ix,weights=vals)
        for d,v in zip(u,summed):
            if abs(v)>1e-25:
                hist[int(d)][col]+=v
    for j,ds in enumerate(sectors):
        n=N[sf,j,ev.fe]; a=A[sf,j]; det=fd^ds
        add(det,ev.fp*a,0)
        add(det,ev.fp*n,1)
        add(det,ev.fp*n*(Ptotal-Pch[ev.fch]),2)
    # Batched pair rows, excluding mutually exclusive alternatives of a channel.
    sf_lookup=np.full(max(svals)+1,-1,dtype=np.int64)
    sf_lookup[svals]=np.arange(len(svals))
    fs=np.array(ev.fs,dtype=np.int64)
    for lo in range(0,ev.n_f,64):
        ia=np.arange(lo,min(lo+64,ev.n_f))[:,None]
        ib=np.arange(ev.n_f)[None,:]
        live=(ia<ib)&(ev.fch[ia]!=ev.fch[ib])
        ii,jj=np.nonzero(live); ii+=lo
        ss=sf_lookup[fs[ii]^fs[jj]]; dd=fd[ii]^fd[jj]; ee=ev.fe[ii]^ev.fe[jj]
        pp=ev.fp[ii]*ev.fp[jj]
        for j,ds in enumerate(sectors):
            add(dd^ds,pp*A[ss,j],3)
            add(dd^ds,pp*N[ss,j,ee],4)
    ds=np.array(sorted(hist),dtype=np.int64)
    h=np.array([hist[int(d)] for d in ds])
    np.savez_compressed(path,ds=ds,h=h,Ptotal=Ptotal)
    print('HIST',len(ds),'baseline',h[ds==0].tolist(),flush=True)
    return ds,h,Ptotal

def xor_span(vectors):
    out=[0]
    for v in vectors:
        if v not in out:
            out += [x^v for x in out]
    return tuple(sorted(out))

def annihilator(vectors,dim):
    # Nullspace of vectors, returned as rows in full-detector coordinates.
    rows={}
    for v in vectors:
        for p,r in sorted(rows.items(),reverse=True):
            if v>>p&1:
                v^=r
        if v:
            rows[v.bit_length()-1]=v
    ans=[]
    for j in range(dim):
        if j in rows:
            continue
        v=1<<j
        for p,r in sorted(rows.items()):
            if (r&v).bit_count()&1:
                v^=1<<p
        ans.append(v)
    assert all(not ((r&v).bit_count()&1) for r in ans for v in vectors)
    return ans

def records_for(kernel, full):
    out=[]
    for row in annihilator(kernel,len(full)):
        d=0
        for j in bits(row):
            d^=full[j]
        out.append(d)
    return out

def qasm_for(text,records,space):
    body='\n'.join(s for s in text.splitlines() if not re.match(r'\s*//\s*DETECTOR\b',s))+'\n'
    return body+''.join('// DETECTOR '+' '.join(f'c[{space["record_clbits"][j]}]' for j in bits(d))+'\n' for d in records)

def search(name):
    stem=TARGETS[name]; text=stem.with_suffix('.qasm').read_text()
    data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    space=json.loads((HERE/f'{name}_space.json').read_text())
    full=space['full_records']; dim=len(full)
    ev=rebind(Eval(text,data),full)
    hp=HERE/f'{name}_hist.npz'
    if hp.exists():
        z=np.load(hp); ds,h,Ptotal=z['ds'],z['h'],float(z['Ptotal'])
    else:
        ds,h,Ptotal=make_hist(ev,hp)
    lookup={int(d):i for i,d in enumerate(ds)}
    def score(kernel):
        span=xor_span(kernel)
        vals=h[[lookup[d] for d in span if d in lookup]].sum(axis=0)
        a1=Ptotal-vals[0]; n1=vals[1]
        loss2=vals[4]-vals[2]+a1*n1
        return dict(kernel=list(kernel),rank=dim-(len(span).bit_length()-1),loss1=n1,
                    loss2=loss2,loss=n1+loss2,A1=a1,exp_acc=math.exp(-a1),
                    pair_acceptance=vals[3])
    base=score([])
    baseline=json.loads((HERE/f'{name}_baseline.json').read_text())
    assert abs(base['loss2']-baseline['loss2'])<1e-14,(base,baseline)
    assert abs(base['A1']-baseline['A1'])<1e-13,(base,baseline)
    print(name,'BASE MATCH',base,flush=True)
    seen={}; singles=[]; examined=collections.Counter()
    def consider(vectors,kind):
        key=xor_span(vectors)
        examined[kind]+=1
        if key in seen:
            return seen[key]
        r=score(vectors);r['kind']=kind
        # Preserve only FT states for further search, all single drops separately.
        if abs(r['loss1'])<1e-14:
            seen[key]=r
        return r
    consider([],'base')
    for i in range(dim):
        r=consider([1<<i],'single_drop');r['drop_generator']=i
        singles.append(r)
    # Exhaust all coordinate drops up to four generators.
    for k in (2,3,4):
        for ids in itertools.combinations(range(dim),k):
            consider([1<<i for i in ids],f'drop_{k}')
            consider([sum(1<<i for i in ids)],f'small_rank1_{k}')
    # All codimension-one relaxations that affect singles or pairs (all weights).
    # Any unlisted syndrome has zero gain and loss through second order.
    for d in ds:
        if d:
            consider([int(d)],'syndrome_hyperplane')
    for k in (2,3,4):
        # Every subspace supported on <=4 removed coordinates. Generate from its
        # nonzero vectors; canonical spans eliminate repeats across supports.
        for ids in itertools.combinations(range(dim),k):
            vs=xor_span([1<<i for i in ids])[1:]
            # The codimension-one case is above; enumerate 2D kernels here.
            for i,a in enumerate(vs):
                for b in vs[i+1:]:
                    if a<b<(a^b):
                        consider([a,b],f'small_subspace_{k}')
    # The remaining subspaces supported on four coordinates: 3D kernels.
    # Their annihilator in that 4D space is one nonzero parity.
    for ids in itertools.combinations(range(dim),4):
        for parity in range(1,16):
            local=annihilator([parity],4)
            kernel=[sum(1<<ids[j] for j in bits(v)) for v in local]
            consider(kernel,'small_subspace_rank3_4')
    ft=list(seen.values())
    baseA=base['A1']
    # Finite-p screening: exact loss2 times leading acceptance-normalization gain.
    # Only a ranking proxy; final candidates use exact2 third order and judge MC.
    def proxy(r):
        return r['loss2']*math.exp(r['A1']-baseA)
    seeds=sorted(ft,key=proxy)[:40]
    vectors=sorted({v for r in sorted(ft,key=proxy)[:100] for v in r['kernel']})
    for seed in seeds:
        cur=seed
        for step in range(dim):
            opts=[consider(cur['kernel']+[v],'greedy') for v in vectors if v not in xor_span(cur['kernel'])]
            opts=[r for r in opts if abs(r['loss1'])<1e-14]
            if not opts:
                break
            best=min(opts,key=proxy)
            if proxy(best)>=proxy(cur)-1e-15:
                break
            cur=best
    ft=list(seen.values())
    # Exact second-order loss versus exp(-A1) Pareto set.
    front=[];bestacc=-1
    for r in sorted(ft,key=lambda r:(round(r['loss2'],16),-r['exp_acc'])):
        if r['exp_acc']>bestacc+1e-12:
            front.append(r);bestacc=r['exp_acc']
    best=sorted(ft,key=proxy)[:30]
    out=dict(base=base,single_drops=singles,pareto=front,best_proxy=best,
             counts=dict(examined),unique_ft=len(ft),hist_syndromes=len(ds),
             full_records=full)
    (HERE/f'{name}_search.json').write_text(json.dumps(out,indent=2))
    print(name,'SEARCH',json.dumps({k:v for k,v in out.items() if k not in ('single_drops','best_proxy','full_records')}),flush=True)
    print(name,'BEST',json.dumps(best[:10]),flush=True)

if __name__=='__main__':
    for name in sys.argv[1:] or TARGETS:
        search(name)
