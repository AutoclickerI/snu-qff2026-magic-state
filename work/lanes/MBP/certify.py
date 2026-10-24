"""Finite algebra and geometry certificates used in REPORT."""
from mbp import *
from grid import transform,P0
def main():
    stabs=[]
    for mask in range(1,8):
        ss=set()
        for j in range(3):
            if mask>>j&1:ss^=set(GENS[j])
        stabs.append(ss)
    bases=[]
    for tri in itertools.combinations(range(1,8),3):
        if tri[0]^tri[1]^tri[2]==0:continue
        ss=[stabs[i-1] for i in tri]
        assert all(len(s)==4 for s in ss)
        assert all(len(a&b)==2 for a,b in itertools.combinations(ss,2))
        assert len(set.intersection(*ss))==1
        bases.append(tri)
    assert len(bases)==28
    quadruples={3:[],4:[]}
    for ss in itertools.combinations(range(1,8),4):
        wt=4 if __import__('functools').reduce(int.__xor__,ss)==0 else 3
        quadruples[wt].append(ss)
    assert {k:len(v) for k,v in quadruples.items()}=={3:28,4:7}
    def gd4(q,k):
        r,c=divmod(q,6)
        rr,cc=[(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
        return 6*rr+cc
    em=[];reps={(r,c):transform(0,r,c) for r in range(3) for c in range(2)}
    for k in range(8):
        hh,ww=(4,5) if k<4 else (5,4)
        for r in range(7-hh):
            for c in range(7-ww):
                mp=transform(k,r,c);hits=[]
                for (rr,cc),rp in reps.items():
                    for g in range(8):
                        if all(gd4(rp[q],g)==mp[q] for q in P0):hits.append((rr,cc,g))
                assert len(hits)==1
                em.append(dict(sym=k,row=r,col=c,representative=hits[0][:2],global_symmetry=hits[0][2]))
    assert len(em)==48
    vec=[1,2,0,0,0,0,0]
    for u,v in [(0,4),(1,5),(0,6),(1,6),(6,2)]:vec[v]^=vec[u]
    assert [{i for i,x in enumerate(vec) if x>>j&1} for j in range(2)]==[set(GENS[0]),set(GENS[1])]
    out=dict(independent_weight4_bases=bases,pairwise_intersection=2,triple_intersection=1,redundant_quadruples_by_dependency_weight=quadruples,
      direct_obstruction='Three distinct ancillas must all neighbour the common block cell. Among three square-grid neighbours of a cell, one pair is opposite; that pair has only one common neighbour, contradicting its required second shared block cell.',
      prefix_embeddings=em,partial_tree_output_rows=vec)
    (OUT/'algebra_geometry_certificate.json').write_text(json.dumps(out,indent=2)+'\n');print('28 bases, 48 embeddings, tree subspace: verified')
if __name__=='__main__':main()
