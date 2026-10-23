"""Grid-free screening with actual tprep STANDARD channels and final single-error decoding.

Ideal encoded input for extraction gadgets; actual noisy prep for MQT ancillas.
The X and Y logical-memory failure probabilities average to the T-state loss for
a Pauli-diagonal, logical-state-independent accepted Clifford extraction map.
All intermediate syndrome/flag bits are postselected zero. Terminal ideal
syndromes are used for correction, NOT postselected. No geometry is enforced.
"""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import json,itertools,math
from pathlib import Path
from dataclasses import replace
import numpy as np
import stim
from tprep.noise import apply_noise,STANDARD,schedule

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'evaluations';OUT.mkdir(exist_ok=True)
POOR_H=[(0,1,2,3),(1,2,4,5),(2,3,5,6)]
POOR_CX=[(3,8),(5,9),(6,7),(10,9),(10,8),(9,7),(7,8),(0,7),(8,9),(7,9),(10,7),(1,7),(2,8),(4,9)]

def ps(basis,qs,n=7):
    s=['_']*n
    for q in qs:s[q]=basis
    return stim.PauliString(''.join(s))

def ideal_prep(H,basis):
    st=[ps(b,r) for b in ['X','Z'] for r in H]
    st.append(ps(basis,range(7)))
    return stim.Tableau.from_stabilizers(st).to_circuit()

def poor_round(order='ZX',parallel_anc=False):
    parts=[]
    for k,b in enumerate(order):
        off=4*k if parallel_anc else 0
        anc=range(7+off,11+off)
        init_x={10+off} if b=='Z' else {7+off,8+off,9+off}
        part=[f"{'RX' if q in init_x else 'R'} {q}" for q in anc]
        pairs=POOR_CX if b=='Z' else [(t,c) for c,t in POOR_CX]
        for c,t in pairs:part.append(f'CX {c+off if c>=7 else c} {t+off if t>=7 else t}')
        part.extend(f"{'MX' if q in init_x else 'M'} {q}" for q in anc)
        parts.append(part)
    if parallel_anc:
        # Disjoint ancillas reset just before their first use under ASAP.
        return '\n'.join(parts[0]+parts[1])
    return '\n'.join(sum(parts,[]))

def strip_prep(c):
    # MR in MQT exports represents terminal measurement plus reset; final reset
    # is unneeded. qasm exports actually contain only measurement.
    o=stim.Circuit()
    for ins in c.flattened():
        if ins.name=='MR':o.append('M',ins.targets_copy())
        elif ins.name in ['TICK','DETECTOR','OBSERVABLE_INCLUDE','QUBIT_COORDS']:continue
        else:o.append(ins)
    return o

def ungroup(text):
    # tprep QASM conversion emits one operation per line. A source Stim CX line
    # may contain dependent operations; keeping it grouped would delay all its
    # error channels until the end of the line and change fault propagation.
    from tprep.grid import ARITY
    lines=[]
    for ins in stim.Circuit(text).flattened():
        ts=ins.targets_copy();arity=ARITY.get(ins.name,1)
        assert not ins.gate_args_copy()
        for i in range(0,len(ts),arity):lines.append(ins.name+' '+' '.join(str(x.value) for x in ts[i:i+arity]))
    return '\n'.join(lines)

def infer_H(c):
    t=stim.TableauSimulator();t.do(c)
    words=[]
    for inds in itertools.combinations(range(7),4):
        if t.peek_observable_expectation(ps('X',inds,c.num_qubits))==1 and t.peek_observable_expectation(ps('Z',inds,c.num_qubits))==1:words.append(inds)
    chosen=[];span={0}
    for inds in words:
        v=sum(1<<q for q in inds)
        if v not in span:chosen.append(inds);span|={v^w for w in list(span)}
    assert len(chosen)==3,(chosen,words)
    return chosen

def circuit_for(text,H,basis,existing_input):
    noisy=apply_noise(text,1e-3,noise=replace(STANDARD,initial=0) if existing_input else STANDARD)
    c=ideal_prep(H,basis) if existing_input else stim.Circuit()
    c+=stim.Circuit(noisy)
    n_mid=c.num_measurements
    # Fixed zero syndrome/flag records: verify this noiselessly below.
    for k in range(n_mid):c.append('DETECTOR',[stim.target_rec(k-n_mid)])
    for b in ['X','Z']:
        for inds in H:c.append('MPP',sum(([stim.target_x(q) if b=='X' else stim.target_z(q),stim.target_combiner()] for q in inds),[])[:-1])
    c.append('MPP',sum(([{'X':stim.target_x,'Y':stim.target_y,'Z':stim.target_z}[basis](q),stim.target_combiner()] for q in range(7)),[])[:-1])
    # Full detector model validates all declared mid-circuit parities.
    c.detector_error_model()
    return c,n_mid

