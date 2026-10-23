import sys
sys.path.insert(0, '/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
from pathlib import Path
import tprep

base = Path('/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem/examples/injection.qasm').read_text()
layouts = [
    ([0,6,13,2,7,8,1], 'reference'),
    ([6,0,7,8,1,3,2], 'searched'),
    ([1,2,0,12,7,6,13], 'compact2'),
]
supports = [{0,2,4,6}, {1,2,5,6}, {3,4,5,6}]

def neigh(q):
    r, c = divmod(q, 6)
    return [x for x in (q-1,q+1,q-6,q+6)
            if 0 <= x < 36 and abs(x//6-r)+abs(x%6-c) == 1]

def route(start, goal, blocked):
    prev = {start: None}; queue = [start]
    for x in queue:
        if x == goal:
            p=[]
            while x is not None: p.append(x); x=prev[x]
            return p[::-1]
        for y in neigh(x):
            if y not in blocked and y not in prev:
                prev[y]=x; queue.append(y)
    raise RuntimeError

best=[]
for data, name in layouts:
    blocked=set(data)
    for si,support in enumerate(supports):
      for basis in ('X','Z'):
       for start in range(36):
        if start in blocked: continue
        lines=base.splitlines(); qreg=next(i for i,x in enumerate(lines) if x.startswith('qreg')); lines.insert(qreg+1,'creg c[1];')
        cur=start; lines.append(f'reset q[{cur}];')
        if basis=='X': lines.append(f'h q[{cur}];')
        nroute=0
        complete = True
        for i in sorted(support):
            goals=[x for x in neigh(data[i]) if x not in blocked]
            if not goals:
                complete = False
                break
            p=min((route(cur,g,blocked) for g in goals),key=len)
            for x,y in zip(p,p[1:]):
                lines.extend([f'cx q[{x}],q[{y}];',f'cx q[{y}],q[{x}];',f'cx q[{x}],q[{y}];'])
            nroute += 3*(len(p)-1); cur=p[-1]
            lines.append(f'cx q[{cur}],q[{data[i]}];' if basis=='X' else f'cx q[{data[i]}],q[{cur}];')
        if not complete: continue
        if basis=='X': lines.append(f'h q[{cur}];')
        lines.extend([f'measure q[{cur}] -> c[0];','// DETECTOR c[0]'])
        text='\n'.join(lines)+'\n'; rep=tprep.check(text,data,p=1e-3,shots=20000,seed=0)
        if rep.passed:
            row=(rep.score,rep.acceptance,name,si,basis,start,nroute,sum(x.startswith('cx') for x in lines),text);best.append(row)
            print(row[:8],flush=True)
best.sort(key=lambda x:x[0]); print('BEST',[x[:8] for x in best[:10]])
if best: Path('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/routed_one_best.qasm').write_text(best[0][8])
