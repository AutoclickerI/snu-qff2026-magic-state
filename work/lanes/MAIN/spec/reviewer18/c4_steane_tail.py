#!/usr/bin/env python3
"""Exact finite-p oracle for a seven-tile C4 -> Steane final transition.

The complete preparation BEFORE the two final ticks is PERFECT in this oracle.
It is NOT a submitted/noisily prepared circuit and carries no official pass claim.

Each tile is (D,H,K,L), with native grid edges D-K, H-L, H-D:
  tick -1: CX D,K ; CX H,L
  tick  0: CX H,D ; MZ K ; MZ L
Postselect the 14 individual K/L readouts to zero; do not measure H.
Perfect input inner stabilizers: X_D X_H X_K X_L, Z_D Z_K, Z_H Z_L.
Inner logicals: X_D X_K and Z_H Z_D.
Concatenate the seven inner qubits with the outer Steane code.

STANDARD noise: D2(p) after each of three CXs per tile; X_ERROR(p)
before each MZ. Postmeasurement noise is irrelevant to discarded K/L.
All four tile wires participate at both ticks, so there is no idle noise.
The measurement records are deterministic zero only in the ideal circuit.

Two independent local calculations are compared: explicit 16^3 x 2^2
Pauli/readout-fault enumeration, and a conditional-channel formula.
Global loss enumerates all 4^7 output Paulis with the exact ideal decoder.
Stabilizer algebra and distances are independently certified below.
"""
from itertools import product
from math import prod
import json
from pathlib import Path

# Binary Pauli encoding: I=0, X=1, Z=2, Y=3.
PN = ['I', 'X', 'Z', 'Y']


def enumerate_tile(p):
    d2 = [((a,b), 1-p if a == b == 0 else p/15)
          for a,b in product(range(4), repeat=2)]
    out = [0.0]*4
    for ((d,k),pdk), ((h,l),phl), ((fh,fd),phd) in product(d2, repeat=3):
        for mk,ml in product(range(2), repeat=2):
            # K/L post-CX X bits flip their corresponding final Z readouts.
            if (k&1)^mk or (l&1)^ml:
                continue
            pr = (p if mk else 1-p)*(p if ml else 1-p)
            # Through final H->D, X_H contributes X_D. Z_D only adds Z_H.
            e = d ^ (h&1) ^ fd
            out[e] += pdk*phl*phd*pr
    a = sum(out)
    return a, [w/a for w in out]


def formula_tile(p):
    a = 1-23*p/15+16*p*p/15
    q = (2*p/5)/a                 # checked D2 -> D1 on its retained endpoint
    r = 2*q/3                    # X/Y on H propagate to X on D
    base = q+4*p/5-(4/3)*q*(4*p/5)
    px = (1-r)*base/3+r*(1-base)
    py = pz = base/3
    pi = (1-r)*(1-base)+r*base/3
    return a*a, [pi,px,pz,py]


def syndrome_and_parity(ep):
    sx=sz=px=pz=0
    for col,e in enumerate(ep,1):
        if e&1:
            sx ^= col
            px ^= 1
        if e&2:
            sz ^= col
            pz ^= 1
    return sx,sz,px,pz


def decoded_loss(dist):
    loss = 0.0
    logical = [0.0]*4
    for ep in product(range(4),repeat=7):
        sx,sz,px,pz = syndrome_and_parity(ep)
        lx=px^bool(sx); lz=pz^bool(sz)
        le=lx|(lz<<1)
        w=prod(dist[e] for e in ep)
        logical[le]+=w
        loss+=w*(0.5 if lx else float(lz))
    return loss,logical


def symp(a,b):
    x,z=a; xx,zz=b
    return ((x&zz).bit_count()+(z&xx).bit_count())&1


def xor(a,b):
    return a[0]^b[0],a[1]^b[1]


def pauli(n, pairs):
    x=z=0
    for q,e in pairs:
        if e&1:x^=1<<q
        if e&2:z^=1<<q
    return x,z


def rank(vectors,n):
    basis={}
    for x,z in vectors:
        v=x|(z<<n)
        while v:
            k=v.bit_length()-1
            if k in basis:v^=basis[k]
            else:
                basis[k]=v
                break
    return len(basis)


def cx(a,c,t):
    x,z=a
    if x>>c&1:x^=1<<t
    if z>>t&1:z^=1<<c
    return x,z


