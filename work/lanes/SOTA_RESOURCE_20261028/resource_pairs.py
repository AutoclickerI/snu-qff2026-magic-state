"""All physical second-order loss pairs, split by actual noise event clock.

No top-N approximation: all compatible signature pairs are included. Mutually
exclusive Pauli alternatives from one physical noise channel are subtracted.
This diagnoses the p^2 coefficient; all-orders ablations are in native_risk.py.
"""
import collections,json,time
import resource_risk as nr

def stage(c,t):
    if t>=47 and c['kind']=='idle' and set(c['qubits'])<=nr.D:return 'final_data_idle'
    if t>=44 and nr.isedge(c,nr.B,nr.D):return 'final_BD_gate'
    if t>=44 and nr.isedge(c,nr.D,nr.A):return 'final_DA_gate'
    if t>=44 and nr.isedge(c,nr.B,nr.C):return 'final_BC_gate'
    if t>=46 and c['operation'] in ('M','MX') and c['kind']!='idle':return 'final_readout'
    if 30<=t<=46 and set(c['qubits'])<=nr.B|nr.C:return 'BC_'+c['kind']+'_'+c['operation']
    if t>=40 and set(c['qubits'])<=nr.A:return 'A_cells_40plus'
    if 30<=t<46 and c['kind']=='idle' and set(c['qubits'])<=nr.D:return 'data_wait_30_45'
    if t<30:return 'source_pre30'
    return 'other_t30plus'

def run():
    start=time.perf_counter();f=nr.f;sw=nr.sw;f.DATA=list(nr.D)
    # Preserve the code-coordinate order, not numerical set order.
    f.DATA=nr.ROLES['D']
    ops,dets=f.parse_current(nr.STEM.with_suffix('.qasm').read_text())
    model=f.make_model(ops,dets);engine=f.Engine(model)
    sw.canonicalize_detector_rows(model,engine);engine=f.Engine(model)
    channels=nr.channel_metadata(model)
    active=sum(1<<i for i,p in enumerate(engine.projs) if p[:2]!=(0,0))
    inactive=((1<<len(dets))-1)^active
    groups=collections.defaultdict(list)
    for fault in model.faults:groups[(fault['s'],fault['d'],fault['e'])].append(fault)
    packed=[];buckets=collections.defaultdict(list)
    for key,faults in groups.items():
        weights=collections.defaultdict(float)
        bychannel=collections.defaultdict(lambda:collections.defaultdict(float))
        for fault in faults:
            c=channels[fault['chan']]
            for clock in c['clocks']:
                label=stage(c,clock);value=fault['p']/len(c['clocks'])
                weights[label]+=value;bychannel[label][fault['chan']]+=value
        buckets[key[1]&inactive].append(len(packed));packed.append((key,weights,bychannel))
    totals=collections.defaultdict(float);kernels={};harmful=0
    for ids in buckets.values():
        for ii,ia in enumerate(ids):
            a,wa,ca=packed[ia]
            for ib in ids[ii+1:]:
                b,wb,cb=packed[ib];k=(a[0]^b[0],a[1]^b[1])
                if k not in kernels:kernels[k]=engine.ntable(*k)
                _,losses=kernels[k];loss=0. if losses is None else float(losses[a[2]^b[2]])
                if loss<=1e-12:continue
                harmful+=1
                for sa,pa in wa.items():
                    for sb,pb in wb.items():
                        probability=pa*pb-sum(p*cb[sb].get(c,0.)for c,p in ca[sa].items())
                        if probability>1e-20:totals[tuple(sorted((sa,sb)))]+=probability*loss/1e-6
    c2=sum(totals.values())
    out=dict(scope=__doc__,stem=str(nr.STEM.relative_to(nr.ROOT)),c2=c2,
             cross_stage=[dict(a=a,b=b,c2=v)for(a,b),v in sorted(totals.items(),key=lambda x:-x[1])],
             harmful_signature_pairs=harmful,elapsed_seconds=time.perf_counter()-start,
             note='Idle-event weights split by their true times. c2 is a diagnostic and omits higher orders and the full noisy acceptance normalization.')
    (nr.HERE/'resource_pairs.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':run()
