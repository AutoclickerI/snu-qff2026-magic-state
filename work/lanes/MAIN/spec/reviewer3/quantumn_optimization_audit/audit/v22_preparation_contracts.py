"""Finite GF(2) checks for fresh BC endpoint and punctured-C candidates.
No full noisy score or full-layout feasibility is asserted.
"""
from itertools import combinations, product
import json

GENS = [0b1010101, 0b1100110, 0b1111000]
ALL = 127

def span(gs):
    out = {0}
    for g in gs:
        out |= {v ^ g for v in tuple(out)}
    return out

def rank(gs):
    return len(span(gs)).bit_length() - 1

S = span(GENS)
SIG = lambda e: sum(((e & g).bit_count() % 2) << i for i, g in enumerate(GENS)) | ((e.bit_count() % 2) << 3)
LOGICAL = lambda e: (e.bit_count() % 2) ^ int(bool(SIG(e) & 7))

def gauge_endpoint():
    # C's Z-only instrument cannot distinguish any state supported on S.
    subspaces = {frozenset(span(gs)) for n in range(4) for gs in combinations(sorted(S - {0}), n)}
    assert len(subspaces) == 16
    counts = {}
    for U in subspaces:
        k = len(U).bit_length() - 1
        counts[k] = counts.get(k, 0) + 1
        assert U <= S
        # Accepted terminal C measurements are independent of the B word.
        for b in S:
            for c in U:
                assert SIG(c) == 0
    before = {(b, c) for b in S for c in S}
    after = {(b, c ^ b) for b, c in before}
    assert before == after
    return dict(C_gauge_subspaces_by_dimension=counts,
                total_endpoint_CSS_subspaces=16,
                allowed_total_X_ranks=[3,4,5,6],
                transversal_B_to_C_preserves_current_target=True,
                target_constraints='B: all 7 stabilizers; C: four Z checks only',
                caveat='Full circuit-level fault constraints must be imposed at this new endpoint.')

def punctured_verifier():
    all_cases = []
    for omitted in range(7):
        bit = 1 << omitted
        W = span(GENS + [bit])
        assert len(W) == 16
        checks = [h for h in span(GENS + [ALL]) if h and not h & bit]
        assert len(checks) == 7 and rank(checks) == 3
        basis = min((gs for gs in combinations(checks, 3) if rank(gs) == 3),
                    key=lambda gs: (sum(h.bit_count() for h in gs), gs))
        # A uniform |W> factors |+> on omitted C and |puncture(S)> elsewhere.
        Cp = {c & ~bit for c in S}
        assert len(Cp) == 8
        assert W == {c ^ x for c in Cp for x in (0, bit)}
        # For every measurement record m with nonzero ideal amplitude,
        # K_m(b) is constant across all codewords b, hence preserves arbitrary
        # superpositions and reference entanglement within the B code support.
        for m in range(128):
            if m & bit: continue
            indicators = [int((m ^ b) & ~bit in Cp) for b in S]
            assert len(set(indicators)) == 1
        accepted = []
        for e in range(128):
            accepts = all((h & e).bit_count() % 2 == 0 for h in basis)
            assert accepts == (e in W)
            if accepts:
                assert LOGICAL(e) == 0
                accepted.append(e)
        all_cases.append(dict(omitted=omitted,checks=[list(i for i in range(7) if h>>i&1) for h in basis],
                              accepted_X_patterns=len(accepted),harmful_accepted_X_patterns=0))
    # Explicit 6-CX, 2-layer nearest-neighbor encoder for omitted code index 6.
    physical=[7,9,8,14,13,15]
    pivots=[7,9,14]
    layers=[[(7,8),(9,15),(14,13)],[(7,13),(9,8),(14,15)]]
    values={q:0 for q in physical}
    for j,q in enumerate(pivots):values[q]=1<<j
    for layer in layers:
        assert len({q for gate in layer for q in gate})==2*len(layer)
        for u,v in layer:
            assert abs(u//6-v//6)+abs(u%6-v%6)==1
            values[v]^=values[u]
    produced=set()
    for x in range(8):
        produced.add(sum(((values[q]&x).bit_count()%2)<<i for i,q in enumerate(physical)))
    assert produced == {c & 63 for c in S}
    return dict(all_omissions=all_cases,proof_cases=7*128,
                witness=dict(C_code_order=physical,omit=6,pivots=pivots,CX_layers=layers,CX=6,depth=2),
                caveat='B preparation, full placement, extra exposure on omitted B_i, and all noise still require evaluation.')

def partial_clean():
    representatives={SIG(e):e for e in range(128)}
    dangerous=sorted(s for s,e in representatives.items() if LOGICAL(e))
    benign_nonzero=sorted(s for s,e in representatives.items() if not LOGICAL(e) and s)
    assert len(dangerous)==8 and len(benign_nonzero)==7
    assert benign_nonzero==[8|(i+1) for i in range(7)]
    for i,s in enumerate(benign_nonzero):
        assert all(LOGICAL(e)==0 for e in range(128) if SIG(e)==s)
    return dict(hard_forbidden_logical_classes=dangerous,
                optional_correctable_classes=benign_nonzero,
                partial_clean_policies=2**7,
                caveat='Zero single-fault loss does not guarantee a finite-p improvement; price malignant pairs/triples.')

if __name__=='__main__':
    print(json.dumps(dict(endpoint=gauge_endpoint(),puncture=punctured_verifier(),partial_clean=partial_clean()),indent=2))
