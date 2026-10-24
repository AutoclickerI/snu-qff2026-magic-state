"""Reconstruct evaluated timing witnesses without favoring roundoff noise."""
from build30 import *
import gzip
if __name__=='__main__':
    stem=sys.argv[1] if len(sys.argv)>1 else 'f_timing_best';base=sys.argv[2] if len(sys.argv)>2 else 'f_c0df'
    history=json.loads(gzip.open(H/(stem+'.witnesses.json.gz'),'rt').read())
    c=C.read(H/base);best=screen(base)['total'];rows=[]
    for it in sorted({r['iteration'] for r in history}):
        rr=[r for r in history if r['iteration']==it and 'total' in r and r['exp_minus_A1']>=.5002]
        lo=min(r['total'] for r in rr);near=[r for r in rr if r['total']<=lo+1e-14]
        # Rounding ties are not measured error improvements. Retain the
        # highest-acceptance tied witness for independent verification.
        chosen=max(near,key=lambda r:r['exp_minus_A1']);d=C.clone(c);d['t']=[t+x for t,x in zip(c['t'],chosen['dv'])];d=finish(d)
        name=stem+f'_r{it}';row=save(d,name,[base,'timing_macro_loop',f'round{it}']);row.update(screen(name));rows.append(row)
        print(name,row['total'],row['exp_minus_A1'],flush=True)
        # The running version used strict floating < for incumbent selection;
        # reproduce its actual next-round parent, not our tie-resolved witness.
        actual=min(rr,key=lambda r:r['total'])
        if actual['total']<best:
            c['t']=[t+x for t,x in zip(c['t'],actual['dv'])];c=finish(c);best=actual['total']
    (H/(stem+'.harvest.json')).write_text(json.dumps(rows,indent=2)+'\n')
