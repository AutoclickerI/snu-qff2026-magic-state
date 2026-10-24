"""v35a circuit experiments; all writes and evaluator/cache outputs stay in FRESH."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,copy,contextlib,time,hashlib,importlib.util,traceback
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];D=HERE/'r35';D.mkdir(exist_ok=True)
AUD=ROOT/'work/lanes/MAIN/spec/reviewer6/quantumn_v31s_validated/audit'
sys.path[:0]=[str(HERE/'r35_vendor'),str(ROOT/'work/lanes/MAIN/sparse'),str(AUD/'review6_architecture'),str(ROOT/'work'),str(ROOT/'upstream/snu-qff2026-problem')]
import frontend as f
# Use MAIN's unchanged contraction, reviewer-6's SX-capable integer-Pauli frontend.
spec=importlib.util.spec_from_file_location('sparse35',HERE/'r35_vendor/sparse_walsh.py');sw=importlib.util.module_from_spec(spec);sys.modules['sparse35']=sw;spec.loader.exec_module(sw)
sw.__file__=str(D/'sparse35.py')
import xtim
CACHE=D/'.xtim_cache';CACHE.mkdir(exist_ok=True);xtim.cache_dir=str(CACHE);os.environ['XTIM_TWIRL_CACHE_DIR']=str(CACHE)
# Native emitter from architecture; it accepts SX through its generic gate branch.
spec=importlib.util.spec_from_file_location('emit35',HERE/'r35_vendor/circuit_io.py');io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
BASE=ROOT/'work/lanes/MAIN/v35a'
BASE_LOSS=4.393527676042078e-5

def load(stem):
 stem=Path(stem);md=json.loads(stem.with_suffix('.json').read_text());ops,dets=f.parse_current(stem.with_suffix('.qasm').read_text());return ops,dets,md

def emit(name,ops,dets,md,recipe):
 stem=D/name;ops=sorted(ops,key=lambda o:o.time)
 clean=dict(data_qubits=md['data_qubits'],CX=sum(o.kind=='CX' for o in ops),R=md.get('R'),native_depth=max(o.time for o in ops)+1,source=str(BASE.relative_to(ROOT)),recipe=recipe)
 io.emit(ops,dets,stem,clean)
 return stem

def certify(stem,singles=True):
 assert HERE in Path(stem).resolve().parents,stem
 ops,dets,md=load(stem);f.DATA=md['data_qubits'];m=f.make_model(ops,dets);e=f.Engine(m)
 A,N=e.ntable(0,0);phi=e.phi(0);stabs=[e.expect(phi,(e.B.express(x),e._w(z),c)) for x,z,c in m.gen_m]
 assert abs(A-1)<1e-10 and abs(N[0])<1e-10,(A,N[0])
 assert all(abs(s-1)<1e-10 for s in stabs),stabs
 native_times=[t for groups in m.steps for _,t in groups]
 assert native_times==[o.time for o in ops],[(i,o.time,native_times[i]) for i,o in enumerate(ops) if o.time!=native_times[i]]
 c1=0.;harm=[]
 if singles:
  for fault in m.faults:
   a,n=e.ntable(fault['s'],fault['d']);v=0 if n is None else fault['p']*n[fault['e']];c1+=v
   if v>1e-15:harm.append(fault['label'])
  assert not harm,harm
 r=dict(ideal_acceptance=A,ideal_loss=float(N[0]),stabilizers=stabs,detectors=len(dets),native_depth=max(native_times)+1,schedule_matches=True,singles_checked=singles,c1=c1 if singles else None,harmful_singles=harm if singles else None,sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest())
 Path(str(stem)+'.ideal.json').write_text(json.dumps(r,indent=2));return r

def price(stem,procs=7):
 assert HERE in Path(stem).resolve().parents,stem
 with Path(str(stem)+'.allorders.log').open('w') as log,contextlib.redirect_stdout(log):r=sw.run(stem,72,True,procs)
 Path(str(stem)+'.allorders.json').write_text(json.dumps(r,indent=2))
 return {k:r[k] for k in ('loss','acceptance','seconds','conditional_loss_kernel_omission_bound')}

def speed(stem,shots=50000):
 spec=importlib.util.spec_from_file_location('speed35',ROOT/'work/lanes/XTIM/speed_predict.py');sp=importlib.util.module_from_spec(spec);spec.loader.exec_module(sp);xtim.cache_dir=str(CACHE)
 r=sp.predict(str(stem),shots=shots);Path(str(stem)+'.speed.json').write_text(json.dumps(r,indent=2));return r

def sx_candidates():
 ops,dets,md=load(BASE);data=md['data_qubits'];A=[1,14,8,9,2,16,15]
 masks=[('full',data)]+[(f'q{q}',[q]) for q in data]+[(f'ex{q}',[x for x in data if x!=q]) for q in data]
 stems=[]
 for name,qs in masks:
  oo=copy.deepcopy(ops);changes=[]
  for q in qs:
   a=A[data.index(q)];at=max(o.time for o in oo if o.kind=='CX' and o.qs==(q,a))-1
   conflict=[o for o in oo if o.time==at and q in o.qs]
   if conflict:
    assert len(conflict)==1 and conflict[0].kind in ('T','TDG'),(q,at,conflict)
    assert not any(o.time==at-1 and q in o.qs for o in oo)
    conflict[0].time-=1;changes.append((q,at,at-1))
   assert not any(o.time==46 and q in o.qs for o in oo)
   oo.extend([f.Op('SX',(q,),at),f.Op('SXDG',(q,),46)])
  stems.append(emit('sx_'+name,oo,copy.deepcopy(dets),md,dict(sx_qubits=qs,retimings=changes)))
 (D/'sx_stems.json').write_text(json.dumps(list(map(str,stems)),indent=2));return stems

def screen(stems,procs=7):
 for stem in stems:
  stem=Path(stem);r=dict(stem=stem.name)
  try:
   r['ideal']=certify(stem)
   r['speed']=speed(stem)
   # Price full/SLOW for mechanism as well as fast variants.
   r['allorders']=price(stem,procs)
  except Exception as ex:r.update(error=repr(ex),trace=traceback.format_exc())
  with (D/'screen.jsonl').open('a') as log:log.write(json.dumps(r)+'\n')
  print(json.dumps({k:v for k,v in r.items() if k not in ('ideal','trace')}),flush=True)

if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='generate':print(json.dumps(list(map(str,sx_candidates()))))
 elif mode=='screen':screen(json.loads(Path(sys.argv[2]).read_text()),int(sys.argv[3]) if len(sys.argv)>3 else 7)
 elif mode=='inspect':
  ops,dets,md=load(BASE)
  for t in range(47):print(t,[(o.kind,o.qs,o.bit) for o in ops if o.time==t])
 elif mode=='base':
  ops,dets,md=load(BASE);screen([emit('base',ops,dets,md,dict(kind='control'))],int(sys.argv[2]) if len(sys.argv)>2 else 7)
