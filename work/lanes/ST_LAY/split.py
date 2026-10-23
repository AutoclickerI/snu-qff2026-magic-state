import itertools
from lay3 import nbrs
def conn(S):
    S=set(S); 
    if not S: return False
    st=[next(iter(S))]; seen={st[0]}
    while st:
        u=st.pop()
        for v in nbrs(u):
            if v in S and v not in seen: seen.add(v); st.append(v)
    return seen==S
def split(lay, maxh=8):
    roles=set(sum((lay[k] for k in "dabc"),[]))
    free=[q for q in range(36) if q not in roles]
    best=None
    for asg in itertools.product(range(4),repeat=len(free)):  # 0 none
        h=[[q for q,a in zip(free,asg) if a==j] for j in (1,2,3)]
        if all(conn(lay[k]+hh) for k,hh in zip("abc",h)):
            n=sum(map(len,h))
            if best is None or n<best[0]: best=(n,h)
    return best
if __name__=="__main__":
    L5={'d': [0, 20, 7, 10, 3, 22, 21], 'a': [1, 14, 8, 9, 2, 16, 15], 'b': [6, 26, 13, 11, 4, 23, 27],'c': [12, 25, 19, 17, 5, 29, 28]}
    print(split(L5))