def single_fault_loss(c,nmid,basis):
    d=c.copy()
    for k in range(7):d.append('DETECTOR',[stim.target_rec(k-7)])
    # Stim's independent representation of depolarizing channels agrees to first
    # order. This is a diagnostic sum of single mechanisms, not a finite-p score.
    malignant=[]
    for error in d.detector_error_model().flattened():
        if error.type!='error':continue
        ids={t.val for t in error.targets_copy() if t.is_relative_detector_id()}
        if any(k<nmid for k in ids):continue
        sx=any(nmid+k in ids for k in range(3));sz=any(nmid+k in ids for k in range(3,6))
        correction=sx if basis=='X' else sz if basis=='Z' else sx^sz
        if ((nmid+6 in ids)^correction):malignant.append({'p':error.args_copy()[0],'signature':sorted(ids)})
    return {'malignant_mechanisms':len(malignant),'weight_sum':sum(x['p'] for x in malignant)}

def score(name,text,H,bases=('X','Y'),existing_input=True,shots=5_000_000):
    text=ungroup(text)
    from tprep.qasm import _x_readouts,_x_preparations
    lines=text.splitlines()
    _x_readouts(lines,drop_h=True);_x_preparations(lines)
    text='\n'.join(x for x in lines if x)
    if existing_input:
        # At the boundary all seven data qubits already exist. An I at step zero
        # supplies exactly one idle-equivalent depolarizing channel while the
        # ancillas reset; schedule() then charges every subsequent data wait.
        text='I 0 1 2 3 4 5 6\n'+text
    row={'name':name,'scope':'ideal encoded input, noisy extraction only' if existing_input else 'noisy logical basis-state preparation','shots_per_basis':shots,'p':1e-3,'noise':'tprep.noise.STANDARD; initial=0 only for existing perfect input','num_qubits':stim.Circuit(text).num_qubits,'cx':sum(len(x.targets_copy())//2 for x in stim.Circuit(text) if x.name=='CX'),'basis':{}}
    prog,steps,gaps=schedule(text);row['asap_steps']=1+max(s for st in steps for q,s in st)
    row['stabilizer_supports']=H
    (OUT/(name+'.stim')).write_text(text+'\n')
    for bi,b in enumerate(bases):
        c,nmid=circuit_for(text,H,b,existing_input)
        clean=c.without_noise().compile_sampler(seed=0).sample(32)
        assert not clean[:,:nmid].any(),(name,'nondeterministic intermediate measurement')
        assert not clean[:,nmid:].any(),(name,'wrong ideal logical output',clean[:,nmid:])
        sampler=c.compile_sampler(seed=20261024+bi)
        singles=single_fault_loss(c,nmid,b)
        accept=bad=0
        for n in range(0,shots,100_000):
            m=sampler.sample(min(100_000,shots-n));keep=~m[:,:nmid].any(axis=1)
            sx=m[:,nmid:nmid+3].any(axis=1);sz=m[:,nmid+3:nmid+6].any(axis=1)
            flip=sx if b=='X' else sz if b=='Z' else sx^sz
            loss=m[:,-1]^flip
            accept+=int(keep.sum());bad+=int((keep&loss).sum())
        p=bad/accept;row['basis'][b]={'bad':bad,'accepted':accept,'acceptance':accept/shots,'decoded_failure':p,'sem':math.sqrt(p*(1-p)/accept),'single_fault_diagnostic':singles}
    row['loss']=sum(x['decoded_failure'] for x in row['basis'].values())/len(bases)
    row['sem']=math.sqrt(sum(x['sem']**2 for x in row['basis'].values()))/len(bases)
    (OUT/(name+'.json')).write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
    return row

if __name__=='__main__':
    rows=[]
    for order in ['ZX','XZ']:
        for parallel in [False,True]:
            rows.append(score('poor14_'+order+('_separate' if parallel else '_reuse'),poor_round(order,parallel),POOR_H))
    source=ROOT/'found/munich-quantum-toolkit--qecc/source/scripts/ft_stateprep/eval/circuits/steane'
    for path in sorted(source.glob('*.stim')):
        c=strip_prep(stim.Circuit(path.read_text()));H=infer_H(c)
        basis='Z' if path.name.startswith('zero') else 'X'
        rows.append(score('mqt_'+path.stem,str(c),H,bases=(basis,),existing_input=False))
    (OUT/'summary.json').write_text(json.dumps(rows,indent=2))
