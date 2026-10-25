import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,hashlib,subprocess,sys
from build_candidates import H,Circuit,save

def build(t,name):
    c=Circuit();c.magic();bs=[list(range(7*b,7*b+7)) for b in range(t['n'])]
    for b,typ in enumerate(t['types'][1:],1):
        if typ<2:c.prep(bs[b],3,typ==1)
        elif typ<4:
            for q in bs[b]:c.reset(6,q,typ==3)
        elif typ<6:
            for i,q in enumerate(bs[b]):c.reset(3,q,(i==0) if typ==4 else (i!=0))
            for k,l in enumerate([[(0,1)],[(0,2),(1,3)],[(0,4),(1,5),(2,6)]]):
                for a,z in l:c.cx(4+k,bs[b][a],bs[b][z]) if typ==4 else c.cx(4+k,bs[b][z],bs[b][a])
    for a,b in t['bell_pairs']:
        for qa,qb in zip(bs[a],bs[b]):c.reset(5,qa,True);c.reset(5,qb);c.cx(6,qa,qb)
    R=7;rec={}
    for k,l in enumerate(t['layers']):
        for a,b in l:
            for qa,qb in zip(bs[a],bs[b]):c.cx(R+k,qa,qb)
    for b in range(1,t['n']):
        if not((t['read_x']|t['read_z'])>>b&1):continue
        last=max(k for k,l in enumerate(t['layers']) if any(b in e for e in l))
        for i,q in enumerate(bs[b]):rec[7*b+i]=c.read(R+last+1,q,bool(t['read_x']>>b&1))
    for d in t['physical_detectors']:c.dets.append([v for q,v in rec.items() if d>>q&1])
    for axis in ('x','z'):
        bits=[v for q,v in rec.items() if t['physical_frame_'+axis]>>q&1]
        if bits:c.frames.append('// FRAME_'+axis.upper()+'(0) '+' '.join(f'c[{v}]' for v in bits))
    return save(c,name,t,bs,noise_start=R,round_start=R,change='physical product/cat/Bell search witness; perfect input/resources')

if __name__=='__main__':
    for p in sorted((H/'logs').glob('physical_*.jsonl')):
        for j,line in enumerate(p.read_text().splitlines()):
            t=json.loads(line);name=f'{p.stem}_{j}';build(t,name)
            r=subprocess.run([sys.executable,str(H/'price.py'),name,'1'],capture_output=True,text=True)
            (H/'logs'/f'{name}.process.log').write_text(r.stdout+r.stderr)
            print(r.stdout if not r.returncode else r.stderr,flush=True)
