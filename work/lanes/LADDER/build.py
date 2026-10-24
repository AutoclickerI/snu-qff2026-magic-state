"""Matched constraint ladder. Only emits lane-local files; no noise edits."""
import os,sys,json,re,collections,copy,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/TREP'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
import tprep.qasm as tq
tq.adjacent=lambda a,b:True
A=[1,14,8,9,2,16,15];B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28]
D=[0,20,7,10,3,22,21];PD=[0,20,7,4,3,15,8]
FREE=[5,11,12,16,17,18,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35]
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
A_ORDER=(0,1,2)
LAY=[[(0,2),(1,6),(3,5)],[(0,4),(1,2),(3,6)],[(0,6),(1,5),(3,4)]]

def read(stem):
 text=Path(str(stem)+'.qasm').read_text();h,raw,tail=S.qasm_ops(text);u=S.fold_units(raw);ts=native_times(text,u)
 return h,[dict(lines=x.lines,t=t,tag='unknown',source_i=i) for i,(x,t) in enumerate(zip(u,ts))],tail

def keys(ops):
 c=collections.Counter();out=[]
 for x in ops:
  k=tuple(x['lines']);out.append((k,c[k]));c[k]+=1
 return out

def qs(op):return [int(q) for q in re.findall(r'q\[(\d+)\]',op['lines'][0])]
def bits(op):return [int(q) for q in re.findall(r'c\[(\d+)\]',' '.join(op['lines']))]
def name(op):return S.Unit(op['lines'],[]).name

def source():
 h,op,tail=read(ROOT/'work/lanes/MAIN/v23h_c2c9')
 _,o0,_=read(ROOT/'work/lanes/MAIN/v20');m0=json.loads((ROOT/'work/lanes/MAIN/v20.json').read_text())
 prekeys={keys(o0)[i] for i in m0['prefix_unit_indices']};ks=keys(op)
 # All suffix hop gates, destination preparations, and source checks.
 hopcx={(10,4),(4,10),(15,16),(16,15),(8,9),(9,8),(9,15),(15,9),(15,21),(21,15),(16,22),(22,16)}
 for i,x in enumerate(op):
  if ks[i] in prekeys:x['tag']='prefix'
  elif x['t']>=45:x['tag']='round'
  elif name(x)=='CX' and tuple(qs(x)) in hopcx and (x['t']<37 or tuple(qs(x)) in {(16,22),(22,16)}):x['tag']='hop' # A's late 15->16 is its encoder
  elif set(bits(x))&{43,45,46,53,56,57} or (name(x)=='RESET' and qs(x)==[9] and x['t']==30):x['tag']='hop'
  elif set(qs(x))<=set(A):x['tag']='A'
  elif set(qs(x))<=set(B+C):x['tag']='BC'
  else:raise AssertionError(x)
 assert sum(x['tag']=='prefix' for x in op)==129
 assert {k:sum(name(x)=='CX' for x in op if x['tag']==k) for k in ['prefix','A','BC','hop','round']}==dict(prefix=75,A=11,BC=82,hop=12,round=23)
 return h,op,tail

H,BASE,TAIL=source()

def resetenc(cells,plus,R,tag):
 out=[]
 for i,q in enumerate(cells):out.append(dict(t=R-4,tag=tag,lines=[f'reset q[{q}];']+([f'h q[{q}];'] if (i in [0,1,3])!=plus else [])))
 for k,lay in enumerate([LAY[j] for j in A_ORDER] if plus else LAY):
  for c,t in lay:
   a,b=(cells[t],cells[c]) if plus else (cells[c],cells[t])
   out.append(dict(t=R-3+k,tag=tag,lines=[f'cx q[{a}],q[{b}];']))
 return out

def stripbits(tail,removed):
 out=[]
 for s in tail:
  if s.startswith('// DETECTOR'):
   bs=[int(b) for b in re.findall(r'c\[(\d+)\]',s) if int(b) not in removed]
   if bs:out.append('// DETECTOR '+' '.join(f'c[{b}]' for b in bs))
  else:out.append(s)
 return out

def replace(ops,tail,tag,new):
 gone=[x for x in ops if x['tag']==tag]
 return [x for x in ops if x['tag']!=tag]+new,stripbits(tail,{b for x in gone for b in bits(x)})

def remap(ops,mapping,tags):
 for x in ops:
  if x['tag'] in tags:
   x['lines']=[re.sub(r'q\[(\d+)\]',lambda m:f'q[{mapping.get(int(m[1]),int(m[1]))}]',s) for s in x['lines']]

def compact_prefix(ops,end=32):
 # Fixed per-cell order, latest possible placement <= end; never delay a unit.
 latest={q:end for q in range(36)}
 for x in sorted([o for o in ops if o['tag']=='prefix'],key=lambda o:(o['t'],o.get('source_i',0)),reverse=True):
  x['t']=min(x['t'],*(latest[q] for q in set(qs(x))))
  for q in set(qs(x)):latest[q]=x['t']-1

