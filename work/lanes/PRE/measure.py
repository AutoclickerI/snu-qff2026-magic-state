"""Validate at 1e6 shots and split exact loss/A1 by actual native-schedule time."""
from common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('names',nargs='+');p.add_argument('--procs',type=int,default=8);args=p.parse_args()
for name in args.names:
    path=HERE/f'{name}.json';meta=json.loads(path.read_text())
    check=validate(name)
    ev=Eval((HERE/f'{name}.qasm').read_text(),meta['data_qubits'])
    cli=json.loads((HERE/f'{name}.exact.json').read_text())
    # The CLI already enumerated every pair; reuse its channel sensitivities.
    r=dict(loss1=cli['loss1'],loss2=cli['loss2'],A1=1-cli['acc1'],
           sens=np.array([x['loss_attribution'] for x in cli['locations']]))
    channels=[];preA=preL=0.0;ownedA=ownedL=0.0
    sch=meta['schedule'];ops=sch['ops'];times=sch['times'];npref=sch['npre'];shift=min(times)
    actual,ownership=native_mapping(meta,ev)
    cutoff=max(actual[i] for i in range(npref))
    meta['pre_end_step']=cutoff;meta['depth']=max(actual.values())+1
    meta['native_times']=[actual[i] for i in range(len(ops))]
    path.write_text(json.dumps(meta,indent=2)+'\n')
    lastpre={q:max(actual[i] for i,(k,qs,b) in enumerate(ops) if i<npref and q in qs)
             for q in {q for k,qs,b in ops[:npref] for q in qs}}
    # A pair straddling the boundary is split half to each fault; idle intervals
    # crossing it are apportioned by the number of included native time steps.
    for ci in range(len(ev.m.chans)):
        lab=ev.chan_label(ci);steps=list(map(int,lab['steps'].split('..')))
        first,last=(steps[0],steps[-1]);frac=max(0,min(last,cutoff)-first+1)/(last-first+1)
        ix=ev.fch==ci
        A=float((ev.fp[ix]*(1-ev.a_single[ix])).sum())
        L=float(r['sens'][ci]/2)
        preA+=A*frac;preL+=L*frac
        if lab['kind']=='idle':
            q=lab['qubits'][0];end=lastpre.get(q,-1)
            ownfrac=max(0,min(last,end)-first+1)/(last-first+1)
        else:
            ownfrac=float(ownership[ev.m.chans[ci]['ins']])
        ownedA+=A*ownfrac;ownedL+=L*ownfrac
        channels.append(dict(channel=ci,**lab,A1=A,loss2_half_attribution=L,pre_fraction=frac,construction_pre_fraction=ownfrac))
    summary=dict(name=name,CX=meta['n_2q'],pre_end_step=cutoff,depth=meta['depth'],loss1=r['loss1'],loss2=r['loss2'],
                 A1=r['A1'],pre_A1=preA,suffix_A1=r['A1']-preA,exp_minus_A1=math.exp(-r['A1']),
                 pre_loss2=preL,suffix_loss2=r['loss2']-preL,delta_loss2=r['loss2']-json.loads((HERE/'v12_reference.exact.json').read_text())['loss2'],
                 construction_pre_A1=ownedA,construction_suffix_A1=r['A1']-ownedA,
                 construction_pre_loss2=ownedL,construction_suffix_loss2=r['loss2']-ownedL,
                 passed=check['passed'],acceptance=check['acceptance'],check_shots=check['shots'])
    (HERE/f'{name}.split.json').write_text(json.dumps(dict(summary=summary,channels=channels),indent=2)+'\n')
    print(json.dumps(summary),flush=True)
