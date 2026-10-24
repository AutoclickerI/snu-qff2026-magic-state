"""All-orders, all-channel counterfactual noise ablations in one reverse pass.

This is an evaluator diagnostic, NOT a physical gate deletion. For each original
independent channel j, scale its total error probability by lambda_j, leaving
its conditional Pauli distribution unchanged. Every unnormalized observable is
multiaffine in the lambdas. Consequently its derivative gives its EXACT value
with one entire noise channel made perfect. No Taylor truncation in physical p
is involved. The sparse-kernel cutoff and floating arithmetic caveats of the
parent evaluator still apply.
"""
from pathlib import Path
import sys, json, time
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'audit/reaudit_evaluation/portable'))
import sparse_walsh as sw


def reduce_to(grad, union, scope, shape):
    """Undo broadcasting from a factor's tensor into a product tensor."""
    axes = tuple(i + 1 for i, q in enumerate(union) if q not in scope)
    if axes:
        grad = grad.sum(axis=axes)
    if shape[0] == 1 and grad.shape[0] != 1:
        grad = grad.sum(axis=0, keepdims=True)
    return grad.reshape(shape)


def contract_adjoint(factors, order, weights):
    """Value and derivatives for independently scaling every input channel.

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
        n = max(arrays[i].shape[0] for i in children)
        product = np.ones((n,) + (2,) * len(union))
        for i in children:
            sh = (arrays[i].shape[0],) + tuple(2 if u in scopes[i] else 1 for u in union)
            product *= arrays[i].reshape(sh)
        axis = 1 + union.index(v)
        result = product.mean(axis=axis)
        parent = len(arrays)
        arrays.append(result)
        scopes.append(tuple(u for u in union if u != v))
        tape.append((parent, children, union, axis, product))
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
        grads[i] = g if len(a) != 1 else np.array([g.sum()])
    for parent, children, union, axis, product in reversed(tape):
        gp = np.expand_dims(grads.pop(parent), axis) * (0.5 * product)
        for i in children:
            sh = (arrays[i].shape[0],) + tuple(2 if u in scopes[i] else 1 for u in union)
            g = reduce_to(gp / arrays[i].reshape(sh), union, scopes[i], arrays[i].shape)
            grads[i] = g
    # F_j(lambda)=1 + lambda*(F_j(1)-1), exactly.
    derivatives = np.array([float(np.sum(grads[i] * (arrays[i] - 1))) for i in range(initial)])
    return value, derivatives, peak


def toy_check():
    rng = np.random.default_rng(2718)
    scopes = [(0, 2), (1, 2), (0, 1), (), (2,)]
    factors = [(s, 0.9 + 0.1*rng.random((1 if i % 2 else 5,) + (2,) * len(s)))
               for i, s in enumerate(scopes)]
    weights = rng.normal(size=5)
    order = [0, 1, 2]
    v, grad, _ = contract_adjoint(factors, order, weights)
    direct = float(weights @ sw.contract_selector(list(factors), order, 5)[0])
    errs = []
    for j in range(len(factors)):
        changed = list(factors)
        changed[j] = (changed[j][0], np.ones_like(changed[j][1]))
        v0 = float(weights @ sw.contract_selector(changed, order, 5)[0])
        errs.append(abs(v0 - (v-grad[j])))
    assert abs(v-direct) < 1e-12 and max(errs) < 1e-12
    return dict(value_error=abs(v-direct), max_exact_ablation_error=max(errs))


def run(stem, outfile, nkeys=72):
    start = time.perf_counter()
    m, eng, groups, nd, ks, psi, where, _ = sw.prepare(stem, True)
    compiled = sw.compile_channels(m, groups, nd, ks)
    order = sw.minfill([set(s) for s, _, _ in compiled])['order']
    rows = []
    gradients = []
    channel_ids = list(groups)
    max_check_error = 0.
    for k, key in enumerate([None] + eng.keys[:nkeys]):
        ts = time.perf_counter()
        states, weights, omission = sw.sparse_kernel(eng, ks, psi, where, key)
        factors = sw.factors_for(compiled, states, 0 if key is None else sw.emask_for(key))
        weights = weights / (1 << len(ks))
        value, grad, peak = contract_adjoint(factors, order, weights)
        # First three moments: actual full contractions at four independently
        # chosen perfect-channel interventions, no finite-difference approximation.
        if k < 3:
            for j in [0, len(factors)//3, 2*len(factors)//3, len(factors)-1]:
                changed = list(factors)
                changed[j] = (changed[j][0], np.ones_like(changed[j][1]))
                v0 = float(weights @ sw.contract_selector(changed, order, len(states))[0])
                max_check_error = max(max_check_error, abs(v0 - value + grad[j]))
        rows.append(dict(key=key, value=value, omission_bound=omission, peak_elements=peak,
                         seconds=time.perf_counter()-ts))
        gradients.append(grad)
        print(json.dumps(dict(moment=k, key=key, value=value, seconds=rows[-1]['seconds'])), flush=True)
    out = dict(scope=__doc__, source=str(stem), channels=len(channel_ids), moments=rows,
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
    stem = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'quantumn_review5/work/lanes/MAIN/v30f'
    count = int(sys.argv[2]) if len(sys.argv)>2 else 72
    run(stem, HERE/f'v30f_adjoint_{count}.json', count)
