"""Exact accepted-loss coefficients and diagnostic pair attribution."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys,collections,itertools,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"lanes/NATIVE20261027"))
import rebuild
from qtools.evaluator import sparse_walsh as sw
from qtools.evaluator import frontend as fa

def module(f,m):
    op=m.labels[f['ins']]; t=op.time; qs=f['qs']
    if t>=17:return 'terminal_round'
    if any(q<7 for q in qs):
        if t<=6:return 'injection'
        if t<=8:return 'precheck'
        if t==9 or t==16:return 'T_layers'
        return 'logical_check_or_data_wait'
    if min(qs)>=28:return 'second_cat'
    if min(qs)>=21 and t<=11:return 'first_cat'
    if t<=9:return 'precheck_resource'
    return 'terminal_resource'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--joint-flags',action='store_true');args=parser.parse_args()
    D=list(range(7));text=Path(__file__).with_name('deep_extra_best').joinpath('flag_9_0_5.qasm').read_text()
    original_noise=fa.noise_blocks
    try:
        fa.noise_blocks=lambda text,p,first_order=True:original_noise(text,p,first_order=True)
        m,e,groups,nd,ks,psi,where,_=sw.prepare(None,True,text=text,data_qubits=D)
    finally:fa.noise_blocks=original_noise
    active=sum(1<<i for i,p in enumerate(e.projs) if p[:2]!=(0,0))
    grouped=collections.defaultdict(list)
    for f in m.faults:grouped[f['d']&~active].append(f)
    cache={};acc=collections.defaultdict(float);top=[];first=0.
    def loss(s,d,err):
        key=(s,d)
        if key not in cache:cache[key]=e.ntable(s,d)
        a,n=cache[key]
        return 0 if n is None else max(0.,float(n[err]))
    for f in m.faults:
        first+=f['p']/.001*loss(f['s'],f['d'],f['e'])
    for ff in grouped.values():
        agg=collections.defaultdict(list)
        for f in ff:agg[(f['s'],f['d'],f['e'],module(f,m))].append(f)
        entries=[]
        for (s,d,err,mod),fs in agg.items():
            bychan=collections.defaultdict(float)
            for f in fs:bychan[f['chan']]+=f['p']/.001
            entries.append((s,d,err,mod,sum(bychan.values()),bychan,fs))
        for i,a in enumerate(entries):
            for j in range(i,len(entries)):
                b=entries[j];n=loss(a[0]^b[0],a[1]^b[1],a[2]^b[2])
                if n<1e-15:continue
                weight=a[4]*b[4]-sum(p*b[5].get(ch,0.) for ch,p in a[5].items())
                if i==j:weight*=.5
                val=weight*n
                if val<1e-12:continue
                key=' + '.join(sorted((a[3],b[3])))
                acc[key]+=val
                top.append(dict(value=val,module=key,a=[f['label'] for f in a[6]],b=[f['label'] for f in b[6]],loss=n))
    result=dict(first=first,second=sum(acc.values()),pairs=sorted(acc.items(),key=lambda x:-x[1]),top=sorted(top,key=lambda x:-x['value'])[:50],kernel_tables=len(cache))
    out=Path(__file__).with_name('deep_best_pairs.json');out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='top'},indent=2),flush=True)

if __name__=='__main__':main()
