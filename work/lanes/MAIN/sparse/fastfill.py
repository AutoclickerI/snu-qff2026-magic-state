"""Bitset min-fill elimination equal to sparse_walsh.minfill (same key (fill, degree, vertex), same order)."""


def minfill_adj(adj):
    """adj: dict vertex -> bitmask of neighbours (vertex ids are bit positions). Returns (work_entries, width)."""
    N = dict(adj)
    pc = int.bit_count

    def key(v):
        n = N[v]
        f = 0
        m = n
        while m:
            low = m & -m
            u = low.bit_length() - 1
            f += pc(n & ~N[u] & ~low)
            m ^= low
        return (f // 2, pc(n), v)

    keys = {v: key(v) for v in N}
    width = 0; cost = 0
    while keys:
        v = min(keys.values())[2]
        n = N.pop(v); del keys[v]
        d = pc(n)
        width = max(width, d); cost += 1 << d
        vb = ~(1 << v)
        m = n
        touched = n
        while m:
            low = m & -m
            u = low.bit_length() - 1
            N[u] = (N[u] | n) & ~low & vb
            m ^= low
        m = n
        while m:
            low = m & -m
            touched |= N[low.bit_length() - 1]
            m ^= low
        m = touched & vb
        while m:
            low = m & -m
            u = low.bit_length() - 1
            if u in keys:
                keys[u] = key(u)
            m ^= low
    return cost, width


def adj_of(scopes):
    adj = {}
    for s in scopes:
        mask = 0
        for v in s:
            mask |= 1 << v
        for v in s:
            adj[v] = adj.get(v, 0) | (mask & ~(1 << v))
    return adj
