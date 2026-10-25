"""One-cell coherent move of the retained helper, reusing a measured block.
Transforms the winning unmeasured triangle into a square with a leaf within
35 qubits. The move is two CXs, with reset and a final zero check; all are noisy.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json
from build_candidates import H,Circuit,save
c=Circuit();c.magic();blocks=[list(range(7*b,7*b+7)) for b in range(5)]
for b in range(1,5):c.prep(blocks[b],3,b==1)
D,A,B,C,E=blocks;R=7
for d,a,b,cc,e in zip(*blocks):
    c.cx(R,d,a);c.cx(R,b,cc);c.cx(R+1,b,d);c.cx(R+1,cc,e)
    c.reset(R+2,a);c.cx(R+3,cc,a);c.cx(R+4,a,cc);c.cx(R+5,a,d)
c.readblock(R+1,A)
c.readblock(R+2,B,True)
c.readblock(R+2,E,False,True)
for cc in C:c.dets.append([c.read(R+5,cc)])
t=dict(json.loads((H/'choices.json').read_text())['unmeasured']);t['second_order_p2']=None
save(c,'hop_unmeasured',t,blocks,noise_start=R,round_start=R,change='one-cell coherent helper handoff using the already measured A block; 2 CX + reset + zero read, 3 extra native ticks',hop_graph_edges=[[0,1],[0,2],[1,3],[2,3],[3,4]])
