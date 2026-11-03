"""Controlled all-orders noise ablations of the verified native phase circuit.

Every scenario preserves the physical operations, schedule, detector contract,
and output order. Selected physical noise channels alone are set to identity.
These are counterfactual diagnostics, never claimed as implementable candidates.
Idle intervals are split by their actual native clock, not the earlier operation
to which the judge attaches their noise. The shared evaluator is unchanged.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import collections,hashlib,json,math,sys,time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/EXPAND2_20261027'))
from qtools.evaluator import sparse_walsh as sw
from qtools.version import EVALUATOR_VERSION
from qtools.validity import raw_check
import frontend_axis as f

STEM=ROOT/'work/lanes/SOTA_RESOURCE_20261028/cand/resynth_safe_ed3fedc445723242_d6_20_19_10_2_22_16'
EXPECTED=5.962589946361928e-5
ROLES=dict(D=[6,20,19,10,2,22,16],A=[7,14,13,9,8,21,15],
           B=[12,26,25,11,3,28,17],C=[18,27,24,5,4,29,23])
D,A,B,C=(set(ROLES[x])for x in 'DABC')
MATCHINGS={(frozenset(ROLES[x]),frozenset(ROLES[y])):set(zip(ROLES[x],ROLES[y]))
           for x,y in [('D','A'),('B','C'),('B','D')]}

def channel_metadata(model):
    prog,blocks=f.noise_blocks(model.native,.001,first_order=False)
    _,steps,gaps=f.schedule(model.native)
    byins=collections.defaultdict(list)
    for ins,q,t,n in gaps:byins[ins].append((q,t,n))
    out=[]
    for ci,ch in enumerate(model.chans):
        ii=ch['ins'];op=model.labels[ii];block=blocks[ii];k=block.index(prog[ii].text)
        assert len(steps[ii])==1
        clock=steps[ii][0][1]
        assert clock==op.time,(ci,clock,op)
        if ch['jl']>k+1:
            q,t,n=byins[ii][ch['jl']-(k+2)]
            assert ch['qs']==[q],(ch,byins[ii])
            clocks=list(range(t,t+n));kind='idle'
        else:
            clocks=[clock]
            if ch['jl']<k:kind='measurement_flip' if op.kind in ('M','MX') and ch['jl']==k-1 else 'initial'
            elif op.kind in ('M','MX'):kind='measurement_after'
            elif op.kind in ('R','RX'):kind='reset'
            else:kind='gate'
        out.append(dict(channel=ci,noise=ch['name'],p=ch['p'],qubits=ch['qs'],
                        gate=list(op.qs),operation=op.kind,operation_time=op.time,
                        clocks=clocks,kind=kind))
    return out

def isedge(ch,source,target):
    """The seven code-coordinate interaction edges, excluding helper/encoder CXs."""
    return ch['kind']=='gate' and ch['operation']=='CX' and tuple(ch['gate']) in MATCHINGS[frozenset(source),frozenset(target)]

def profiles():
    return [
      ('baseline','All original channels noisy.',lambda c,t:False),
      ('reset17','Only reset channel on q17 at tick 32 perfect.',lambda c,t:t==32 and c['kind']=='reset' and c['qubits']==[17]),
      ('before_40','Every noise event before actual clock 40 perfect.',lambda c,t:t<40),
      ('before_46','Every noise event before actual clock 46 perfect.',lambda c,t:t<46),
      ('before_47','Every noise event before actual clock 47 perfect.',lambda c,t:t<47),
      ('BC_cells_30_45','Channels supported entirely on final B/C cells during clocks 30..45 perfect; includes their preparation and waits.',lambda c,t:30<=t<46 and set(c['qubits'])<=B|C),
      ('A_cells_40_45','Channels supported entirely on final A cells during clocks 40..45 perfect.',lambda c,t:40<=t<46 and set(c['qubits'])<=A),
      ('data_wait_30_45','Only waiting noise on final data cells during clocks 30..45 perfect.',lambda c,t:30<=t<46 and c['kind']=='idle' and set(c['qubits'])<=D),
      ('BC_and_datawait_30_45','Union of BC_cells_30_45 and data_wait_30_45.',lambda c,t:30<=t<46 and (set(c['qubits'])<=B|C or (c['kind']=='idle' and set(c['qubits'])<=D))),
      ('DA_gate_noise','Depolarizing noise of native late data-to-A interactions perfect; original idles remain.',lambda c,t:t>=44 and isedge(c,D,A)),
      ('BC_verify_noise','Depolarizing noise of native late B-to-C verification interactions perfect; original idles remain.',lambda c,t:t>=44 and isedge(c,B,C)),
      ('DA_and_BC_gate_noise','Union of late D-to-A and B-to-C gate-noise removals.',lambda c,t:t>=44 and (isedge(c,D,A) or isedge(c,B,C))),
      ('BD_gate_noise','Depolarizing noise of final B-to-data interactions perfect; final data waiting remains.',lambda c,t:t>=44 and isedge(c,B,D)),
      ('final_data_wait','Only final data waiting at clocks >=47 perfect.',lambda c,t:t>=47 and c['kind']=='idle' and set(c['qubits'])<=D),
      ('final_measurement_flips','Only measurement-result flips at clocks >=46 perfect.',lambda c,t:t>=46 and c['kind']=='measurement_flip'),
      ('all_late_readout_noise','All physical channels attached to late measurement operations, except waiting, perfect.',lambda c,t:t>=46 and c['operation'] in ('M','MX') and c['kind']!='idle'),
      ('BCprep_and_verify','BC_cells_30_45 union late B-to-C gate noise perfect.',lambda c,t:(30<=t<46 and set(c['qubits'])<=B|C) or (t>=44 and isedge(c,B,C))),
    ]

def evaluate_ablations():
    started=time.perf_counter();text=STEM.with_suffix('.qasm').read_text()
    data=json.loads(STEM.with_suffix('.json').read_text())['data_qubits']
    assert data==ROLES['D']
    raw=raw_check(text,data);assert raw['ok'],raw
    old=(sw.fa,sw.parse_current)
    try:
        sw.fa=f;sw.parse_current=f.parse_current
        model,engine,groups,nd,ks,psi,where,_=sw.prepare(STEM,True)
    finally:sw.fa,sw.parse_current=old
    metadata=channel_metadata(model)
    compiled,elim=sw.compile_best(model,engine,groups,nd,ks,save=False)
    keys=[None]+engine.keys
    kernels=[sw.sparse_kernel(engine,ks,psi,where,key) for key in keys]
    selected=set(sys.argv[1:])
    prior=json.loads((HERE/'resource_ablations.json').read_text())['results'] if selected and (HERE/'resource_ablations.json').exists() else []
    results=[r for r in prior if r['name'] not in selected]
    for name,description,predicate in profiles():
        if selected and name not in selected:continue
        scales={};changes=[]
        for c in metadata:
            removed=[t for t in c['clocks'] if predicate(c,t)]
            if not removed:continue
            n=len(c['clocks']);keep=n-len(removed)
            newp=(.75*(1-(1-4*.001/3)**keep)) if c['kind']=='idle' else (c['p'] if keep else 0.)
            scales[c['channel']]=newp/c['p']
            changes.append(dict(channel=c['channel'],removed_clocks=removed,original_p=c['p'],new_p=newp))
        modified=[]
        for scope,chi,gens,sources in compiled:
            if not any(cid in scales for cid,_ in sources):modified.append((scope,chi,gens,sources));continue
            value=np.ones_like(chi)
            for cid,cc in sources:value*=1-scales.get(cid,1.)*(1-cc)
            modified.append((scope,value,gens,sources))
        vals=[];omission=[];peak=0
        for key,(states,weights,error)in zip(keys,kernels):
            vec,p=sw.contract_quotient(modified,states,0 if key is None else sw.emask_for(key),elim['order'])
            vals.append(float(np.dot(weights,vec)/(1<<len(ks))));omission.append(error);peak=max(peak,p)
        acc=vals[0];obs=sum(w*b*v for w,b,v in zip(engine.W,engine.beta,vals[1:]))
        loss=(acc-obs)/(2*acc)
        result=dict(name=name,description=description,loss=loss,acceptance=acc,
                    changed_channels=len(changes),noise_interventions=changes,
                    gain_vs_noisy_baseline=EXPECTED-loss,
                    relative_gain_vs_noisy_baseline=(EXPECTED-loss)/EXPECTED,
                    peak_bucket_elements=peak)
        results.append(result)
        rank={r[0]:i for i,r in enumerate(profiles())}
        results.sort(key=lambda r:rank[r['name']])
        print(json.dumps({k:v for k,v in result.items() if k!='noise_interventions'}),flush=True)
        (HERE/'resource_ablations.json').write_text(json.dumps(dict(stem=str(STEM.relative_to(ROOT)),
          qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),evaluator_version=EVALUATOR_VERSION,
          frontend_sha256=hashlib.sha256(Path(f.__file__).read_bytes()).hexdigest(),
          scope=__doc__,raw=raw,roles=ROLES,channel_metadata=metadata,results=results,
          note='Removing noise is not an implemented circuit change. Conditional losses and their improvements are not additive or monotone bounds on a redesigned circuit.',
          elapsed_seconds=time.perf_counter()-started),indent=2)+'\n')
    assert abs(results[0]['loss']-EXPECTED)<1e-12,(results[0],EXPECTED)
    sw.COLUMNS.clear()

if __name__=='__main__':evaluate_ablations()
