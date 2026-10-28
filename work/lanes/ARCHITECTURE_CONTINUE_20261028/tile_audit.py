"""Verify the ideal four-qubit tile and enumerate 6x6 seven-square packings."""
import itertools
import json
import math
import numpy as np


def h(state, q):
    out = state.copy()
    for i in range(16):
        if not (i >> q) & 1:
            j = i | (1 << q)
            out[i], out[j] = (state[i] + state[j]) / math.sqrt(2), (state[i] - state[j]) / math.sqrt(2)
    return out


def cx(state, control, target):
    out = np.zeros_like(state)
    for i in range(16):
        out[i ^ (((i >> control) & 1) << target)] = state[i]
    return out


def encode(psi):
    # H=0, D=1, L=2, K=3; D holds the input.
    s = np.zeros(16, complex)
    s[0], s[2] = psi
    s = h(s, 0)
    for c, t in [(0, 1), (1, 3), (0, 2)]:
        s = cx(s, c, t)
    return s


def tile_check():
    error = 0.0
    for psi in [(1, 0), (0, 1), (1 / math.sqrt(2), 1j / math.sqrt(2))]:
        s = encode(psi)
        for c, t in [(1, 3), (0, 2), (0, 1)]:
            s = cx(s, c, t)
        target = np.zeros(16, complex)
        target[0], target[1], target[2], target[3] = psi[0]/math.sqrt(2), psi[0]/math.sqrt(2), psi[1]/math.sqrt(2), psi[1]/math.sqrt(2)
        error = max(error, float(np.max(np.abs(s-target))))
    return error


def neighbors(q):
    r, c = divmod(q, 6)
    return {6*rr+cc for rr, cc in [(r-1,c), (r+1,c), (r,c-1), (r,c+1)] if 0 <= rr < 6 and 0 <= cc < 6}


def connected(cells):
    seen = {next(iter(cells))}
    while True:
        nxt = seen | {v for u in seen for v in neighbors(u) & cells}
        if nxt == seen:
            return seen == cells
        seen = nxt


def packing_check():
    tiles = [{6*r+c, 6*r+c+1, 6*(r+1)+c, 6*(r+1)+c+1} for r in range(5) for c in range(5)]
    packings = connected_free = max_adjacent = 0
    witness = None
    for comb in itertools.combinations(range(25), 7):
        used = set()
        for i in comb:
            if used & tiles[i]:
                break
            used |= tiles[i]
        else:
            packings += 1
            free = set(range(36)) - used
            if connected(free):
                connected_free += 1
                adjacent = sum(bool({v for u in tiles[i] for v in neighbors(u)} & free) for i in comb)
                if adjacent > max_adjacent:
                    max_adjacent, witness = adjacent, [sorted(tiles[i]) for i in comb]
    return dict(packings=packings, connected_free=connected_free,
                max_tiles_adjacent_to_connected_free=max_adjacent, witness=witness)


if __name__ == '__main__':
    result = dict(max_tile_roundtrip_amplitude_error=tile_check(), geometry=packing_check())
    assert result['max_tile_roundtrip_amplitude_error'] < 1e-14
    print(json.dumps(result, indent=2))
