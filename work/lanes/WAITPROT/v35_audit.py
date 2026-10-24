"""Compare every finalist's sparse frontend with the official judge Model."""
from v35_build import *

def audit(name):
 p=V/name;text=p.with_suffix('.qasm').read_text();ev=exact2.Eval(text,DATA)
 fa.DATA=DATA;oo,dd=fa.parse_current(text);original=fa.noise_blocks
 fa.noise_blocks=lambda text,p,first_order=True:original(text,p,first_order=False)
 try:m=fa.make_model(oo,dd)
 finally:fa.noise_blocks=original
 records=[];rows=[]
 for i,ins in enumerate(ev.m.prog):
  if ins.name in ('M','MX'):
   k=int(re.search(r'instruction (\d+)',ev.m.labels[i]).group(1));raw=exact2.qasm_lines(text)[k-1][1]
   records.append(int(re.search(r'c\[(\d+)\]',raw).group(1)))
  elif ins.name=='DETECTOR':rows.append(frozenset(records[len(records)-int(t[5:-1])]for t in ins.targets))
 reorder=[rows.index(frozenset(row))for row in dd]
 assert len(m.rots)==len(ev.m.rots) and m.Q==ev.m.Q
 assert all(a[:3]==b[:3]and abs(a[3]-b[3])<1e-15 for a,b in zip(m.rots,ev.m.rots))
 assert all(m.proj_m[i]==ev.m.proj_m[j]for i,j in enumerate(reorder))
 assert len(m.chans)==len(ev.m.chans) and len(m.faults)==len(ev.m.faults)
 for a,b in zip(m.chans,ev.m.chans):assert list(a['qs'])==list(b['qubits'])and abs(a['p']-b['prob'])<1e-16
 for a,b in zip(m.faults,ev.m.faults):
  d=sum(((b['d']>>j)&1)<<k for k,j in enumerate(reorder))
  assert(a['chan'],a['pauli'],a['s'],a['e'],a['d'])==(b['chan'],b['pauli'],b['s'],b['e'],d)
  assert abs(a['p']-b['p'])<1e-16
 actual=[(x.name,tuple(x.qubits),ev.m.steps[i][0][1])for i,x in enumerate(ev.m.prog)if x.qubits]
 planned=[('T_DAG'if o.kind=='TDG'else o.kind,tuple(o.qs),o.time)for o in oo]
 assert actual==planned,('native mismatch',name)
 r=dict(stem=name,sha256=hashlib.sha256(text.encode()).hexdigest(),channels=len(m.chans),faults=len(m.faults),detectors=len(dd),all_channels_faults_rotations_projectors_and_observables_match=True,native_ticks_match=True,c1=float(ev.fp@ev.n_single))
 p.with_suffix('.audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
 return r
if __name__=='__main__':
 for name in sys.argv[1:]:audit(name)
