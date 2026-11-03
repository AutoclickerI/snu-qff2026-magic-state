"""Transversal S on the encoded-zero B resource, with full native noise.

S on all seven B qubits fixes the ideal Steane zero state. Applied before its
final literal-zero C verification, it can convert earlier X residues into Y
so both the C readout and B phase readout see them. The real noisy pulse uses
the one clock freed by the earlier B factory. No ideal gate is inserted.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,contextlib,copy,io,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/PREFIX2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/REBUILD20261027'))
from qtools import write_stem
from qtools.validity import raw_check
from joint import emit
import frontend_axis as f
import record_contract,pairs
from axis_echo import exact


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--price',action='store_true')
    args=ap.parse_args()
    base=ROOT/'work/lanes/NATIVE2_20261027/boundary/b45_with48A_bebb981712ea9921_d6_20_19_10_2_22_16'
    data=json.loads(base.with_suffix('.json').read_text())['data_qubits']
    original,dets=f.parse_current(base.with_suffix('.qasm').read_text())
    B=[12,26,25,11,3,28,17];C=[18,27,24,5,4,29,23]
    f.DATA=data;record_contract.fa=f;pairs.fa=f
    folder=HERE/'b_phase';folder.mkdir(exist_ok=True)
    rows=[]
    for placement,gate in [('gap','S'),('before_check','S'),('before_check','SDG'),('before_check','none')]:
        ops=copy.deepcopy(original)
        tick=45
        if placement=='before_check':
            tick=44
            for b,c in zip(B,C):
                coupling=[o for o in ops if o.kind=='CX' and o.qs==(b,c) and o.time==44]
                assert len(coupling)==1,(b,c,coupling)
                coupling[0].time=45
                read=[o for o in ops if o.kind=='M' and o.qs==(c,) and o.time==45]
                assert len(read)==1,(c,read)
                read[0].time=46
        if gate!='none':
            ops += [f.Op(gate,(q,),tick) for q in B]
        occupied=set()
        for o in ops:
            for q in o.qs:
                assert (o.time,q) not in occupied,('collision',o)
                occupied.add((o.time,q))
        ops.sort(key=lambda o:o.time)
        text=emit(ops,dets);raw=raw_check(text,data)
        name=f'{placement}_{gate.lower()}'
        stem=write_stem(text,data,folder,name,source=dict(parent=str(base),placement=placement,gate=gate,
                         rationale='Transversal S fixes the ideal B zeroL state; all native pulse and idle noise retained.'))
        row=dict(name=name,stem=str(stem),raw=raw,cx=sum(o.kind=='CX' for o in ops),ticks=max(o.time for o in ops)+1)
        if raw['ok']:
            single=record_contract.singles(f.make_model(*f.parse_current(text)))
            row['c1']=single['c1'];row['harmful_single_count']=len(single['harmful_faults'])
            if row['c1']<1e-10:
                with contextlib.redirect_stdout(io.StringIO()):
                    pair=pairs.audit(stem,stem.with_suffix('.pairs.json'))
                row['c2']=pair['c2']
                if args.price and row['c2']<35:
                    row['exact']=exact(stem)
        rows.append(row)
        (folder/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
        print(json.dumps(row),flush=True)


if __name__=='__main__':main()