def direct_readout(ops,tail):
 # Undo the two reversible classical-parity readout CXs and update the XORs.
 new=[]
 for x in ops:
  if x['tag']=='round' and name(x)=='CX' and tuple(qs(x)) in [(19,25),(17,16)]:continue
  if x['tag']=='round' and set(bits(x))&{19,22,23,24}:x['t']-=1
  new.append(x)
 # A bit 19 previously measured A5 XOR C3. C bit22 previously C1 XOR C2.
 out=[]
 for s in tail:
  bs=set(map(int,re.findall(r'c\[(\d+)\]',s)))
  if s.startswith('// DETECTOR'):
   if 19 in bs:bs.symmetric_difference_update({24})
   if 22 in bs:bs.symmetric_difference_update({23})
   s='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bs))
  out.append(s)
 return new,out

def emit(stem,ops,tail,data,R,note,extra=None):
 ops=sorted(copy.deepcopy(ops),key=lambda x:x['t'])
 used={q for o in ops for q in qs(o)};bar='barrier '+','.join(f'q[{q}]' for q in sorted(used))+';'
 out=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];','creg c[256];'];line_tags={};units=[]
 # Empty logical steps must not collapse; an isolated fresh measured clock is noise-irrelevant.
 clock=next((q for q in range(36) if q not in used),None)
 for t in range(max(o['t'] for o in ops)+1):
  layer=[o for o in ops if o['t']==t]
  if not layer:
   clock = clock if clock is not None else next((q for q in range(36) if any(q in qs(o) and o['t'] < t for o in ops) and not any(q in qs(o) and o['t'] >= t for o in ops) and S.Unit(max((o for o in ops if q in qs(o)), key=lambda o:o['t'])['lines'], []).name == 'MEASURE'), None)
   assert clock is not None,(stem,'no disposable measured clock cell',t)
   layer=[dict(t=t,tag='clock',lines=[f'measure q[{clock}] -> c[255];'])]
  busy=set()
  for o in layer:
   assert not busy&set(qs(o)),(stem,'cell conflict',t,busy&set(qs(o)),o)
   busy.update(qs(o))
   units.append(o)
   for s in o['lines']:line_tags[str(len(out)+1)]=o['tag'];out.append(s)
  if t<max(o['t'] for o in ops):out.append(bar)
 out+=tail;text='\n'.join(out)+'\n'
 (OUT/(stem+'.qasm')).write_text(text)
 h,raw,tt=S.qasm_ops(text);uu=S.fold_units(raw);nt=native_times(text,uu)
 assert [u.lines for u in uu]==[o['lines'] for o in units],(stem,'fold changed')
 assert nt==[o['t'] for o in units],(stem,'native time mismatch',[(a,b) for a,b in zip(nt,[o['t'] for o in units]) if a!=b])
 md=dict(data_qubits=data,R=R,CX=sum(name(o)=='CX' for o in ops),native_depth=max(nt)+1,note=note,units=units,line_tags=line_tags)
 if extra:md.update(extra)
 (OUT/(stem+'.qasm')).write_text(text);(OUT/(stem+'.json')).write_text(json.dumps(md,indent=2)+'\n')
 print(stem,md['CX'],R,md['native_depth'],note,flush=True)
 return copy.deepcopy(ops),list(tail)

