"""Rank all64 local square orientations with native resource witnesses."""
import contextlib,io,json,sys
from pathlib import Path
import joint_resource_beam as jb
import joint_resource_peel as jp
from partial_contract import make_contract
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]


def finish_time(rec,releases):
    plus=set(rec['initial_plus_qubits']);known_plus={4,12,14,18,25,26}
    reuse={q for q in rec['cells'] if q!=17 and ((q in plus)==(q in known_plus))}
    last={q:releases[q]-1+int(q not in reuse) for q in rec['cells']}
    layers={}
    for a,b in reversed(rec['backward_path']):
        t=max(last[a],last[b])+1;last[a]=last[b]=t
        layers.setdefault(t,[]).append([a,b])
    # q14 is deliberately reset to plus after all its temporary uses.
    reset=max(releases[14],last[14]+1);last[14]=reset
    return max(41,1+max(last.values())),reset,layers,sorted(reuse)


if __name__=='__main__':
    releases={int(k):v for k,v in json.loads((ROOT/'work/lanes/NATIVE2_20261027/prefix_release.json').read_text())['release'].items()}
    records=[]
    for mask in range(64):
        pc=make_contract(mask,late_c14=True);jp.pc=pc;jb.pc=pc
        for trial in range(3):
            seed=4000+mask*3+trial
            with contextlib.redirect_stdout(io.StringIO()):
                rec=jp.run(seed,True,[0,15,60][trial],True,[1.5,.5,1.5][trial])
            R,reset,layers,reuse=finish_time(rec,releases)
            rec.update(orientation=mask,resource_round=R,late_plus_time=reset,
                       scheduled_layers=layers,reused_input_qubits=reuse,roles=dict(A=pc.A,B=pc.B,C=pc.C,D=pc.D))
            out=HERE/'joint_resource'/f'orientation_{mask:02x}_{trial}.json'
            out.write_text(json.dumps(rec,indent=2)+'\n')
            row=dict(mask=mask,trial=trial,stem=str(out.relative_to(ROOT)),cx=rec['cx'],
                     depth=rec['depth'],round=R,unsafe_axis_checks=rec['unsafe_cx_axis_checks'])
            records.append(row);print(json.dumps(row),flush=True)
        (HERE/'orientation_peel_results.json').write_text(json.dumps(records,indent=2)+'\n')
