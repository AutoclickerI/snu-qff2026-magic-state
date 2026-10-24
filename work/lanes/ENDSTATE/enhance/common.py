import os,sys,json,re,copy,time,hashlib,contextlib
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;P=H.parent;ROOT=H.parents[3]
sys.path[:0]=[str(ROOT/'work'),str(ROOT/'work/lanes/EVAL')]
import xtim,tprep
xtim.cache_dir=str(H/'.xtim_cache');os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
SUPPORTS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]

def load(stem):
 p=json.loads(Path(stem).with_suffix('.plan.json').read_text())
 for o in p['ops']:
  if o['name']=='CX':
   line=next(s for s in o['lines']if s.startswith('cx '));qs=list(map(int,re.findall(r'q\[(\d+)\]',line)));assert set(qs)==set(o['qs']);o['qs']=qs
 return p
def bit(p):return max(map(int,re.findall(r'c\[(\d+)\]','\n'.join(s for o in p['ops']for s in o['lines']))))+1

def save(p,name):
 p=copy.deepcopy(p);ops=sorted(p['ops'],key=lambda o:o['t']);times=sorted({o['t']for o in ops});ct={t:i for i,t in enumerate(times)};used=sorted({q for o in ops for q in o['qs']});bar='barrier '+','.join(f'q[{q}]'for q in used)+';';nb=bit(p)
 p['h']=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{nb}];'];lines=p['h'][:]
 for t in times:
  layer=[o for o in ops if o['t']==t];busy=[q for o in layer for q in o['qs']];assert len(busy)==len(set(busy)),(t,layer)
  for o in layer:
   if o['name']=='CX':u,v=o['qs'];assert abs(u//6-v//6)+abs(u%6-v%6)==1
   lines+=o['lines'];o['t']=ct[t]
  lines.append(bar)
 lines+=p['tail'];p['ops']=ops;m=p['meta'];D=m['data_qubits'];A=m['A'];B=m['B'];C=m['C'];round_times=[]
 for pair in list(zip(D,A))+list(zip(B,C)):round_times.append(max(o['t']for o in ops if o['name']=='CX'and o['qs']==list(pair)))
 m.update(R=min(round_times),round_start_range=[min(round_times),max(round_times)],native_depth=len(times),cx=sum(o['name']=='CX'for o in ops),source_task='v34m acceptance-headroom retarget',acceptance_floor=.5005)
 text='\n'.join(lines)+'\n';m['qasm_sha256']=hashlib.sha256(text.encode()).hexdigest();stem=H/name;stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(m,indent=2));stem.with_suffix('.plan.json').write_text(json.dumps(p,indent=1));return stem

def verify(stem):
 stem=Path(stem);start=time.monotonic();m=json.loads(stem.with_suffix('.json').read_text());r=tprep.check(stem.with_suffix('.qasm').read_text(),m['data_qubits'],p=0.0,shots=128,seed=0)
 out=dict(passed=r.passed,acceptance=r.acceptance,loss=r.score,details=str(r),seconds=time.monotonic()-start,qasm_sha256=m['qasm_sha256']);stem.with_suffix('.ideal.json').write_text(json.dumps(out,indent=2));assert r.passed and r.acceptance>1-1e-12 and r.score<1e-12,out;return out

def score(stem,procs=1):
 stem=Path(stem);v=verify(stem);sys.path.insert(0,str(H/'sparse'));import sparse_walsh as sw;sw.__file__=str(H/'sparse_output.py')
 with stem.with_suffix('.sparse.log').open('w')as f,contextlib.redirect_stdout(f):r=sw.run(stem,72,True,procs)
 import frontend
 native,_=frontend.parse_current(stem.with_suffix('.qasm').read_text());meta=json.loads(stem.with_suffix('.json').read_text());summary=dict(depth=max(o.time for o in native)+1)
 if 'A'in meta:
  times=[]
  for pair in list(zip(meta['data_qubits'],meta['A']))+list(zip(meta['B'],meta['C'])):times.append(max(o.time for o in native if o.kind=='CX'and o.qs==tuple(pair)))
  summary['round_range']=[min(times),max(times)]
 r['native_summary']=summary;meta['actual_native']=summary;stem.with_suffix('.json').write_text(json.dumps(meta,indent=2))
 r['noiseless_verification']=v;stem.with_suffix('.allorders.json').write_text(json.dumps(r,indent=2));return dict(stem=stem.name,loss=r['loss'],acceptance=r['acceptance'],seconds=r['seconds'])
