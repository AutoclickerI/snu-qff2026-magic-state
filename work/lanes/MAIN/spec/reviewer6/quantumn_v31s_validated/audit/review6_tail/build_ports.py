"""Port the physical SX/SXDG round gauge to pinned review-6 circuit inputs.

Every inserted gate receives native D1(p); gates occupy prior data idle slots.
Only a conflicting terminal single-qubit T/Tdg is retimed, across idle noise.
No source/frame/ancilla conjugation, full-frame update, or new tick is used.
"""
from pathlib import Path
import json,hashlib,sys,copy
import frontend as fa
from circuit_io import emit,certify
from judge_subset.noise import noise_blocks,schedule
from judge_subset.grid import adjacent
HERE=Path(__file__).resolve().parent
COMMIT='abf26aa98bede59bb07f7da838dd1b3a3fdf76f0'
A=[1,14,8,9,2,16,15]

def build(source,target=None):
    source=Path(source)
    if not source.is_absolute():source=HERE/source
    md=json.loads(source.with_suffix('.json').read_text());data=md['data_qubits']
    text=source.with_suffix('.qasm').read_text()
    ops,dets=fa.parse_current(text);ops=copy.deepcopy(ops)
    depth=max(o.time for o in ops)+1;last_tick=depth-1
    coupling={q:max(o.time for o in ops if o.kind=='CX'and o.qs==(q,a))
              for q,a in zip(data,A)}
    mods=[];in_times={}
    for q in data:
        t=coupling[q]-1;in_times[q]=t
        conflict=[o for o in ops if o.time==t and q in o.qs]
        if conflict:
            assert len(conflict)==1 and conflict[0].kind in ['T','TDG'],(q,t,conflict)
            o=conflict[0]
            assert not any(x.time==t-1 and q in x.qs for x in ops),(q,t-1)
            o.time=t-1;mods.append(dict(gate=o.kind,qubit=q,old_tick=t,new_tick=t-1,
                                     reason='Free gauge input slot by crossing depolarizing idle only'))
        assert not any(o.time==last_tick and q in o.qs for o in ops),(q,last_tick)
        # The next data operation must be its final A coupling, and no later
        # non-round operation may remain on that data wire.
        later=[o for o in ops if o.time>t and q in o.qs]
        assert len(later)==2 and all(o.kind=='CX'for o in later),(q,later)
        ops += [fa.Op('SX',(q,),t),fa.Op('SXDG',(q,),last_tick)]
    ops.sort(key=lambda o:o.time)
    target=HERE/(target or source.name+'_sx')
    emit(ops,dets,target,data,metadata=dict(scope=__doc__,source_commit=COMMIT,
         input=source.name,input_qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
         input_SX_ticks=in_times,output_SXDG_tick=last_tick,retimings=mods))
    native,_=fa.native_text(ops);prog,blocks=noise_blocks(native,.001)
    physical_gate_noise=[]
    for ins,block in zip(prog,blocks):
        if ins.name in ['SQRT_X','SQRT_X_DAG']:
            assert block[block.index(ins.text)+1]==f'DEPOLARIZE1(0.001) {ins.qubits[0]}'
            physical_gate_noise.append(ins.text)
    assert len(physical_gate_noise)==14
    assert all(adjacent(*o.qs)for o in ops if o.kind=='CX')
    _,steps,_=schedule(native)
    native_depth=max(t for groups in steps for _,t in groups)+1
    assert native_depth==depth
    result=dict(name=target.name,input_SX_ticks=in_times,retimings=mods,
                output_tick=last_tick,native_depth=native_depth,
                physical_gauge_noise_channels=14,nearest_neighbor_CX=True,
                qasm_sha256=hashlib.sha256(target.with_suffix('.qasm').read_bytes()).hexdigest(),
                **certify(ops,dets,data,fa))
    target.with_name(target.name+'_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
    return result

if __name__=='__main__':
    for name in sys.argv[1:] or ['inputs/v30g','inputs/v31s']:build(name)
