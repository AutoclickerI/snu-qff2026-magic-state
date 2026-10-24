import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,hashlib,ast,itertools
H=Path(__file__).resolve().parent;D=H/'a35';ROOT=H.parents[2]
sys.path[:0]=[str(D/'sparse'),str(H)]
from a34_search import read,A,DATA
import frontend as f
p=ROOT/'work/lanes/EXENC/exenc.py';tree=ast.parse(p.read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='score');ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(p),'exec'),ns);score=ns['score']
def span(rows):
 out={0}
 for r in rows:out|={v^r for v in list(out)}
 return out
rows=[sum(1<<i for i in r) for r in [[0,2,4,6],[1,2,5,6],[3,4,5,6]]];stabs=span(rows);flagmask=sum(1<<i for i in [2,3,6]);assert flagmask^127 in stabs and flagmask not in stabs
out=[]
for name in ['v35a','v35b']:
 stem=D/'inputs'/name;s=read(stem);ops,dets=f.parse_current(s[0]);prep=[u for u in ops if u.kind=='CX' and 38<=u.time<=43 and set(u.qs)<=set(A)];layers=[[list(u.qs) for u in prep if u.time==t] for t in range(38,44)];assert len(prep)==11
 flag={8}
 for u in reversed([u for u in ops if u.kind=='CX' and u.time>=44 and set(u.qs)<=set(A)]):
  c,t=u.qs
  if c in flag:flag.symmetric_difference_update({t})
 assert flag=={8,9,15};back=set(flag)
 for u in reversed(prep):
  c,t=u.qs
  if c in back:back.symmetric_difference_update({t})
 assert back=={8}
 vec=score(layers,[1,14,8,2],A,A);assert vec==[0,3,4,0,4,0,0,0];blind=sum(vec[i+1] for i in [2,3,6]);assert blind==4
 f.DATA=DATA;m=f.make_model(ops,dets);eng=f.Engine(m);aa,nn=eng.ntable(0,0);assert abs(eng.A0-1)<1e-10 and abs(nn[0])<1e-10
 pairs=[dict(pair=[i,j],detected=bool(((1<<i|1<<j)&flagmask).bit_count()%2)) for i,j in itertools.combinations(range(7),2)];assert sum(r['detected'] for r in pairs)==12
 r=dict(source=name,qasm_sha256=hashlib.sha256(s[0].encode()).hexdigest(),CX=sum(u.name=='CX' for u in s[3]),native_depth=max(s[4])+1,encoder_layers=layers,plus_pivots=[1,14,8,2],flag_output=sorted(flag),flag_input=sorted(back),flag_code_support=[2,3,6],local_vector_units=vec,blind_units=blind,detected_units=sum(vec)-blind,phase_pairs=pairs,ideal_acceptance=eng.A0,ideal_loss=float(nn[0]),scope='GF(2) and native schedule exact; ideal arithmetic floating. Local EXENC proxy is not full finite-p loss.')
 out.append(r);print(name,r['qasm_sha256'],r['CX'],r['native_depth'],vec,blind,flush=True)
assert out[0]['qasm_sha256']=='b606bd3902d28000e0ee073fc50a7c0870aaa1f2e1ab8947fdb7fd70c762218e'
(D/'current_contract_certificate.json').write_text(json.dumps(out,indent=2))
