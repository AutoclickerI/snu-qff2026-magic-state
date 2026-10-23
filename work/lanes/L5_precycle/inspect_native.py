from search_v10 import *
from tprep.qasm import to_stim
from tprep.noise import apply_noise
import xtim
for n in ['v10_reference','nreset_s4_b0']:
    text=(HERE/(n+'.qasm')).read_text();data=json.loads((HERE/(n+'.json')).read_text())['data_qubits']
    st,_=to_stim(text)
    start=time.monotonic();r=tprep.check(text,data,shots=100000,seed=0)
    print(n,'seconds',time.monotonic()-start,'score',r.score,'diagnosis',r.diagnosis,flush=True)
    (HERE/(n+'_stim.txt')).write_text(st)
