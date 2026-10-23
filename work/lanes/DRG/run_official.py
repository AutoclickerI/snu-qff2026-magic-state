import json,sys,os
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work');import fast_check,tprep
q='work/submissions/v11_A1i_alap45.qasm'; j='work/submissions/v11_A1i_alap45.json'; text=open(q).read();data=json.load(open(j))['data_qubits']
out=[]
for seed in (0,1000,2000):
 r=fast_check.check(text,data,shots=10**8,seed=seed,procs=12)
 print(seed,r.score,r.sem,r.acceptance,r.n_2q,r.passed,flush=True);out.append({'seed':seed,'score':r.score,'sem':r.sem,'acceptance':r.acceptance,'n_2q':r.n_2q,'passed':r.passed})
print('mean',sum(x['score'] for x in out)/3)
json.dump(out,open('work/lanes/DRG/v11_A1i_alap45_seeds.json','w'),indent=2)
