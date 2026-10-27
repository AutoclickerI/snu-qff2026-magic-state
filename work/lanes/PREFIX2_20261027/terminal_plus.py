"""Resynthesize the final Z-syndrome extraction from its parity contract.

The target ancilla is |+_L>: uniform over the [7,4,3] Hamming code.
Three pure Z-record parities replace the old partial encoder/decoder's mixed
resource record contract. Native CNOT synthesis chooses the product input basis
freely, forbids propagated logical-Z singleton and CNOT-pair hooks, and validates
the complete circuit with the independently implemented raw-state checker.
"""
import os,sys,json,random,copy,itertools
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'T14'));sys.path.insert(0,str(H.parent/'PREFIX20261027'))
from qcirc import parse,emit,adjacent
from qtools import write_stem,price
from qtools.validity import raw_check
from search_phase import singles
A=[1,14,8,9,2,16,15];D=[0,20,7,10,3,22,21]
EDGES=[(a,b) for a in range(7) for b in range(7) if adjacent(A[a],A[b])]
SUP=[{0,2,4,6},{1,2,5,6},{3,4,5,6}]

def search(seed=0,width=900,depth=18):
    rng=random.Random(seed);start=tuple(range(9,16));beam=[(start,[],0.)];seen={start:0};solutions=[]
    for dep in range(1,depth+1):
        nxt={}
        for rows,path,cost in beam:
            for a,b in EDGES:
                if not rows[a] or path and path[-1]==(a,b):continue
                if rows[a]^rows[b]==8:continue
                new=list(rows);new[b]^=new[a];new=tuple(new)
                if 8 in new:continue
                if seen.get(new,999)<dep:continue
                nz=sum(x!=0 for x in new)
                unsafe=sum(x!=0 and x<8 for x in new)
                nc=cost+.04*unsafe
                pp=path+[(a,b)]
                if nz==4:
                    solutions.append(dict(rows=new,path=pp,cost=nc,seed=seed))
                    continue
                score=2.1*nz+.15*sum(x.bit_count() for x in new)+nc+rng.random()*.1
                if new not in nxt or score<nxt[new][0]:nxt[new]=(score,new,pp,nc)
        beam=[(r,p,c) for score,r,p,c in sorted(nxt.values())[:width]]
        for rows,path,cost in beam:seen[rows]=dep
        print('beam',seed,dep,'states',len(beam),'solutions',len(solutions),flush=True)
        if solutions and dep>=min(len(s['path']) for s in solutions)+2:break
    unique={tuple(s['path']):s for s in solutions}
    return sorted(unique.values(),key=lambda s:(len(s['path'])+.5*s['cost'],s['cost']))[:20]

def build(base,rec,name,mode='asap',herald=True):
    base=Path(base);units,dets=parse(base.with_suffix('.qasm').read_text())
    assert json.loads(base.with_suffix('.json').read_text())['data_qubits']==D
    bit=max(u['b'] for u in units if u['b'] is not None)+1
    removed=[];kept=[]
    for u in units:
        if u['t']>=20 and set(u['q'])&set(A) and not(u['t']==20 and u['k']=='M' and u['b']>=500):
            assert set(u['q'])<=set(A+D) or u['q']==(17,16),u
            removed.append(u)
        else:kept.append(u)
    gone={u['b'] for u in removed if u['b'] is not None}
    dets=[d for d in dets if not set(d)&gone]
    if herald:
        read={u['q'][0] for u in kept if u['t']==20 and u['k']=='M' and u['q'][0] in A}
        for q in A:
            if q not in read:
                kept.append(dict(k='M',q=(q,),t=20,b=bit));dets.append([bit]);bit+=1
    # Earliest product input is tick21 after the existing source-zero heralds.
    last={q:21 for q in A};gates=[]
    for a,b in reversed(rec['path']):
        a,b=A[a],A[b];t=max(last[a],last[b])+1
        gates.append(dict(k='CX',q=(a,b),t=t,b=None));last[a]=last[b]=t
    init={q:min([u['t'] for u in gates if q in u['q']]+[22])-1 for q in A}
    for i,q in enumerate(A):kept.append(dict(k='RX' if rec['rows'][i] else 'R',q=(q,),t=init[q],b=None))
    # Shift the independent B/C preparation and readout only if the new A
    # preparation needs a later data interaction. Source/transfer times stay.
    delta=max(0,max(last.values())+1-28)
    if delta:
        for u in kept:
            source=(u['t']<16 or u['b'] in (500,501) or
                    17<=u['t']<=19 and set(u['q'])<=set(A+D) or
                    set(u['q'])<=set(A))
            if not source:u['t']+=delta
    kept+=gates;readbits=[]
    joint=max(last.values())+1
    for a,d in zip(A,D):
        t=last[a]+1 if mode=='asap' else joint
        # The B->D operation at29 is the independent final X syndrome check.
        assert t<29+delta,(mode,t,rec)
        kept.append(dict(k='CX',q=(d,a),t=t,b=None))
        kept.append(dict(k='M',q=(a,),t=t+1,b=bit));readbits.append(bit);bit+=1
    dets += [[readbits[i] for i in sorted(s)] for s in SUP]
    text=emit(kept,dets)
    return write_stem(text,D,H/'cand',name,source=dict(parent=str(base),encoder=rec,mode=mode,herald=herald,tail_shift=delta))

def main():
    base=Path(sys.argv[1]);nets=[]
    if (H/'terminal_plus_networks.json').exists():nets=json.loads((H/'terminal_plus_networks.json').read_text())
    else:
        for seed in range(3):nets+=search(seed)
    (H/'terminal_plus_networks.json').write_text(json.dumps(nets,indent=2)+'\n')
    ans=[];best=1
    for i,rec in enumerate(nets):
        for mode in ['asap','parallel']:
            try:
                st=build(base,rec,f'terminal_plus_{i:03d}_{mode}',mode)
                raw=raw_check(st.with_suffix('.qasm').read_text(),D)
                row=dict(stem=str(st),source_cx=len(rec['path']),raw=raw)
                if raw['ok']:
                    c1,n=singles(st);row.update(c1=c1,harmful=n)
                    if c1<1e-5:
                        pr=price(st,1);row.update(loss=pr['loss'],acceptance=pr['acceptance'])
                        if pr['acceptance']>=.5002 and pr['loss']<best:
                            best=pr['loss'];(H/'terminal_plus_best.json').write_text(json.dumps(row,indent=2)+'\n')
                print(json.dumps(row),flush=True);ans.append(row)
            except Exception as ex:
                print('ERROR',i,mode,repr(ex),flush=True);ans.append(dict(i=i,mode=mode,error=repr(ex)))
            (H/'terminal_plus_results.json').write_text(json.dumps(ans,indent=2)+'\n')

if __name__=='__main__':main()
