"""X/Y-observable Clifford-round loss; no matching of distinct DEM marginals.

The identity 1-F = (Pr(decoded X flips|accept)+Pr(decoded Y flips|accept))/2
is exact for a Pauli channel on the encoded T state and state-independent acceptance.
The `exact_loss` entry point truncates the fault expansion after order two. For FT
rounds this is simply the accepted harmful pairs. Stim's DEM probabilities retain
their finite-p conversion, so the returned number can contain O(p^3) terms; it is
not an all-orders physical prediction.
The separate `conditional_loss` entry point sums all orders by an exact Walsh
transform of the two independent DEM parity distributions.
There is no approximate-disjoint option; the supported noise admits an exact DEM.

Observables 0..2: X stabilizer flips; 3..5: Z stabilizer flips; 6: the
transversal X^7 or Y^7 parity change, including any declared Pauli frame.
"""
from collections import defaultdict

import stim


def mechanisms(circuit):
    out = defaultdict(list)
    dem = circuit.detector_error_model(decompose_errors=False)
    for inst in dem.flattened():
        if inst.type != "error":
            continue
        det, mask = 0, 0
        for target in inst.targets_copy():
            if target.is_relative_detector_id():
                det ^= 1 << target.val
            elif target.is_logical_observable_id():
                mask ^= 1 << target.val
            else:
                raise ValueError(f"Unexpected DEM target {target}")
        out[det].append((inst.args_copy()[0], mask))
    return out


def decoded_flip(mask, logical):
    sx, sz = bool(mask & 7), bool(mask & 56)
    return ((mask >> 6) & 1) ^ (sx if logical == "X" else sx ^ sz)


def marginal_loss(circuit, logical):
    if logical not in ("X", "Y"):
        raise ValueError("Use the transversal X or Y logical probe")
    groups = mechanisms(circuit)
    flip = lambda m: decoded_flip(m, logical)
    silent = groups.get(0, ())
    first = sum(p for p, mask in silent if flip(mask))
    pairs = 0.0
    for events in groups.values():
        for i, (pi, mi) in enumerate(events):
            for pj, mj in events[:i]:
                if flip(mi ^ mj):
                    pairs += pi * pj
    # Conditional second-order expansion. This correction vanishes for FT rounds.
    normalization = -first * sum(p for p, _ in silent)
    normalization += sum(p * p for p, mask in silent if flip(mask))
    return {"first": first, "pairs": pairs, "normalization": normalization,
            "second": pairs + normalization, "cost": first + pairs + normalization,
            "mechanisms": sum(map(len, groups.values()))}


def exact_loss(circ_x, circ_y, *, details=False):
    x, y = marginal_loss(circ_x, "X"), marginal_loss(circ_y, "Y")
    cost = (x["cost"] + y["cost"]) / 2
    if details:
        return {"cost": cost, "first": (x["first"] + y["first"]) / 2,
                "second": (x["second"] + y["second"]) / 2, "x": x, "y": y}
    return cost


def logical_y(circuit):
    """Replace the two seven-body logical MPPs in an X/Z probe by Y^7.

    Pass the Z probe for teleportation: Y needs the same X-frame correction.
    Any other observable-frame transformation is the caller's responsibility.
    """
    out, count = stim.Circuit(), 0
    for inst in circuit.flattened():
        targets = inst.targets_copy()
        if inst.name == "MPP":
            products, product = [], []
            for target in targets:
                if product and not target.is_combiner and not product[-1].is_combiner:
                    products.append(product)
                    product = []
                product.append(target)
            if product:
                products.append(product)
            new = []
            for product in products:
                paulis = [t for t in product if not t.is_combiner]
                if len(paulis) == 7:
                    count += 1
                    product = [stim.target_y(t.value, invert=t.is_inverted_result_target)
                               if not t.is_combiner else t for t in product]
                new.extend(product)
            targets = new
        out.append(inst.name, targets, inst.gate_args_copy())
    if count != 2:
        raise ValueError(f"Expected two transversal seven-body logical MPPs, got {count}")
    return out


def conditional_marginal(circuit, logical):
    """All-orders accepted flip probability via the exact independent DEM.

    A Walsh transform evaluates the distribution on detector+observable parity
    bits. No physical-fault pairing is inferred. Noise-channel exclusivity is
    retained by Stim's exact independent decomposition, not an approximation.
    """
    import numpy as np
    nd=circuit.num_detectors
    n=nd+7
    if n>24:
        raise ValueError(f'{n} parity bits exceed this explicitly bounded dense evaluator')
    weights=np.zeros(1<<n)
    for det,events in mechanisms(circuit).items():
        for p,mask in events:
            weights[det | (mask<<nd)] += np.log1p(-2*p)
    def fwht(a):
        h=1
        while h<len(a):
            v=a.reshape(-1,2*h)
            l=v[:,:h].copy();r=v[:,h:].copy()
            v[:,:h]=l+r;v[:,h:]=l-r
            h*=2
        return a
    total=weights.sum()
    phi=np.exp((total-fwht(weights))/2)
    probs=fwht(phi)/(1<<n)
    accepted=probs[::1<<nd]
    acc=float(accepted.sum())
    bad=float(sum(p for mask,p in enumerate(accepted) if decoded_flip(mask,logical)))
    return dict(cost=bad/acc,acceptance=acc,unconditional=bad,parity_bits=n)


def conditional_loss(circ_x,circ_y,*,details=False):
    """Exact all-orders Clifford-round infidelity conditioned on acceptance."""
    x=conditional_marginal(circ_x,'X');y=conditional_marginal(circ_y,'Y')
    if abs(x['acceptance']-y['acceptance'])>1e-10:
        raise ValueError('X/Y probe acceptance differs; state-independent premise fails')
    r=dict(cost=(x['cost']+y['cost'])/2,acceptance=x['acceptance'],x=x,y=y)
    return r if details else r['cost']


def gmodel_probes(model, assign, orient):
    """Drop-in probe construction for an existing GModel, without modifying it.

    Pass the returned pair to exact_loss (order two) or conditional_loss (all
    orders). This preserves GModel's existing ideal-input round/noise boundary.
    """
    import gmodel as G
    from qcirc import Circ
    from tprep.noise import STANDARD, apply_noise
    from tprep.qasm import to_stim
    c=Circ();c.g('id',*[G.P(q) for q in G.DATA0])
    model.emit(c,assign,orient)
    bit_check={b:(t if B=='X' else 3+t) for (t,B),bits in model.checks.items() for b in bits}
    c.detectors=[];c=c.rescheduled(lazy_init=True)
    native,errors=to_stim(c.text())
    if errors:raise ValueError('; '.join(errors))
    noisy=apply_noise(native,1e-3,STANDARD)
    bits=[b for kind,qs,b in c.sops if kind in ('M','MX')]
    return tuple(model._full(noisy,bits,bit_check,L) for L in 'XY')
