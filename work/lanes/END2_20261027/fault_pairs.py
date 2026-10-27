"""Whole-circuit exact single-fault diagnostics and accepted fault-pair numerator.

The reported second-order numerator equals the loss coefficient only when the
first-order numerator is zero. It is a diagnostic, not a full noisy ranking.
"""
import argparse,collections,json,os,sys,time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'work/tools'))
from qtools.evaluator import frontend as f

def analyse(stem,pairs=True):
    stem=Path(stem);text=stem.with_suffix('.qasm').read_text()
    f.DATA=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    ops,dets=f.parse_current(text);m=f.make_model(ops,dets);e=f.Engine(m)
    active=sum(1<<i for i,p in enumerate(e.projs) if p[:2]!=(0,0))
    cache={};first=0.;harm=[]
    def n(s,d,err):
        key=s,d
        if key not in cache:cache[key]=e.ntable(s,d)
        a,N=cache[key]
        return 0. if N is None else max(0.,float(N[err]))
    def label(ff):
        op=m.labels[ff['ins']]
        return dict(time=op.time,kind=op.kind,qubits=list(op.qs),pauli=ff['pauli'],label=ff['label'])
    for ff in m.faults:
        val=ff['p']/.001*n(ff['s'],ff['d'],ff['e'])
        first+=val
        if val>1e-10:harm.append(dict(contribution=val,**label(ff)))
    out={'stem':str(stem),'first_order':first,'harmful_count':len(harm),'harmful':sorted(harm,key=lambda r:-r['contribution'])}
    print(json.dumps({k:v for k,v in out.items() if k!='harmful'}),flush=True)
    if pairs:
        groups=collections.defaultdict(list)
        for ff in m.faults:groups[ff['d']&~active].append(ff)
        top=[];total=0.;scope=collections.defaultdict(float)
        BC={12,26,25,11,3,28,17,18,27,24,5,4,29,23}
        def region(ff):
            o=m.labels[ff['ins']]
            return 'BC_late' if 31<=o.time<=46 and set(o.qs)<=BC else 'rest'
        for ff in groups.values():
            aggregate=collections.defaultdict(list)
            for fault in ff:aggregate[(fault['s'],fault['d'],fault['e'],region(fault))].append(fault)
            items=[]
            for key,fs in aggregate.items():
                bychan=collections.defaultdict(float)
                for fault in fs:bychan[fault['chan']]+=fault['p']/.001
                items.append((key,sum(bychan.values()),bychan,fs))
            for i,(a,wa,ca,fa) in enumerate(items):
                for j in range(i,len(items)):
                    b,wb,cb,fb=items[j];loss=n(a[0]^b[0],a[1]^b[1],a[2]^b[2])
                    if loss<1e-14:continue
                    w=wa*wb-sum(p*cb.get(ch,0.) for ch,p in ca.items())
                    if i==j:w*=.5
                    val=w*loss
                    if val<1e-12:continue
                    total+=val;key=' + '.join(sorted((a[3],b[3])));scope[key]+=val
                    top.append(dict(contribution=val,scope=key,numerator=loss,a=[label(v) for v in fa],b=[label(v) for v in fb]))
        out.update(second_order_pair_numerator=total,second_is_loss_coefficient=first<1e-10,pair_scopes=dict(scope),top_pairs=sorted(top,key=lambda r:-r['contribution'])[:60],tables=len(cache))
    target=Path(str(stem)+'.faults.json');target.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('harmful','top_pairs')}),flush=True)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--singles-only',action='store_true');a=ap.parse_args();analyse(a.stem,not a.singles_only)
