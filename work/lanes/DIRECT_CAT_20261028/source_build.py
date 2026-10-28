import os,sys,json,collections
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
sys.path[:0]=[str(R/'work/lanes/NATIVE20261027'),str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027'),str(R/'work/tools')]
import rebuild,smallcat as s
from joint import emit
D,PA,PB,C,K=[list(range(i,i+7)) for i in (0,7,14,21,28)]
c=rebuild.Circuit();c.magic(D);c.prep(PA,3,True);c.prep(PB,3,False)
for d,a,b in zip(D,PA,PB):c.cx(7,d,a);c.cx(8,b,d)
c.cat(C,4);c.cat(K,6)
for j,(u,v) in enumerate(((0,1),(2,5),(4,6))):
 c.cx(8,C[u],PA[(0,1,3)[j]]);c.cx(9,C[v],PA[(0,1,3)[j]])
 c.cx(10,K[u],PB[(0,1,3)[j]]);c.cx(11,K[v],PB[(0,1,3)[j]])
c.readblock(10,PA)
for b in PB:c.add(9,f'h q[{b}];')
c.readblock(12,PB)
for d in D:c.add(9,f't q[{d}];')
for j,d in enumerate(D):c.cx(10,C[j],d);c.cx(12,K[j],d)
c.dets.append([c.read(11,q,True) for q in C]);c.dets.append([c.read(13,q,True) for q in K])
for d in D:c.add(13,f'tdg q[{d}];')
ops,dets=s.f.parse_current(c.text());base,bd=s.f.parse_current((R/'work/lanes/SOTA_DETECT_20261028/deep_hybrid_input.qasm').read_text());orig=collections.Counter((o.kind,o.qs,o.bit) for o in ops);bc=collections.Counter((o.kind,o.qs,o.bit) for o in base);print('source ops',len(ops),'input',len(base),'source_missing',sum((orig-bc).values()));print('missing',list((orig-bc).items())[:30]);print('detectors',dets)
(H/'source_original.qasm').write_text(c.text());(H/'source_original.json').write_text(json.dumps({'data_qubits':D,'abstract':True},indent=2)+'\n')
