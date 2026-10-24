"""Counterfactual idle-channel scaling; does not alter a physical circuit."""
from common import *
import numpy as np
stem=Path(sys.argv[1]);md=json.loads(stem.with_suffix('.json').read_text());ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),md['data_qubits']);base=ev.fp.copy();chs={i for i,c in enumerate(ev.m.chans)if c['gap']is not None and c['gap'][1]+c['gap'][2]<=md['R']};ix=np.array([i for i,c in enumerate(ev.fch)if c in chs]);rows=[]
for f in(0.,.25,.5,.75,1.):
 ev.fp=base.copy();ev.fp[ix]*=f;r=mom.evaluate(ev);rows.append(dict(fraction=f,**r));print(json.dumps(rows[-1]),flush=True)
coef=np.polynomial.polynomial.polyfit([r['fraction']for r in rows],[r['total']for r in rows],3);err=max(abs(np.polynomial.polynomial.polyval(r['fraction'],coef)-r['total'])for r in rows);p=coef.copy();p[0]-=5e-5;roots=np.polynomial.polynomial.polyroots(p);inside=[float(r.real)for r in roots if abs(r.imag)<1e-9 and 0<=r.real<=1]
result=dict(rows=rows,cubic_coefficients=coef.tolist(),fit_error=err,target=5e-5,idle_strength_at_target=inside,scope='Uniform scaling of pre-round idle categorical fault probabilities in the through-third-order model. Not a realizable schedule, not a time-step bound, not an all-orders claim.')
stem.with_suffix('.idle_curve.json').write_text(json.dumps(result,indent=2));append_result(stem.name,result,'Idle-exposure diagnostic.');print(json.dumps(result),flush=True)
