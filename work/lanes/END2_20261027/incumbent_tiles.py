"""Exact local tile packing with the incumbent data coordinates constrained.

This deliberately does not redo global seven-square packing. Each coordinate
stays at its incumbent cell except the explicitly selected one-hop moves.
All role choices and exclusions are enumerated, so an empty result is a finite
geometry certificate, not a time-limited solver outcome.
"""
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
D0 = [6, 20, 19, 10, 2, 22, 16]
B0 = [12, 26, 25, 11, 3, 28, 17]
A0 = [0, 14, 13, 9, 1, 21, 15]
C0 = [18, 27, 24, 5, 4, 29, 23]


def nb(q):
    return [p for p in range(36) if abs(q // 6 - p // 6) + abs(q % 6 - p % 6) == 1]


def options(d, all_data, *, square=True, fixed_b=None):
    rows = []
    for a in nb(d):
        for b in nb(d):
            if a == b or (fixed_b is not None and b != fixed_b):
                continue
            for c in nb(b):
                if len({d, a, b, c}) != 4:
                    continue
                is_square = c in nb(a)
                if square and not is_square:
                    continue
                cells = {d, a, b, c}
                if (cells - {d}) & set(all_data):
                    continue
                rows.append(dict(D=d, A=a, B=b, C=c, square=is_square,
                                 mask=sum(1 << q for q in cells)))
    return rows


def enumerate_packings(data, *, square=True, fixed_b=False, max_keep=32):
    if len(set(data)) != 7:
        return dict(count=0, reason='data collision', options=[])
    opts = [options(d, data, square=square,
                    fixed_b=B0[i] if fixed_b else None) for i, d in enumerate(data)]
    order = sorted(range(7), key=lambda i: len(opts[i]))
    count = 0
    best_score = None
    best = []
    by_squares = {}

    def visit(k, mask, chosen):
        nonlocal count, best_score, best
        if k == 7:
            count += 1
            rows = [chosen[i] for i in range(7)]
            nsq = sum(r['square'] for r in rows)
            by_squares[nsq] = by_squares.get(nsq, 0) + 1
            score = (-nsq, sum(r['B'] != B0[i] for i, r in enumerate(rows)),
                     sum(r['A'] != A0[i] for i, r in enumerate(rows)),
                     sum(r['C'] != C0[i] for i, r in enumerate(rows)))
            if best_score is None or score < best_score:
                best_score, best = score, []
            if score == best_score and len(best) < max_keep:
                best.append([{k: v for k, v in row.items() if k != 'mask'} for row in rows])
            return
        i = order[k]
        for row in opts[i]:
            if not mask & row['mask']:
                chosen[i] = row
                visit(k + 1, mask | row['mask'], chosen)
                del chosen[i]

    visit(0, 0, {})
    return dict(count=count, options=[len(o) for o in opts],
                counts_by_square_number=by_squares, best_score=best_score, best=best)


def main():
    out = dict(incumbent_D=D0, incumbent_B=B0, scope='six fixed data coordinates; D16 stays or takes one grid edge', cases=[])
    for last in [16] + nb(16):
        data = D0[:-1] + [last]
        for fixed_b in [True, False]:
            item = dict(data=data, fixed_b=fixed_b,
                        square_only=enumerate_packings(data, fixed_b=fixed_b),
                        mixed_square_tree=enumerate_packings(data, square=False, fixed_b=fixed_b))
            out['cases'].append(item)
            print(json.dumps(dict(data=data, fixed_b=fixed_b,
                                  square_count=item['square_only']['count'],
                                  mixed_count=item['mixed_square_tree']['count'],
                                  best_score=item['mixed_square_tree'].get('best_score'))), flush=True)
    (HERE / 'evidence' / 'incumbent_tiles.json').write_text(json.dumps(out, indent=2) + '\n')


def one_hop_neighborhood():
    """Minimum number of moved outputs, each moved at most one grid edge."""
    result = dict(incumbent_D=D0, scope='All data coordinates stay or take one edge; all B roles free.', levels=[])
    for moved_count in (1, 2):
        level = dict(moved_count=moved_count, tried=0, data_collisions=0, feasible_assignments=[])
        for indices in itertools.combinations(range(7), moved_count):
            for endpoints in itertools.product(*(nb(D0[i]) for i in indices)):
                data = D0[:]
                for i, q in zip(indices, endpoints):
                    data[i] = q
                level['tried'] += 1
                if len(set(data)) != 7:
                    level['data_collisions'] += 1
                    continue
                pack = enumerate_packings(data, square=True, fixed_b=False, max_keep=4)
                if pack['count']:
                    level['feasible_assignments'].append(dict(data=data, moves=list(zip(indices, [D0[i] for i in indices], endpoints)), **pack))
        result['levels'].append(level)
        print(json.dumps(dict(moved_count=moved_count, tried=level['tried'],
            collisions=level['data_collisions'], feasible_assignments=len(level['feasible_assignments']))), flush=True)
        if level['feasible_assignments']:
            result['minimum_moved_outputs'] = moved_count
            result['best'] = min(level['feasible_assignments'], key=lambda p: p['best_score'])
            print(json.dumps(result['best']), flush=True)
            break
    (HERE / 'evidence' / 'incumbent_onehop_neighborhood.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    main()
