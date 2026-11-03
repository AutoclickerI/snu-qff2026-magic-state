"""Exact algebraic single-fault criterion for grouped logical-W checks.

Scope: ideal encoded |T_L> input, GHZ controls, physical T/CX/TDG shared basis,
all cat X-product outcomes +1, and an ideal final six-stabilizer projector.
This is not a native full-noise score and does not include cat movement faults.

All coefficient arithmetic below is Gaussian integers and rational numbers.
The orthogonal-target probability is represented exactly as a+b*sqrt(2).
No numerical tolerance is used in the 896-operator classification.
"""
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE=Path(__file__).resolve().parent
SUPPORTS=(85,102,120)
ALL=127


def in_hamming(mask):
    return all((mask&s).bit_count()%2==0 for s in SUPPORTS)


def submasks(mask):
    sub=mask
    while True:
        yield sub
        if not sub:return
        sub=(sub-1)&mask


def projected_operator(suffix,q=None,pauli='W'):
    """Integer coefficients of I,X,Z,XZ, divided by sqrt(2**power)."""
    coeff=[0j]*4
    power=suffix.bit_count()+(pauli=='Y')
    for ys in submasks(suffix):
        count=ys.bit_count()
        base=(-1)**count*(1j)**count
        terms=[(suffix,ys,base)]
        if pauli=='Y':
            terms=[(suffix|(1<<q),ys,base),
                   (suffix|(1<<q),ys|(1<<q),base*1j)]
        elif pauli=='Z':
            terms=[(suffix,ys|(1<<q),base)]
        for x,z,c in terms:
            if in_hamming(x) and in_hamming(z):
                coeff[(x.bit_count()%2)+2*(z.bit_count()%2)]+=c
    assert all(z.real==int(z.real) and z.imag==int(z.imag)for z in coeff)
    return coeff,power


def square(a,b,power):
    """Exact norm squared of (a+b/sqrt(2))/sqrt(2**power)."""
    u=Fraction(2*int(a.real*a.real+a.imag*a.imag)+int(b.real*b.real+b.imag*b.imag),2**(power+1))
    v=Fraction(int((a*b.conjugate()).real),2**power)
    return u,v


def state_probabilities(coeff,power):
    ci,cx,cz,cxz=coeff
    # <T-|X|T+>=i/sqrt(2), <T-|Z|T+>=1,
    # <T-|XZ|T+>=-1/sqrt(2); <T+|XZ|T+>=-i/sqrt(2).
    bad=square(cz,1j*cx-cxz,power)
    good=square(ci,cx-1j*cxz,power)
    return good,bad


def fano_line(indices):
    indices=list(indices)
    if len(indices)!=3:return False
    return (indices[0]+1)^(indices[1]+1)^(indices[2]+1)==0


def algebraic_fault(q,suffix,pauli):
    coeff,power=projected_operator(suffix,q,pauli)
    good,bad=state_probabilities(coeff,power)
    expected=((pauli=='Y' and suffix.bit_count()==2 and fano_line([q]+[i for i in range(7)if suffix>>i&1])) or
              (pauli=='Z' and suffix.bit_count()==4 and fano_line([i for i in range(7)if not suffix>>i&1])))
    assert (bad!=(0,0))==expected,(q,suffix,pauli,coeff,good,bad)
    if expected:assert good==(0,0) and bad==(Fraction(1,4),0)
    return dict(q=q,suffix=suffix,pauli=pauli,harmful=expected,
        logical_coefficients=[[int(c.real),int(c.imag)]for c in coeff],normalization_power=power,
        good_probability=[str(x)for x in good],bad_probability=[str(x)for x in bad])


def audit_order(groups_by_round,timeline):
    """Return all dangerous CX faults in any interleaving of complete checks.

    Each timeline item is (round,data_index). Cat preparation must implement
    an ideal GHZ, and each round must visit each data index exactly once.
    Different rounds may use different cat partitions. The check parities
    are independently postselected. Their measurement time must be after
    that round's final data interaction.
    """
    rounds=len(groups_by_round)
    assert sorted(timeline)==[(r,q)for r in range(rounds)for q in range(7)]
    group_for={}
    for r,groups in enumerate(groups_by_round):
        assert sorted(q for g in groups for q in g)==list(range(7))
        for g,group in enumerate(groups):
            for q in group:group_for[r,q]=g
    last={q:max(i for i,(_,j)in enumerate(timeline)if j==q)for q in range(7)}
    harmful=[]
    for i,(r,q)in enumerate(timeline):
        if i!=last[q]:continue
        suffix=[j for rr,j in timeline[i+1:]if rr==r and group_for[rr,j]==group_for[r,q]]
        if len(suffix)==2 and fano_line([q]+suffix):
            harmful.append(dict(timeline_index=i,round=r,group=group_for[r,q],data=q,
                                suffix=suffix,pauli='XY',bad_numerator='1/4'))
        if len(suffix)==4 and fano_line(j for j in range(7)if j not in suffix):
            harmful.append(dict(timeline_index=i,round=r,group=group_for[r,q],data=q,
                                suffix=suffix,pauli='XZ',bad_numerator='1/4'))
    return harmful


def cycle(groups):
    second=[g[1:]+g[:1]for g in groups]
    ticks=[]
    for i in range(max(map(len,groups))):
        tick=[(r,g[i])for r,gs in enumerate((groups,second))for g in gs if i<len(g)]
        assert len({q for r,q in tick})==len(tick)
        ticks.append(tick)
    return ticks,[x for tick in ticks for x in tick]


def main():
    rows=[]
    for q in range(7):
        for mask in range(128):
            if mask>>q&1:continue
            for p in 'YZ':rows.append(algebraic_fault(q,mask,p))
    partial=[]
    for mask in range(128):
        coeff,power=projected_operator(mask)
        good,bad=state_probabilities(coeff,power)
        assert bad==(0,0)
        partial.append(dict(mask=mask,good_probability=[str(x)for x in good],
                            bad_probability=[str(x)for x in bad]))
    orders=[]
    for perm in itertools.permutations(range(7)):
        groups=[list(perm[:3]),list(perm[3:])]
        ticks,timeline=cycle(groups)
        harmful=audit_order([groups,groups],timeline)
        expected=fano_line(groups[1][-3:])
        assert bool(harmful)==expected
        orders.append(dict(groups=groups,safe=not harmful,harmful=harmful))
    count=sum(r['safe']for r in orders)
    assert count==4032
    result=dict(scope=__doc__,operator_cases=len(rows),harmful_operator_cases=sum(r['harmful']for r in rows),
        exact_operators=rows,partial_W_cases=partial,two_cat_cyclic_ordered_partitions=len(orders),
        two_cat_cyclic_safe_ordered_partitions=count,two_cat_cyclic_orders=orders)
    (HERE/'exact_suffix_constraints.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ('exact_operators','partial_W_cases','two_cat_cyclic_orders')},indent=2))


if __name__=='__main__':main()
