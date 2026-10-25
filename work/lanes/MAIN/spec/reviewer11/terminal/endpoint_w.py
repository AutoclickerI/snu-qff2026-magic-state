"""Exact v36g endpoint S^7 plus constant logical-X frame screen.

Physical S gates replace the final seven data idles, preserving the noise and
schedule. On the Steane code S^7 is logical S-dagger; X_L S_L-dagger fixes T_L.
The unchanged sparse evaluator is reused after an exact output-Pauli pullback.
"""
from pathlib import Path
import copy,dataclasses,hashlib,json,multiprocessing as mp,sys,time
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
EVAL=ROOT/'quantumn_review11/work/lanes/MAIN/sparse'
sys.path.insert(0,str(EVAL))
import sparse_walsh as sw
fa=sw.fa
stem=ROOT/'quantumn_review11/work/lanes/MAIN/v36g'
start=time.perf_counter()
m,eng,groups,nd,ks,psi,where,dense=sw.prepare(stem,True)
original_generators=copy.deepcopy(m.gen_m)
oldX=m.Q['X',0,0];oldY=m.Q['Y',0,0]
# S-dagger X S = -Y, S-dagger Y S = X. Weight-four
# stabilizers transform X_g -> X_g Z_g with positive phase.
new_generators=[fa.mul(original_generators[i],original_generators[i+3])
                for i in range(3)]+original_generators[3:]
negY=(oldY[0],oldY[1],-oldY[2])
newQ={}
for key in m.Q:
    T,a,b=key;P=(0,0,1)
    for j,g in enumerate(new_generators):
        if (a|(b<<3))>>j&1:P=fa.mul(P,g)
    newQ[key]=fa.mul(P,negY if T=='X' else oldX)
m.Q=newQ;m.gen_m=new_generators;m.cxz=1   # FRAME_X(1); FRAME_Z(0)
for f in m.faults:
    e=f['e'];a=e&7;b=(e>>3)&7;x=(e>>6)&1;z=(e>>7)&1
    f['e']=(a^b)|(b<<3)|((x^z)<<6)|(z<<7)|(e&~255)
neweng=fa.Engine(m)
assert neweng.B.vecs==eng.B.vecs
A0,N0=neweng.ntable(0,0)
assert A0>1-1e-10 and abs(N0[0])<1e-10,(A0,N0[0])
compiled,elim=sw.compile_best(m,neweng,groups,nd,ks)
sw._CTX.update(eng=neweng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
with mp.get_context('fork').Pool(4) as pool:
    rows=list(pool.imap(sw._row,[None]+neweng.keys))
A=rows[0]['value'];O=sum(w*b*r['value'] for w,b,r in zip(neweng.W,neweng.beta,rows[1:]))
L=(A-O)/(2*A)
baseline=json.loads((EVAL/'v36g_canonical_sparse_result.json').read_text())
rec={'source_commit':'0ff9423a8e69c13998ab1baf7bf09c8e97558a60',
     'baseline_loss':baseline['loss'],'baseline_acceptance':baseline['acceptance'],
     'loss':L,'acceptance':A,'delta_loss':L-baseline['loss'],
     'ideal_acceptance':A0,'ideal_loss':float(N0[0]),'seconds':time.perf_counter()-start,
     'width':elim['width'],'moments':rows,
     'transformation':'Endpoint physical S on all outputs, FRAME_X(1), FRAME_Z(0); exact observable/signature pullback; final D1(p) unchanged.'}
(HERE/'endpoint_w_result.json').write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({k:v for k,v in rec.items() if k!='moments'},indent=2),flush=True)
# Emit a complete legal QASM, then ask the untouched official judge about it.
lines=stem.with_suffix('.qasm').read_text().splitlines();idx=next(i for i,l in enumerate(lines) if l.startswith('// DETECTOR'))
meta=json.loads(stem.with_suffix('.json').read_text());data=meta['data_qubits']
lines[idx:idx]=[f's q[{q}];' for q in data]
lines+=['// FRAME_X(1)','// FRAME_Z(0)']
qasm='\n'.join(lines)+'\n'
(HERE/'endpoint_w.qasm').write_text(qasm)
(HERE/'endpoint_w.json').write_text(json.dumps({'data_qubits':data,'source':'endpoint_w.py'},indent=2)+'\n')
OFFICIAL=ROOT/'official'
if not OFFICIAL.is_dir():
    OFFICIAL=ROOT/'deliverables/quantumn_v36c_handoff/official'
sys.path.insert(0,str(OFFICIAL))
import tprep
from tprep.qasm import to_stim
from tprep.noise import schedule
native,errors=to_stim(qasm);assert not errors,errors
_,steps,_=schedule(native)
report=tprep.check(qasm,data,shots=100000,seed=0)
official={'qasm_sha256':hashlib.sha256(qasm.encode()).hexdigest(),
          'native_depth':max(t for group in steps for _,t in group)+1,
          'report':dataclasses.asdict(report),'scope':'Official validity check only; sampled score not used for ranking.'}
(HERE/'endpoint_w_official.json').write_text(json.dumps(official,indent=2)+'\n')
print(json.dumps(official,indent=2),flush=True)
