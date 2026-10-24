from common import *
import moments_gradient as mg,numpy as np
stem=H/'catalog0_d6_r100_w40';ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits']);fp=ev.fp.copy();r,g=mg.evaluate(ev);ref=mom.evaluate(ev);assert abs(r['total']-ref['total'])<1e-14
np.savez_compressed(H/'catalog0_d6_r100_w40.gradient.npz',fp=fp,gradient=g,fch=ev.fch)
rows=[];by=np.bincount(ev.fch,weights=fp*g,minlength=len(ev.m.chans));indices=sorted(range(len(by)),key=lambda i:abs(by[i]),reverse=True)[:6]+np.random.default_rng(0).choice(len(by),6,replace=False).tolist()
for ci in dict.fromkeys(indices):
 mask=ev.fch==ci;eps=1e-4;vals=[]
 for sign in [-1,1]:ev.fp=fp.copy();ev.fp[mask]*=1+sign*eps;vals.append(mom.evaluate(ev)['total'])
 numerical=(vals[1]-vals[0])/(2*eps);pred=by[ci];error=abs(numerical-pred);row=dict(channel=int(ci),analytic=pred,numerical=numerical,error=error,label=ev.chan_label(ci));rows.append(row);print(json.dumps(row),flush=True);assert error<1e-12+1e-6*abs(pred),row
identity=float(fp@g)-(2*r['second']+3*r['third']);assert abs(identity)<1e-12
idle=[]
for ci,ch in enumerate(ev.m.chans):
 if ch['gap']is None:continue
 q,start,n=ch['gap'];p=ch['prob'];dp=-.75*math.log1p(-4e-3/3)*(1-4e-3/3)**n;idle.append(dict(channel=ci,per_tick=float(by[ci]/p*dp),marginal=float(by[ci]),label=ev.chan_label(ci),gap=list(ch['gap'])))
out=dict(passed=True,derivative_checks=rows,euler_error=identity,top_idle=sorted(idle,key=lambda x:abs(x['per_tick']),reverse=True)[:40]);(H/'gradient_validation.json').write_text(json.dumps(out,indent=2));append_result('exact_third_gradient',dict(passed=True,checks=len(rows),euler_error=identity,top_idle=out['top_idle'][:5]),'Analytic physical-channel probability derivative of full exact second+cubic objective. Validated against centered finite differences and homogeneous polynomial identity. No circuit claim.');print('PASS',flush=True)
