"""Explicit v37j source/factory boundary for a new native terminal resource.

The cut retains source lifetimes through their final heralds and removes old
resource lifetimes. Source TDG gates can then cross empty slots and CX gates
where their wire is control. No nonlocal gates enter the exported prefix.
The optional ideal-resource completion is a separately labeled diagnostic.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/tools'));sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from qtools import write_stem
from joint import emit
from partial_square import D,A,B,C,prep,prep_shortened_c,ideal_contract_check
from record_contract import complete

# First tick at which the old source lifetime is over. Data cells are retained
# through the entire boundary. Conservative source guards are kept through
# their last read/reset boundary, even when they are identity in the ideal state.
RELEASE={0:37,1:40,3:39,4:36,5:36,7:41,8:37,9:40,11:35,12:33,13:41,
         14:37,15:41,17:30,18:32,21:38,23:0,24:33,25:31,26:16,27:30,
         28:31,29:0,30:27,31:0,32:0,33:0,34:0,35:0}

def extract(retime=True):
    ops,ds=f.parse_current((ROOT/'work/lanes/MAIN/v37j.qasm').read_text())
    source=next(o for o in ops if o.bit==366);assert source.qs==(1,) and source.time==29
    source.kind='R';source.bit=None
    removed=[];kept=[]
    for o in ops:
        if o.time>44:continue
        if all(q in D or o.time<RELEASE[q] for q in o.qs):kept.append(o)
        else:removed.append(o)
    if retime:
        # A diagonal phase commutes through CX with this wire as control.
        for phase in [o for o in kept if o.kind in ('T','TDG')]:
            q=phase.qs[0]
            earlier=[o for o in kept if o.time<phase.time and q in o.qs]
            floor=0
            for o in earlier:
                if o.kind=='CX' and o.qs[0]==q:continue
                floor=max(floor,o.time+1)
            occupied={o.time for o in kept if o is not phase and q in o.qs}
            new=next(t for t in range(floor,phase.time+1) if t not in occupied)
            phase.time=new
    bits={o.bit for o in kept if o.bit is not None}
    dets=[row-{366} for row in ds if row-{366} and row-{366}<=bits]
    text=emit(kept,dets);raw=raw_check(text,D)
    actual_release={q:1+max((o.time for o in kept if q in o.qs),default=-1) for q in range(36) if q not in D}
    meta=dict(data_qubits=D,source='v37j',fixed_source_record=366,retimed_phases=retime,
              source_ticks=max(o.time for o in kept)+1,cx=sum(o.kind=='CX' for o in kept),
              T=sum(o.kind in ('T','TDG') for o in kept),release=actual_release,
              conservative_lifetime_cuts=RELEASE,roles=dict(D=D,A=A,B=B,C=C),raw=raw,
              preserved_records=sorted(bits),detectors=[sorted(r) for r in dets],
              excluded_operation_count=len(removed))
    return kept,dets,meta

def ideal_completion(prefix,dets,meta):
    # The native prefix is tested with a perfect instantaneous resource, with
    # artificial preparation time explicitly removed by END2's diagnostic.
    cut=max(o.time for o in prefix)+1;ops=copy.deepcopy(prefix);dets=copy.deepcopy(dets)
    prep(ops,A,cut,True);prep(ops,B,cut,False);prep_shortened_c(ops,cut)
    ops.extend(f.Op('CX',(b,c),cut+4) for b,c in zip(B,C))
    R=cut+5
    for i in range(7):
        ops.extend([f.Op('CX',(D[i],A[i]),R),f.Op('CX',(B[i],C[i]),R),f.Op('CX',(B[i],D[i]),R+1)])
        if i<6:ops.append(f.Op('CX',(C[i],A[i]),R+1))
    for offset,block,kind in [(400,A,'M'),(407,B,'MX'),(414,C,'MX')]:
        ops.extend(f.Op(kind,(q,),R+2,offset+i) for i,q in enumerate(block))
    f.DATA=list(D);model=f.make_model(*f.parse_current(emit(ops,dets)))
    records=complete(model,dets);extra=[r for r in records['missing'] if any(b>=400 for b in r['bits'])]
    assert all(not r['reference'] for r in extra)
    dets += [set(r['bits']) for r in extra]
    text=emit(ops,dets);raw=ideal_contract_check(text,D)
    stem=HERE/'boundary'/'stripped_prefix_perfect_partial_resource'
    stem.parent.mkdir(parents=True,exist_ok=True);stem.with_suffix('.qasm').write_text(text)
    out=dict(data_qubits=D,ideal_contract=raw,gate_valid=False,diagnostic_only=True,
        source='Explicit stripped v37j source prefix',resource_state='A plusL; B zeroL; C shortened span; B->C precorrelated',
        square_mask=63,inserted_ticks=list(range(cut,cut+5)),source_boundary=meta,
        actual_terminal_times=[cut,cut+1,cut+2],resource_contract=extra)
    stem.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    return stem

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--no-retime',action='store_true');ap.add_argument('--diagnose',action='store_true');a=ap.parse_args()
    ops,dets,meta=extract(not a.no_retime)
    stem=write_stem(emit(ops,dets),D,HERE/'boundary','source_prefix',source=meta)
    (HERE/'prefix_release.json').write_text(json.dumps(dict(stem=str(stem),**meta),indent=2)+'\n')
    print(json.dumps(dict(stem=str(stem),**meta),indent=2),flush=True)
    if a.diagnose and meta['raw']['ok']:
        from partial_incumbent import diagnose
        diagnostic=ideal_completion(ops,dets,meta)
        result=diagnose(diagnostic)
        result['scope']=f'Noisy explicitly stripped source through tick{meta["source_ticks"]-1}; perfect instantaneous resource at tick{meta["source_ticks"]}; artificial preparation noise and elapsed time excluded.'
        diagnostic.with_suffix('.diagnostic.json').write_text(json.dumps(result,indent=2)+'\n')
