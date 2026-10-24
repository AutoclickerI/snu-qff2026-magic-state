"""Shorten the diagonal parity network while preserving the7T CCZ polynomial.

BFS is exact only within this3-wire nearest-neighbor linear-parity walk
family, returning to the identity. No claim of global gate optimality.
The resulting full-target witness is checked by the unchanged judge.
"""
from collections import deque
import json
import toffoli_witness as w

start=((1,2,4),0);goal=((1,2,4),15)
previous={start:None};edge={};queue=deque([start]);need={3:1,5:2,6:4,7:8}
while queue:
    state=queue.popleft()
    if state==goal:break
    rows,seen=state
    for c,t in [(0,1),(1,0),(1,2),(2,1)]:
        new=list(rows);new[t]^=new[c]
        bit=need.get(new[t],0);nxt=(tuple(new),seen|bit)
        if nxt not in previous:
            previous[nxt]=state
            edge[nxt]=(c,t,new[t]if bit and not seen&bit else None)
            queue.append(nxt)
path=[];state=goal
while previous[state]is not None:
    path.append(edge[state]);state=previous[state]
path.reverse()

def ccz_gates():
    gates=[('t',(0,)),('t',(1,)),('t',(2,))]
    for c,t,parity in path:
        gates.append(('cx',(c,t)))
        if parity is not None:gates.append(('t'if parity==7 else'tdg',(t,)))
    return gates

if __name__=='__main__':
    (w.HERE/'nonlinear_AND_parity_walk.json').write_text(json.dumps(dict(scope=__doc__,CX=len(path),path=path,
        visited_states=len(previous)),indent=2)+'\n')
    w.ccz_gates=ccz_gates
    w.main('_8cx')
