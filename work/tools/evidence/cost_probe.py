import json
from pathlib import Path
import sys
import time
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from qtools.evaluator import sparse_walsh as sw
from qtools.registry import load_registry


def span(vecs):
    piv = {}
    for v in vecs:
        while v:
            h = v.bit_length()-1
            if h not in piv:
                piv[h] = v
                break
            v ^= piv[h]
    return tuple(piv.values())


def work(compiled, states, order):
    from collections import defaultdict
    import numpy as np
    classes = {}
    def count(b):
        if b not in classes:
            rho = np.zeros(len(states), dtype=np.int64)
            for j, mask in enumerate(b):
                rho |= (np.bitwise_count(states & mask) & 1).astype(np.int64) << j
            classes[b] = len(np.unique(rho))
        return classes[b]
    pos = {v: i for i, v in enumerate(order)}
    groups = defaultdict(list)
    for entry in compiled:
        groups[min((pos[v] for v in entry[0]), default=len(pos))].append(entry)
    factors = []
    work = 0
    for entries in groups.values():
        scope = tuple(sorted(set().union(*(set(e[0]) for e in entries))))
        b = span([km for e in entries for km, _, _ in e[2]])
        work += count(b) * 2**len(scope) * len(entries)
        factors.append((scope, b))
    for v in order:
        bucket = [f for f in factors if v in f[0]]
        factors = [f for f in factors if v not in f[0]]
        if not bucket:
            continue
        union = tuple(sorted(set().union(*(set(s) for s, _ in bucket))))
        b = span([mask for _, bb in bucket for mask in bb])
        work += count(b) * 2**len(union) * len(bucket)
        factors.append((tuple(q for q in union if q != v), b))
    return work


if __name__ == '__main__':
    m,e,g,nd,ks,psi,where,_ = sw.prepare(HERE/'tests/fixtures'/sys.argv[1],True)
    states,_,_ = sw.sparse_kernel(e,ks,psi,where,None)
    for key, ops in load_registry()['bases'].items():
        c,elim=sw.compile_best(m,e,g,nd,ks,registry={'bases':{key:ops},'threshold':100},save=False)
        if elim['width']>14:
            continue
        cost=work(c,states,elim['order'])
        t=time.perf_counter();v,peak=sw.contract_quotient(c,states,0,elim['order'])
        print(json.dumps(dict(key=key,width=elim['width'],work=elim['work_entries'],quotient_work=cost,
                              seconds=time.perf_counter()-t,states=len(states))),flush=True)
