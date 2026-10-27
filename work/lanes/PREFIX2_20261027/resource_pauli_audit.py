"""Fast native-resource single-fault audit with full Pauli propagation.

This standalone resource audit uses the explicit ideal incoming encoded T
state, exact recorded helper corrections, and the official CSS decoder rule.
It screens all fifteen CX Paulis, reset/readout errors and one-qubit/idle
depolarizing channels. The assembled full circuit remains the final oracle.
"""
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
from partial_contract import make_four_square_contract,make_partial_contract,STEANE_X
from terminal_variants import make_variant


def audit(pc,module,details=False):
    operations=[dict(o) for o in module['operations']]
    R=max(o['time'] for o in operations)+1
    term=pc.terminal();detectors=[set(r) for r in pc.DETECTORS]
    helperbits={};bid=30
    corr={(r['helper'],r['time']):r for r in module.get('helper_byproducts',[])}
    for o in operations:
        if o['kind'] not in ('M','MX'):continue
        key=o['qs'][0],o['time'];o['bit']=bid;helperbits[key]=bid;bid+=1
        if o.get('zero_flag'):detectors.append({o['bit']})
        elif key in corr:
            p=corr[key];x=sum(1<<q for q in p['X']);z=sum(1<<q for q in p['Z']);flips=0
            for kind,qs,_,bit in term:
                if kind=='CX':
                    a,b=qs
                    if x>>a&1:x^=1<<b
                    if z>>b&1:z^=1<<a
                elif (kind=='M' and x>>qs[0]&1) or (kind=='MX' and z>>qs[0]&1):flips^=1<<bit
            assert not any((x|z)>>q&1 for q in pc.D),'Unsafe recorded byproduct reaches data'
            for det in detectors:
                if sum(flips>>b&1 for b in det if b<30)&1:det.add(o['bit'])
    operations.extend(dict(kind=k,qs=list(qs),time=R+t,bit=b) for k,qs,t,b in term)
    operations.sort(key=lambda o:(o['time'],o['kind'],o['qs']))
    columns={b:sum(1<<(14+j) for j,row in enumerate(detectors) if b in row) for b in range(bid)}
    xs=[0]*36;zs=[0]*36
    for i,q in enumerate(pc.D):xs[q]=1<<i;zs[q]=1<<(7+i)
    nxt={};idle=[{} for _ in operations]
    end=max(o['time'] for o in operations)+1
    for i in range(len(operations)-1,-1,-1):
        o=operations[i]
        for q in o['qs']:
            if q in nxt:
                next_time,next_kind=nxt[q]
                gap=0 if next_kind in ('R','RX') else next_time-o['time']-1
            else:gap=0 if o['kind'] in ('M','MX') else end-o['time']-1
            if gap>0:idle[i][q]=gap
            nxt[q]=(o['time'],o['kind'])
    harmful=[];total=0.;channels=0;minimum={}
    def loss(sig):
        if sig>>14:return 0.
        xp=sig&127;zp=(sig>>7)&127
        sx=any((xp&g).bit_count()&1 for g in STEANE_X)
        sz=any((zp&g).bit_count()&1 for g in STEANE_X)
        lx=(xp.bit_count()&1)^sx;lz=(zp.bit_count()&1)^sz
        return .5 if lx else 1. if lz else 0.
    def add(sig,weight,o,pauli,kind):
        nonlocal total,channels
        channels+=1;v=loss(sig)*weight
        if v:
            total+=v
            if details:harmful.append(dict(time=o['time'],kind=o['kind'],qubits=o['qs'],channel=kind,pauli=pauli,c1=v,signature=sig))
    for i in range(len(operations)-1,-1,-1):
        o=operations[i];kind=o['kind'];qs=o['qs']
        for q,n in idle[i].items():
            for p,s in [('X',xs[q]),('Y',xs[q]^zs[q]),('Z',zs[q])]:add(s,n/3,o,p,f'idle q{q} n{n}')
        if kind=='CX':
            a,b=qs;pa=[0,xs[a],xs[a]^zs[a],zs[a]];pb=[0,xs[b],xs[b]^zs[b],zs[b]]
            for j in range(4):
                for k in range(4):
                    if j or k:add(pa[j]^pb[k],1/15,o,'IXYZ'[j]+'IXYZ'[k],'depol2')
            xs[a]^=xs[b];zs[b]^=zs[a]
        elif kind in ('H','S','SDG'):
            q=qs[0]
            for p,s in [('X',xs[q]),('Y',xs[q]^zs[q]),('Z',zs[q])]:add(s,1/3,o,p,'depol1')
            if kind=='H':xs[q],zs[q]=zs[q],xs[q]
            else:xs[q]^=zs[q]
        elif kind in ('R','RX'):
            q=qs[0];add(xs[q] if kind=='R' else zs[q],1,o,'X' if kind=='R' else 'Z','reset');xs[q]=zs[q]=0
        elif kind in ('M','MX'):
            q=qs[0]
            for p,s in [('X',xs[q]),('Y',xs[q]^zs[q]),('Z',zs[q])]:add(s,1/3,o,p,'meas_after')
            if kind=='M':xs[q]^=columns[o['bit']]
            else:zs[q]^=columns[o['bit']]
            add(xs[q] if kind=='M' else zs[q],1,o,'X' if kind=='M' else 'Z','readout')
        else:raise ValueError(kind)
    return dict(resource_c1=total,harmful=harmful if details else None,components=channels,
        detector_count=len(detectors),scope='Ideal source input; all resource and terminal channels, full Pauli audit')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('module');ap.add_argument('--index',type=int,default=0);ap.add_argument('--all',action='store_true');ap.add_argument('--output')
    a=ap.parse_args();doc=json.loads(Path(a.module).read_text())
    if doc.get('b_only'):
        pc=make_partial_contract(doc['roles'],0,True,False)
        pc.DETECTORS=pc.DETECTORS[:6]
        pc.terminal=lambda:doc['terminal_operations']
    elif 'terminal_operations' in doc:pc=make_variant(doc['square_mask'],doc.get('swap_mask',0),doc.get('drop_free',True),True)
    else:pc=make_four_square_contract(True,True)
    rows=[]
    for i,row in enumerate(doc['candidates']):
        if not a.all and i!=a.index:continue
        res=audit(pc,row,True);res.update(index=i,resource_ready=row['resource_ready'],cx=row['cx']);rows.append(res)
    dest=Path(a.output) if a.output else Path(a.module).with_suffix('.paulis.json');dest.write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps([{k:v for k,v in r.items() if k!='harmful'} for r in rows],indent=2),flush=True)


if __name__=='__main__':main()
