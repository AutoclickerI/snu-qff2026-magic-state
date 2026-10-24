import os,sys,json,re
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'));from model import Model
from tprep.noise import schedule
A=[1,14,8,9,2,16,15];B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28];D=[0,20,7,10,3,22,21]
rows=[]
for path in sorted(HERE.glob('*.qasm')):
 data=json.loads(path.with_suffix('.json').read_text())['data_qubits'];m=Model(path.read_text(),data);prog,steps,gaps=schedule(m.text)
 ops=[dict(step=t,name=i.name,qubits=list(qs)) for i,ss in zip(prog,steps) for qs,t in ss]
 def lastcx(u,v):return max(o['step'] for o in ops if o['name']=='CX' and o['qubits']==[u,v])
 rs=[lastcx(d,a) for d,a in zip(D,A)];rb=[lastcx(b,d) for b,d in zip(B,D)];rc=[lastcx(b,c) for b,c in zip(B,C)]
 assert len(set(rs))==1 and rb==[rs[0]+1]*7 and rc==rs,(path.name,rs,rb,rc)
 R=rs[0];stats=dict(file=path.name,R=R,B_data_steps=rb,last_measurement=max(o['step'] for o in ops if o['name'] in ('M','MX')),cx=sum(o['name']=='CX' for o in ops))
 for k,cells in [('A',A),('BC',B+C)]:
  init={q:max(o['step'] for o in ops if o['qubits']==[q] and o['name'] in ('R','RX','M','MX') and o['step']<R) for q in cells}
  cx=[o for o in ops if o['name']=='CX' and set(o['qubits'])<=set(cells) and o['step']<R and all(o['step']>=init[q] for q in o['qubits'])]
  stats[k+'_prep']=[min(init.values()),max(o['step'] for o in cx)];stats[k+'_cx']=len(cx);stats[k+'_init']=init
  stats[k+'_idle_steps']=sum(max(0,min(first+n,R)-max(first,init[q]+1)) for _,q,first,n in gaps if q in cells)
 stats['hops']={f'{u}->{v}':sorted([lastcx(u,v),lastcx(v,u)]) for u,v in [(4,10),(15,16),(8,9),(9,15),(15,21),(16,22)]}
 stats['tdg']={o['qubits'][0]:o['step'] for o in ops if o['name']=='T_DAG'}
 # Preserve exact model text timing, independent of the builder's planned steps.
 path.with_suffix('.judge_schedule.json').write_text(json.dumps(ops,indent=1));rows.append(stats);print(path.name,'R',R,'BC',stats['BC_prep'],'A',stats['A_prep'],'cx',stats['cx'],flush=True)
(HERE/'schedule_summary.json').write_text(json.dumps(rows,indent=2))