def certify_code():
    n=28
    inner=[]; ix=[]; iz=[]; expected=[]
    for i in range(7):
        d,h,k,l=range(4*i,4*i+4)
        inner += [pauli(n,[(j,1) for j in (d,h,k,l)]),
                  pauli(n,[(d,2),(k,2)]),pauli(n,[(h,2),(l,2)])]
        expected += [pauli(n,[(h,1)]),pauli(n,[(k,2)]),pauli(n,[(l,2)])]
        ix.append(pauli(n,[(d,1),(k,1)]))
        iz.append(pauli(n,[(h,2),(d,2)]))
    gens=inner[:]
    for b in range(3):
        row=[i for i in range(7) if (i+1)>>b&1]
        for src,p in ((ix,1),(iz,2)):
            g=(0,0)
            for i in row:g=xor(g,src[i])
            gens.append(g)
            expected.append(pauli(n,[(4*i,p) for i in row]))
    logicals=[]
    for src in (ix,iz):
        g=(0,0)
        for a in src:g=xor(g,a)
        logicals.append(g)
    def decode(g):
        for i in range(7):
            d,h,k,l=range(4*i,4*i+4)
            g=cx(g,d,k);g=cx(g,h,l)
        for i in range(7):g=cx(g,4*i+1,4*i)
        return g
    images=[decode(g) for g in gens]
    assert rank(gens,n)==27
    assert not any(symp(a,b) for a,b in product(gens,repeat=2))
    assert images==expected
    assert all(not symp(g,l) for g,l in product(gens,logicals))
    assert symp(*logicals)==1
    assert decode(logicals[0])==pauli(n,[(4*i,1) for i in range(7)])
    assert decode(logicals[1])==pauli(n,[(4*i,2) for i in range(7)])
    # Exact inner logical-coset minimum weights from all 256 four-qubit Paulis.
    ig=inner[:3]; lx=ix[0];lz=iz[0]
    minw=[99]*4
    for ep in product(range(4),repeat=4):
        e=pauli(4,list(enumerate(ep)))
        if any(symp(e,g) for g in ig):continue
        label=symp(e,lz)|(symp(e,lx)<<1)
        minw[label]=min(minw[label],sum(bool(a) for a in ep))
    # Outer undetected cosets, weighted by exact minimum inner-coset weights.
    outerw=[99]*4
    for ep in product(range(4),repeat=7):
        sx,sz,px,pz=syndrome_and_parity(ep)
        if sx or sz:continue
        label=px|(pz<<1)
        outerw[label]=min(outerw[label],sum(minw[e] for e in ep))
    assert min(outerw[1:])==6
    # Seven disjoint 2x2 tiles in the top seven cells of a 3x3 tile grid.
    placements=[]
    for rr,cc in list(product(range(3),repeat=2))[:7]:
        # H D / L K in a 6x6 grid.
        h=12*rr+2*cc; d=h+1;l=h+6;k=h+7
        placements.append(dict(D=d,H=h,K=k,L=l))
    assert len({q for tile in placements for q in tile.values()})==28
    def adjacent(a,b):return abs(a//6-b//6)+abs(a%6-b%6)==1
    assert all(adjacent(t[a],t[b]) for t in placements
               for a,b in [('D','K'),('H','L'),('H','D')])
    return dict(n=28,k=1,stabilizer_rank=27,all_stabilizers_commute=True,
                decoded_generators_match=True,logical_XZ_map_to_Steane=True,
                inner_logical_min_weights=dict(zip(PN,minw)),
                concatenated_logical_min_weights=dict(zip(PN,outerw)),
                distance=min(outerw[1:]),grid_tiles=placements,
                preparation_excluded=True)


def main():
    p=0.001
    ae,de=enumerate_tile(p)
    af,df=formula_tile(p)
    assert abs(ae-af)<1e-13
    assert max(abs(a-b) for a,b in zip(de,df))<1e-13
    le,logicals=decoded_loss(de)
    lf,_=decoded_loss(df)
    assert abs(le-lf)<1e-15
    lowp=1e-6
    _,lowd=formula_tile(lowp)
    lowl,_=decoded_loss(lowd)
    baseline=3.6211236525327396e-5
    out=dict(p=p,scope='PERFECT pre-tail concatenated-code input; two noisy native ticks only',
             noise='STANDARD D2 after CX, readout flip p, no waiting; discarded postmeasurement noise irrelevant',
             physical_channels_per_tile=3,readout_checks=14,
             independent_calculations=dict(tile_acceptance_enumeration=ae,
                 tile_acceptance_formula=af,local_distribution_max_abs_difference=max(abs(a-b) for a,b in zip(de,df)),
                 loss_enumeration=le,loss_formula=lf),
             effective_output_paulis=dict(zip(PN,df)),
             acceptance=af**7,loss=lf,logical_paulis_after_ideal_decoder=dict(zip(PN,logicals)),
             leading_pauli_rates_in_p_over_15=dict(X=10,Y=6,Z=6),
             c2=22.026666666666667,low_p_crosscheck=dict(p=lowp,loss_over_p2=lowl/lowp**2),
             baseline_v37g_L=baseline,ideal_oracle_relative_gain=1-lf/baseline,
             target_gaps={str(t):t-lf for t in (2.5e-5,2.8e-5,0.7*baseline,0.9*baseline)},
             gap_caveat='Differences are design targets, NOT additive certified preparation-noise budgets; noisy full-circuit A and L must be evaluated jointly.',
             official_validation=False,code_certificate=certify_code())
    dst=Path(__file__).with_suffix('.json')
    dst.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
