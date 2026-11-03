"""Exact whole-circuit noise counterfactuals, never additive loss allocations.

An operation's channel and all attached idle channels share its source label.
This attribution convention is recorded in the output; cut differences are
not bounds on obtainable improvement and do not add under postselection.
"""
import argparse,json,os,sys
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'work/tools'))
from qtools.evaluator import sparse_walsh as sw

def run(stem,cuts,output):
    stem=Path(stem);data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    rows=[]
    for lo,hi in cuts:
        m,e,groups,nd,ks,psi,where,_=sw.prepare(stem,True)
        removed=[]
        for cid,channel in enumerate(m.chans):
            t=m.labels[channel['ins']].time
            if not lo<=t<hi:
                channel['p']=0
                for f in groups[cid]:f['p']=0
                removed.append(cid)
        compiled,elim=sw.compile_best(m,e,groups,nd,ks,save=False)
        sw._CTX.update(eng=e,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
        try:
            vals=[sw._row(k) for k in [None]+e.keys]
            A=vals[0]['value'];obs=sum(w*b*v['value'] for w,b,v in zip(e.W,e.beta,vals[1:]))
            out=dict(noisy_source_times=[lo,hi],loss=(A-obs)/(2*A),acceptance=A,
                     noiseless_channels=len(removed),total_channels=len(m.chans))
            rows.append(out);print(json.dumps(out),flush=True)
        finally:sw._CTX.clear();sw.COLUMNS.clear()
    Path(output).write_text(json.dumps(dict(stem=str(stem),data_qubits=data,
        convention='Noise including following idle is attached to source operation time. Nonadditive counterfactuals.',
        experiments=rows),indent=2)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('output');ap.add_argument('--cuts',default='0:1000,0:24,24:1000,30:1000,35:1000,40:1000,44:1000')
    a=ap.parse_args();run(a.stem,[tuple(map(int,x.split(':'))) for x in a.cuts.split(',')],a.output)
