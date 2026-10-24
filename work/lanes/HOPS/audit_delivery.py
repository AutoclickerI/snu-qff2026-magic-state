from build import *
import hashlib
p=OUT/'best';text=p.with_suffix('.qasm').read_text();h,u,ts,tail,m=read(p)
def last(c,t):return max(tt for x,tt in zip(u,ts)if x.lines==[f'cx q[{c}],q[{t}];'])
ra=[last(d,a)for d,a in zip(m['data_qubits'],A)];rc=[last(b,c)for b,c in zip(B,C)];rb=[last(b,d)for b,d in zip(B,m['data_qubits'])]
assert ra==rc==[45]*7 and rb==[46]*7
assert max(ts)+1==m['native_depth']==48
assert sum(x.name=='CX'for x in u)==m['CX']==203
meta=dict(file='best.qasm',sha256=hashlib.sha256(text.encode()).hexdigest(),data_qubits=m['data_qubits'],data_to_A=ra,B_to_C=rc,B_to_data=rb,CX=203,native_depth=48,detectors=len([x for x in tail if x.startswith('// DETECTOR')]),native_operations=[dict(t=t,lines=x.lines)for x,t in zip(u,ts)])
p.with_suffix('.judge_schedule.json').write_text(json.dumps(meta,indent=2)+'\n')
print({k:v for k,v in meta.items()if k!='native_operations'})
