"""All-orders, all-channel counterfactual noise ablations in one reverse pass.

This is an evaluator diagnostic, NOT a physical gate deletion. For each original
independent channel j, scale its total error probability by lambda_j, leaving
its conditional Pauli distribution unchanged. Every unnormalized observable is
multiaffine in the lambdas. Consequently its derivative gives its EXACT value
with one entire noise channel made perfect. No Taylor truncation in physical p
is involved. The sparse-kernel cutoff and floating arithmetic caveats of the
parent evaluator still apply. Channels merged into one evaluator factor (equal
signature image) are attributed separately: a channel's table is chi_j(lambda)
= 1 + lambda*(chi_j - 1), and the merged factor is the product of its channels'.
"""
from pathlib import Path
import sys, json, time
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import sparse_walsh as sw


def reduce_to(grad, union, scope, batch):
    """Undo the gather of a factor over scope (batch rows) onto union's columns: sum the other union bits (and the
    selector when batch is 1)."""
    g = grad.reshape((len(grad),) + (2,) * len(union))
    axes = tuple(len(union) - k for k, q in enumerate(union) if q not in scope)
    if axes:
        g = g.sum(axis=axes)
    if batch == 1 and len(g) != 1:
        g = g.sum(axis=0, keepdims=True)
    return g.reshape(len(g), -1)


def contract_adjoint(factors, order, weights):
    """Value and its gradient with respect to every input factor array (sw.contract_selector's elimination).

    Inputs are positive characteristic factors at the small physical error
    rate used here. Dividing by an input factor avoids storing all partial
    products; a zero or negative factor is explicitly rejected.
    """
    scopes = [s for s, _ in factors]
    arrays = [a for _, a in factors]
    for a in arrays:
        if a.min() <= 0:
            raise ValueError('This memory-efficient reverse pass requires positive factors')
    initial = len(arrays)
    active = list(range(initial))
    tape = []
    peak = 0
    for v in order:
        children = [i for i in active if v in scopes[i]]
        if not children:
            continue
        active = [i for i in active if i not in children]
        union = tuple(sorted(set().union(*(set(scopes[i]) for i in children))))
        product = None
        for i in sorted(children, key=lambda i: arrays[i].shape[0]):
            product = sw.multiply(product, np.take(arrays[i], sw.columns(scopes[i], union), axis=1))
        p = union.index(v)
        pairs = product.reshape(len(product), -1, 2, 1 << p)
        result = 0.5 * (pairs[:, :, 0] + pairs[:, :, 1]).reshape(len(product), -1)
        parent = len(arrays)
        arrays.append(result)
        scopes.append(tuple(u for u in union if u != v))
        tape.append((parent, children, union, p, product))
        active.append(parent)
        peak = max(peak, product.size)
    vec = np.ones(len(weights))
    for i in active:
        assert not scopes[i]
        vec *= arrays[i].reshape(-1)
    value = float(np.dot(weights, vec))
    grads = {}
    for i in active:
        a = arrays[i].reshape(-1)
        g = weights * vec / a
        grads[i] = (g if len(a) != 1 else np.array([g.sum()])).reshape(-1, 1)
    for parent, children, union, p, product in reversed(tape):
        gp = grads.pop(parent)
        gp = (0.5 * product.reshape(len(product), -1, 2, 1 << p)) * gp.reshape(len(gp), -1, 1, 1 << p)
        gp = gp.reshape(len(gp), -1)
        for i in children:
            g = gp / np.take(arrays[i], sw.columns(scopes[i], union), axis=1)
            grads[i] = reduce_to(g, union, scopes[i], arrays[i].shape[0])
    return value, [grads[i] for i in range(initial)], peak


def channel_derivatives(compiled, states, emask, grads):
    """d value / d lambda_j for every source channel j, from the gradients of its merged factor binned by pattern t:
    the factor is chi[t] = prod_j chi_j[t] and d chi_j(lambda)/d lambda = chi_j - 1."""
    out = {}
    for (scope, chi, gens, sources), g in zip(compiled, grads):
        row, col = sw.patterns(scope, gens, states, emask, {})
        idx = row[:, None] ^ col[None, :]
        binned = np.bincount(np.broadcast_to(idx, g.shape).ravel(), g.ravel(), minlength=len(chi))
        for c, chi_c in sources:
            out[c] = float(np.sum(binned * chi / chi_c * (chi_c - 1)))
    return out


