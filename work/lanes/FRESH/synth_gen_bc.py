"""BCPOL contracts. Independent CSS target and exhaustive X-fault verification."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import itertools,collections
import original_synth_gen as O
import ft_gen as ft
import stim
B,C,ROWS=ft.B,ft.C,ft.ROWS
nb=O.nb

def span(vs):
 s={0}
 for v in vs:s|={x^v for x in list(s)}
 return s

def generators(kind='policy',value=9,endpoint_rank=None):
 bg=[sum(1<<B[i] for i in row) for row in ROWS]
 cg=[sum(1<<C[i] for i in row) for row in ROWS]
 if kind=='endpoint':
  rank=endpoint_rank or (5 if value else 6)
  if rank==3:cg=[]
  elif rank==4:cg=[__import__('functools').reduce(int.__xor__,[cg[i] for i in range(3) if value>>i&1],0)]
  elif rank==5:
   coeff=[a for a in range(1,8) if (a&value).bit_count()%2==0]
   cg=[__import__('functools').reduce(int.__xor__,[cg[i] for i in range(3) if a>>i&1],0) for a in coeff[:2]]
 elif kind=='c6':cg=[x&~(1<<C[value]) for x in cg]
 return bg+cg

def extra_cells(value,endpoint_rank=5):
 gs=generators('endpoint',value,endpoint_rank)[3:]
 zspan=span([sum(1<<i for i in row) for row in ROWS]+[127]);out=[]
 for i,q in enumerate(C):
  if all(not(g>>q&1) for g in gs) and (1<<i) not in zspan:
   zspan |= {v^(1<<i) for v in list(zspan)};out.append(q)
 assert len(out)==6-endpoint_rank
 return out

def sig(e,kind,value):
 sc=ft.sig(e-({C[value]} if kind=='c6' else set()),C)
 return ft.sig(e,B),sc

def violates(sb,sc,kind,value):
 if kind=='policy':return sb==sc and sb not in (0,value)
 if kind=='endpoint':return sc==0 and ft.dangerous(sb)
 return (sb^sc) in (0,9+value) and ft.dangerous(sb)

def faults(d):
 out=[];res=collections.Counter();kind=d.get('kind','policy');value=d.get('value',9)
 for src in ft.sources(d,d['cells']):
  e=ft.propagate(d['ops'],src);sb,sc=sig(e,kind,value)
  bad=violates(sb,sc,kind,value)
  if kind=='endpoint' and d.get('extra_check') and bool(set(extra_cells(value,d.get('endpoint_rank',5)))&e):bad=False
  if bad:out.append(src)
  accepted=(sb==sc) if kind=='policy' else (sc==0 and not(d.get('extra_check') and set(extra_cells(value,d.get('endpoint_rank',5)))&e)) if kind=='endpoint' else ((sb^sc) in (0,9+value))
  if accepted and sb:res[sb]+=1
 return out,dict(res)

def verify(d):
 kind=d.get('kind','policy');value=d.get('value',9);cells=d['cells'];gs=generators(kind,value,d.get('endpoint_rank'))
 c=stim.Circuit()
 for q in cells:c.append('R',[q])
 for q in d['pivots']:c.append('H',[q])
 for layer in d['ops']:
  used=set()
  for u,v in layer:
   assert v in nb(u) and not ({u,v}&used);used|={u,v};c.append('CX',[u,v])
 sim=stim.TableauSimulator();sim.do(c)
 if kind=='c6' and d.get('helper_x'):sim.postselect_x(C[value],desired_value=False)
 xs={q:1<<q for q in d['pivots']}
 for layer in d['ops']:
  for u,v in layer:
   for q,x in xs.items():
    if x>>u&1:xs[q]^=1<<v
 if kind=='c6' and d.get('helper_x'):xs={q:x&~(1<<C[value]) for q,x in xs.items()}
 target_ok=span(gs)==span(xs.values())
 expectations=[]
 for g in gs:
  p=stim.PauliString(36)
  for q in cells:
   if g>>q&1:p[q]='X'
  expectations.append(sim.peek_observable_expectation(p))
 bad,res=faults(d)
 return dict(stim_target_pass=target_ok and all(x==1 for x in expectations),policy_pass=not bad,policy_faults=len(bad),clean_pass=not ft.faults(d,cells,'clean'),residual_classes=res,cx=sum(map(len,d['ops'])),depth=len(d['ops']))

class Model(O.Model):
 def __init__(self,D,cap,seed=0,kind='policy',value=9,helper_x=False,extra_check=False,endpoint_rank=None):
  self.kind,self.value=kind,value;self.endpoint_rank=endpoint_rank or (5 if kind=='endpoint' and value else 6)
  self.project_helper=helper_x;self.extra_check=extra_check
  assert not extra_check or (kind=='endpoint' and self.endpoint_rank in (3,4,5))
  gs=generators(kind,value,self.endpoint_rank)
  targets={q:sum(((g>>q)&1)<<j for j,g in enumerate(gs)) for q in B+C}
  signatures={q:ft.sig({q},B)|(ft.sig({q}-({C[value]} if kind=='c6' else set()),C)<<4) for q in B+C}
  super().__init__(D,cap,seed,target_rows=targets,signature_rows=signatures,free_target_x=[C[value]] if kind=='c6' and helper_x else [],extra_signature_cells=extra_cells(value,self.endpoint_rank) if extra_check else ())
  self.card(list(self.nz.values()),len(gs))
 def cut(self,source):
  if source in self.added:return
  self.added.add(source);t,qs=source;hs=list(self.h[t][qs[0]]);guard=[]
  if len(qs)==2:
   hs=[self.xor(a,b) for a,b in zip(hs,self.h[t][qs[1]])];guard=[-self.sel[t-1][qs]]
  if self.kind=='endpoint':
   dif=hs[4:];diffs=[0];bad=range(1,9)
  else:
   dif=[self.xor(hs[i],hs[i+4]) for i in range(4)]
   diffs=[0,9+self.value] if self.kind=='c6' else [0]
   bad=[v for v in range(1,16) if v!=self.value] if self.kind=='policy' else range(1,9)
  for diff in diffs:
   for sb in bad:self.add(guard+[(-z if diff>>i&1 else z) for i,z in enumerate(dif)]+[(-z if sb>>i&1 else z) for i,z in enumerate(hs[:4])])
 def candidate(self):return dict(super().candidate(),kind=self.kind,value=self.value,helper_x=self.project_helper,extra_check=self.extra_check,endpoint_rank=self.endpoint_rank)

def trace(d):return repr((sorted(d['pivots']),[(q,[tuple(e) for l in d['ops'] for e in l if q in e]) for q in sorted(d['cells'])]))
