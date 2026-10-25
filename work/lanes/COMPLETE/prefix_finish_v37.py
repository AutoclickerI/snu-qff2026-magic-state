"""Open three cancelling guard pairs to advance the last phase fanout.
This confines additional repair to the17--33 prefix/source completion and keeps
the R45 A and65-CX resource schedules fixed. All eight pair subsets are tested.
"""
import os,sys,json
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
import v37,handoff_v37 as ho
H=v37.H
PAIRS=[{(25,3,4),(26,3,4)},{(26,9,10),(27,9,10)},{(23,5,11),(24,5,11)}]
PREFER={(27,3,4):26,(28,9,3):27,(29,9,10):28,(26,5,11):24,(27,17,11):26,(28,10,11):27}
if __name__=='__main__':
    out=[]
    for mask in range(8):
        c=ho.make(11,1);drops=set().union(*(s for i,s in enumerate(PAIRS) if mask>>i&1))
        v37.remove(c,drops)
        for o in c['ops']:
            if v37.key(o) in PREFER:o['t']=PREFER[v37.key(o)]
        c['meta']['source']+=f'; phase-fanout completion pair mask{mask}'
        name=f'v37_prefix_finish{mask}';st,info=v37.schedule(c,name,-1,seconds=5);print(name,info['status'],flush=True)
        if st:out.append(name)
    (H/'v37_prefix_finish_names.json').write_text(json.dumps(out))
