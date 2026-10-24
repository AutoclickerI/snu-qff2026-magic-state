import json,sys
sys.path.insert(0,'work');import fast_check
s='work/lanes/FRESH/corr_d11_k57_s35_002_freshbase_w0_fast_zlast';t=open(s+'.qasm').read();d=json.load(open(s+'.json'))['data_qubits'];r=fast_check.check(t,d,shots=10**8,seed=2000,procs=4);print(r)
