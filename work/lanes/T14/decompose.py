"""Split v36c into the data/prefix component and the A, B/C and readout suffix components.

Wire lives: a qubit's timeline is cut after every measurement and before every reset. CX units join the two
lives they touch, except the round's D->A and B->D CXs. The component holding the data lives entering the round
is the prefix (injection, cat check, blue check, hops, data guards and echoes); every other unit is suffix.
"""
import sys, json
from collections import defaultdict
sys.path.insert(0, '.')
from qcirc import parse

D = [0, 20, 7, 10, 3, 22, 21]
A = [1, 14, 8, 9, 2, 16, 15]
B = [6, 26, 13, 11, 4, 23, 27]


def lives(units):
    order = sorted(range(len(units)), key=lambda i: units[i]['t'])
    cur, nlife, life_of = {}, 0, {}
    ended = set()
    for i in order:
        u = units[i]
        ls = []
        for q in u['q']:
            if q not in cur or u['k'] in ('R', 'RX') or q in ended:
                cur[q] = (q, nlife); nlife += 1; ended.discard(q)
            ls.append(cur[q])
        life_of[i] = ls
        if u['k'] in ('M', 'MX'):
            ended.add(u['q'][0])
    return life_of


def is_round(u):
    if u['k'] != 'CX' or u['t'] < 43:
        return False
    c, t = u['q']
    return (c in D and t in A) or (c in B and t in D)


def split(units):
    life_of = lives(units)
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for i, u in enumerate(units):
        for l in life_of[i]:
            find(l)
        if u['k'] == 'CX' and not is_round(u):
            a, b = life_of[i]
            parent[find(a)] = find(b)
    # data lives entering the round
    entry = set()
    for i, u in enumerate(units):
        if is_round(u):
            for q, l in zip(u['q'], life_of[i]):
                if q in D:
                    entry.add(find(l))
    comp = defaultdict(list)
    for i, u in enumerate(units):
        comp[find(life_of[i][0])].append(i)
    return life_of, find, entry, comp


if __name__ == '__main__':
    units, dets = parse(open(sys.argv[1]).read())
    life_of, find, entry, comp = split(units)
    print('data entry components', len(entry))
    for root, idx in sorted(comp.items(), key=lambda kv: min(units[i]['t'] for i in kv[1])):
        qs = sorted({q for i in idx for q in units[i]['q']})
        ts = [units[i]['t'] for i in idx]
        cx = sum(units[i]['k'] == 'CX' for i in idx)
        bits = sorted(units[i]['b'] for i in idx if units[i]['b'] is not None)
        tag = 'PREFIX' if root in entry else ''
        print(tag, 'units', len(idx), 'cx', cx, 't', min(ts), max(ts), 'qubits', qs, 'bits', bits)
