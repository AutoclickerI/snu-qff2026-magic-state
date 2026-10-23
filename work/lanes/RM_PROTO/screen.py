import sys,os,time,json
sys.dont_write_bytecode=True
from score import *
for name in sys.argv[1:]:
 q=(BASE/(name+'.qasm')).read_text();j=json.loads((BASE/(name+'.json')).read_text());ev=exact2.Eval(q,j['data_qubits'])
 first=float(ev.fp@ev.n_single);a1=float(ev.fp@(1-ev.a_single))
 out={'name':name,'first':first,'A1':a1,'approx_acceptance':float(np.exp(-a1))}
 r=exact2.run(ev,procs=1);out.update(second=r['loss2'],acc2=r['acc2'])
 print(json.dumps(out),flush=True)
 with (BASE/'subset_screen.jsonl').open('a') as f:f.write(json.dumps(out)+'\n')
