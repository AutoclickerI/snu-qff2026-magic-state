"""Exhaustive layout enumeration for the high-tail data d0,d1,d3,d5.

For each subset of one-hop moves, enumerate all fresh destinations and all
three Bell edges.  A Bell edge is accepted when its two members cover every
plaquette data site for Z CNOT adjacency.  This is the finite layout space
searched by L2; extras are then added from vacated data sites/fresh neighbors.
"""
from itertools import combinations, product
from layout_model import DATA0, PLAQ, GRID, BELL0, Extra, LayoutModel, adj

TARGET=tuple(range(7))

def neighbors(q): return [(x,y) for x,y in GRID if adj(q,(x,y))]

def edge_list(occupied):
    return [(a,b) for a in GRID for b in GRID if a<b and adj(a,b) and a not in occupied and b not in occupied]

def covers(pair, positions, ds):
    return all(any(adj(q,positions[d]) for q in pair) for d in ds)

def layouts(max_moves=2):
    out=[]; seen=set(); base=set(DATA0)
    for r in range(max_moves+1):
      for moved in combinations(TARGET,r):
        opts=[]
        for d in moved:
            opts.append([q for q in neighbors(DATA0[d]) if q not in base or q in {DATA0[x] for x in moved}])
        for dests in product(*opts) if opts else [()]:
            pos=list(DATA0)
            for d,q in zip(moved,dests):pos[d]=q
            if len(set(pos))<7: continue
            # Destination must be fresh; allow old source only when its owner moved.
            oldowners={DATA0[x] for x in moved}
            if any(q in base and q not in oldowners for q in dests):continue
            occ=set(pos)
            all_edges=edge_list(occ)
            eds=[]
            for t,ds in enumerate(PLAQ):
                eds.append([e for e in all_edges if covers(e,pos,ds)])
            # choose disjoint Bell edges, excluding all old data sites (prep-before-move)
            choices=[]
            for t,ds in enumerate(PLAQ):
                choices.append(list(eds[t]))
            for bells in product(*choices):
                if len(set(q for e in bells for q in e))<6:continue
                key=(tuple(pos),tuple(bells))
                if key in seen:continue
                seen.add(key)
                moves={d:[q] for d,q in zip(moved,dests)}
                try:m=LayoutModel(moves=moves,bells=bells)
                except ValueError:continue
                out.append((moved,dests,bells,m))
    return out

if __name__=='__main__':
  for lim in (0,1,2,3,4):
    xs=layouts(lim); print('max_moves',lim,'layouts',len(xs),'distinct_pos',len({(x[1],x[2]) for x in xs}))
