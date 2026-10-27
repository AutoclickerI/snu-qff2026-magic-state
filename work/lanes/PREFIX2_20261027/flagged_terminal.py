"""Joint native ancilla encoding, short decoding, and complete record contract.

After the data-to-ancilla transversal, a short native decoder isolates selected
|+> factors. Those qubits are read in X and herald ancilla phase faults. The
remaining Z readouts enforce a basis of all three Hamming parity checks.
"""
import os,sys,json,itertools
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import terminal_plus as tp
from terminal_layers import flags
from qcirc import parse,emit
from qtools import write_stem,price
from qtools.validity import raw_check
from search_phase import singles
H=Path(__file__).resolve().parent;A=tp.A;D=tp.D

def build(base,encoder,decoder,name,mode='asap',herald=True):
    base=Path(base);units,dets=parse(base.with_suffix('.qasm').read_text())
    assert json.loads(base.with_suffix('.json').read_text())['data_qubits']==D
    bit=max(u['b'] for u in units if u['b'] is not None)+1
    kept=[];removed=[]
    for u in units:
        old_herald=u['t']==20 and u['k']=='M' and u['b']>=500 and u['q'][0] in A
        if u['t']>=20 and set(u['q'])&set(A) and not(herald and old_herald):removed.append(u)
        else:kept.append(u)
    gone={u['b'] for u in removed if u['b'] is not None};dets=[d for d in dets if not set(d)&gone]
    if herald:
        read={u['q'][0] for u in kept if u['t']==20 and u['k']=='M' and u['q'][0] in A}
        for q in A:
            if q not in read:kept.append(dict(k='M',q=(q,),t=20,b=bit));dets.append([bit]);bit+=1
    start=21 if herald else 20
    last={q:start for q in A};added=[];prep=[]
    for a,b in reversed(encoder['path']):
        a,b=A[a],A[b];t=max(last[a],last[b])+1
        prep.append(dict(k='CX',q=(a,b),t=t,b=None));last[a]=last[b]=t
    for i,q in enumerate(A):
        t=min([u['t'] for u in prep if q in u['q']]+[start+1])-1
        added.append(dict(k='RX' if encoder['rows'][i] else 'R',q=(q,),t=t,b=None))
    added+=prep;joint=max(last.values())+1
    for a,d in zip(A,D):
        t=last[a]+1 if mode=='asap' else joint
        added.append(dict(k='CX',q=(d,a),t=t,b=None));last[a]=t
    last_data_cx=max(last.values())
    rows=list(range(9,16))
    for a,b in decoder['path']:
        rows[b]^=rows[a];aa,bb=A[a],A[b];t=max(last[aa],last[bb])+1
        added.append(dict(k='CX',q=(aa,bb),t=t,b=None));last[aa]=last[bb]=t
    fs=flags(rows);assert fs==decoder['flags'],(fs,decoder)
    reads=[]
    for i,q in enumerate(A):
        added.append(dict(k='MX' if i in fs else 'M',q=(q,),t=last[q]+1,b=bit));reads.append(bit)
        if i in fs:dets.append([bit])
        bit+=1
    # Complete independent deterministic Z-record parity space.
    piv={};zrows=[]
    for mask in range(1,128):
        if any(mask>>i&1 for i in fs):continue
        v=0
        for i,r in enumerate(rows):
            if mask>>i&1:v^=r
        if v:continue
        x=mask
        while x:
            h=x.bit_length()-1
            if h not in piv:piv[h]=x;zrows.append(mask);break
            x^=piv[h]
    assert len(zrows)==3,(rows,fs,zrows)
    dets += [[reads[i] for i in range(7) if mask>>i&1] for mask in zrows]
    end=max(u['t'] for u in added);delta=max(end-30,last_data_cx-28)
    for u in kept:
        source=(u['t']<16 or u['b'] in (500,501) or
                17<=u['t']<=19 and set(u['q'])<=set(A+D) or
                u['t']==20 and set(u['q'])<=set(A))
        if not source:u['t']+=delta
    text=emit(kept+added,dets)
    return write_stem(text,D,H/'cand',name,source=dict(parent=str(base),encoder=encoder,decoder=decoder,mode=mode,herald=herald,tail_shift=delta))

def main():
    base=sys.argv[1]
    encs=json.loads((H/'terminal_layer_networks.json').read_text())
    decs=json.loads((H/'terminal_decoders.json').read_text())
    # Preserve representatives by flag mask and gate count; inverse gate order
    # can have different fault behavior, so retain up to two orders per state.
    distinct={};chosen=[]
    for d in sorted(decs,key=lambda d:(len(d['path']),-len(d['flags']))):
        key=(len(d['path']),tuple(d['flags']),tuple(d['rows']))
        if distinct.get(key,0)>=2:continue
        distinct[key]=distinct.get(key,0)+1;chosen.append(d)
    chosen=chosen[:20]
    # At least one full decoder provides the stronger seven-record control.
    configurations=[]
    for i,e in enumerate(encs[:10]):
        for j,d in enumerate(chosen[:6]):
            configurations.append((i,j,e,d,True))
        configurations.append((i,99,e,dict(path=e['path'],rows=e['rows'],flags=flags(list(e['rows']))),True))
    for i,e in enumerate(encs[:6]):
        for j,d in enumerate(chosen[:2]):configurations.append((i,j,e,d,False))
    results=[];best=1
    for i,j,e,d,h in configurations:
        try:
            st=build(base,e,d,f'flagterm_e{i}_d{j}_h{int(h)}','asap',h)
            raw=raw_check(st.with_suffix('.qasm').read_text(),D)
            row=dict(stem=str(st),prep_cx=len(e['path']),decode_cx=len(d['path']),flags=d['flags'],herald=h,raw=raw)
            if raw['ok']:
                c1,n=singles(st);row.update(c1=c1,harmful=n)
                if c1<1e-5:
                    p=price(st,1);row.update(loss=p['loss'],acceptance=p['acceptance'])
                    if p['acceptance']>=.5002 and p['loss']<best:
                        best=p['loss'];(H/'flagged_terminal_best.json').write_text(json.dumps(row,indent=2)+'\n')
            print(json.dumps(row),flush=True);results.append(row)
        except Exception as ex:
            print('ERROR',i,j,h,repr(ex),flush=True);results.append(dict(i=i,j=j,herald=h,error=repr(ex)))
        (H/'flagged_terminal_results.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
