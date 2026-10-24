import os,sys,json,hashlib
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
sys.dont_write_bytecode=True
from score import BASE,tq,tp,tc
from tprep.exact import verify
from tprep.parse import declarations,parse
from tprep.noise import STANDARD,schedule
out={}
for name in sys.argv[1:]:
 q=(BASE/(name+'.qasm')).read_text();j=json.loads((BASE/(name+'.json')).read_text());text,labels,errors=tq.convert(q)
 frame,post=declarations(text);ex=verify(text,j['data_qubits'],frame=frame,postselect=post)
 r=tc.check_stim(text,j['data_qubits'],shots=64,p=0,seed=0)
 ins=parse(text);_,steps,gaps=schedule(text)
 out[name]={'qasm_sha256':hashlib.sha256(q.encode()).hexdigest(),'bytes':len(q.encode()),'statements':sum(l.split('//')[0].count(';') for l in q.splitlines()),'measure_reset':sum(len(i.qubits) for i in ins if i.name in ['M','MX','R','RX']),'T_count':sum(len(i.qubits) for i in ins if i.name in ['T','T_DAG']),'CX_count':sum(len(i.qubits)//2 for i in ins if i.name=='CX'),'active_qubits':len(set(q for i in ins for q in i.qubits)),'rotation_rank':ex['rank'],'rank_limit':22,'noiseless':ex,'format_except_grid':r.format_ok,'class_ok':r.class_ok,'correctness_ok':r.correct_ok,'grid_enforced':False,'diagnosis':str(r.diagnosis),'depth':max(t for row in steps for qs,t in row)+1,'terminal_data_idles':{q:sum(n for i,qu,t,n in gaps if qu==q and i==max(k for k,x in enumerate(ins) if q in x.qubits)) for q in j['data_qubits']}}
 assert r.format_ok and r.class_ok and r.correct_ok,(name,str(r))
 print(name,json.dumps(out[name]),flush=True)
(BASE/'judge_limits.json').write_text(json.dumps(out,indent=2)+'\n')