def main():
 emit('f00_base',BASE,TAIL,D,45,'Canonical v23h_c2c9, same native operations and schedule')
 op,tail=replace(copy.deepcopy(BASE),TAIL,'BC',resetenc(B,False,45,'BC')+resetenc(C,False,45,'BC'))
 emit('f01_sepBC',op,tail,D,45,'Replace only BC preparation, 82 -> 18 CX; original 7-CX BC check and readout retained')
 op,tail=replace(op,tail,'A',resetenc(A,True,45,'A'))
 emit('f02_stdA',op,tail,D,45,'Replace A preparation/checks by standard 9-CX encoder ending at44')
 op,tail=replace(op,tail,'hop',[])
 # The original ancilla cells overlap unmoved data. Fresh reset ancilla lifetimes can be relabelled freely.
 mp=dict(zip(A+B+C,FREE));remap(op,mp,{'A','BC','round'})
 # Round data endpoints must follow unmoved data; remap above also touched data q10,22,21 only if in A/B/C (none).
 dm=dict(zip(D,PD))
 for x in op:
  if x['tag']=='round' and name(x)=='CX':
   x['lines']=[re.sub(r'q\[(\d+)\]',lambda m:f'q[{dm.get(int(m[1]),int(m[1]))}]',s) for s in x['lines']]
 # Remapping must use separate roles: FREE contains old output IDs, so rebuild round from baseline with simultaneous role map.
 op=[x for x in op if x['tag']!='round']+[copy.deepcopy(x) for x in BASE if x['tag']=='round']
 remap(op,{**mp,**dm},{'round'})
 emit('f03_nohops',op,tail,PD,45,'Remove 12 hop CX plus destination/source guards; reset ancillas relabelled onto 21 prefix-free cells')
 compact_prefix(op)
 emit('f04_prefix32_R45',op,tail,PD,45,'Only retime prefix to latest feasible completion at32; suffix remains R45')
 compact=copy.deepcopy(op)
 for R in [42,39,36,33]:
  oo=copy.deepcopy(compact)
  for x in oo:
   if x['tag'] in {'A','BC','round'}:x['t']-=45-R
  emit('f05_R'+str(R),oo,tail,PD,R,'Only shift entire standard-block suffix earlier; compact v23 prefix fixed')
 base33=oo
 # Direct readout before relabelling makes original pair recognition unambiguous.
 dr=[copy.deepcopy(x) for x in BASE if x['tag']=='round'];dr,dt=direct_readout(dr,tail)
 for x in dr:x['t']-=12
 remap(dr,{**mp,**dm},{'round'})
 oo=[copy.deepcopy(x) for x in base33 if x['tag']!='round']+dr
 emit('f06_sep33_v23',oo,dt,PD,33,'Only remove the two readout parity CXs and read A/C directly; v23 prefix')
 # Canonical older reference copied with measured provenance.
 h,old,ot=read(ROOT/'work/lanes/MAIN/gf/sep33')
 for x in old:
  x['tag']='round' if x['t']>=33 else 'A' if set(qs(x))<=set(FREE[:7]) else 'BC' if set(qs(x))<=set(FREE[7:]) else 'prefix'
  if x['tag']=='A' and name(x)=='CX':x['t']=30+A_ORDER.index(x['t']-30)
 emit('f07_sep33_old',old,ot,PD,33,'Older v11/v16 prefix, 9-CX ABC, direct readout; A layer order '+str(A_ORDER))
 # One at a time reimposition on f05_R33; restore the original reset/MX policy and guards with each encoder.
 for tag in ['BC','A']:
  repl=[copy.deepcopy(x) for x in BASE if x['tag']==tag]
  for x in repl:x['t']-=12
  remap(repl,mp,{tag})
  rev,rt=replace(copy.deepcopy(base33),tail,tag,repl)
  # Restore full original detector definitions, dropping bits absent in this reverse circuit.
  live={b for x in rev for b in bits(x)}
  rt=stripbits(TAIL,set(range(256))-live)
  emit('r_'+tag,rev,rt,PD,33,'Only restore original '+tag+' prep at its original offset from R; ancilla lifetimes on prefix-free cells')
 # Reverse timing is exactly f04; prefix stretched at R33 is an infeasible requirement.
 # Hops: earliest per-cell schedule, all data sources follow their unchanged compact prefix.
 hop=[copy.deepcopy(x) for x in BASE if x['tag']=='hop']
 pre=[copy.deepcopy(x) for x in base33 if x['tag']=='prefix']
 avail={q:0 for q in range(36)}
 for x in pre:
  for q in qs(x):avail[q]=max(avail[q],x['t']+1)
 for x in sorted(hop,key=lambda x:(x['t'],x['source_i'])):
  x['t']=max(avail[q] for q in qs(x))
  for q in qs(x):avail[q]=x['t']+1
 earliest=max(avail[q] for q in D)
 (OUT/'reverse_hops_feasibility.json').write_text(json.dumps(dict(earliest_R=earliest,reason='Same directed hop/guard per-cell order, prefix fixed; ASAP resource lower bound',hop=hop),indent=2))
 # Price hops at the first feasible R with a matched no-hop reference. Space reserved for the entire hop path.
 RR=max(earliest,37)
 usedhop=set(D+PD)|{q for x in hop for q in qs(x)}
 acells=[q for q in range(36) if q not in usedhop][:21];assert len(acells)==21
 for mode in ['nohop','hop']:
  mop=copy.deepcopy(pre)+(copy.deepcopy(hop) if mode=='hop' else [])
  for tag,cc,plus in [('A',acells[:7],True),('BC',acells[7:14],False),('BC',acells[14:],False)]:mop+=resetenc(cc,plus,RR,tag)
  dd=D if mode=='hop' else PD
  mr=[copy.deepcopy(x) for x in BASE if x['tag']=='round']
  for x in mr:x['t']+=RR-45
  remap(mr,{**dict(zip(A+B+C,acells)),**dict(zip(D,dd))},{'round'});mop+=mr
  mt=stripbits(TAIL,set(range(256))-{b for x in mop for b in bits(x)})
  emit('r_hops_'+mode,mop,mt,dd,RR,'Matched reverse hops comparison at feasible R='+str(RR))
 (OUT/'source_receipts.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'work/lanes/MAIN/v23h_c2c9.qasm',ROOT/'work/lanes/MAIN/v20.json',ROOT/'work/lanes/MAIN/gf/sep33.qasm']},indent=2))
if __name__=='__main__':main()
