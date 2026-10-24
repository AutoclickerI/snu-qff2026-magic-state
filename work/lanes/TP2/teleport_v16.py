"""Grid-valid reference conversion: teleport into A, move B into measured D.
B's known X offsets enter C's syndrome/parity record and leave O after B->O;
reset destinations is the simple explicit version used here. Verification is
performed immediately before the B move to bound the unchecked interval.
"""
import os,sys,json,re
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent
variant=sys.argv[1] if len(sys.argv)>1 else 'bmove'
reuse=variant=='reuse';omove=variant in ('omove','reuse')
sys.path.insert(0,str(H.parent/'DR'))
from steane_full import GENS,LAYOUTS
src=(H.parents[1]/'candidates/v16_bc2m.qasm').read_text().splitlines()
by={};t=0;dets=[]
for s in src:
 if s.startswith('barrier'):t+=1;continue
 if s.startswith('// DETECTOR'):
  rec=list(map(int,re.findall(r'c\[(\d+)\]',s)))
  if all(x<14 or x>=35 for x in rec):dets.append(s)
 if t>=50 or s.startswith(('OPENQASM','include','qreg','creg','//')) or not s.strip():continue
 by.setdefault(t,[]).append(s)
lay=LAYOUTS['L5'];d,o,b,c=[lay[k] for k in 'dabc'];bits={};n=47
for i in range(7):
 by.setdefault(50,[]).append(f'cx q[{o[i]}],q[{d[i]}];')
 bits['d',i]=n;by.setdefault(51,[]).append(f'measure q[{d[i]}] -> c[{n}];');n+=1
 # Move O back to D, or B into D. Both are strictly grid local.
 tv=53 if reuse else (54 if omove else 52)
 by.setdefault(tv,[]).append(f'cx q[{b[i]}],q[{c[i]}];')
 bits['c',i]=n;by.setdefault(tv+1,[]).append(f'measure q[{c[i]}] -> c[{n}];');n+=1
 if not reuse:by.setdefault(52,[]).append(f'reset q[{d[i]}];')
 srcq=o[i] if omove else b[i];shift=int(reuse)
 by.setdefault(53-shift,[]).append(f'cx q[{srcq}],q[{d[i]}];')
 by.setdefault(54-shift,[]).append(f'cx q[{d[i]}],q[{srcq}];')
 ctl,tgt=(b[i],d[i]) if omove else (d[i],o[i])
 by.setdefault(55-shift,[]).append(f'cx q[{ctl}],q[{tgt}];')
 bits['b',i]=n;by.setdefault(56-shift,[]).extend([f'h q[{ctl}];',f'measure q[{ctl}] -> c[{n}];']);n+=1
bar='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
out=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{n}];']
end=55 if reuse else 56
for t in range(end+1):
 out.append(f'// step {t}');out+=by.get(t,[])
 if t<end:out.append(bar)
for k in 'dbc':
 for S in GENS:dets.append('// DETECTOR '+' '.join(f'c[{bits[k,i]}]' for i in S))
dets.append('// DETECTOR '+' '.join(f'c[{bits["c",i]}]' for i in range(7)))
out+=dets;out+=['// FRAME_X(0) '+('' if reuse else ' '.join(f'c[{bits["d",i]}]' for i in range(7))),'// FRAME_Z(0)']
text='\n'.join(out)+'\n';stem=H/('tp_v16' if variant=='bmove' else 'tp_v16_'+variant)
stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=(d if omove else o),R=50,Rmax=50,last_step=end,O=o,B=b,C=c,moves=13,cx=text.count('cx '),source=f'v16 same prefix+prep, teleport, {variant} to measured D'),indent=2))
print(stem)
