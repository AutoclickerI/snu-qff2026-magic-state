#!/usr/bin/env python3
"""Exhaust all seven disjoint axis-aligned unit 2x2 tiles on the 6x6 grid.

Only a STATIC connected eight-cell ancillary region is tested. This is not
a no-go for moving helpers, teleportation, borrowing code cells, gauge changes,
non-unit-square inner encodings, or a different terminal contraction.
"""
from itertools import combinations
from pathlib import Path
import json

N=36
def neighbours(q):
    r,c=divmod(q,6)
    return {6*a+b for a,b in ((r-1,c),(r+1,c),(r,c-1),(r,c+1))
            if 0<=a<6 and 0<=b<6}
sq=[]
for r in range(5):
    for c in range(5):
        cells={6*r+c,6*r+c+1,6*(r+1)+c,6*(r+1)+c+1}
        near=set().union(*(neighbours(q) for q in cells))-cells
        sq.append((cells,sum(1<<q for q in cells),near))

def components(cells):
    remain=set(cells);out=[]
    while remain:
        seed=remain.pop();comp={seed};stack=[seed]
        while stack:
            fresh=neighbours(stack.pop())&remain
            remain-=fresh;comp|=fresh;stack.extend(fresh)
        out.append(comp)
    return sorted(out,key=lambda c:(-len(c),sorted(c)))

all_receipts=[]
for comb in combinations(range(25),7):
    used=0
    for j in comb:
        if used&sq[j][1]:break
        used|=sq[j][1]
    else:
        free={q for q in range(N) if not (used>>q&1)}
        comps=components(free)
        degree=[len(sq[j][2]&free) for j in comb]
        comp_cover=[[i for i,j in enumerate(comb) if sq[j][2]&cc] for cc in comps]
        all_receipts.append(dict(tile_ids=list(comb),tiles=[sorted(sq[j][0]) for j in comb],
            free=sorted(free),components=[sorted(c) for c in comps],
            free_connected=len(comps)==1,tile_free_degree=degree,
            tiles_touching_any_free=sum(bool(d) for d in degree),
            component_tile_coverage=comp_cover))

connected=[r for r in all_receipts if r['free_connected']]
full=[r for r in connected if r['tiles_touching_any_free']==7]
best=max(connected,key=lambda r:(r['tiles_touching_any_free'],sum(r['tile_free_degree'])),default=None)
best_any=max(all_receipts,key=lambda r:(min(r['tile_free_degree']),sum(r['tile_free_degree'])))
summary=dict(grid=[6,6],unit_squares=25,tiles=7,unused_cells=8,
    disjoint_packings=len(all_receipts),connected_free_packings=len(connected),
    connected_free_packings_touching_all_seven=len(full),
    max_covered_tiles_with_all_eight_free_connected=max((r['tiles_touching_any_free'] for r in connected),default=0),
    connected_coverage_histogram={str(k):sum(r['tiles_touching_any_free']==k for r in connected) for k in range(8)},
    best_connected=best,best_unrestricted=best_any,
    scope='Fixed seven disjoint unit-square tiles, no data/helper movement, and ancillas restricted to the eight unused cells. A necessary adjacency condition only, not a gate-synthesis or fault-tolerance certificate.',
    not_excluded=['mobile helpers','borrowing code cells','gauge changes','teleportation','non-unit-square encoding','other terminal contraction'])
dst=Path(__file__).with_suffix('.json')
dst.write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
