"""Exact character factors for uniform Pauli channels; no circuit or judge edit.

A channel uniform over the nonzero vectors of F_2^d has characteristic
1 when the queried character is trivial on its image, otherwise
1 - 2^d * p/(2^d-1).  The image may have lower rank than d.
The full signature includes kernel, residual detector and observable bits.
"""
from collections import Counter
import numpy as np


def compile_character_channels(compiled, merge=False):
    fast=[]; fallback=[]; identities=0; source_terms=0;constant=1.
    for scope,p0,terms in compiled:
        source_terms+=len(terms)
        n=len(terms);d=(n+1).bit_length()-1
        if (1<<d)!=n+1 or not terms:
            fallback.append((scope,p0,terms));continue
        probs=[t[3] for t in terms]
        p=probs[0]
        # Equality is exact on represented inputs: near-uniform channels
        # must never be silently approximated as uniform.
        if any(q != p for q in probs):
            fallback.append((scope,p0,terms));continue
        kb=max(k.bit_length() for k,_,_,_ in terms)
        rb=len(scope);mask=(1<<kb)-1;rmask=(1<<rb)-1
        images=[k|(r<<kb)|(e<<(kb+rb)) for k,r,e,_ in terms]
        counts=Counter([0]+images)
        piv={}
        for original in sorted(counts):
            v=original
            while v:
                bit=v.bit_length()-1
                if bit not in piv:
                    piv[bit]=v;break
                v^=piv[bit]
        rank=len(piv)
        if rank>d or len(counts)!=(1<<rank) or set(counts.values())!={1<<(d-rank)}:
            fallback.append((scope,p0,terms));continue
        # Reduced basis makes the image-subspace identity canonical.
        for bit in sorted(piv):
            for high in sorted(piv):
                if high>bit and (piv[high]>>bit)&1:
                    piv[high]^=piv[bit]
        basis=tuple(sorted((v&mask,(v>>kb)&rmask,v>>(kb+rb)) for v in piv.values()))
        # Keep both levels rather than replacing p0+n*p by one. This also
        # preserves an unnormalized input factor without a tolerance gate.
        trivial,nontrivial=p0+n*p,p0-p
        if not basis:
            identities+=1;constant*=trivial;continue
        fast.append((scope,trivial,nontrivial,basis))
    before=len(fast)
    if merge:
        combined={}
        for scope,trivial,nontrivial,basis in fast:
            key=(scope,basis)
            old_trivial,old_nontrivial=combined.get(key,(1.,1.))
            combined[key]=(old_trivial*trivial,old_nontrivial*nontrivial)
        fast=[(scope,trivial,nontrivial,basis) for (scope,basis),(trivial,nontrivial) in combined.items()]
    return dict(fast=fast,fallback=fallback,constant=constant),dict(
        original_channels=len(compiled),original_terms=source_terms,
        character_channels_before_merge=before,character_channels=len(fast),
        character_generators=sum(len(basis) for *_,basis in fast),
        identity_channels_dropped=identities,fallback_channels=len(fallback),
        retained_constant_factor=constant)


def character_factors(model,states,emask,original_factors):
    outer_cache={};inner_cache={};factors=[]
    for scope,trivial,nontrivial,basis in model['fast']:
        full=any(k for k,_,_ in basis)
        size=len(states) if full else 1
        parity=np.zeros((size,1<<len(scope)),dtype=np.bool_)
        for km,rm,e in basis:
            if full:
                if km not in outer_cache:
                    outer_cache[km]=(np.bitwise_count(states&km)&1).astype(np.bool_)
                outer=outer_cache[km]
            else:
                outer=np.zeros(1,dtype=np.bool_)
            ik=(len(scope),rm)
            if ik not in inner_cache:
                ix=np.arange(1<<len(scope),dtype=np.uint32)
                inner_cache[ik]=(np.bitwise_count(ix&rm)&1).astype(np.bool_)
            parity|=outer[:,None]^inner_cache[ik][None,:]^bool((e&emask).bit_count()&1)
        vals=np.where(parity,nontrivial,trivial).reshape((size,)+(2,)*len(scope),order='F')
        factors.append((scope,vals))
    factors.extend(original_factors(model['fallback'],states,emask))
    if model['constant'] != 1.:
        factors.append(((),np.array([model['constant']])))
    return factors
