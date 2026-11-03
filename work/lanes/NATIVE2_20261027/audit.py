"""Exact first- and second-order diagnostic for a completed native circuit."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,collections,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'work/tools'))
from qtools.evaluator import sparse_walsh as sw,frontend as f

def audit(stem,pairs=True):
    start=time.perf_counter();stem=Path(stem)
    meta=json.loads(stem.with_suffix('.json').read_text());data=meta['data_qubits']
    source=meta.get('source',{});round_tick=source.get('round_tick',10**6)
    last_cat=source.get('cat_final_read',source.get('cat_control',0)+1)
    aq={1,14,8,9,2,16,15};dq=set(data);rq={6,26,13,11,4,23,27,12,25,19,17,5,29,28,18,31,35,34}
    def region(ff):
        op=m.labels[ff['ins']];qs=set(op.qs);t=op.time
        if qs&rq:
            if qs&dq:return 'B_to_D'
            return 'BC_resource' if t<=round_tick else 'BC_readout'
        if t>last_cat:
            if qs<=dq:return 'postW_data'
            if qs&dq and qs&aq:return 'D_to_A'
            return 'A_resource' if t<round_tick else 'A_decode_or_read'
        if t<source.get('cat_start',0):return 'source_or_precheck'
        return 'W_cat_or_data'
    # Coefficients require each physical channel's linear-in-p weights, while
    # sw.prepare deliberately builds exact finite-p channel probabilities.
    f.DATA=list(data)
    ops,dets=f.parse_current(stem.with_suffix('.qasm').read_text())
    m=f.make_model(ops,dets);e=f.Engine(m)
    sw.canonicalize_detector_rows(m,e);e=f.Engine(m)
    active=sum(1<<i for i,p in enumerate(e.projs) if p[:2]!=(0,0))
    tables={};single=[];c1=0.
    def loss(s,d,err):
        key=(s,d)
        if key not in tables:tables[key]=e.ntable(s,d)
        a,n=tables[key]
        return 0. if n is None else max(0.,float(n[err]))
    def brief(ff):
        op=m.labels[ff['ins']]
        return dict(t=op.time,kind=op.kind,gate=list(op.qs),qs=ff['qs'],pauli=ff['pauli'],
                    label=ff['label'],chan=ff['chan'])
    for ff in m.faults:
        val=ff['p']/.001*loss(ff['s'],ff['d'],ff['e']);c1+=val
        if val>1e-12:single.append(dict(value=val,**brief(ff)))
    out=dict(stem=str(stem),c1=c1,singles=sorted(single,key=lambda x:-x['value']))
    print('singles',json.dumps(out),flush=True)
    if pairs:
        buckets=collections.defaultdict(list)
        for ff in m.faults:buckets[ff['d']&~active].append(ff)
        acc=collections.defaultdict(float);stage=collections.defaultdict(float);top=[]
        for fs in buckets.values():
            agg=collections.defaultdict(list)
            for ff in fs:
                op=m.labels[ff['ins']]
                agg[ff['s'],ff['d'],ff['e'],op.time,region(ff)].append(ff)
            entries=[]
            for (s,d,err,t,mod),faults in agg.items():
                bychan=collections.defaultdict(float)
                for ff in faults:bychan[ff['chan']]+=ff['p']/.001
                entries.append((s,d,err,t,sum(bychan.values()),bychan,faults,mod))
            for i,a in enumerate(entries):
                for j in range(i,len(entries)):
                    b=entries[j];n=loss(a[0]^b[0],a[1]^b[1],a[2]^b[2])
                    if n<1e-12:continue
                    weight=a[4]*b[4]-sum(p*b[5].get(ch,0.) for ch,p in a[5].items())
                    if i==j:weight*=.5
                    val=weight*n
                    if val<1e-12:continue
                    acc[tuple(sorted((a[3],b[3])))]+=val
                    stage[tuple(sorted((a[7],b[7])))]+=val
                    top.append(dict(value=val,a=[brief(ff) for ff in a[6]],b=[brief(ff) for ff in b[6]],loss=n))
        out.update(c2=sum(acc.values()),regions=[dict(t1=k[0],t2=k[1],value=v) for k,v in sorted(acc.items(),key=lambda x:-x[1])],
                   stage_pairs=[dict(a=k[0],b=k[1],value=v) for k,v in sorted(stage.items(),key=lambda x:-x[1])],
                   top_pairs=sorted(top,key=lambda x:-x['value'])[:100])
    out.update(kernel_tables=len(tables),seconds=time.perf_counter()-start)
    stem.with_suffix('.audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('top_pairs','regions','singles')},indent=2),flush=True)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--singles',action='store_true');a=ap.parse_args();audit(a.stem,not a.singles)
