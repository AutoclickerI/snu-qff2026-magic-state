"""Exact rational terminal-channel and decoder analysis at official p=1/1000.

No claim of an achievable circuit below a threshold. 'Universal' here follows
only if the stated last-operation/no-signalling proof applies to all valid
retained Steane-output circuits, as analyzed in the accompanying notes.
"""
from fractions import Fraction as F
from decimal import Decimal, localcontext
from itertools import product, combinations
import json
from pathlib import Path

def dec(x):
    return Decimal(x.numerator)/Decimal(x.denominator)

def noise_signature(paulis):
    sx=sz=px=pz=0
    for i,k in enumerate(paulis):
        x=k in (1,2); z=k in (2,3)
        if x:sx^=i+1;px^=1
        if z:sz^=i+1;pz^=1
    return sx,sz,px,pz

def distribution(q):
    # Rational integer weights with one shared denominator.
    probs=[1-q,q/3,q/3,q/3]
    den=1
    import math
    for a in probs:den=math.lcm(den,a.denominator)
    ws=[int(a*den) for a in probs]
    dd={}
    for pp in product(range(4),repeat=7):
        n=math.prod(ws[k] for k in pp)
        key=noise_signature(pp)
        dd[key]=dd.get(key,0)+n
    return {k:F(n,den**7) for k,n in dd.items()}

def analyze(q, certified=F(0)):
    dd=distribution(q)
    assert sum(dd.values())==1
    rows=[]
    for x0,z0 in product(range(8),repeat=2):
        vx=vy=F(0)
        for (sx,sz,px,pz),prob in dd.items():
            # Starting syndrome representative contains one X/Z when nonzero.
            fx=px^bool(x0)^bool(sx^x0)
            fz=pz^bool(z0)^bool(sz^z0)
            vx+=prob*((-1)**fz)
            vy+=prob*((-1)**(fx^fz))
        norm2=(vx*vx+vy*vy)/2
        rows.append((norm2,x0,z0,vx,vy))
    best=max(rows)
    with localcontext() as ctx:
        ctx.prec=65
        lower=(1-dec(best[0]).sqrt())/2
        code=next(r for r in rows if r[1:3]==(0,0))
        ideal_loss=(1-(code[3]+code[4])/2)/2
        out=dict(q=str(q),maximum_fidelity_input_syndrome=list(best[1:3]),
                 minimum_loss_over_arbitrary_input=str(lower),
                 perfect_T_codespace_input_loss=str(dec(ideal_loss)),
                 vx=str(dec(best[3])),vy=str(dec(best[4])),
                 maximum_norm_squared_numerator=str(best[0].numerator),
                 maximum_norm_squared_denominator=str(best[0].denominator))
    # A purely rational certificate for the rounded-down lower bound.
    if q==F(1,5000) and not certified:certified=F(465,10**9)
    out['certified_lower_bound']=str(certified)
    if certified:
        assert all(r[0] <= (1-2*certified)**2 for r in rows)
    return out

if __name__=='__main__':
    p=F(1,1000);q=p/5;a=1-4*q/3;lam=1-16*p/15
    r0=(1+6*lam/a+9*lam/a**2)/16
    r1=(1+2*lam/a-3*lam/a**2)/16
    r2=(1-2*lam/a+lam/a**2)/16
    assert min(r0,r1,r2)>=0 and r0+6*r1+9*r2==1
    out=dict(p=str(p),depolarizing_factor_q=str(q),
             residual_two_qubit_Pauli_probabilities=dict(II=str(r0),each_weight1=str(r1),each_weight2=str(r2)),
             independent_terminal_channels={})
    for name,qq in [('universal_extracted_channel',q),('one_idle',p),('perfect_partner_final_CX_marginal',4*p/5)]:
        out['independent_terminal_channels'][name]=analyze(qq)
    qeff=q+4*p/5-F(4,3)*q*(4*p/5)
    out['independent_terminal_channels']['two_tick_universal']=analyze(qeff,F(1162,100000000))
    # Check EVERY output pair, avoiding an untested code-automorphism assumption.
    pair_norms=[]
    dd_cert=F(3333,10000000)
    for i,j in combinations(range(7),2):
        dd={}
        for aa,bb in product(range(4),repeat=2):
            pp=[0]*7;pp[i]=aa;pp[j]=bb
            dd[noise_signature(pp)]=1-p if (aa,bb)==(0,0) else p/15
        best=F(0)
        for x0,z0 in product(range(8),repeat=2):
            vx=vy=F(0)
            for (sx,sz,px,pz),pr in dd.items():
                fx=px^bool(x0)^bool(sx^x0);fz=pz^bool(z0)^bool(sz^z0)
                vx+=pr*(-1)**fz;vy+=pr*(-1)**(fx^fz)
            best=max(best,(vx*vx+vy*vy)/2)
        assert best <= (1-2*dd_cert)**2
        pair_norms.append(best)
    assert len(pair_norms)==21 and len(set(pair_norms))==1
    best=max(pair_norms)
    with localcontext() as ctx:
        ctx.prec=65
        out['last_output_output_CX']=dict(minimum_loss=str((1-dec(best).sqrt())/2),
                                        certified_lower_bound=str(dd_cert),pairs_checked=21)
    # R/RX and first-use preparation: preserve the exact Bloch-vector length.
    residual_reset=(p-F(2,3)*q)/(1-F(4,3)*q)
    assert 0<=residual_reset<=1
    assert (1-F(4,3)*q)*(1-2*residual_reset)==1-2*p
    extra=dict(pairs_checked=21,maximum_norm_squared=str(best),
               each_pair_certified_loss_at_least=str(dd_cert),
               residual_reset_flip_probability=str(residual_reset),reset_factorization_exact=True)
    out['additional_certificates']=extra
    Path(__file__).with_name('additional_certificates.json').write_text(json.dumps(extra,indent=2)+'\n')
    path=Path(__file__).with_suffix('.json');path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