def toy_check():
    rng = np.random.default_rng(2718)
    scopes = [(0, 2), (1, 2), (0, 1), (), (2,)]
    factors = [(s, 0.9 + 0.1*rng.random((1 if i % 2 else 5, 1 << len(s))))
               for i, s in enumerate(scopes)]
    weights = rng.normal(size=5)
    order = [0, 1, 2]
    v, grads, _ = contract_adjoint(factors, order, weights)
    direct = float(weights @ sw.contract_selector(list(factors), order, 5)[0])
    errs = []
    for j in range(len(factors)):
        changed = list(factors)
        changed[j] = (changed[j][0], np.ones_like(changed[j][1]))
        v0 = float(weights @ sw.contract_selector(changed, order, 5)[0])
        errs.append(abs(v0 - (v - float(np.sum(grads[j] * (factors[j][1] - 1))))))
    assert abs(v-direct) < 1e-12 and max(errs) < 1e-12
    return dict(value_error=abs(v-direct), max_exact_ablation_error=max(errs))


def run(stem, outfile, nkeys=72):
    start = time.perf_counter()
    m, eng, groups, nd, ks, psi, where, _ = sw.prepare(stem, True)
    compiled, elim = sw.compile_best(m, eng, groups, nd, ks)   # detector basis moves coordinates, not channels
    order = elim['order']
    entry_of = {c: i for i, e in enumerate(compiled) for c, _ in e[3]}
    rows = []
    gradients = []
    channel_ids = list(groups)
    checked = [channel_ids[j] for j in (0, len(channel_ids)//3, 2*len(channel_ids)//3, len(channel_ids)-1)]
    max_check_error = 0.
    for k, key in enumerate([None] + eng.keys[:nkeys]):
        ts = time.perf_counter()
        states, weights, omission = sw.sparse_kernel(eng, ks, psi, where, key)
        emask = 0 if key is None else sw.emask_for(key)
        factors = sw.factors_for(compiled, states, emask)
        weights = weights / (1 << len(ks))
        value, grads, peak = contract_adjoint(factors, order, weights)
        deriv = channel_derivatives(compiled, states, emask, grads)
        # First three moments: actual full contractions with four independently
        # chosen channels made perfect inside their merged factors.
        if k < 3:
            for c in checked:
                i = entry_of[c]
                scope, chi, gens, sources = compiled[i]
                chi_c = dict(sources)[c]
                changed = list(factors)
                changed[i] = sw.factors_for([(scope, chi / chi_c, gens, [])], states, emask)[0]
                v0 = float(weights @ sw.contract_selector(changed, order, len(states))[0])
                max_check_error = max(max_check_error, abs(v0 - value + deriv[c]))
        rows.append(dict(key=key, value=value, omission_bound=omission, peak_elements=peak,
                         seconds=time.perf_counter()-ts))
        gradients.append(np.array([deriv[c] for c in channel_ids]))
        print(json.dumps(dict(moment=k, key=key, value=value, seconds=rows[-1]['seconds'])), flush=True)
    out = dict(scope=__doc__, source=str(stem), channels=len(channel_ids), factors=len(compiled), moments=rows,
               seconds=time.perf_counter()-start, toy=toy_check(),
               max_direct_counterfactual_moment_error=max_check_error,
               derivative_parameter='lambda_j multiplying the current total channel error probability')
    if nkeys == 72:
        A = rows[0]['value']; dA = gradients[0]
        O = sum(w*b*r['value'] for w,b,r in zip(eng.W,eng.beta,rows[1:]))
        dO = sum(w*b*g for w,b,g in zip(eng.W,eng.beta,gradients[1:]))
        N = (A-O)/2; dN = (dA-dO)/2
        base = N/A
        ablations = []
        for j, cid in enumerate(channel_ids):
            aa = float(A-dA[j]); nn = float(N-dN[j]); ll = nn/aa
            ablations.append(dict(channel=cid, original_noise=m.chans[cid],
                                  d_acceptance=float(dA[j]), d_unnormalized_loss=float(dN[j]),
                                  perfect_channel_acceptance=aa, perfect_channel_loss=ll,
                                  hypothetical_loss_reduction=base-ll))
        out.update(acceptance=A, loss=base, channel_ablations=ablations,
                   ranking=sorted(ablations, key=lambda x:-x['hypothetical_loss_reduction']))
    outfile.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['moments','channel_ablations','ranking']}), flush=True)
    return out


if __name__ == '__main__':
    print(json.dumps(toy_check()), flush=True)
    stem = Path(sys.argv[1]) if len(sys.argv)>1 else HERE.parent/'v36b'
    count = int(sys.argv[2]) if len(sys.argv)>2 else 72
    run(stem, HERE/f'{stem.name}_adjoint_{count}.json', count)
